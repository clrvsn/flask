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

function mk_filter(mid, fld, eid) {
    var el = $('#'+eid),
        meta = meta_indx[mid],
        field = meta.field[fld];

    filter[fld] = {};
    if (field.type === 'enum') {
        function mk_one(v) {
            var chk = mk('input#'+v.val+'_chk', {type:'checkbox', checked:'checked'}),
                div = mk('div.checkbox', mk('label', chk, v.txt ));
            chk.click(function () {
                toggle_filter(fld, v.val)
            });
            el.append(div);
            filter[fld][v.val] = true;
        }
        if (!field.required) {
            mk_one({val:'<none>', txt:'None'});
        }
        _.each(field.enum_vals, mk_one);
    }
    if (field.type === 'ref') {
        var coll = meta_indx[field.ref_id].name;
        data[coll].forEach(function(obj) {
            var chk = mk('input#'+obj._id+'_chk', {type:'checkbox', checked:'checked'}),
                div = mk('div.checkbox', mk('label', chk, obj[field.ref_field] ));
            chk.click(function () {
                toggle_filter(fld, obj._id)
            });
            el.append(div);
            filter[fld][obj._id] = true;
        });
    }
}

function do_filter(mid, fld, val) {
    var meta = meta_indx[mid],
        field = meta.field[fld];

    if (field.type === 'enum') {
        if (val[fld] == null && !(filter[fld]['<none>']))
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
