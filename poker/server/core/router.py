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
