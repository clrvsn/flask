#-------------------------------------------------------------------------------
# Name:        serve
# Purpose:
#
# Author:      Martin
#
# Created:     02/02/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from app import app

from waitress import serve
serve(app, port=80)
