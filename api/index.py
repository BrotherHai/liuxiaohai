from flask import Flask
import feedparser
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def home():
    name=request.args["name"]
    page_dict = feedparser.parse(name)
    return page_dict

@app.route('/about')
def about():
    return 'About'
