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
from data import *

api = Api(app)

#-------------------------------------------------------------------------------

class Meta(Resource):
    def get(self, _id):
        return mongo.db._meta.find_one_or_404(_id)
    def put(self, _id):
        data = request.get_data()
        obj = json.loads(data)
        mongo.db._meta.update({'_id': _id}, obj, upsert=True)
        return obj, 201
    def delete(self, _id):
        mongo.db._meta.remove(_id)
        return '', 204

class MetaList(Resource):
    def get(self):
        return list(mongo.db._meta.find(sort=[('_id',pymongo.ASCENDING)]))
    def post(self):
        data = request.get_data()
        obj = json.loads(data)
        _id = mongo.db._meta.insert(obj)
        return mongo.db._meta.find_one(_id)

api.add_resource(MetaList, '/api/meta')
api.add_resource(Meta,     '/api/meta/<string:_id>')

class OptionsList(Resource):
    def get(self):
        db = DataBase(mongo.db)
        opts = [{'val':x['_id'], 'txt':x['label']} for x in db._meta]
        objs = [{'_id':'META', 'opts':opts}]
        for meta in db._meta:
            if 'txt_field' in meta:
                fld = meta['txt_field']
                #print meta['name'], fld
                opts = [{'val':x['_id'], 'txt':x[fld]} for x in filter_removed(db[meta['name']])]
                obj = {'_id': meta['_id'], 'opts': opts}
                objs.append(obj)
        return objs

api.add_resource(OptionsList, '/api/options')

#-------------------------------------------------------------------------------

PRFX = {}

def get_prfx(db,coll):
    if not PRFX.has_key(coll):
        meta = db._meta.find_one({'name':coll})
        PRFX[coll] = meta['_id']
    return PRFX[coll]

def mk_id(pre,num):
    if isinstance(num, (dict,list)):
        num = len(num)+1
    return pre + ('0000' + str(num))[-4:]

def id_max(coll):
    alpha = ''.join(chr(i+65) for i in range(26))
    high = coll.find_one(sort=[('_id', pymongo.DESCENDING)])
    return int(high['_id'].strip(alpha)) if high else 0

class Data(Resource):
    def get(self, coll, _id):
        clctn = mongo.db[coll]
        return clctn.find_one_or_404(_id)
    def put(self, coll, _id):
        data = request.get_data()
        obj = json.loads(data)
        mongo.db[coll].update({'_id': _id}, obj)
        return obj, 201
    def delete(self, coll, _id):
        mongo.db[coll].remove(_id)
        return '', 204

class DataList(Resource):
    def get(self, coll):
        #print list(mongo.db[coll].find())
        return list(mongo.db[coll].find(sort=[('_id',pymongo.ASCENDING)]))
    def post(self, coll):
        data = request.get_data()
        cltn = mongo.db[coll]
        hi = id_max(cltn)
        obj = json.loads(data)
        obj['_id'] = mk_id(get_prfx(mongo.db,coll), hi+1)
        _id = cltn.insert(obj)
        obj = cltn.find_one(_id)
        return obj

api.add_resource(DataList, '/api/data/<string:coll>')
api.add_resource(Data,     '/api/data/<string:coll>/<string:_id>')

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
