﻿#-------------------------------------------------------------------------------
# Name:        lispy
# Purpose:
#
# Author:      Martin
#
# Created:     05/05/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# http://norvig.com/lispy.html

from app import app
from data import *
import sexpr

def parse(src):
    def enlisp(s):
        if isa(s,list):
            return map(enlisp,s)
        else:
            return atom(s)
    return enlisp(sexpr.parse(src))

Num  = (int, float, complex) # A Lisp Number is implemented as a Python int or float
Bool = bool

class List(list):
    pass
class Str(unicode):
    pass
class Sym(unicode):
    Table = {}
    def __new__(cls, *args, **kwargs):
        if not Sym.Table.has_key(args[0]):
            Sym.Table[args[0]] =  super(Sym, cls).__new__(cls, *args, **kwargs)
        return Sym.Table[args[0]]


_quote, _if, _set, _define, _lambda, _begin, _definemacro, = map(Sym,
    "quote if assign def fn begin mac".split())

def atom(token):
    'Numbers become numbers; #t and #f are booleans; "..." string; otherwise Symbol.'
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token[0] == '"':
        return Str(token[1:-1]) #.decode('string_escape'))
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            if not token in ('i','j'):
                try:
                    return complex(token.replace('i', 'j', 1))
                except ValueError:
                    pass
            return Sym(token)

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        # Bind parm list to corresponding args, or single parm to list of args
        self.outer = outer
        if isa(parms, Sym):
            self.update({parms:list(args)})
        else:
            if len(args) != len(parms):
                raise TypeError('expected %s, given %s, '
                                % (to_string(parms), to_string(args)))
            self.update(zip(parms,args))
    def find(self, var):
        "Find the innermost Env where var appears."
        if var in self:
            return self
        elif self.outer is None:
            raise KeyError(var)
        else:
            return self.outer.find(var)


def _db(*args):
    db = DataBase(app.config['MONGO_URI'])
    return db[str(args[0])]

def _orderby(seq, fun):
    seq = seq[:]
    seq.sort(cmp=fun)
    return seq
def _orderby_down(seq, fun):
    seq = seq[:]
    seq.sort(cmp=fun, revese=True)
    return seq

import figure
def _fig(*args, **kwargs):
    fig = figure.Fig(*args,**kwargs)
    return fig.render()

FIG = """
;(def cols 12)
(def docs (db 'document))
(len docs)
;(: (/ n 2))
(fig width: '5cm height: '4cm viewBox: "0 0 100 100"
    (rect x: 20 y: 20 width: 20 height: 20)
    (rect x: 50 y: 20 width: 30 height: 15)
    (rect x: 20 y: 50 width: 20 height: 20)
    (rect x: 50 y: 50 width: 20 height: 40)
)
        (def docs (db 'document))
        (def f (fn (id depth) (begin
            (def doc (docs id))
            (if (> depth 0)
                (dict
                    'name doc.name
                    'children (map
                                    (fn (i) (f i (- depth 1)))
                                    (doc 'related_ids [])
                    )
                )
                (dict
                    'name doc.name
                )
            )
        )))
        (f 'DOC0001 2)
"""


def standard_env():
    "An environment with some 'standard' procedures."
    import math, operator as op
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        # Operators
        '=':op.eq, '!=':op.ne,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le,
        '!':op.not_,
        'is':op.is_, 'isnt':op.is_not,
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        'and':op.and_, 'or':op.or_, 'not':op.not_, 'xor':op.xor,

        'abs':     abs,
        #'append':  op.add,
        'apply':   apply,

        # LISP list operations
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x,y: [x] + y,
        #'nth':     lambda x,y: x[y],
        #'eq?':     op.is_,
        #'equal?':  op.eq,
        'len':      len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x,list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Num),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Sym),
        'string?': lambda x: isinstance(x, Str),
        'bool?': lambda x: isinstance(x, Bool),
        'bool':op.truth,
        #'obj': lambda *x: {k:v for k,v in x},
        #'!': lambda x: x,
        ':': range,
        'db': _db,
        'upper': lambda x: x.upper(),
        'lower': lambda x: x.lower(),
        'orderby': _orderby,
        'orderby_down': _orderby_down,
        'fig': _fig,
        'rect': figure.rect,
    })
    return env

def arc_env(env=None):
    env = env if env else Env()
    import math, operator as op
    def foldl(seq, fn, dflt):
        return reduce(fn, seq) if seq else dflt
    def mk_foldl(fn, dflt):
        return lambda *x: foldl(x, fn, dflt)
    env.update({
        '+': mk_foldl(op.add, 0),
        '-': mk_foldl(op.sub, 0),
        '*': mk_foldl(op.mul, 1),
        '/': mk_foldl(op.truediv, 1),
    })
    return env

ARC = """
    (list (+) (+ 1) (+ 1 2) (+ 1 2 3))
    (list (-) (- 1) (- 1 2) (- 1 2 3))
    (list (*) (* 1) (* 1 2) (* 1 2 3))
    (list (/) (/ 1) (/ 1 2) (/ 1 2 3))
"""

def is_pair(x): return x != [] and isa(x, list)
def cons(x, y): return [x]+y

isa = isinstance
#global_env = standard_env()
global_env = arc_env(standard_env())

_db = None
def db():
    global _db
    if _db is None:
        _db = DataBase(app.config['MONGO_URI'])
    return _db

def _lookup(x, env):
    if '.' in x:
        names = x.split('.')
        obj = env.find(names[0])[names[0]]
        for name in names[1:]:
            new_obj = obj.get(name, None)
            if new_obj is None:
                _id = obj.get(name+'_id', None)
                if _id is None:
                    break
                pre = _id[:3]
                nm = db()._meta[pre]['name']
                new_obj = db()[nm][_id]
            obj = new_obj
        return obj
    else:
        return env.find(x)[x]

def _pairs(x):
    n = len(x)
    if n % 2:
        return [(x[2*i + 1], x[2*i + 2]) for i in range((n-1)/2)]
    else:
        return [(x[2*i + 1], x[2*i + 2]) for i in range(n/2-1)]

def _last(x):
    return x[-1]

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isa(x, Sym):             # variable reference
        return _lookup(x, env)
    elif not isa(x, list):      # constant literal
        return x
    elif x[0] == _quote:        # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == _if:           # (if test conseq ... alt)
        for test, conseq in _pairs(x):
            if eval(test, env):
                return eval(conseq, env)
        return eval(_last(x), env)
    elif x[0] == _define:       # (define var exp ...)
        for var, exp in _pairs(x):
            env[var] = eval(exp, env)
    elif x[0] == _set:          # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == _lambda:       # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    # Extra special forms
    elif x[0] == 'dict':
        return {eval(k,env):eval(v,env) for k,v in _pairs(x)}
    elif x[0] == 'from':
        return _from(x[1:], env)
##    elif x[0] == 'fig':
##        return _fig(x[1:], env)
    else:                       # (proc arg...)
        proc = eval(x[0], env)
        if callable(proc):
            #args = [eval(exp, env) for exp in x[1:]]
            args = []
            kwargs = {}
            kw = None
            app = None
            for arg in x[1:]:
                if kw:
                    kwargs[kw] = eval(arg, env)
                    kw = None
                    continue
                elif app:
                    if app == '*':
                        args.extend(eval(arg, env))
                    elif app == '**':
                        kwargs.update(eval(arg, env))
                    app = None
                    continue
                elif isinstance(arg,basestring):
                    if arg[-1] == ':':
                        kw = arg[:-1]
                        continue
                    elif arg in ('*','**'):
                        app = arg
                        continue
                args.append(eval(arg, env))
            return proc(*args,**kwargs)
        if hasattr(proc, '__getitem__'):
            if isinstance(proc,dict):
                args = [eval(exp, env) for exp in x[1:]]
                return proc.get(*args)
            return proc[eval(x[1], env)]

def _from(args, env):
    objs = eval(args[0],env)
    prms = args[1]
    obj = None
    for arg in args[2:]:
        op = arg[0]
        if op == 'count':
            return 1 if obj else len(objs)
        elif op == 'at':
            obj = objs[eval(arg[1],env)]
        elif op == 'where':
            pred = Procedure(prms, arg[1], env)
            objs = [val for idx,val in enumerate(objs) if pred(*((val,idx,objs)[:len(prms)]))]
        elif op == 'select':
            proj = Procedure(prms, arg[1], env)
            objs = [proj(*((val,idx,objs)[:len(prms)])) for idx,val in enumerate(objs)]
        elif op == 'orderby':
            for a in reversed(arg[1:]):
                key = Procedure(prms, a, env)
                objs.sort(key=key)
        elif op == 'orderby_down':
            for a in reversed(arg[1:]):
                key = Procedure(prms, a, env)
                objs.sort(key=key, reverse=True)
    return obj if obj else objs

##def _fig(args, env):
##    import figure
##    fig = figure.Fig()
##    def f(node,arg):
##        hd = arg[0]
##        if hd[-1] == ':':
##            node._attr[hd[:-1]] = eval(arg[1],env)
##        else:
##            kid = figure.Node(hd)
##            for a in arg[1:]:
##                f(kid,a)
##            node.append(kid)
##    for arg in args:
##        f(fig,arg)
##    return fig.render()

def _select(bdy):
    pass

#global_env['from'] = _from

def main():
    SRC = """
        (def circle-area (fn (r) (* pi (* r r))))
        (circle-area 3)
        (def fact (fn (n) (if (<= n 1) 1 (* n (fact (- n 1))))))
        (fact 10)
        (fact 100)
        (def first car)
        (first '(1 2 3))
        (def rest cdr)
        (rest '(1 2 3))
        (def count (fn (item L) (if L (+  (equal? item (first L)) (count item (rest L))) 0)))
        (count 0 (list 0 1 2 3 0 0))
        (count 'the '(the more the merrier the bigger the better))
        (def twice (fn (x) (* 2 x)))
        (twice 5)
        (def repeat (fn (f) (fn (x) (f (f x)))))
        ((repeat twice) 10)
        ((repeat (repeat twice)) 10)
        ((repeat (repeat (repeat twice))) 10)
        ((repeat (repeat (repeat (repeat twice)))) 10)
        (pow 2 16)
        (def fib (fn (n) (if (< n 2) 1 (+ (fib (- n 1)) (fib (- n 2))))))
        (def range (fn (a b) (if (= a b) '() (cons a (range (+ a 1) b)))))
        (range 0 10)
        (map fib (range 0 10))
        (map fib (range 0 20))
    """
    LNQ = """
        (def numbers '(5 4 1 3 9 8 6 7 2 0)
             digits '(zero one two three four five six seven eight nine)
             words '(cherry apple blueberry)
             doubles '(1.7 2.3 1.9 4.1 2.9)
        )
        ; Where - Simple 1
        (from numbers (n)
            (where (< n 5))
        )
        ;
        (from digits (digit index)
            (where (< (len digit) index))
        )
        ; Select - Transformation
        (from numbers (n)
            (select (digits n))
        )
        ; Select - Anonymous Types 1
        (from '(aPPLE BlUeBeRrY cHeRry) (w)
            (select (dict 'upper (upper w) 'lower (lower w)))
        )
        ; OrderBy - Simple 1
        (from words (w)
            (orderby w)
        )
        ; OrderBy - Simple 2
        (from words (w)
            (orderby (len w))
        )
        ; OrderBy - Comparer
        (orderby '(aPPLE AbAcUs bRaNcH BlUeBeRrY ClOvEr cHeRry)
                 (fn (w1 w2)
                     (if (< (lower w1) (lower w2)) -1
                         (> (lower w1) (lower w2)) 1
                         0
                     )
                 )
        )
        ; OrderByDescending - Simple 1
        (from doubles (d)
            (orderby_down d)
        )
        ; ThenBy - Simple
        (from digits (d)
            (orderby (len d) d)
        )
        (from digits (d)
            (where (= (d 1) 'i))
            (reverse)
        )
    """
    MON = """
        ;(! '(1 2 3))
        ;(from (db 'dependency) (d)
        ;    (where (and (= d.from 'start) (= d.to 'end)))
        ;    (select (dict 'from d.from_init.name 'to d.to_init.name))
        ;)
        ;(from (db 'initiative) (i)
        ;    (where (= i.category 'impact))
        ;    (select i.name)
        ;)
        ;(def docs (db 'document))
        ;(docs 'DOC0010)
        ;(! "\\"prob
        ;ably\\"")

        (def docs  (db 'document)
             doc   (docs 'DOC0006) ;req.args.id)
             rdocs (map (fn (i) (docs i)) (doc 'related_ids []))
        )
        (dict
            'desc    (doc 'desc "")
            'related rdocs
            'link    (doc 'link "")
            'content (doc 'content "")
        )
        (dict
            'docs (db 'document)
            'grps (db 'docgroup)
            'figs [
                ((db '_svg) 'prog-plan)
                ((db '_svg) 'prog-plan-legend)
            ]
        )
    """
    #for exp in parse(u"(def name \"Marcus Baumgartner & Paulo Cinelli\") {obj ('name name)} (+ 2 3.14e-10i)"):
    for exp in parse(MON):
        #print exp, '=>',
        print eval(exp)

def execute(src, args=None):
    env = Env()
    env.update(global_env)
    if args:
        env.update(args)
    rslt = ''
    for exp in parse(src):
        #print exp, '=>',
        rslt = eval(exp, env)
        #print rslt
    return rslt

if __name__ == '__main__':
    main()
