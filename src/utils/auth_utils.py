import os
import hashlib
import hmac
import uuid
from datetime import datetime
from flask import request
from typing import Dict, Optional, Tuple, Any
from src.utils.errors import MissingParameterException, UserNotFoundException

def hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    if not salt:
        salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return {'hash': pwd_hash, 'salt': salt}

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return hmac.compare_digest(pwd_hash, stored_hash)

def get_auth_token_from_request(data: Optional[Dict] = None) -> Optional[str]:
    """從 Authorization header 或 payload 取得 token"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.lower().startswith('bearer '):
        return auth_header.split(' ', 1)[1].strip()
    if data:
        return data.get('token')
    return None

def require_auth_user_id(db) -> str:
    """驗證 session 並回傳 user_id"""
    data = {}
    if request.method not in ('GET', 'DELETE'):
        try:
            data = request.json or {}
        except Exception:
            data = {}
    token = get_auth_token_from_request(data)
    if not token:
        raise MissingParameterException('token')
    session = db.get_session(token)
    if not session:
        raise UserNotFoundException('session')
    expires_at = session.get('expires_at')
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at) < datetime.now():
                db.delete_session(token)
                raise UserNotFoundException('session')
        except Exception:
            pass
    return session.get('user_id')
