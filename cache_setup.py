from flask import Flask
from flask_caching import Cache

def create_app():
    app = Flask(__name__)
    
    config = {
        "DEBUG": True,
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache",
        "CACHE_DEFAULT_TIMEOUT": 12 * 60 * 60 # 12 hours
    }
    
    app.config.from_mapping(config)
    
    cache = Cache(app)
    
    return app, cache

app, cache = create_app()
