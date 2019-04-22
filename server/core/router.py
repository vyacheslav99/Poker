from . import handlers


routers = {
    'GET': {
        ('/', '/api', '/api/status'): handlers.index,
        '/api/file': handlers.get_file
    },
    'POST': {
        ('/', '/api', '/api/status'): handlers.index,
        '/api/file': handlers.get_file
    }
}
