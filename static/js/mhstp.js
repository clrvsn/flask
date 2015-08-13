/* global: mk */

//==============================================================================
// Fiscal Dates

var FiscalDate = function (fy, t, end) {
    this.fy = fy;
    this.t = t;
    this.end = end;
};

FiscalDate.prototype.fiscal_str = function () {
    return 'FY' + this.fy + '-T' + (this.t + 1);
};


function mk_fyt(s, end) {
    var re = /FY(\d+)[ -]*(T(\d))?/i,
        m = re.exec(s);

    if (m && m[0]) {
        return new FiscalDate(Number(m[1]), Number(m[3] || '1') - 1, end);
    }
    return undefined;
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
    if (yr === undefined)
        return undefined;

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

var init_grid = {
    cols: 6,
    rows: 12,
    colw: 170,
    rowh: 65,
};

function mk_init_rect(d) {
    if (d.byprog_col === undefined || d.byprog_row === undefined) {
        return undefined;
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
                var rect = d3.select(this)
                  .classed('hover', true);
                _.each(d.lines, function (line) {
                    line.classed('hover', true);
                });
                if (init_rect.hover) {
                    init_rect.hover(true, rect[0][0]);
                }
            })
            .on('mouseleave', function () {
                var rect = d3.select(this)
                  .classed('hover', false);
                _.each(d.lines, function (line) {
                    line.classed('hover', false);
                });
                if (init_rect.hover) {
                    init_rect.hover(false);
                }
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

    mk_one(0, 'T', rag.T);
    mk_one(1, 'S', rag.S);
    mk_one(2, 'C', rag.C);

    g.classed("rag", true)
     .attr("transform", "translate(" + x + " " + y + ")");

    return g;
}

function init_rag(ini) {
    //if (ini.tp_rag_t || ini.tp_rag_s || ini.tp_rag_c) {
        var r = mk_init_rect(ini);

        if (r) {
            var g = mk_ini_rag_g(ini, d3.select(this), r.r - (8 + 3 * 12), r.t - 8);
            if (init_rag.click) {
                g.on('click', function () {init_rag.click(ini);});
            }
        }
    //}
}

//==============================================================================
// Data & Meta Data

var data,
    meta_indx = {},
    enum_vals = {};

function set_data(d) {
    data = d;

    data.meta.forEach(function(m) {
        meta_indx[m._id] = m;
        m.field = {};
        m.fields.forEach(function(f) {
            m.field[f.name] = f;
            if (f.type === 'enum') {
                vals = {};
                f.enum_vals.forEach(function(v) {
                    vals[v.val] = v.txt;
                });
                enum_vals[m._id.toLowerCase() + '_' + f.name] = vals;
            }
        });
    });
}

var index = {};

function mk_index(name, objs) {
    var indx = {};
    _.each(objs, function (obj) {
        indx[obj._id] = obj;
    });
    index[name] = indx;
}

//==============================================================================
// Toggles

var toggle = {};

function mk_toggle(name, label, state, eid) {
    var el = $('#'+eid);

    var att = state ? {type:'checkbox', checked:'checked'} : {type:'checkbox'};
        chk = mk('input#'+name+'_chk', att),
        div = mk('div.checkbox', mk('label', chk, label));
    chk.click(function () {
        toggle[name] = !(toggle[name]);
        render();
    });
    el.append(div);
    toggle[name] = state;
}
function mk_toggle_inline(name, label, state, eid) {
    var el = $('#'+eid);

    var att = state ? {type:'checkbox', checked:'checked'} : {type:'checkbox'};
        inp = mk('input#'+name+'_chk', att),
        wrp = mk('label.checkbox-inline', inp, label);
    inp.click(function () {
        toggle[name] = !(toggle[name]);
        render();
    });
    el.append(wrp);
    toggle[name] = state;
}

//==============================================================================
// Choices

var choice = {};


function mk_choice_inline(name, eid, opts, state) {
    var el = $('#'+eid);

    function mk_one(opt) {
        var chk = state == opt.val ? {checked:'checked'} : {};
            inp = mk('input', {name: name+'_rad', type: 'radio', value: opt.val}, chk),
            wrp = mk('label.radio-inline', inp, opt.txt);
        inp.click(function () {
            choice[name] = opt.val;
            render();
        });
        el.append(wrp);
    }

    _.each(opts, function (opt) {
        mk_one(opt);
    });

    choice[name] = state;
}

//==============================================================================
// Filters

var filter = {};

function toggle_filter(fld, val)
{
    filter[fld][val] = !(filter[fld][val]);
    render();
}

function set_all_filters(fld, state) {
    _.each(filter[fld], function (v,k) {
        $('#'+k+'_chk').prop('checked',state);
        filter[fld][k] = state;
    });
    render();
}

function mk_filter(mid, fld, eid, state) {
    var el = $('#'+eid),
        meta = meta_indx[mid],
        field = meta.field[fld];

    filter[fld] = {};

    if (field.type === 'enum') {
        if (state === undefined) {
            state = _.pluck(field.enum_vals, 'val');
            state.push('_none_');
        }

        var mk_one = function (v) {
            var set = _.contains(state, v.val),
                chk = {checked:set},
                inp = mk('input#'+v.val+'_chk', {type:'checkbox'}, chk),
                wrp = mk('div.checkbox', mk('label', inp, v.txt ));
            inp.click(function () {
                toggle_filter(fld, v.val);
            });
            el.append(wrp);
            filter[fld][v.val] = set;
        };
        if (!field.required) {
            mk_one({val:'_none_', txt:'None'});
        }
        _.each(field.enum_vals, mk_one);
    }
    if (field.type === 'ref') {
        var coll = meta_indx[field.ref_id].name;

        if (state === undefined) {
            state = _.pluck(data[coll], '_id');
        }

        data[coll].forEach(function(obj) {
            var set = _.contains(state, obj._id),
                chk = {checked:set},
                inp = mk('input#'+obj._id+'_chk', {type:'checkbox'}, chk),
                wrp = mk('div.checkbox', mk('label', inp, obj[field.ref_field] ));
            inp.click(function () {
                toggle_filter(fld, obj._id);
            });
            el.append(wrp);
            filter[fld][obj._id] = set;
        });
    }
}

function do_filter(mid, fld, val) {
    var meta = meta_indx[mid],
        field = meta.field[fld];

    if (field.type === 'enum') {
        if (val[fld] === undefined && !(filter[fld]['_none_']))
            return false;
        return !_.any(field.enum_vals, function(v) {
            return (val[fld] === v.val && !(filter[fld][v.val]));
        });
    }
    if (field.type === 'ref') {
        var fld_name = field.name.substr(0,field.name.length-3),
            f = val[fld_name];
        if (f === undefined) return false;
        return !_.any(data[meta_indx[field.ref_id].name], function(obj) {
            return (f._id === obj._id && !(filter[fld][obj._id]));
        });
    }
}

//==============================================================================
// D3 Helpers

function d3_add(svg, slctr, data, elnm, fn) {
    var r = svg.selectAll(slctr)
               .data(data)
               .enter()
               .append(elnm);

    if (fn !== undefined)
        r.each(fn);

    return r;
}

function d3_def_arrow(defs, fill) {
    defs.append("marker")
        .attr({
            id: "arrow",
            viewBox: "-20 -10 20 20",
            markerWidth: 12,
            markerHeight: 12,
            refx: 0,
            refy: 0,
            orient: "auto",
            markerUnits: "userSpaceOnUse"
        })
        .append("path")
        .attr({
            d: "M -20 -6 0 0 -20 6",
            fill: fill,
        });
}

function d3_def_circle(defs, fill) {
    defs.append("marker")
        .attr({
            id: "circle",
            viewBox: "-5 -5 10 10",
            markerWidth: 10,
            markerHeight: 10,
            //refx: 0,
            //refy: 0,
            markerUnits: "userSpaceOnUse"
        })
        .append("circle")
        .attr({
            r: 3, cx: 0, cy: 0,
            fill: fill,
        });
}

//==============================================================================
// RAG Helpers

function rag_desc(rag, desc) {
    if (desc)
        return marked(desc);
    if (rag === 'green')
        return 'Progressing according to plan.';
    if (!rag)
        return 'n/a';
    return 'TBD';
}

function rag_act(rag, act) {
    if (act)
        return marked(act);
    if (rag === 'green')
        return 'No action needed.';
    if (!rag)
        return 'n/a';
    return 'TBD';
}

//==============================================================================
// ToolTip Helpers

function ini_tip(enum_vals, ini) {
    var s = mk_fyt(ini.start, false),
        e = mk_fyt(ini.end, true),
        t = '<table class="tip">\n' +
            '  <tr><th>Status:</th><td>{0}</td></tr>\n' +
            '  <tr><th>Type:</th><td>{1}</td></tr>\n' +
            '  <tr><th>Category:</th><td>{2}</td></tr>\n' +
            '  <tr><th>Programme:</th><td>{3}</td></tr>\n' +
            '  <tr><th>Function:</th><td>{4}</td></tr>\n' +
            '  <tr><th>Start:</th><td>{5}</td></tr>\n' +
            '  <tr><th>End:</th><td>{6}</td></tr>\n' +
            '</table>';

    return fmt(t,
        enum_vals.ini_state[ini.state],
        enum_vals.ini_type[ini.type],
        enum_vals.ini_category[ini.category],
        ini.program.name,
        ini['function'],
        s ? s.fiscal_str() : '',
        e ? e.fiscal_str() : ''
    );
}

function dep_tip(init_indx, dep) {
    var t = '<p>{0}</p>\n' +
            '<table class="tip">\n' +
            '  <tr><th>From:</th><td>{1}</td></tr>\n' +
            '  <tr><th>To:</th><td>{2}</td></tr>\n' +
            '</table>';

    return fmt(t,
        dep.desc || 'Awaiting description.',
        init_indx[dep.from_init_id].name,
        init_indx[dep.to_init_id].name
    );
}

