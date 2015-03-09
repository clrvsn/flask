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
from flask.ext.pymongo import ASCENDING
from app import app, mongo


##@app.route('/byprog/init.csv')
##def byprog_init_csv():
##    inits = models.Initiative.query.all()
##    fields = ['id','name','state','start','end','type','category','program','function','byprog_col','byprog_row','byprog_txt']
##    csv = ','.join(fields) + '\n'
##    csv += '\n'.join([','.join([str(getattr(init,name) or '') for name in fields]) for init in inits])
##    return csv

##@app.route('/bytime/init.csv')
##def bytime_init_csv():
##    inits = models.Initiative.query.order_by('function').all()
##    fields = ['id','name','state','start','end','type','category','program','function']
##    csv = ','.join(fields) + '\n'
##    csv += '\n'.join([','.join([str(getattr(init,name) or '') for name in fields]) for init in inits])
##    #print csv
##    return csv

##@app.route('/bytime.json')
##def bytime_json():
##    inits = models.Initiative.query.order_by('function').all()
##    hards = {}
##    for dpn in models.Dependency.query.filter(models.Dependency.type == 'HARD').all():
##        if not dpn.from_init_id in hards.keys():
##            hards[dpn.from_init_id] = []
##        hards[dpn.from_init_id].append(dpn.to_init_id)
##    fields = ['id','name','state','start','end','type','category','program','function']
##    jsn = [{name: str(getattr(init,name) or '') for name in fields} for init in inits]
##    inits = []
##    for init in models.Initiative.query.order_by('function').all():
##        ini = {name: str(getattr(init,name) or '') for name in fields}
##        ini['to'] = hards.get(ini['id'], [])
##        inits.append(ini)
##    #print jsn
##    return jsonify({'inits': inits})

##@app.route('/inits.json')
##def inits_json():
##    fields = ['id','name','state','start','end','type','category','program','function']
##    inits = [{name: str(getattr(init,name) or '') for name in fields} for init in models.Initiative.query.all()]
##    return jsonify(inits=inits)

##def mk_lookup(cursor, fields=('_id','name')):
##    lookup = {}
##    for row in cursor:
##        lookup[row['_id']] = {k:v for k,v in row.iteritems() if not fields or k in fields}
##    return lookup


@app.route('/')
def front_page():
    return render_template("front.html")

@app.route('/byprog')
def inis_byprog():
    return render_template("byprog.html",
                           title='Initiatives by Programme')
@app.route('/bytime')
def inis_bytime():
    return render_template("bytime.html",
                           title='Initiatives Timeline')

@app.route('/inits')
def inis_page():
    return render_template("inis.html",
                           title='Initiatives List')

@app.route('/init/<id>')
def ini_page(id):
    ini = mongo.db.initiative.find_one(id)
    if ini:
        return render_template("ini.html",
                           title=ini['name'], id=id)

@app.route('/funcs')
def funs_page():
    return render_template("funs.html",
                           title='Functional Areas Status')

@app.route('/caps')
@app.route('/caps/<id>')
def caps_page(id=''):
    title = 'Capabilities'
    if id:
        if id[0:3] == 'FUN':
            fun = mongo.db.function.find_one(id)
            #print fun
            title += ' (' + fun['name'] + ")"
        elif id[0:3] == 'INI':
            ini = mongo.db.initiative.find_one(id)
            title += ' (' + ini['name'] + ")"
    return render_template("caps.html", title=title, id=id)


def deref(old,fields=None):
    typs = {
        'ACT': mongo.db.actor,
        'CAP': mongo.db.capability,
        'FUN': mongo.db.function,
        'INI': mongo.db.initiative,
        'PCS': mongo.db.process,
        'PGM': mongo.db.programme,
    }
    if fields:
        for k in fields:
            if not k in old:
                old[k] = ''
    new = {}
    for k,v in old.iteritems():
        if not fields or k in fields:
            if k.endswith('_id') and k != '_id':
                typ = v[0:3]
                obj = typs[typ].find_one(v)
                if obj:
                    new[k[0:-3]] = deref(obj)
            else:
                new[k] = v
    return new

def deref_ini(old, fields=None):
    ini = deref(old,fields)
    if 'function_ids' in ini:
        if ini['function_ids'] == 'ALL':
            ini['function'] = 'ALL'
        else:
            funcs = [mongo.db.function.find_one(fid) for fid in ini['function_ids'].split()]
            ini['function'] =  '/'.join(f.get('abbr', f['name']) if f else '?' for f in funcs)
        del ini['function_ids']
    return ini

@app.route('/api/ini/<id>')
def ini_api(id):
    fields = ['_id','name','state','start','end','type','category',
              'program_id','function_ids','byprog_txt']
    def get(id):
        return deref_ini(mongo.db.initiative.find_one(id), fields)
    return jsonify(
        ini   = deref_ini(mongo.db.initiative.find_one(id)),
        froms = [get(ini['from_init_id']) for ini in mongo.db.dependency.find({'type': 'HARD', 'to_init_id': id})],
        tos   = [get(ini['to_init_id']) for ini in mongo.db.dependency.find({'type': 'HARD', 'from_init_id': id})],
        softs = [get(ini['from_init_id']) for ini in mongo.db.dependency.find({'type': 'SOFT', 'to_init_id': id})]
              + [get(ini['to_init_id']) for ini in mongo.db.dependency.find({'type': 'SOFT', 'from_init_id': id})])


@app.route('/api/byprog')
def byprog_api():
    fields = ['_id','name','state','start','end','type','category','program_id',
              'function_ids','byprog_col','byprog_row','byprog_txt']
    return jsonify(
        inits = [deref_ini(ini,fields) for ini in mongo.db.initiative.find({'removed': '0'})],
        hards = list(mongo.db.dependency.find({'type': 'HARD'})),
        softs = list(mongo.db.dependency.find({'type': 'SOFT'})))

@app.route('/api/bytime')
def bytime_api():
    hards = {}
    for dpn in mongo.db.dependency.find({'type': 'HARD'}):
        if not dpn['from_init_id'] in hards.keys():
            hards[dpn['from_init_id']] = []
        hards[dpn['from_init_id']].append(dpn['to_init_id'])
    fields = ['_id','name','state','start','end','type','category','program_id','function_ids']
    inits = []
    for init in mongo.db.initiative.find({'removed': '0'}).sort('function_ids', ASCENDING):
        ini = {name: init.get(name, '') for name in fields}
        ini['to'] = hards.get(ini['_id'], [])
        prog = mongo.db.programme.find_one(ini['program_id'])
        ini['program'] = prog['name'] if prog else ''
        del ini['program_id']
        if ini['function_ids'] == 'ALL':
            ini['function'] = 'ALL'
        else:
            funcs = [mongo.db.function.find_one(fid) for fid in ini['function_ids'].split()]
            ini['function'] =  ' / '.join(f.get('abbr', f['name']) if f else '?' for f in funcs)
        del ini['function_ids']
        inits.append(ini)
    return jsonify({'inits': inits})

def mk_options(cursor, field='name'):
    return [(row[field], row['_id']) for row in cursor]

@app.route('/api/caps')
@app.route('/api/caps/<id>')
def caps_api(id=None):
    #print id
    if id:
        if id[0:3] == 'FUN':
            fun = mongo.db.function.find_one(id)
            caps = list(mongo.db.capability.find({'function_id': id}))
            inis = list(mongo.db.initiative.find())
            return jsonify(caps=caps, fun=fun, inis=mk_options(inis))
        elif id[0:3] == 'INI':
            ini = mongo.db.initiative.find_one(id)
            caps = list(mongo.db.capability.find({'init_id': id}))
            funs = list(mongo.db.function.find())
            return jsonify(caps=caps, funs=mk_options(funs), ini=ini)
    else:
        caps = list(mongo.db.capability.find())
        funs = list(mongo.db.function.find())
        inis = list(mongo.db.initiative.find())
        return jsonify(caps=caps, funs=mk_options(funs), inis=mk_options(inis))

@app.route('/api/funs')
def funs_api():
    funs = list(mongo.db.function.find())
    for fun in funs:
        fun['ncap'] = mongo.db.capability.find({'function_id': fun['_id']}).count()
    return jsonify({'funs': funs})

if __name__ == '__main__':
    pass
