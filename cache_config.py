from flask_caching import Cache

cache = Cache()

def init_cache(app):
    cache.init_app(app)
