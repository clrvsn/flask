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
import models

@app.route('/')
def hello_world():
    return render_template("front.html")

@app.route('/byprog')
def byprog():
    return render_template("byprog.html",
                           title='Initiatives by Program')

@app.route('/byprog/init.csv')
def byprog_init_csv():
    inits = models.Initiative.query.all()
    fields = ['id','name','state','start','end','type','category','program','function','byprog_col','byprog_row','byprog_txt']
    csv = ','.join(fields) + '\n'
    csv += '\n'.join([','.join([str(getattr(init,name) or '') for name in fields]) for init in inits])
    return csv


if __name__ == '__main__':
    pass
