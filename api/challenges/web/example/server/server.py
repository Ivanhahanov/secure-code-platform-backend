#!/usr/bin/env python3
from flask import Flask
import os

app = Flask(__name__)
flag = os.getenv('SCP_FLAG')


@app.route('/')
def index():
    return flag


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
