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
import json

@app.route('/')
def front_page():
    return render_template("front.html")

@app.route('/edfun')
def edit_fun():
    return render_template("edit_fun.html",
                            title='Functional Areas Editor')
@app.route('/try')
def try_it():
    return render_template("try.html")

@app.route('/editor')
def editor():
    return render_template("editor.html",
                            title='Editor')

@app.route('/cq/<string:query>')
def cq(query):
    return render_template("cq.html",
                            title='ClearQuest Query: '+query,
                            query=query)

@app.route('/edit/<name>')
def edit_any(name):
    meta = mongo.db.meta.find_one({'name': name})
    return render_template("edit.html",
                            title=meta['label'] + ' Editor', id=meta['_id'])

@app.route('/byprog')
def inis_byprog():
    return render_template("byprog.html",
                           title='Initiatives by Programme')
@app.route('/byprog/force')
def inis_byprogf():
    return render_template("byprog_force.html",
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


def filter_removed(inis):
    return filter(lambda o: not o.get('removed', False), inis)

def deref(old,fields=None):
    typs = {
        'AGT': mongo.db.agent,
        'CAP': mongo.db.capability,
        'FUN': mongo.db.function,
        'INI': mongo.db.initiative,
        'PCS': mongo.db.process,
        'PGM': mongo.db.programme,
        'DEM': mongo.db.demand,
    }
    if fields:
        for k in fields:
            if not k in old:
                old[k] = ''
    new = {}
    for k,v in old.iteritems():
        if not fields or k in fields:
            if v:
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
            funcs = [mongo.db.function.find_one(fid) for fid in ini['function_ids']] #.split()]
            ini['ncaps'] = mongo.db.capability.find({'init_id': ini['_id']}).count()
            ini['function'] =  '/'.join(f.get('abbr', f['name']) if f else '?' for f in funcs)
        del ini['function_ids']
    return ini

@app.route('/data/ini/<id>')
def ini_api(id):
    fields = ['_id','name','state','start','end','type','category',
              'program_id','function_ids','byprog_txt','removed',
              'biz_pm_id','it_pm_id']
    def get(id):
        return deref_ini(mongo.db.initiative.find_one(id), fields)
    return jsonify(
        ini   = deref_ini(mongo.db.initiative.find_one(id)),
        froms = filter_removed([get(ini['from_init_id']) for ini in mongo.db.dependency.find({'type': 'hard', 'to_init_id': id})]),
        tos   = filter_removed([get(ini['to_init_id']) for ini in mongo.db.dependency.find({'type': 'hard', 'from_init_id': id})]),
        softs = filter_removed([get(ini['from_init_id']) for ini in mongo.db.dependency.find({'type': 'soft', 'to_init_id': id})])
              + filter_removed([get(ini['to_init_id']) for ini in mongo.db.dependency.find({'type': 'soft', 'from_init_id': id})]))

@app.route('/data/byprog')
def byprog_api():
    fields = ['_id','name','state','start','end','type','category','program_id',
              'function_ids','byprog_col','byprog_row','byprog_txt']
    return jsonify(
        inits = [deref_ini(ini,fields) for ini in filter_removed(mongo.db.initiative.find())],
        hards = list(mongo.db.dependency.find({'type': 'hard'})),
        softs = list(mongo.db.dependency.find({'type': 'soft'})))

@app.route('/data/byprogf')
def byprogf_api():
    fields = ['_id','name','state','start','end','type','category','program_id',
              'function_ids','byprog_txt']
    inis = [deref_ini(ini,fields) for ini in filter_removed(mongo.db.initiative.find(sort=[('_id', ASCENDING)]))]
    indx = {ini['_id']: i for i,ini in enumerate(inis)}
    def is_link(d):
        return d['from_init_id'] in indx.keys() and d['to_init_id'] in indx.keys()
    def mk_link(d):
        return {'source': indx[d['from_init_id']], 'target': indx[d['to_init_id']], 'type': d['type']}
        #return {'source': int(d['from_init_id'][3:])-1, 'target':  int(d['to_init_id'][3:])-1, 'type': d['type']}
    return jsonify(
        inits = inis,
        links = map(mk_link, filter(is_link, mongo.db.dependency.find({'type': 'soft'})))
              + map(mk_link, filter(is_link, mongo.db.dependency.find({'type': 'hard'}))))


@app.route('/data/bytime')
def bytime_api():
    hards = {}
    for dpn in mongo.db.dependency.find({'type': 'hard'}):
        if not dpn['from_init_id'] in hards.keys():
            hards[dpn['from_init_id']] = []
        hards[dpn['from_init_id']].append(dpn['to_init_id'])
    fields = ['_id','name','state','start','end','type','category','program_id','function_ids']
    inits = []
    for init in filter_removed(mongo.db.initiative.find().sort('function_ids', ASCENDING)):
        ini = {name: init.get(name, '') for name in fields}
        ini['to'] = hards.get(ini['_id'], [])
        prog = mongo.db.programme.find_one(ini['program_id'])
        ini['program'] = prog['name'] if prog else ''
        del ini['program_id']
        if ini['function_ids'] == 'ALL':
            ini['function'] = 'ALL'
        else:
            #funcs = [mongo.db.function.find_one(fid) for fid in ini['function_ids'].split()]
            funcs = [mongo.db.function.find_one(fid) for fid in ini['function_ids']]
            ini['function'] =  ' / '.join(f.get('abbr', f['name']) if f else '?' for f in funcs)
        del ini['function_ids']
        inits.append(ini)
    return jsonify({'inits': inits})

def mk_options(cursor, field='name'):
    opts = []
    for row in cursor:
        try:
            opt = (row[field], row['_id'])
            opts.append(opt)
        except:
            pass
    return opts

@app.route('/data/caps')
@app.route('/data/caps/<id>')
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

@app.route('/data/funs')
def funs_api():
    funs = list(mongo.db.function.find())
    for fun in funs:
        fun['ncap'] = mongo.db.capability.find({'function_id': fun['_id']}).count()
    return jsonify({'funs': funs})

if __name__ == '__main__':
    pass
