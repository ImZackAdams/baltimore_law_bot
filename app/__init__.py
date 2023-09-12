from flask import Flask
from .views import views

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(views)
