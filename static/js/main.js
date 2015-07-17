if (!Array.prototype.forEach)
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

// from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/isArray
if (!Array.isArray) {
  Array.isArray = function(arg) {
    return Object.prototype.toString.call(arg) === '[object Array]';
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

function num (x) {
    return x - 0;
}

var _NUM = '0123456789';
var _LWR = 'abcdefghijklmnopqrstuvwxyz';
var _UPR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

function _isValid(parm,val) {
    if (parm == "") return true;
    for (i=0; i<parm.length; i++) {
        if (val.indexOf(parm.charAt(i),0) == -1) return false;
    }
    return true;
}

function isNumber(parm) {return _isValid(parm,_NUM);}
function isLower(parm) {return _isValid(parm,_LWR);}
function isUpper(parm) {return _isValid(parm,_UPR);}
function isAlpha(parm) {return _isValid(parm,_LWR+_UPR);}
function isAlphanum(parm) {return _isValid(parm,_LWR+_UPR+_NUM);}

// Make Underscore templates more like Moustache
//_.templateSettings = {
//  interpolate: /\{\{(.+?)\}\}/g
//};
//Backform.bootstrap2();

// from http://stackoverflow.com/questions/2419749/get-selected-elements-outer-html
(function($) {
    $.fn.outerHTML = function (arg) {
        var ret;

        // If no items in the collection, return
        if (!this.length)
            return typeof arg == "undefined" ? this : null;
        // Getter overload (no argument passed)
        if (!arg) {
            return this[0].outerHTML ||
                (ret = this.wrap('<div>').parent().html(), this.unwrap(), ret);
        }
        // Setter overload
        $.each(this, function (i, el) {
            var fnRet,
                pass = el,
                inOrOut = el.outerHTML ? "outerHTML" : "innerHTML";

            if (!el.outerHTML)
                el = $(el).wrap('<div>').parent()[0];

            if (jQuery.isFunction(arg)) {
                if ((fnRet = arg.call(pass, i, el[inOrOut])) !== false)
                    el[inOrOut] = fnRet;
            }
            else
                el[inOrOut] = arg;

            if (!el.outerHTML)
                $(el).children().unwrap();
        });

        return this;
    }
})(jQuery);


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
// Generate HTML

function mk() {
    var el = arguments[0].split('.'),
        cls = (el.length > 1) ? el[1] : '',
        id = el[0].split('#');

    el = $('<'+id[0]+'/>');
    if (id.length > 1) {
        el.attr('id', id[1]);
    }
    if (cls) {
        el.addClass(cls);
    }

    _.each(_.tail(arguments), function (arg) {
        if (arg) {
            if (arg.constructor == Object) {
                el.attr(arg)
            } else if (_.isArray(arg)) {
                _.each(arg, function (a) {el.append(a);});
            } else {
                el.append(arg);
            }
        }
    });

    return el;
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

//var CalendarDate = function (cd, end) {
//    var d = cd.split('-');
//    this.date = new Date(d[0], d[1]-1, d[2], 0, 0);
//    this.end = end;
//}

function mk_date(yr, mn, dy) {
    if (yr == null)
        return null;

    if (_.isString(yr)) {
        var d = yr.split('-');
        yr = d[0] - 0;
        mn = d[1] - 1;
        dy = d[2] - 1;
    }
    if (yr < 100) yr = yr + 2000;
    return new Date(yr, mn, dy, 0, 0, 0);
}

function mk_date_now() {
    return new Date();
}

function date_col(date, fst_date, cols_per_year) {
    var ms = date.getTime() - fst_date.getTime(),
        ms_per_year = 365 * 24 * 60 * 60 * 1000,
        col = (ms / ms_per_year) * cols_per_year;

    return col;
}

function cmp_date(date1, date2) {
    return date1.getTime() - date2.getTime();
}

//==============================================================================

function mk_class(s) {
    return s.toLowerCase().replace(/ /g, "").replace(/-/g, "");
}

//==============================================================================
// Initiatives

/*var RAG = {
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
};*/

var init_grid = {
    cols: 6,
    rows: 12,
    colw: 170,
    rowh: 65,
};

function mk_init_rect(d) {
    if (d.byprog_col == null || d.byprog_row == null) {
        return null;
    }
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
        typ = d.type ? mk_class(d.type) : "project";
    if (r) {
        d3.select(this)
            .append("rect")
            .classed(typ, true)
            .classed(mk_class(d.category), true)
            .classed(mk_class(d.state), true)
            .attr({
                x: r.l,  y: r.t,  width: r.w,  height: r.h,
                rx: typ === "project" ? 5 : (typ === "activity" ? (init_grid.rowh-20)/2 : 0),
                ry: typ === "project" ? 5 : (typ === "activity" ? (init_grid.rowh-20)/2 : 0),
            })
            .on('mouseenter', function () {
                d3.select(this)
                  .classed('hover', true);
                _.each(d.lines, function (line) {
                    line.classed('hover', true);
                });
            })
            .on('mouseleave', function () {
                d3.select(this)
                  .classed('hover', false);
                _.each(d.lines, function (line) {
                    line.classed('hover', false);
                });
            })
            .on('click', function () {window.location.href = '/init/'+d._id;});
    }
}

function init_text(d) {
    var text = d3.select(this)
                 .append("text")
                 .text(d.name);

    d3plus.textwrap()
          .container(text)
          .padding(3)
          .valign("middle")
          .draw();

    /*if (d.brkn_name) {
        g.selectAll("text")
            .data(function(d) {
                var ns = d.brkn_name.split("|");
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
    }*/
}

function mk_ini_rag_g(ini, node, x, y) {
    var g = node.append("g");

    function mk_one(i, ltr, clr) {
        g.append("circle")
         .classed('rag', true)
         .classed('rag-'+clr, clr !== 'grey')
         .attr({
            r: 6,
            cx: 5 + i * 12,
            cy: 5,
         });
        g.append("text")
         .text(ltr)
         .attr({
            x: 4.5 + i * 12,
            y: 8.25,
         });
    }

    var rag = {T: ini.ini_rag_t || 'grey', S: ini.ini_rag_s || 'grey', C: ini.ini_rag_c || 'grey'};

    mk_one(0, 'T', rag['T']);
    mk_one(1, 'S', rag['S']);
    mk_one(2, 'C', rag['C']);

    g.classed("rag", true)
     .attr("transform", "translate(" + x + " " + y + ")");

    return g;
}

function init_rag(ini) {
    //if (ini.tp_rag_t || ini.tp_rag_s || ini.tp_rag_c) {
        var r = mk_init_rect(ini);

        if (r) {
            mk_ini_rag_g(ini, d3.select(this), r.r - (8 + 3 * 12), r.t - 8);
        }
    //}
}


