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

api.add_resource(BareMetaList, '/api/meta')
api.add_resource(BareMeta,     '/api/meta/<string:_id>')

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
        #print list(mongo.db[coll].find())
        return list(mongo.db[coll].find(sort=[('_id',pymongo.ASCENDING)]))
    def post(self):
        data = request.get_data()
        hi = id_max(mongo.db[coll])
        obj = json.loads(data)
        obj['_id'] = mk_id(prfx, hi+1)
        _id = mongo.db[coll].insert(obj)
        #print hi, _id, obj
        obj = mongo.db[coll].find_one(_id)
        #print obj
        return obj
    return type(coll.capitalize()+'List', (Resource,), {'get': get, 'post': post})

def mongo_db():
    from pymongo import MongoClient
    return MongoClient(app.config['MONGO_URI']).get_default_database()

for meta in mongo_db().meta.find():
    prfx,coll = meta['_id'], str(meta['name'])
    api.add_resource(mk_list_resource(coll,prfx), '/api/data/%s'%(coll,))
    api.add_resource(mk_model_resource(coll),     '/api/data/%s/<string:_id>'%(coll,))

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

class ExecLispy(Resource):
    def post(self):
        import lispy
        data = request.get_data()
        rslt = lispy.execute(data)
        #print data, '=>', rslt
        return rslt

api.add_resource(ExecLispy, '/api/exec')

class Lib(Resource):
    def get(self, _id):
        return mongo.db._lib.find_one_or_404(_id)
    def put(self, _id):
        data = request.get_data()
        obj = json.loads(data)
        mongo.db._lib.update({'_id': _id}, obj, upsert=True)
        return obj, 201
    def delete(self, _id):
        mongo.db._lib.remove(_id)
        return '', 204

class LibList(Resource):
    def get(self):
        return list(mongo.db._lib.find(sort=[('_id',pymongo.ASCENDING)]))
    def post(self):
        data = request.get_data()
        obj = json.loads(data)
        _id = mongo.db._lib.insert(obj)
        return mongo.db._lib.find_one(_id)

class ExecLib(Resource):
    def get(self, _id):
        import lispy
        l = mongo.db._lib.find_one(_id)
        return lispy.execute(l['src']) if l else ''

api.add_resource(LibList, '/api/lib')
api.add_resource(Lib,     '/api/lib/<string:_id>')
api.add_resource(ExecLib, '/api/exec/<string:_id>')

#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()
