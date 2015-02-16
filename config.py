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

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'kmod.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
