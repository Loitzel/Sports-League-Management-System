from flask import session, redirect, url_for, flash
from functools import wraps

def editor_required(f):
    """
    Decorator that checks if user is either an admin or editor.
    Admins have all privileges while editors can modify data but not structures.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session or (not session.get('is_admin') and not session.get('is_editor')):
            flash('You need to be an admin or editor to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

def admin_required(f):
    """
    Decorator that checks if user is an admin.
    Only admins can make structural changes to the database.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('You need to be an admin to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap