#-------------------------------------------------------------------------------
# Name:        lispish
# Purpose:
#
# Author:      Martin
#
# Created:     17/05/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import math, operator as op

DELIMS = "()'{}:[]"
SPACE = " \t\n\r"

def lex(string):
    tokens = []
    token = ""
    esc = False
    in_str = False
    in_cmnt = False
    for c in unicode(string):
        if in_cmnt:
            if c == '\n':
                in_cmnt = False
        elif in_str:
            if c == '\\':
                esc = True
            elif c == '"' and not esc:
                tokens.append('"'+token+'"')
                token = ""
                in_str = False
                esc = False
            else:
                token += c
                esc = False
        else:
            if c in DELIMS+SPACE+'";':
                if token:
                    tokens.append(token)
                    token = ""
                if c in DELIMS:
                    tokens.append(c)
                elif c == '"':
                    in_str = True
                elif c == ';':
                    in_cmnt = True
            else:
                token += str(c)
    if token:
        tokens.append(token)
    return tokens

def parse(string):
    tokens = lex(string)
    def get():
        return tokens.pop(0) if tokens else None
    def atom(token):
        if token == '#t':
            return True
        elif token == '#f':
            return False
        elif token[0] == '"':
            return token[1:-1]
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return intern(token)
    def exp():
        quote = False
        lst = []
        token = get()
        while token != None:
            if token in ')}]':
                break
            elif token == "'":
                quote = True
            elif token in '({[':
                lst.append(['quote', exp()] if quote else exp())
                quote = False
            else:
                lst.append(['quote', atom(token)] if quote else atom(token))
                quote = False
            token = get()
        return lst
    return exp()

#-------------------------------------------------------------------------------

class Env(object):
    def __init__(self, parms=(), args=(), outer=None):
        # Bind parm list to corresponding args, or single parm to list of args
        self._dict = {}
        self.outer = outer
        if isinstance(parms, str):
            self._dict.update({parms: list(args)})
        else:
            if len(args) != len(parms):
                raise TypeError('expected %s, given %s, '
                                % (str(parms), str(args)))
            self._dict.update(zip(parms,args))
    def update(self, vals):
        self._dict.update(vals)
    def define(self, var, val):
        self._dict[var] = val
        return val
    def defined(self, var):
        if var in self._dict:
            return True
        elif not self.outer is None:
            return self.outer.defined(var)
        return False
    def get(self, var):
        if var in self._dict:
            return self._dict[var]
        elif self.outer is None:
            raise LookupError(var)
        else:
            return self.outer.get(var)
    def set(self, var, val):
        if var in self._dict:
            self._dict[var] = val
            return val
        elif self.outer is None:
            raise LookupError(var)
        else:
            return self.outer.set(var,val)


class Proc(object):
    "A user-defined procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

#-------------------------------------------------------------------------------
# Evaluator

def _cond(exp,env):
    for i in range(len(exp)/2-1):
        test, conseq = exp[2*i + 1], exp[2*i + 2]
        if eval(test, env):
            return eval(conseq, env)
    return eval(exp[-1], env)

def _def(exp,env):
    (_, var, exp) = exp
    val = eval(exp, env)
    env[var] = val
    return val

def _set(exp,env):
    (_, var, exp) = exp
    val = eval(exp, env)
    env.set(var, val)
    return val

def mk_bool_op(fn):
    def _(exp, env):
        if len(exp) > 2:
            prev = eval(exp[1], env)
            for i in range(2,len(exp)):
                this = eval(exp[i], env)
                if not fn(prev, this):
                    return False
                prev = this
        return True
    return _

SF = {
    'quote': lambda exp,env: exp[1],
    '?': _cond,
    'def': _def,
    'fn': lambda exp,env: Proc(exp[1], exp[2], env),
    'and': mk_bool_op(op.and_),
    'or': mk_bool_op(op.or_),
    'eval': lambda exp,env: eval(eval(exp[1],env),env),
    'def?': lambda exp,env: env.defined(eval(exp[1],env)),
}

def eval(exp, env):
    if isinstance(exp, str):
        return env.get(exp)
    elif not isinstance(exp, list):
        return exp
    else:
        hd = exp[0]
        if isinstance(hd,str) and hd in SF:
            return SF[exp[0]](exp,env)
        else:
            hd = eval(hd, env)
            if callable(hd):
                args = [eval(arg, env) for arg in exp[1:]]
                return hd(*args)
            if hasattr(hd, '__getitem__'):
                return hd[eval(exp[1], env)]

#-------------------------------------------------------------------------------
# Standard Environment

def mk_cmp_op(fn):
    def cmp(*args):
        if len(args) > 1:
            for i in range(len(args)-1):
                if not fn(args[i], args[i+1]):
                    return False
        return True
    return cmp

def mk_std_env():
    env = Env()
    env.update({
        '+': lambda *args: reduce(op.add, args) if args else 0,
        '-': lambda *args: reduce(op.sub, args) if args else 0,
        '*': lambda *args: reduce(op.mul, args) if args else 1,
        '/': lambda *args: reduce(op.truediv, args) if args else 1,
        '%': lambda *args: reduce(op.mod, args) if args else 1,
        '=': mk_cmp_op(op.eq),
        '>': mk_cmp_op(op.gt),
        '<': mk_cmp_op(op.lt),
        '>=': mk_cmp_op(op.ge),
        '<=': mk_cmp_op(op.le),
        'not': lambda arg: not arg,
        'list': lambda *args: list(args),
        'len': lambda arg: len(arg),
        'rev': lambda arg: list(reversed(arg)),
        'atom?': lambda arg: not isinstance(arg,list),
        'list?': lambda arg: isinstance(arg,list),
        'nil?': lambda arg: arg == [],
        'in?': lambda e,s: e in s,
        'apply': lambda fn,args: fn(*args),

        'num?': lambda arg: isinstance(arg,(int,float)),
        'int?': lambda arg: isinstance(arg,int),
        'float?': lambda arg: isinstance(arg,float),
        'str?': lambda arg: isinstance(arg,(str,unicode)),
        'int': lambda arg: int(arg),
        'float': lambda arg: float(arg),
        'str': lambda arg: unicode(arg),

        'max': lambda *args: max(args),
        'min': lambda *args: min(args),
        'zip': lambda *args: map(list,zip(*args)),
        'map': lambda fn,*args: map(fn,*args),

    })
    return env

#-------------------------------------------------------------------------------

SRC = """
    ; Joe Ganley's Lisp
    (list (+) (+ 1) (+ 1 2) (+ 1 2 3))
    (list (-) (- 1) (- 1 2) (- 1 2 3))
    (list (*) (* 1) (* 1 2) (* 1 2 3))
    (list (/) (/ 1) (/ 1 2) (/ 1 2 3))
    (list (%) (% 1) (% 1 2) (% 1 2 3))
    (list (=) (= 1) (= 1 2) (= 1 2 3) (= 1 1 1))
    (list (>) (> 1) (> 1 2) (> 1 2 3) (> 3 2 1))
    (list (<) (< 1) (< 1 2) (< 1 2 3))
    (list (? #t 'then 'else) (? #f 1 #f 2 3))
    (list (and #f #f) (and #t #f) (and #f #t) (and #t #t))
    (list (or #f #f) (or #t #f) (or #f #t) (or #t #t))
    (list (atom? '()) (atom? 'foo) (atom? 3.14))
    (eval '(+ 1 2))

    ; Arc
    (list ('(1 2 3) 1) ("ABC" 1) ('abc 1))
    (apply + '(1 2))
    (list (def? 'foo) (def? '+))
    (list (int? 'foo) (int? 3.14) (int? 314))

    ; Etc.
    (+ '(1 2 3) '(a b c))
    (list (max 1 2 3) (min 1 2 3))
    (list (zip) (zip '(1 2 3)) (zip '(1 2 3) '(4 5 6)))
    (map + '(1 2 3) '(10 20 30))

    (map not '(#t #f #f #t))
"""

def main():
    print lex(u'"Marcus Baumgartner & Paulo Cinelli"')
    print parse(u'{obj \'name "Marcus Baumgartner \\"&\\" Paulo Cinelli"}')
    env = mk_std_env()
    for exp in parse(SRC):
        #print exp, '=>',
        print eval(exp,env)

if __name__ == '__main__':
    main()
