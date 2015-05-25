#-------------------------------------------------------------------------------
# Name:        sexpr
# Purpose:
#
# Author:      Martin
#
# Created:     04/05/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

DELIMS = u"()'{}[]"
SPACE = u" \t\n\r"

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
    def exp():
        quote = False
        in_list = False
        in_dict = False
        lst = []
        token = get()
        while token != None:
            if token in ')}]':
                break
            elif token == "'":
                quote = True
            elif token in '({':
                lst.append(['quote', exp()] if quote else exp())
                quote = False
            elif token == '[':
                lst.append(['quote', ['list'] + exp()] if quote else ['list'] + exp())
                quote = False
            else:
                lst.append(['quote', token] if quote else token)
                quote = False
            token = get()
        return lst
    return exp()

def main():
##    print lex('abc')
##    print lex('(abc (1 2 3) zyz)')
##    print lex('(abc (123) zyz)')
##
##    print parse('abc')
##    print parse('(abc (1 2 3) zyz)')
##    print parse('(abc (123) zyz)')
##
##    print parse('abc ced(abc (123) zyz)(abc (1 2 3) zyz)')
    print lex(u'"Marcus Baumgartner & Paulo Cinelli"')
    print parse(u'{obj \'name "Marcus Baumgartner \\"&\\" Paulo Cinelli"}')
    print parse('(+ (list (+ 1 2) 2 3))')
    print parse('(+ [(+ 1 2) 2 3])')
    print parse('(+ \'[1 2 3])')

if __name__ == '__main__':
    main()
