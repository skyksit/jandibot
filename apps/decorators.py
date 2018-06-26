# coding: utf-8
from __future__ import unicode_literals
"""
@author: skyksit
"""
from functools import wraps

def on_command(commands):
    def decorator(func):
        func.commands = commands
    
        @wraps(func)
        def _decorator(*args, **kwargs):
            return func(*args, **kwargs)
        return _decorator
    
    return decorator