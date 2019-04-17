from . import handlers


routers = {
    ('/', '/api', '/api/status'): handlers.index,
    '/api/file': handlers.get_file
}
