#-------------------------------------------------------------------------------
# Name:        app
# Purpose:
#
# Author:      MAKEE2
#
# Created:     02-02-2015
# Copyright:   (c) MAKEE2 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)

import views
import api