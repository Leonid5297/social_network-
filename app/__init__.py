from flask import Flask

app = Flask(__name__)

from app import views
from app import tests
from app import views_all
