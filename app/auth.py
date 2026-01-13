from flask import session, redirect, url_for, flash
from functools import wraps
from .models import Account

def login_user(user_id, email, role):
    """Store user info in session"""
    session['user_id'] = user_id
    session['email'] = email
    session['role'] = role

def logout_user():
    """Clear user session"""
    session.clear()

def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        return Account.query.get(session['user_id'])
    return None

def is_authenticated():
    """Check if user is logged in"""
    return 'user_id' in session