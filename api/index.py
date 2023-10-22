from flask import Flask
import feedparser

app = Flask(__name__)

@app.route('/')
def home():
    name=request.args["name"]
    page_dict = feedparser.parse(name)
    return page_dict

@app.route('/about')
def about():
    return 'About'
