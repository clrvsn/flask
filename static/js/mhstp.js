//==============================================================================
// Data & Meta Data

var data,
    meta_indx = {},
    enum_vals = {};

function set_data(d) {
    data = d;

    data.meta.forEach(function(m) {
        meta_indx[m._id] = m;
        m.field = {}
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
        if (state == null) {
            state = _.pluck(field.enum_vals, 'val');
            state.push('_none_')
        }

        function mk_one(v) {
            var set = _.contains(state, v.val),
                chk = set ? {checked:'checked'} : {},
                inp = mk('input#'+v.val+'_chk', {type:'checkbox'}, chk),
                wrp = mk('div.checkbox', mk('label', inp, v.txt ));
            inp.click(function () {
                toggle_filter(fld, v.val)
            });
            el.append(wrp);
            filter[fld][v.val] = set;
        }
        if (!field.required) {
            mk_one({val:'_none_', txt:'None'});
        }
        _.each(field.enum_vals, mk_one);
    }
    if (field.type === 'ref') {
        var coll = meta_indx[field.ref_id].name;

        if (state == null) {
            state = _.pluck(data[coll], '_id');
        }

        data[coll].forEach(function(obj) {
            var set = _.contains(state, obj._id),
                chk = set ? {checked:'checked'} : {},
                inp = mk('input#'+obj._id+'_chk', {type:'checkbox'}, chk),
                wrp = mk('div.checkbox', mk('label', inp, obj[field.ref_field] ));
            inp.click(function () {
                toggle_filter(fld, obj._id)
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
        if (val[fld] == null && !(filter[fld]['_none_']))
            return false;
        return !_.any(field.enum_vals, function(v) {
            return (val[fld] === v.val && !(filter[fld][v.val]));
        })
    }
    if (field.type === 'ref') {
        var fld_name = field.name.substr(0,field.name.length-3),
            f = val[fld_name];
        if (f == null) return false;
        return !_.any(data[meta_indx[field.ref_id].name], function(obj) {
            return (f._id === obj._id && !(filter[fld][obj._id]));
        })
    }
}

//==============================================================================
// D3 Helpers

function d3_add(svg, slctr, data, elnm, fn) {
    var r = svg.selectAll(slctr)
               .data(data)
               .enter()
               .append(elnm);

    if (fn != null)
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

function dep_tip(enum_vals, dep) {
    var t = '<p>{0}</p>\n' +
            '<table class="tip">\n' +
            '  <tr><th>From:</th><td>{1}</td></tr>\n' +
            '  <tr><th>To:</th><td>{2}</td></tr>\n' +
            '</table>';

    return fmt(t,
        dep.desc || 'Awaiting description.',
        dep.from_init.name,
        dep.to_init.name
    );
}

