#-------------------------------------------------------------------------------
# Name:        login
# Purpose:
#
# Author:      Martin
#
# Created:     29/05/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import flask
from app import app, mongo, login_manager
from flask.ext.login import UserMixin, login_user, logout_user, login_required

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

class User(UserMixin):
    def __init__(self, user):
        self.id = user['_id']
        self.user = user
    def check_password(self, pw):
        return pw == self.user['password']
    @property
    def name(self):
        return self.user['name']


@login_manager.user_loader
def load_user(user_id):
    user = mongo.db._user.find_one(user_id)
    if user:
        return User(user)

class LoginForm(Form):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        #print self.username
        user = mongo.db._user.find_one(self.username.data)
        if user is None:
            self.username.errors.append('Unknown user')
            return False

        user = User(user)
        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True




def main():
    pass

if __name__ == '__main__':
    main()
