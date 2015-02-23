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
}


//==============================================================================

function mk_class(s) {
    return s.toLowerCase().replace(/ /g, "").replace(/-/g, "");
}

