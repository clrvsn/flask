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

from flask import render_template, jsonify
from app import app
import models

@app.route('/')
def hello_world():
    return render_template("front.html")

@app.route('/byprog')
def byprog():
    return render_template("byprog.html",
                           title='Initiatives by Programme')

@app.route('/byprog/init.csv')
def byprog_init_csv():
    inits = models.Initiative.query.all()
    fields = ['id','name','state','start','end','type','category','program','function','byprog_col','byprog_row','byprog_txt']
    csv = ','.join(fields) + '\n'
    csv += '\n'.join([','.join([str(getattr(init,name) or '') for name in fields]) for init in inits])
    return csv

@app.route('/bytime')
def bytime():
    return render_template("bytime.html",
                           title='Initiatives Timeline')

@app.route('/bytime/init.csv')
def bytime_init_csv():
    inits = models.Initiative.query.order_by('function').all()
    fields = ['id','name','state','start','end','type','category','program','function']
    csv = ','.join(fields) + '\n'
    csv += '\n'.join([','.join([str(getattr(init,name) or '') for name in fields]) for init in inits])
    #print csv
    return csv

@app.route('/bytime.json')
def bytime_json():
    inits = models.Initiative.query.order_by('function').all()
    hards = {}
    for dpn in models.Dependency.query.filter(models.Dependency.type == 'HARD').all():
        if not dpn.from_init_id in hards.keys():
            hards[dpn.from_init_id] = []
        hards[dpn.from_init_id].append(dpn.to_init_id)
    fields = ['id','name','state','start','end','type','category','program','function']
    jsn = [{name: str(getattr(init,name) or '') for name in fields} for init in inits]
    inits = []
    for init in models.Initiative.query.order_by('function').all():
        ini = {name: str(getattr(init,name) or '') for name in fields}
        ini['to'] = hards.get(ini['id'], [])
        inits.append(ini)
    #print jsn
    return jsonify({'inits': inits})

@app.route('/inits.json')
def inits_json():
    fields = ['id','name','state','start','end','type','category','program','function']
    inits = [{name: str(getattr(init,name) or '') for name in fields} for init in models.Initiative.query.all()]
    return jsonify(inits=inits)

@app.route('/inits')
def init_list():
    return render_template("init_list.html",
                           title='Initiatives List')

@app.route('/funcs')
def func_areas():
    return render_template("func_area.html",
                           title='Functional Areas Status')

if __name__ == '__main__':
    pass
