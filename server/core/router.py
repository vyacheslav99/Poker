from . import handlers


routers = {
    ('/', '/api', '/api/status'): handlers.index
}
