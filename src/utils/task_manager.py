"""
非同步任務管理器 (Async Task Manager)
使用 Python asyncio 實現輕量級背景任務佇列

版本: v1.0.0
最後更新: 2026-02-05
"""

import asyncio
import uuid
import time
import functools
from typing import Dict, Optional, Callable, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import json

from src.utils.logger import get_logger

logger = get_logger()


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"      # 等待執行
    RUNNING = "running"      # 執行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失敗
    CANCELLED = "cancelled"  # 已取消


@dataclass
class TaskProgress:
    """任務進度"""
    task_id: str
    task_name: str
    status: TaskStatus
    progress: float  # 0.0 - 1.0
    message: str
    created_at: str
    priority: int = 5  # 1-10, 數字越大優先級越高
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None  # 關聯用戶 ID
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class TaskManager:
    """
    非同步任務管理器
    
    使用 asyncio 在背景執行耗時任務，支援：
    - 任務提交與追蹤
    - 進度更新與推播
    - 結果儲存與查詢
    - 任務取消
    """
    
    def __init__(self, enable_persistence: bool = True):
        self.tasks: Dict[str, TaskProgress] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.enable_persistence = enable_persistence
        self.db = None  # 延遲初始化（避免循環依賴）
        self.thread: Optional[threading.Thread] = None
        self._shutdown = False
        
        # 進度訂閱者 (task_id -> callback)
        self.progress_subscribers: Dict[str, List[Callable]] = {}
    
    def start(self):
        """啟動任務管理器（在獨立線程中運行 event loop）"""
        if self.thread is not None and self.thread.is_alive():
            logger.warning("TaskManager 已經在運行")
            return
        
        self._shutdown = False
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        
        # 等待 event loop 初始化完成
        for _ in range(50):  # 最多等待 5 秒
            if self.loop is not None:
                logger.info("TaskManager 已啟動")
                
                # 初始化資料庫連線
                if self.enable_persistence:
                    self._init_database()
                    self._restore_pending_tasks()
                
                return
            time.sleep(0.1)
        
        raise RuntimeError("TaskManager 啟動失敗：event loop 未能初始化")
    
    def _run_event_loop(self):
        """在獨立線程中運行 asyncio event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_forever()
        finally:
            # 清理
            self.loop.close()
            logger.info("TaskManager event loop 已關閉")
    
    def _init_database(self):
        """初始化資料庫連線"""
        try:
            from src.utils.database import get_database
            self.db = get_database()
            logger.info("TaskManager 資料庫連線已建立")
        except Exception as e:
            logger.error(f"TaskManager 資料庫初始化失敗: {e}")
            self.enable_persistence = False
    
    def _restore_pending_tasks(self):
        """從資料庫恢復 pending 任務"""
        if not self.db:
            return
        
        try:
            pending_tasks = self.db.get_pending_tasks(limit=100)
            restored_count = 0
            
            for task_data in pending_tasks:
                task_id = task_data['task_id']
                
                # 重建 TaskProgress 物件
                task_progress = TaskProgress(
                    task_id=task_id,
                    task_name=task_data['task_name'],
                    status=TaskStatus.PENDING,
                    priority=task_data.get('priority', 5),
                    progress=task_data.get('progress', 0.0),
                    message=task_data.get('message', '等待執行'),
                    created_at=task_data['created_at'],
                    metadata=json.loads(task_data['metadata']) if task_data.get('metadata') else None,
                    user_id=task_data.get('user_id')
                )
                
                self.tasks[task_id] = task_progress
                restored_count += 1
            
            if restored_count > 0:
                logger.info(f"已從資料庫恢復 {restored_count} 個待執行任務")
        
        except Exception as e:
            logger.error(f"恢復待執行任務失敗: {e}")
    
    def _persist_task(self, task_progress: TaskProgress):
        """將任務持久化到資料庫"""
        if not self.enable_persistence or not self.db:
            return
        
        try:
            task_data = {
                'task_id': task_progress.task_id,
                'task_name': task_progress.task_name,
                'status': task_progress.status.value,
                'priority': task_progress.priority,
                'progress': task_progress.progress,
                'message': task_progress.message,
                'result': json.dumps(task_progress.result) if task_progress.result else None,
                'error': task_progress.error,
                'metadata': json.dumps(task_progress.metadata) if task_progress.metadata else None,
                'created_at': task_progress.created_at,
                'started_at': task_progress.started_at,
                'completed_at': task_progress.completed_at,
                'user_id': task_progress.user_id
            }
            
            self.db.save_task(task_data)
        
        except Exception as e:
            logger.error(f"任務持久化失敗 (task_id={task_progress.task_id}): {e}")
    
    def shutdown(self):
        """關閉任務管理器"""
        self._shutdown = True
        
        if self.loop:
            # 取消所有運行中的任務
            for task_id, task in self.running_tasks.items():
                if not task.done():
                    self.loop.call_soon_threadsafe(task.cancel)
            
            # 停止 event loop
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("TaskManager 已關閉")
    
    def submit_task(
        self,
        func: Callable,
        task_name: str,
        *args,
        priority: int = 5,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """
        提交非同步任務
        
        Args:
            func: 要執行的函數（可以是同步或異步）
            task_name: 任務名稱
            *args, **kwargs: 傳給函數的參數
            priority: 優先級 (1-10，數字越大優先級越高)
            user_id: 關聯的用戶 ID
            metadata: 任務元數據
            
        Returns:
            task_id: 任務 ID
        """
        if self.loop is None:
            raise RuntimeError("TaskManager 尚未啟動，請先調用 start()")
        
        task_id = uuid.uuid4().hex
        
        # 建立任務進度物件
        task_progress = TaskProgress(
            task_id=task_id,
            task_name=task_name,
            status=TaskStatus.PENDING,
            priority=priority,
            progress=0.0,
            message="任務已提交，等待執行",
            created_at=datetime.utcnow().isoformat() + "Z",
            metadata=metadata or {},
            user_id=user_id
        )
        
        self.tasks[task_id] = task_progress
        self._persist_task(task_progress)  # 持久化初始狀態
        
        # 包裝執行函數
        async def _execute():
            try:
                # 更新為運行中
                task_progress.status = TaskStatus.RUNNING
                task_progress.started_at = datetime.utcnow().isoformat() + "Z"
                task_progress.message = "任務執行中..."
                self._notify_progress(task_id, task_progress)
                self._persist_task(task_progress)  # 持久化運行狀態
                
                # 執行函數
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    # 同步函數在 executor 中執行，使用 functools.partial 處理參數
                    if args or kwargs:
                        partial_func = functools.partial(func, *args, **kwargs)
                        result = await self.loop.run_in_executor(None, partial_func)
                    else:
                        result = await self.loop.run_in_executor(None, func)
                
                # 完成
                task_progress.status = TaskStatus.COMPLETED
                task_progress.progress = 1.0
                task_progress.message = "任務完成"
                task_progress.completed_at = datetime.utcnow().isoformat() + "Z"
                task_progress.result = result
                self._notify_progress(task_id, task_progress)
                self._persist_task(task_progress)  # 持久化完成狀態
                
                logger.info(f"任務完成: {task_name} (ID: {task_id})")
                
            except asyncio.CancelledError:
                task_progress.status = TaskStatus.CANCELLED
                task_progress.message = "任務已取消"
                task_progress.completed_at = datetime.utcnow().isoformat() + "Z"
                self._notify_progress(task_id, task_progress)
                self._persist_task(task_progress)  # 持久化取消狀態
                logger.warning(f"任務已取消: {task_name} (ID: {task_id})")
                
            except Exception as e:
                task_progress.status = TaskStatus.FAILED
                task_progress.message = f"任務失敗: {str(e)}"
                task_progress.completed_at = datetime.utcnow().isoformat() + "Z"
                task_progress.error = str(e)
                self._notify_progress(task_id, task_progress)
                self._persist_task(task_progress)  # 持久化失敗狀態
                logger.error(f"任務失敗: {task_name} (ID: {task_id}), 錯誤: {e}", exc_info=True)
            
            finally:
                # 清理
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
        
        # 提交到 event loop
        future = asyncio.run_coroutine_threadsafe(_execute(), self.loop)
        self.running_tasks[task_id] = future
        
        logger.info(f"任務已提交: {task_name} (ID: {task_id})")
        
        return task_id
    
    def update_progress(
        self,
        task_id: str,
        progress: float,
        message: Optional[str] = None
    ):
        """
        更新任務進度（從任務內部調用）
        
        Args:
            task_id: 任務 ID
            progress: 進度 (0.0 - 1.0)
            message: 進度訊息
        """
        if task_id not in self.tasks:
            logger.warning(f"任務不存在: {task_id}")
            return
        
        task_progress = self.tasks[task_id]
        task_progress.progress = max(0.0, min(1.0, progress))
        
        if message:
            task_progress.message = message
        
        self._notify_progress(task_id, task_progress)
        self._persist_task(task_progress)  # 持久化進度更新
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            是否成功取消
        """
        if task_id not in self.tasks:
            logger.warning(f"任務不存在: {task_id}")
            return False
        
        task_progress = self.tasks[task_id]
        
        # 只能取消 PENDING 或 RUNNING 狀態的任務
        if task_progress.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            logger.warning(f"任務狀態不支持取消: {task_progress.status.value}")
            return False
        
        # 如果任務正在執行，取消 asyncio.Task
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            try:
                future.cancel()
                logger.info(f"已發送取消信號給任務: {task_id}")
            except Exception as e:
                logger.error(f"取消任務失敗: {e}")
                return False
        else:
            # PENDING 狀態的任務直接標記為 CANCELLED
            task_progress.status = TaskStatus.CANCELLED
            task_progress.message = "任務已取消（未開始執行）"
            task_progress.completed_at = datetime.utcnow().isoformat() + "Z"
            self._notify_progress(task_id, task_progress)
            self._persist_task(task_progress)
            logger.info(f"任務已取消: {task_id}")
        
        return True
    
    def get_task_status(self, task_id: str) -> Optional[TaskProgress]:
        """
        查詢任務狀態
        
        Args:
            task_id: 任務 ID
            
        Returns:
            TaskProgress 或 None
        """
        return self.tasks.get(task_id)
    
    def subscribe_progress(self, task_id: str, callback: Callable[[TaskProgress], None]):
        """
        訂閱任務進度更新
        
        Args:
            task_id: 任務 ID
            callback: 回調函數，接收 TaskProgress 參數
        """
        if task_id not in self.progress_subscribers:
            self.progress_subscribers[task_id] = []
        
        self.progress_subscribers[task_id].append(callback)
    
    def unsubscribe_progress(self, task_id: str, callback: Callable):
        """取消訂閱"""
        if task_id in self.progress_subscribers:
            self.progress_subscribers[task_id].remove(callback)
    
    def _notify_progress(self, task_id: str, progress: TaskProgress):
        """通知所有訂閱者"""
        if task_id in self.progress_subscribers:
            for callback in self.progress_subscribers[task_id]:
                try:
                    callback(progress)
                except Exception as e:
                    logger.error(f"進度回調失敗: {e}")
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任務
        
        Args:
            task_id: 任務 ID
            
        Returns:
            是否成功取消
        """
        if task_id not in self.running_tasks:
            return False
        
        future = self.running_tasks[task_id]
        if not future.done():
            future.cancel()
            logger.info(f"已取消任務: {task_id}")
            return True
        
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        清理舊任務記錄
        
        Args:
            max_age_hours: 保留最近幾小時的任務
        """
        from datetime import timezone as tz
        now = datetime.now(tz.utc)
        to_remove = []
        
        for task_id, progress in self.tasks.items():
            created_at = datetime.fromisoformat(progress.created_at.replace('Z', '+00:00'))
            age_hours = (now - created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours and progress.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED
            ]:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            if task_id in self.progress_subscribers:
                del self.progress_subscribers[task_id]
        
        # 同時清理資料庫中的舊任務
        if self.enable_persistence and self.db:
            try:
                db_removed = self.db.delete_old_tasks(max_age_hours)
                logger.info(f"從資料庫清理了 {db_removed} 個舊任務")
            except Exception as e:
                logger.error(f"資料庫清理失敗: {e}")
        
        if to_remove:
            logger.info(f"清理了 {len(to_remove)} 個記憶體中的舊任務")


# 全局實例（單例模式）
_task_manager_instance = None

def get_task_manager() -> TaskManager:
    """取得任務管理器實例（單例）"""
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = TaskManager()
        _task_manager_instance.start()
    return _task_manager_instance
