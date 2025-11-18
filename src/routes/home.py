from flask import render_template
from app import app

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')
