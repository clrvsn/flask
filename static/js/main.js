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

//==============================================================================
// String Format

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

//==============================================================================

var create = (function() {
    function F() {}
    return function (proto, props) {
        F.prototype = proto;
        obj = new F();
        for (var prop in props) {
            if (props.hasOwnProperty(prop))
                obj.prototype[prop] = props[prop];
        }
        return obj;
    };
})();

//==============================================================================

function num (x) {
    return x - 0;
}

var _NUM = '0123456789';
var _LWR = 'abcdefghijklmnopqrstuvwxyz';
var _UPR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

function _isValid(parm,val) {
    if (parm === "") return true;
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

//==============================================================================
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
    };
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
        //cls = (el.length > 1) ? el[1] : '',
        cls = (el.length > 1) ? _.tail(el) : [],
        id = el[0].split('#');

    el = $('<'+id[0]+'/>');
    if (id.length > 1) {
        el.attr('id', id[1]);
    }
    if (cls) {
        el.addClass(cls.join(' '));
    }

    _.each(_.tail(arguments), function (arg) {
        if (arg) {
            if (arg.constructor == Object) {
                el.attr(arg);
            } else if (_.isArray(arg)) {
                _.each(arg, function (a) {el.append(a);});
            } else {
                el.append(arg);
            }
        }
    });

    return el;
}
