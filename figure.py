#-------------------------------------------------------------------------------
# Name:        figure
# Purpose:
#
# Author:      Martin
#
# Created:     18/05/2015
# Copyright:   (c) Martin 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class Node(list):
    def __init__(self, name, *kids, **attr):
        super(Node,self).__init__(kids)
        self._name = name
        self._attr = attr
    def render(self, depth=1):
        sp = '  '
        attr = ' '.join('%s="%s"' % (k,str(v)) for k,v in self._attr.iteritems())
        kids = ('\n' + sp*depth).join(k.render(depth+1) for k in self)
        elem = '<' + self._name
        if attr:
            elem += ' ' + attr
        if kids:
            elem += '>\n' + (sp*depth) + kids + '\n' + (sp*(depth-1)) + '</' + self._name + '>'
        else:
            elem += '/>'
        return elem

class Fig(Node):
    def __init__(self, *kids, **attr):
        super(Fig,self).__init__('svg', *kids, **attr)
    def render(self):
        fig = '<?xml version="1.0"?>\n'
        fig += super(Fig,self).render()
        return fig

#-------------------------------------------------------------------------------
# 9.2 The ‘rect’ element
# 9.3 The ‘circle’ element
# 9.4 The ‘ellipse’ element
# 9.5 The ‘line’ element

def rect(*args, **kwargs): return Node('rect', *args, **kwargs)
def circle(*args, **kwargs): return Node('circle', *args, **kwargs)
def ellipse(*args, **kwargs): return Node('ellipse', *args, **kwargs)
def line(*args, **kwargs): return Node('line', *args, **kwargs)


class PointList(list):
    def __str__(self):
        return ' '.join("%g,%g" % p for p in self)

class PolyPoint(Node):
    def __init__(self, name, *kids, **attr):
        super(PolyPoint,self).__init__(name, *kids, **attr)
        if 'points' in self._attr:
            self._attr['points'] = PointList(self._attr['points'])

#-------------------------------------------------------------------------------
# 9.6 The ‘polyline’ element
# 9.7 The ‘polygon’ element

def polyline(*args, **kwargs): return PolyPoint('polyline', *args, **kwargs)
def polygon(*args, **kwargs): return PolyPoint('polygon', *args, **kwargs)


def main():
    #print Node('circle',cx=12,cy=24,r=44).render()
    #print Node('g', Node('circle',cx=12,cy=24,r=44)).render()
    #print Fig(Node('g', Node('circle',cx=12,cy=24,r=44))).render()
    print [(x,y) for x in range(3) for y in range(3)]

if __name__ == '__main__':
    main()
