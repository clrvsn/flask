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

app = Flask('kmod')
app.config.from_object('config')
mongo = PyMongo(app)

import views
