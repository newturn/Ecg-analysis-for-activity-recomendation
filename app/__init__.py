from flask import Flask
from flask_bootstrap import Bootstrap

import secrets


app = Flask(__name__)
app.config['MAX_CONTENT_PATH'] = 12000
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

bootstrap = Bootstrap(app)
from app import routes
