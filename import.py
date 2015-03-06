#-------------------------------------------------------------------------------
# Name:        import
# Purpose:
#
# Author:      MAKEE2
#
# Created:     11-02-2015
# Copyright:   (c) MAKEE2 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from app import db, models
#import codecs, csv

def col_num(ltrs):
    i = 0
    for ltr in ltrs:
        i = i * 26 + ord(ltr) - 64
    return i - 1


def load_csv(name, sep='\t'):
    with codecs.open('import/'+name, encoding='utf-8') as csv:
        return [[x.strip(' \r\n') for x in line.split(sep)] for line in csv.readlines()]

def load_init():
    inits = {}
    for row in load_csv('init.csv', ','):
        id = row[0]
        inits[id] = {
            'id': id,
            'byprog_txt': row[1],
            'byprog_col': float(row[2]),
            'byprog_row': float(row[3]),
        }
    return inits

def load_meta():
    i = 0
    def _(x):
        global i
        if x[0]:
            i = col_num(x[0])
        else:
            i += 1
        return {'col': i, 'name': x[2], 'type': x[3]} if x[2] else None
    csv = load_csv('meta.csv', ',')
    return map(_, csv)

def mk_id(pre,dct):
    return pre + ('0000' + str(len(dct)+1))[-4:]

def load_hub():
    inits = load_init()
    meta = load_meta()
    data = load_csv('hub.csv')
    progs = {}
    procs = {}
    ppl = {}
    def mk_person(name):
        if name and name.lower() in ['n/a','tbd','']:
            name = None
        if name:
            if not name in ppl.keys():
                ppl[name] = {'id': mk_id('PSN',ppl), 'name': name}
            return ppl[name]['id']
    def mk_program(name):
        if name:
            if not name in progs.keys():
                progs[name] = {'id': mk_id('PGM',progs), 'name': name}
            return progs[name]['id']
    def mk_process(title, row, idx):
        if title:
            if not title in procs.keys():
                procs[title] = {
                    'id': mk_id('PCS',procs),
                    'title': title,
                    'level': 0,
                    'owner_id': mk_person(row[idx+1]),
                    'leader_id': mk_person(row[idx+2]),
                }
            return procs[title]['id']
    for row in data:
        id = row[0]
        init = inits[id]
        for col in meta:
            if col and col['col'] < len(row):
                idx = col['col']
                name = col['name']
                value = row[idx]
                if value.lower() in ['n/a','tbd','']:
                    value = None
                if col['name'] == 'program':
                    name = name + '_id'
                    value = mk_program(value)
                elif col['name'] == 'process':
                    name = name + '_id'
                    value = mk_process(value, row, idx)
                elif col['type'] == 'Person':
                    name = name + '_id'
                    value = mk_person(value)
                elif col['type'] == 'Bool':
                    if value:
                        value = value.lower() in ['yes']
                else:
                    value = value or None
                init[name] = value
    for pers in ppl.values():
        p = models.Person.query.get(pers['id'])
        if p is None:
            p = models.Person(**pers)
            print p.id, p.name
            db.session.add(p)
    db.session.commit()
    for prog in progs.values():
        p = models.Program.query.get(prog['id'])
        if p is None:
            p = models.Program(**prog)
            print p.id, p.name
            db.session.add(p)
    db.session.commit()
    for proc in procs.values():
        p = models.Process.query.get(proc['id'])
        if p is None:
            p = models.Process(**proc)
            print p.id, p.title
            db.session.add(p)
    db.session.commit()
    for init in inits.values():
        print init['id']
        ini = models.Initiative.query.get(init['id'])
        if ini is None:
            ini = models.Initiative(**init)
            print ini.id, ini.name
            db.session.add(ini)
    db.session.commit()
    #return inits.values()

def load_deps():
    for row in load_csv('deps.csv', ','):
        id,frm,to,typ = row
        d = models.Dependency.query.get(id)
        if d is None:
            d = models.Dependency(**{'id': id, 'from_init_id': frm, 'to_init_id': to, 'type': typ})
            print d.id
            db.session.add(d)
    db.session.commit()


def load_csv_1st(name, sep=','):
    import codecs, csv
    with codecs.open('data/'+name, encoding='utf-8') as csvfile:
        rows = list(csv.reader(csvfile))
        #rows = [[x.strip(' \r\n') for x in line.split(sep)] for line in csv.readlines()]
        data = []
        fields = rows[0]
        for row in rows[1:]:
            obj = {fields[i]: row[i] for i in range(len(fields)) if row[i]}
            data.append(obj)
        return data

def try_mongo():
    from pymongo import MongoClient
    mongo = MongoClient()
    db = mongo.kmod
    #stuff = db.stuff
    #foo = stuff.insert({'_id': 42, 'foo': 23})
    #bar = stuff.insert({'_id': 43, 'bar': 19})
    #print stuff.find_one(42)
    print list(db.capability.find())

def csvs_to_mongo(csvs):
    import csv
    from pymongo import MongoClient
    mongo = MongoClient()
    kmod = mongo.kmod
    for name in csvs:
        with open('data/'+name+'.csv', 'rb') as csvfile:
            rows = list(csv.DictReader(csvfile))
            data = []
            for row in rows:
                obj = {k: v for k,v in row.iteritems() if v}
                data.append(obj)
            coll = kmod[name]
            coll.insert(data)
            print name

def main():
    #print load_csv('init.csv', ',')
    #print load_meta()
    #print col_num('CJ')
    #load_hub()
    #for init in hub: print init
    #    print init['id'], init['process']
    #load_deps()
    try_mongo()
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(load_csv_1st('capability.csv'))
    #csvs_to_mongo(['actor','capability','dependency','function','initiative','process','programme'])

if __name__ == '__main__':
    main()
