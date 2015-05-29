#-------------------------------------------------------------------------------
# Name:        config
# Purpose:
#
# Author:      MAKEE2
#
# Created:     12-02-2015
# Copyright:   (c) MAKEE2 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#import os
#basedir = os.path.abspath(os.path.dirname(__file__))

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'kmod.db')
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SECRET_KEY = "JumpingJackFlash"

def read_cfg():
    import os.path
    path = os.path.split(__file__)[0]
    f = open(os.path.join(path,'app.cfg'))
    env = f.readline().strip(' \n')
    f.close()
    return env

ENV = read_cfg()
#print repr(ENV)

if ENV == 'prod':
    MONGO_URI = "mongodb://flask:tanstaafl@ds037642-a0.mongolab.com:37642,ds037642-a1.mongolab.com:37642/deploy?replicaSet=rs-ds037642"
elif ENV == 'test':
    MONGO_URI = "mongodb://martin:nevada92@ds063630.mongolab.com:63630/mhstp"
else:
    MONGO_URI = "mongodb://localhost:27017/kmod"
