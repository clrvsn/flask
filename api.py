#-------------------------------------------------------------------------------
# Name:        api
# Purpose:
#
# Author:      MAKEE2
#
# Created:     19/03/2015
# Copyright:   (c) MAKEE2 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#
# RESTful API HTTP methods
#
# Collection URI, such as http://example.com/resources/
#   GET     List the URIs and perhaps other details of the collection's members.
#   PUT     Replace the entire collection with another collection.
#   POST    Create a new entry in the collection. The new entry's URI is
#           assigned automatically and is usually returned by the operation.[9]
#   DELETE  Delete the entire collection.
#
# Element URI, such as http://example.com/resources/item17
#   GET     Retrieve a representation of the addressed member of the collection,
#           expressed in an appropriate Internet media type.
#   PUT     Replace the addressed member of the collection, or if it doesn't
#           exist, create it.
#   POST    Not generally used. Treat the addressed member as a collection in
#           its own right and create a new entry in it.[9]
#   DELETE  Delete the addressed member of the collection.
#
# The PUT and DELETE methods are referred to as idempotent, meaning that the
# operation will produce the same result no matter how many times it is
# repeated. The GET method is a safe method (or nullipotent), meaning that
# calling it produces no side-effects. In other words, retrieving or accessing
# a record doesn't change it.
#
# [9] http://thereisnorightway.blogspot.com/2012/05/api-example-using-rest.html
#-------------------------------------------------------------------------------

import json, pymongo
from app import app, mongo
from flask import request
from flask.ext.restful import reqparse, abort, Api, Resource

api = Api(app)

#-------------------------------------------------------------------------------

def elab_meta(meta):
    for field in meta['fields']:
        typ = field['type'].split('.')
        if len(typ) == 2:
            typ,etc = typ
            if '-' in typ:
                typ,mod = typ.split('-')
                field[mod] = True
            if typ == 'ref':
                _id,fld = etc.split(':')
                omet = mongo.db.meta.find_one(_id)
                opts = filter(lambda o: not o.get('removed', False),
                              mongo.db[omet['name']].find(fields=['_id',fld,'removed']))
                field['type'] = 'ref'
                field['opts'] = []
                for opt in opts:
                    try:
                        #field['opts'].append([opt[fld],opt['_id']])
                        field['opts'].append({'txt': opt[fld], 'val': opt['_id']})
                    except:
                        pass
            elif typ == 'enum':
                opts = etc.split('|')
                field['type'] = 'enum'
                #field['opts'] = [[opt,opt] for opt in opts]
                field['opts'] = [{'txt': opt, 'val': opt} for opt in opts]
    return meta

class Meta(Resource):
    def get(self, _id):
        return elab_meta(mongo.db.meta.find_one_or_404(_id))
##    def put(self, _id):
##        data = request.get_data()
##        obj = json.loads(data)
##        mongo.db.meta.update({'_id': _id}, obj)
##        return obj, 201

class MetaList(Resource):
    def get(self):
        return [elab_meta(m) for m in mongo.db.meta.find(sort=[('_id',pymongo.ASCENDING)])]

api.add_resource(MetaList, '/api/meta')
api.add_resource(Meta,     '/api/meta/<string:_id>')

class BareMeta(Resource):
    def get(self, _id):
        return mongo.db.meta.find_one_or_404(_id)
    def put(self, _id):
        data = request.get_data()
        obj = json.loads(data)
        mongo.db.meta.update({'_id': _id}, obj, upsert=True)
        return obj, 201
    def delete(self, _id):
        mongo.db.meta.remove(_id)
        return '', 204

class BareMetaList(Resource):
    def get(self):
        return list(mongo.db.meta.find(sort=[('_id',pymongo.ASCENDING)]))
    def post(self):
        data = request.get_data()
        obj = json.loads(data)
        _id = mongo.db.meta.insert(obj)
        return mongo.db.meta.find_one(_id)

api.add_resource(BareMetaList, '/api/baremeta')
api.add_resource(BareMeta,     '/api/baremeta/<string:_id>')

class OptionsList(Resource):
    def get(self):
        opts = [{'val':x['_id'], 'txt':x['label']} for x in mongo.db.meta.find()]
        objs = [{'_id':'META', 'opts':opts}]
        for meta in mongo.db.meta.find():
            if 'txt_field' in meta:
                fld = meta['txt_field']
                opts = [{'val':x['_id'], 'txt':x[fld]} for x in mongo.db[meta['name']].find() if not 'removed' in x or not x['removed']]
                obj = {'_id': meta['_id'], 'opts': opts}
                objs.append(obj)
        return objs

api.add_resource(OptionsList, '/api/options')

#-------------------------------------------------------------------------------

def mk_id(pre,num):
    if isinstance(num, (dict,list)):
        num = len(num)+1
    return pre + ('0000' + str(num))[-4:]

def id_max(coll):
    alpha = ''.join(chr(i+65) for i in range(26))
    high = coll.find_one(sort=[('_id', pymongo.DESCENDING)])
    return int(high['_id'].strip(alpha)) if high else 0

def mk_model_resource(coll):
    def get(self, _id):
        clctn = mongo.db[coll]
        return clctn.find_one_or_404(_id)
    def put(self, _id):
        data = request.get_data()
        obj = json.loads(data)
        mongo.db[coll].update({'_id': _id}, obj)
        return obj, 201
    def delete(self, _id):
        mongo.db[coll].remove(_id)
        return '', 204
    return type(coll.capitalize(), (Resource,), {'get': get, 'put': put, 'delete': delete})

def mk_list_resource(coll,prfx):
    def get(self):
        return list(mongo.db[coll].find(sort=[('_id',pymongo.ASCENDING)]))
    def post(self):
        data = request.get_data()
        hi = id_max(mongo.db[coll])
        obj = json.loads(data)
        obj['_id'] = mk_id(prfx, hi+1)
        _id = mongo.db[coll].insert(obj)
        return mongo.db[coll].find_one(_id)
    return type(coll.capitalize()+'List', (Resource,), {'get': get, 'post': post})

from pymongo import MongoClient
for meta in MongoClient().kmod.meta.find():
    prfx,coll = meta['_id'], str(meta['name'])
    api.add_resource(mk_list_resource(coll,prfx), '/api/kmod/'+coll)
    api.add_resource(mk_model_resource(coll),     '/api/kmod/'+coll+'/<string:_id>')

#-------------------------------------------------------------------------------

class ClearQuestQuery(Resource):
    def get(self, query):
        import urllib, urllib2, xmltodict
        anti = 'http://clearquestweb-hbg.ikea.com/cqweb/restapi/cq2_helsingborg/IKEA/QUERY/Public%20Queries/ProductSpecific/Sales/MHS%20TP/'
        post = '?format=xml&loginId=look&password=look&noframes=true'
        url = anti + urllib.quote(query) + post
        rsp = urllib2.urlopen(url)
        xml = rsp.read()
        return xmltodict.parse(xml)

api.add_resource(ClearQuestQuery, '/api/cq/<string:query>')

#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
