from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

def create_app():
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__)

    # Application Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database Configuration (Fix for Heroku PostgreSQL)
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # UAT flag for gated UI rollouts
    # Set env var UAT_UI=true to enable the redesigned mobile UI in UAT
    app.config['UAT_UI'] = os.environ.get('UAT_UI', 'false').lower() in ['1', 'true', 'yes', 'on']
    
    # Email Configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@bayonnehockeyclub.com')
    
    # File Upload Configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'documents')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar'}
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Flask-Login settings
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models here to avoid circular imports
        from app.models import User, Player, Folder, File, PasswordResetToken, PlayerDocument

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Import and register blueprints
        from app.routes import main
        app.register_blueprint(main)

        # Create all database tables
        db.create_all()

        # Expose UAT flag to all templates
        @app.context_processor
        def inject_uat_flag():
            return {"is_uat_ui": app.config.get('UAT_UI', False)}

    return app