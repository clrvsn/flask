#-------------------------------------------------------------------------------
# Name:        data
# Purpose:
#
# Author:      Martin
#
# Created:     15/05/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------


class DataBase(object):
    def __init__(self, db_or_uri):
        if isinstance(db_or_uri, str):
            from pymongo import MongoClient
            client = MongoClient(db_or_uri)
            self._db = client.get_default_database()
        else:
            self._db = db_or_uri
        self._cache = {}
    def __getattr__(self, coll):
        if not self._cache.has_key(coll):
            #print 'Fetching',coll
            self._cache[coll] = Collection(self._db[coll].find())
        return self._cache[coll]
    def __getitem__(self, coll):
        if not self._cache.has_key(coll):
            #print 'Fetching',coll
            self._cache[coll] = Collection(self._db[coll].find())
        return self._cache[coll]

class Collection(list):
    def __init__(self, *args, **kwargs):
        super(Collection, self).__init__(*args, **kwargs)
        self._index = None
    def _get_index(self):
        if not self._index:
            #print 'Indexing',coll
            self._index = {d['_id']:d for d in self}
        return self._index
    def __getitem__(self, key):
        if isinstance(key,int):
            return super(Collection, self).__getitem__(key)
        else:
            return self._get_index().get(key, None)
    #def get(self, key, dflt=None):
    #    return self._get_index().get(key, dflt)
    def where(self, spec):
        if callable(spec):
            return Collection(filter(spec, self))
        def fn(val):
            for k,v in spec.iteritems():
                if not val.has_key(k) or val[k] != v:
                    return False
            return True
        return Collection(filter(fn, self))
    def sort(self, spec, drctn='up'):
        if callable(spec):
            return Collection(sorted(self, cmp=spec, reverse=(drctn=='down')))
        if isinstance(spec, str):
            return Collection(sorted(self, key=lambda v: v.get(spec, None), reverse=(drctn=='down')))

def filter_removed(inis):
    return filter(lambda o: not o.get('removed', False), inis)

def main():
    pass

if __name__ == '__main__':
    main()
