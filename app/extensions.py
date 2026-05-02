from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Tenés que iniciar sesión para acceder.'
login_manager.login_message_category = 'warning'