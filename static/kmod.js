﻿if (!Array.prototype.forEach)
{
  Array.prototype.forEach = function(fun /*, thisp*/)
  {
    var len = this.length;
    if (typeof fun != "function")
      throw new TypeError();

    var thisp = arguments[1];
    for (var i = 0; i < len; i++)
    {
      if (i in this)
        fun.call(thisp, this[i], i, this);
    }
  };
}

function fmt() {
    // The string containing the format items (e.g. "{0}")
    // will and always has to be the first argument.
    var theString = arguments[0];

    // start with the second argument (i = 1)
    for (var i = 1; i < arguments.length; i++) {
        // "gm" = RegEx options for Global search (more than one instance)
        // and for Multiline search
        var regEx = new RegExp("\\{" + (i - 1) + "\\}", "gm");
        theString = theString.replace(regEx, arguments[i]);
    }

    return theString;
}

// Make Underscore templates more like Moustache
_.templateSettings = {
  interpolate: /\{\{(.+?)\}\}/g
};


funcition mk_id(prefix, num) {
    if (_.isArray(num)) {
        num = num.length + 1;
    }
    return prefix + ('0000' + num).slice(-4);
}

//==============================================================================
// Geometry

var ACCY = 10e-6;

// Find intersection of line segments KL and MN
function intersect_linesegs(xk,yk, xl,yl, xm,ym, xn,yn) {
    var xlk = xl - xk,
        ylk = yl - yk,
        xnm = xn - xm,
        ynm = yn - ym,
        xmk = xm - xk,
        ymk = ym - yk,
        det = xnm * ylk - ynm * xlk;

    if (Math.abs(det) < ACCY) {
        // The two line segments are parallel
        return undefined;
    }
    var detinv = 1.0 / det,
        s = (xnm * ymk - ynm * xmk) * detinv,
        t = (xlk * ymk - ylk * xmk) * detinv;

    if (s < 0 || s > 1 || t < 0 || t > 1) {
        // Intersection not within line segments
        return undefined;
    }
    return {
        x: xk + xlk * s,
        y: yk + ylk * s,
    };
}

// Find intersection of line segment KL and rectangle MNPQ
function intersect_lineseg_rect(xk,yk, xl,yl, xm,ym, xn,yn, xp,yp, xq,yq) {
    var seg_pairs = [
            [xk,yk, xl,yl, xm,ym, xn,yn],
            [xk,yk, xl,yl, xn,yn, xp,yp],
            [xk,yk, xl,yl, xp,yp, xq,yq],
            [xk,yk, xl,yl, xq,yq, xm,ym],
        ],
        i = 0,
        n = seg_pairs.length;

    for (; i < n; i++) {
        var pair = seg_pairs[i],
            xy = intersect_linesegs.apply(this, pair);

        if (xy) {
            return xy;
        }
    }

    return undefined;
}


//==============================================================================
// Fiscal Dates

var FiscalDate = function (fy, t, end) {
    this.fy = fy;
    this.t = t;
    this.end = end;
}

FiscalDate.prototype.fiscal_str = function () {
    return 'FY' + this.fy + '-T' + (this.t + 1);
};


function mk_fyt(s, end) {
    var re = /FY(\d+)[ -]*(T(\d))?/i,
        m = re.exec(s);

    if (m && m[0]) {
        return new FiscalDate(Number(m[1]), Number(m[3] || '1') - 1, end);
    }
    return null;
}
function fyt_col(fyt, fst) {
    return fyt ? Math.max(0, (fyt.fy - fst + (fyt.t + (fyt.end ? 1 : 0))/3)) : 0;
    //return fyt ? Math.max(0, (fyt.fy - fst + fyt.t/3)) : 0;
}


//==============================================================================

function mk_class(s) {
    return s.toLowerCase().replace(/ /g, "").replace(/-/g, "");
}

//==============================================================================
// Initiatives

var RAG = {
    'INI0025': {T: 'G', S: 'G', C: 'G'},
    'INI0026': {T: 'G', S: 'G', C: 'G'},
    'INI0052': {T: 'G', S: 'G', C: 'G'},
    'INI0023': {T: 'G', S: 'G', C: 'G'},
    'INI0003': {T: 'G', S: 'G', C: 'G'},
    'INI0002': {T: 'G', S: 'G', C: 'G'},
    'INI0051': {T: 'G', S: 'G', C: 'A'},

    'INI0035': {T: 'G', S: 'G', C: 'G'},
    'INI0041': {T: 'G', S: 'A', C: 'A'},
    'INI0049': {T: 'G', S: 'G', C: 'G'},
    //'': {T: 'G', S: 'G', C: 'G'},

    'INI0030': {T: 'G', S: 'G', C: 'G'},
    'INI0017': {T: 'G', S: 'G', C: 'G'},
    'INI0005': {T: 'G', S: 'G', C: 'G'},
    'INI0020': {T: 'G', S: 'G', C: 'G'},

    'INI0032': {T: 'G', S: 'G', C: 'G'},
    'INI0031': {T: 'G', S: 'G', C: 'G'},

    'INI0009': {T: 'G', S: 'G', C: 'G'},

    'INI0038': {T: 'A', S: 'R', C: 'G'},

    'INI0043': {T: 'G', S: 'G', C: 'G'},
    'INI0044': {T: 'G', S: 'G', C: 'G'},
    'INI0042': {T: 'G', S: 'G', C: 'G'},
    'INI0021': {T: 'G', S: 'G', C: 'A'},
    'INI0022': {T: 'G', S: 'G', C: 'A'},
};

var init_grid = {
    cols: 6,
    rows: 12,
    colw: 170,
    rowh: 65,
};

function mk_init_rect(d) {
    var x = d.byprog_col * init_grid.colw + 20,
        y = d.byprog_row * init_grid.rowh + 10 + init_grid.rowh/2,
        w = init_grid.colw - 40,
        h = init_grid.rowh - 20;
    return {
        l: x,
        t: y,
        r: x + w,
        b: y + h,
        w: w,
        h: h,
        cx: x + w/2,
        cy: y + h/2,
    };
}

function init_rect(d) {
    var r = mk_init_rect(d),
        typ = mk_class(d.type);
    d3.select(this)
        .append("rect")
        .classed(typ, true)
        .classed(mk_class(d.category), true)
        .classed(mk_class(d.state), true)
        .attr({
            x: r.l,  y: r.t,  width: r.w,  height: r.h,
            rx: typ === "project" ? 5 : (typ === "activity" ? (init_grid.rowh-20)/2 : 0),
            ry: typ === "project" ? 5 : (typ === "activity" ? (init_grid.rowh-20)/2 : 0),
        });
        //.on('click', function () {window.location.href = '/init/'+d._id;});
}

function init_text(d) {
    var g = d3.select(this);

    g.selectAll("text")
        .data(function(d) {
            var ns = d.byprog_txt.split("|");
            return ns.map(function(n) {
                return {
                    col: d.byprog_col,
                    row: d.byprog_row,
                    n: ns.length,
                    name: n,
                };
            });
        })
        .enter()
        .append("text")
        .text(function(d) {return d.name})
        .attr({
            x: function(d)    { return d.col * init_grid.colw + init_grid.colw/2; },
            y: function(d, i) { return d.row * init_grid.rowh + init_grid.rowh/2 + (9 - d.n*6 + i*12) + init_grid.rowh/2; },
        });
}

function mk_ini_rag_g(ini, node, x, y) {
    var g = node.append("g");

    function mk_one(i, ltr, clr) {
        g.append("circle")
         .classed(clr, true)
         .attr({
            r: 5.5,
            cx: 5 + i * 10,
            cy: 5,
         });
        g.append("text")
         .text(ltr)
         .attr({
            x: 4 + i * 10,
            y: 8.5,
         });
    }

    var rag = RAG[ini._id] || {T: '-', S: '-', C: '-'},
        clrs = {R: 'red', A: 'amber', G: 'green', '-': 'grey'};

    mk_one(0, 'T', clrs[rag['T']]);
    mk_one(1, 'S', clrs[rag['S']]);
    mk_one(2, 'C', clrs[rag['C']]);

    g.classed("rag", true)
     .attr("transform", "translate(" + x + " " + y + ")");

    return g;
}

function init_rag(d) {
    var r = mk_init_rect(d);

    mk_ini_rag_g(d, d3.select(this), r.r - 25, r.t - 5);
}


