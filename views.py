#-------------------------------------------------------------------------------
# Name:        views
# Purpose:
#
# Author:      MAKEE2
#
# Created:     12-02-2015
# Copyright:   (c) MAKEE2 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from flask import render_template
from app import app

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/byprog')
def byprog():
    return render_template("byprog.html",
                           title='Initiatives by Program')
