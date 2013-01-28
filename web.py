   
from flask import Flask, request, redirect, session, render_template, url_for
from jinja2 import Template
import json
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.htm')

if __name__ == "__main__":
    app.config['DEBUG'] = True
    # Start server
    port = int(os.environ.get("PORT", 5000))
    app.run('0.0.0.0', port)