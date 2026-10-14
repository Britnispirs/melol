from flask import Flask, session
import os
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    # Секретный ключ для сессий
    app.secret_key = os.environ.get("SECRET_KEY", "yanedaun-super-secret-key-2026")
    
    # Регистрация блюпринтов
    from app.routes import main
    from app.admin import admin
    
    app.register_blueprint(main)
    app.register_blueprint(admin)
    
    # Глобальные переменные в шаблонах
    @app.context_processor
    def inject_globals():
        return {
            "is_admin": session.get("is_admin", False),
            "current_year": datetime.now().year,
        }
    
    return app
