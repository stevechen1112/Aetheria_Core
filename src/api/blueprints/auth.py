from flask import Blueprint, request, jsonify
import uuid
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

# This assumes we can import these from the parent or a shared module
# For simplicity in this large file context, I'll expect them to be passed in or imported from src
from src.utils.errors import MissingParameterException

auth_bp = Blueprint('auth', __name__)

# Note: We need access to db and logger. 
# In a proper refactor, these would be initialized in the app factory.
# For now, I'll use a hack to get them or assume they are available.
from src.utils.database import get_database
from src.utils.logger import get_logger

db = get_database()
logger = get_logger()

from src.utils.auth_utils import hash_password, verify_password, get_auth_token_from_request


@auth_bp.route('/register', methods=['POST'])
def register_member():
    """會員註冊"""
    data = request.json or {}
    # Backward-compat: older clients used email instead of username
    username = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password')
    phone = data.get('phone')
    display_name = data.get('display_name')
    consents = data.get('consents') or {}

    email = (data.get('email') or '').strip() or None
    if email is None and '@' in username:
        email = username

    if not username:
        raise MissingParameterException('username')
    if not password:
        raise MissingParameterException('password')

    # 檢查使用者名稱是否已註冊
    if db.get_member_by_username(username):
        return jsonify({'status': 'error', 'message': '使用者名稱已被使用'}), 409

    user_id = uuid.uuid4().hex
    hashed = hash_password(password)
    db.create_member({
        'user_id': user_id,
        'username': username,
        'email': email,  # email 選填
        'phone': phone,
        'display_name': display_name or username,  # 預設用 username
        'password_hash': hashed['hash'],
        'password_salt': hashed['salt']
    })

    if consents:
        db.save_member_consents(user_id, consents)

    token = uuid.uuid4().hex
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    db.create_session(token, user_id, expires_at)

    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'token': token,
        'expires_at': expires_at
    })

@auth_bp.route('/login', methods=['POST'])
def login_member():
    """會員登入"""
    data = request.json or {}
    # Backward-compat: older clients used email instead of username
    username = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password')

    if not username:
        raise MissingParameterException('username')
    if not password:
        raise MissingParameterException('password')

    member = db.get_member_by_username(username)
    if not member:
        return jsonify({'status': 'error', 'message': '帳號或密碼錯誤'}), 401

    if not verify_password(password, member.get('password_hash'), member.get('password_salt')):
        return jsonify({'status': 'error', 'message': '帳號或密碼錯誤'}), 401

    token = uuid.uuid4().hex
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    db.create_session(token, member.get('user_id'), expires_at)

    return jsonify({
        'status': 'success',
        'user_id': member.get('user_id'),
        'token': token,
        'expires_at': expires_at
    })

@auth_bp.route('/logout', methods=['POST'])
def logout_member():
    """會員登出"""
    # Note: get_auth_token_from_request is needed here
    # Since it's a simple helper, I'll redefine or import it.
    from flask import request as flask_request
    auth_header = flask_request.headers.get('Authorization', '')
    token = None
    if auth_header.lower().startswith('bearer '):
        token = auth_header.split(' ', 1)[1].strip()
    if not token:
        data = flask_request.json or {}
        token = data.get('token')
        
    if not token:
        raise MissingParameterException('token')
    db.delete_session(token)
    return jsonify({'status': 'success'})
