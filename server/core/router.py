"""
Модуль для регистрации точек входа вызовов api.
Прописывать здесь только методы из controller.py
"""

from . import controller


routers = {
    'GET': {
        ('/', '/api', '/api/status'): controller.index,
        '/api/file': controller.get_file
    },
    'POST': {
        ('/', '/api', '/api/status'): controller.index,
        '/api/file': controller.get_file
    }
}
