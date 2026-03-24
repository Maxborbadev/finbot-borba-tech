from functools import wraps
from flask import session, redirect, url_for


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_uuid" not in session and "admin_uuid" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def usuario_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_uuid" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin_uuid" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper