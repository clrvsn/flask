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

from flask import render_template, jsonify, request, render_template_string
#from flask.ext.pymongo import ASCENDING
from app import app, mongo
from data import *
import json

@app.route('/')
def front_page():
    return render_template("front.html")

@app.route('/try')
def try_it():
    return render_template("try.html")

##@app.route('/edfun')
##def edit_fun():
##    return render_template("edit_fun.html",
##                            title='Functional Areas Editor')
##@app.route('/editor')
##def editor():
##    return render_template("editor.html",
##                            title='Editor')

@app.route('/cq/<string:query>')
def cq(query):
    return render_template("cq.html",
                            title='ClearQuest Query: '+query,
                            query=query)
@app.route('/page/<name>')
def page(name):
    import lispy
    db_page = mongo.db._page.find_one(name)
    page = {}
    def elab(v):
        if isinstance(v,dict):
            if v.has_key('proc'):
                obj = ''
                if v['proc'] == 'lispy' and v.has_key('source'):
                    obj = lispy.execute(v['source'], {
                        'req': {
                            'args': request.args,
                            'form': request.form}})
                elif v['proc'] == 'jinja' and v.has_key('source'):
                    obj = render_template_string(v['source'],
                            title=title,
                            data=data,
                            req={
                                'args': request.args,
                                'form': request.form})
                return obj
            elif v.has_key('source'):
                return v['source']
    title = elab(db_page['title']) if 'title' in db_page else ''
    data = elab(db_page['data']) if 'data' in db_page else {}
    page['title'] = title
    page['data'] = json.dumps(data)
    for k,v in db_page.iteritems():
        if k not in ('data'):
            page[k] = elab(v)
    return render_template("page.html", **page)

@app.route('/edit/<name>')
def edit_any(name):
    meta = mongo.db._meta.find_one({'name': name})
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


def deref(db, old, fields=None):
    meta = db._meta
    TYPS = {}
    for m in meta:
        TYPS[m['_id']] = m['name']

    if fields:
        for k in fields:
            if not k in old:
                old[k] = ''
    new = {}
    for k,v in old.iteritems():
        if not fields or k in fields:
            if v is not None and v != '':
                if k.endswith('_id') and k != '_id':
                    typ = v[0:3]
                    obj = db[TYPS[typ]][v]
                    if obj:
                        new[k[0:-3]] = deref(db,obj)
                else:
                    new[k] = v
    return new

def deref_ini(db, old, fields=None):
    ini = deref(db, old, fields)
    if fields and 'ncaps' in fields:
        ini['ncaps'] = len(db.capability.where({'init_id': ini['_id']}))
    if 'function_ids' in ini:
        if ini['function_ids'] == 'ALL':
            ini['function'] = 'ALL'
        else:
            funcs = [db.function[fid] for fid in ini['function_ids']] #.split()]
            ini['function'] =  '/'.join(f.get('abbr', f['name']) if f else '?' for f in funcs)
        del ini['function_ids']
    return ini

@app.route('/data/ini/<_id>')
def ini_api(_id):
    db = DataBase(mongo.db)
    fields = ['_id','name','state','start','end','type','category',
              'program_id','function_ids','byprog_txt','removed','ncaps']
    def get(typ,id1,id2):
        inis = [deref_ini(db, db.initiative[ini[id1]], fields)
                for ini in db.dependency.where({'type': typ, id2: _id})]
        return filter_removed(inis)
    return jsonify(
        ini   = deref_ini(db, db.initiative[_id]),
        froms = get('hard','from_init_id','to_init_id'),
        tos   = get('hard','to_init_id','from_init_id'),
        softs = get('soft','from_init_id','to_init_id') + get('soft','to_init_id','from_init_id'))

@app.route('/data/byprog')
def byprog_api():
    db = DataBase(mongo.db)
    fields = ['_id','name','state','start','end','type','category','program_id',
              'function_ids','byprog_col','byprog_row','byprog_txt']
    return jsonify(
        inits = [deref_ini(db,ini,fields) for ini in filter_removed(db.initiative)],
        hards = db.dependency.where({'type': 'hard'}),
        softs = db.dependency.where({'type': 'soft'}))

@app.route('/data/byprogf')
def byprogf_api():
    db = DataBase(mongo.db)
    fields = ['_id','name','state','start','end','type','category','program_id',
              'function_ids','byprog_txt']
    inis = [deref_ini(db,ini,fields) for ini in filter_removed(db.initiative.sort('_id'))]
    indx = {ini['_id']: i for i,ini in enumerate(inis)}
    def is_link(d):
        return d['from_init_id'] in indx.keys() and d['to_init_id'] in indx.keys()
    def mk_link(d):
        return {'source': indx[d['from_init_id']], 'target': indx[d['to_init_id']], 'type': d['type']}
        #return {'source': int(d['from_init_id'][3:])-1, 'target':  int(d['to_init_id'][3:])-1, 'type': d['type']}
    return jsonify(
        inits = inis,
        links = map(mk_link, filter(is_link, db.dependency.where({'type': 'soft'})))
              + map(mk_link, filter(is_link, db.dependency.where({'type': 'hard'}))))


@app.route('/data/bytime')
def bytime_api():
    db = DataBase(mongo.db)
    hards = {}
    for dpn in db.dependency.where({'type': 'hard'}):
        if not dpn['from_init_id'] in hards.keys():
            hards[dpn['from_init_id']] = []
        hards[dpn['from_init_id']].append(dpn['to_init_id'])
    fields = ['_id','name','state','start','end','type','category','program_id','function_ids']
    inits = []
    for init in filter_removed(db.initiative.sort('function_ids')):
        ini = {name: init.get(name, '') for name in fields}
        ini['to'] = hards.get(ini['_id'], [])
        prog = db.programme[ini['program_id']]
        ini['program'] = prog['name'] if prog else ''
        del ini['program_id']
        if ini['function_ids'] == 'ALL':
            ini['function'] = 'ALL'
        else:
            funcs = [db.function[fid] for fid in ini['function_ids']]
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
    db = DataBase(mongo.db)
    #print id
    if id:
        if id[0:3] == 'FUN':
            fun  = db.function[id]
            caps = db.capability.where({'function_id': id})
            inis = db.initiative
            return jsonify(caps=caps, fun=fun, inis=mk_options(inis))
        elif id[0:3] == 'INI':
            ini  = db.initiative[id]
            caps = db.capability.where({'init_id': id})
            funs = db.function
            return jsonify(caps=caps, funs=mk_options(funs), ini=ini)
    else:
        caps = db.capability
        funs = db.function
        inis = db.initiative
        return jsonify(caps=caps, funs=mk_options(funs), inis=mk_options(inis))

@app.route('/data/funs')
def funs_api():
    db = DataBase(mongo.db)
    funs = db.function
    for fun in funs:
        fun['ncap'] = len(db.capability.where({'function_id': fun['_id']}))
    return jsonify({'funs': funs})

if __name__ == '__main__':
    pass
