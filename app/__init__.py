from flask  import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app

    
