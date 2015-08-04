init_grid.cols = 3;
init_grid.rows = 1;
init_grid.colw = 170;
init_grid.rowh = 65;

var w = init_grid.cols * init_grid.colw,
    h = init_grid.rows * init_grid.rowh + init_grid.rowh/2,
    init_indx = {},
    meta_indx = {},
    enum_vals = {};


function soft_line(d) {
    var d1 = init_indx[d.from_init_id],
        d2 = init_indx[d.to_init_id];
    d3.select(this)
        .attr({
            x1: d1.byprog_col * init_grid.colw + init_grid.colw/2,
            y1: d1.byprog_row * init_grid.rowh + init_grid.rowh,
            x2: d2.byprog_col * init_grid.colw + init_grid.colw/2,
            y2: d2.byprog_row * init_grid.rowh + init_grid.rowh,
        });
}

function hard_line_sense(dep) {
    var d1 = init_indx[dep.from_init._id],
        d2 = init_indx[dep.to_init._id],
        r1 = mk_init_rect(d1),
        xk = r1.cx, yk = r1.cy,
        r2 = mk_init_rect(d2),
        xl = r2.cx, yl = r2.cy,
        xm = r2.l, ym = r2.t,
        xn = r2.r, yn = r2.t,
        xp = r2.r, yp = r2.b,
        xq = r2.l, yq = r2.b,
        p = intersect_lineseg_rect(xk,yk, xl,yl, xm,ym, xn,yn, xp,yp, xq,yq);
    
    if (!p) {
        p = {x: xl, y: yl};
    }
    
    d3.select(this) //.append('line')
        .classed('sense', true)
        .attr({
            x1: xk,
            y1: yk,
            x2: p.x,
            y2: p.y,
        })
        .on('mouseenter', function (dep) {
            dep.line.classed('hover', true);
        })
        .on('mouseleave', function (dep) {
            dep.line.classed('hover', false);
        });
}
function hard_line(dep) {
    var d1 = init_indx[dep.from_init._id],
        d2 = init_indx[dep.to_init._id],
        r1 = mk_init_rect(d1),
        xk = r1.cx, yk = r1.cy,
        r2 = mk_init_rect(d2),
        xl = r2.cx, yl = r2.cy,
        xm = r2.l, ym = r2.t,
        xn = r2.r, yn = r2.t,
        xp = r2.r, yp = r2.b,
        xq = r2.l, yq = r2.b,
        p = intersect_lineseg_rect(xk,yk, xl,yl, xm,ym, xn,yn, xp,yp, xq,yq);
    
    if (!p) {
        p = {x: xl, y: yl};
    }
    
    dep.line = d3.select(this) //.append('line')
        .classed('draw', true)
        .attr({
            x1: xk,
            y1: yk,
            x2: p.x,
            y2: p.y,
            "marker-end": "url(#arrow)",
        });
}

$(function () {
    $('#dep-info').dialog({
        autoOpen: false,
        resizable: false,
        width: 600,
    });
    $('#dep-info-icon').click(function () {
        $('#dep-info').dialog('open');
        //$('#dep-info').modal();
        event.preventDefault();
    });
    $('#rag-info').dialog({
        autoOpen: false,
        resizable: false,
        width: 900,
    });
});

d3.json(api, function (data) {

    data.meta.forEach(function(m) {
        meta_indx[m._id] = m;
        m.fields.forEach(function(f) {
            if (f.type === 'enum') {
                vals = {};
                f.enum_vals.forEach(function(v) {
                    vals[v.val] = v.txt;
                });
                enum_vals[m._id.toLowerCase() + '_' + f.name] = vals;
            }
        });
    });

    init_grid.rows = Math.max(data.softs.length+1, Math.max(data.froms.length, data.tos.length));
    h = init_grid.rows * init_grid.rowh + init_grid.rowh/2;

    var caps = mk('ul', _.map(data.caps, function (x) {return mk('li',x.name);}));

    if (data.ini.type === 'prestudy') {
        $("#caps_out_ttl").text("Capabilities Covered:");
        $("#caps_in_ttl").text("");
    } else {
        $("#caps_out_ttl").text("Capabilities to Move Out:");
        $("#caps_in_ttl").text("Capabilities to Move In:");
    }

    $("#objective").text(data.ini.objective || '');
    $("#tp_objective").text(data.ini.tp_objective || '');
    $("#biz_pm_id").text(data.ini.biz_pm ? (data.ini.biz_pm.name) : (data.ini.state == 'pending' ? 'TBD' : ''));
    $("#it_pm_id").text(data.ini.it_pm ? (data.ini.it_pm.name) : (data.ini.state == 'pending' ? 'TBD' : ''));
    $("#caps_out").append(caps);

    $("#sg_tp_rep_id").text(data.ini.sg_tp_rep ? (data.ini.sg_tp_rep.name) : (data.ini.state == 'pending' ? 'TBD' : ''));
    $("#sg_chair_id").text(data.ini.sg_chair ? (data.ini.sg_chair.name) : (data.ini.state == 'pending' ? 'TBD' : ''));
    $("#orderer_id").text(data.ini.orderer ? (data.ini.orderer.name) : (data.ini.state == 'pending' ? 'TBD' : ''));

    $("#type").text(enum_vals.ini_type[data.ini.type]);
    $("#category").text(enum_vals.ini_category[data.ini.category]);
    $("#state").text(enum_vals.ini_state[data.ini.state]);
    $("#process").text(data.ini.process.title);
    $("#start").text(data.ini.start || '');
    $("#end").text(data.ini.end || '');

    var inis = [data.ini],
        irow = (init_grid.rows-1) / 2,
        top_soft, bot_soft;

    data.ini.byprog_row = irow - 1/2;
    data.ini.byprog_col = 1;
    init_indx[data.ini._id] = data.ini;
    top_soft = data.ini;
    bot_soft = data.ini;

    _.each(data.froms, function (e, i) {
        e.byprog_row = irow - (data.froms.length/2) + i;
        e.byprog_col = 0;
        inis.push(e);
        init_indx[e._id] = e;
    });
    _.each(data.tos, function (e, i) {
        e.byprog_row = irow - (data.tos.length/2) + i;
        e.byprog_col = 2;
        inis.push(e);
        init_indx[e._id] = e;
    });
    _.each(data.softs, function (e, i) {
        e.byprog_row = irow - 1/2 + (i%2 ? -1 : 1) *  Math.floor(1 + i/2);
        e.byprog_col = 1;
        inis.push(e);
        init_indx[e._id] = e;
        top_soft = top_soft ? (top_soft.byprog_row < e.byprog_row ? top_soft : e) : e;
        bot_soft = bot_soft ? (bot_soft.byprog_row > e.byprog_row ? bot_soft : e) : e;
    });

    var svg = d3.select("#diagram")
                .append("svg")
                .attr("width", w)
                .attr("height", h);

    svg.append("defs")
        .append("marker")
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
            d: "M-20,-8L0,0L-20,8",
            fill: "black",
        });

    if (data.softs.length > 0) {
        svg.selectAll("line.soft")
            .data([{from_init_id:top_soft._id, to_init_id:bot_soft._id}])
            .enter()
            .append("line")
            .classed("soft", true)
            .each(soft_line);
    }

    //var froms = _.map(data.froms, function (x) {return {from_init_id:x._id, to_init_id:_id};}),
    //    tos = _.map(data.tos, function (x) {return {from_init_id:_id, to_init_id:x._id};});

    var froms = _.where(data.deps_from, {type: 'hard'}),
        tos = _.where(data.deps_to, {type: 'hard'});

    svg.selectAll("line.sense")
        .data(froms.concat(tos))
        .enter()
        .append("line")
        .each(hard_line_sense);

    svg.selectAll("line.draw")
        .data(froms.concat(tos))
        .enter()
        .append("line")
        .each(hard_line);


    var gs = svg.selectAll("g.init")
             .data(inis)
             .enter()
             .append("g")
             .classed("init", true)
             .classed("this", function(d){return d._id == _id;});


    gs.each(init_rect);
    gs.each(init_text);
    init_rag.click = function (ini) {
        $('#rag-ini-name').text(ini.name);
        $('#rag-update').text(ini.ini_rag_date || 'unknown date');
        $('#rag-t').attr('class', 'rag-' + ini.ini_rag_t || 'grey');
        $('#rag-t-desc').html(rag_desc(ini.ini_rag_t, ini.ini_rag_t_desc));
        $('#rag-t-act').html(rag_act(ini.ini_rag_t, ini.ini_rag_t_act));
        $('#rag-t-resp').text(ini.ini_rag_t_resp ? ini.ini_rag_t_resp.name : '');
        $('#rag-t-due').text(ini.ini_rag_t_due || '');
        $('#rag-s').attr('class', 'rag-' + ini.ini_rag_s || 'grey');
        $('#rag-s-desc').html(rag_desc(ini.ini_rag_s, ini.ini_rag_s_desc));
        $('#rag-s-act').html(rag_act(ini.ini_rag_s, ini.ini_rag_s_act));
        $('#rag-s-resp').text(ini.ini_rag_s_resp ? ini.ini_rag_s_resp.name : '');
        $('#rag-s-due').text(ini.ini_rag_s_due || '');
        $('#rag-c').attr('class', 'rag-' + ini.ini_rag_c || 'grey');
        $('#rag-c-desc').html(rag_desc(ini.ini_rag_c, ini.ini_rag_c_desc));
        $('#rag-c-act').html(rag_act(ini.ini_rag_c, ini.ini_rag_c_act));
        $('#rag-c-resp').text(ini.ini_rag_c_resp ? ini.ini_rag_c_resp.name : '');
        $('#rag-c-due').text(ini.ini_rag_c_due || '');
        $('#rag-info').dialog('open');
    };
    gs.each(init_rag);

    $('.init').qtip({
        content: {
            title: function() {
                var ini = this.context.__data__;
                return ini.name;
            },
            text: function() {
                var ini = this.context.__data__;
                return ini_tip(enum_vals, ini);
            },
        },
        style: {
            classes: 'qtip-shadow'
        },
        position: {
            my: 'bottom center',
            at: 'top center',
            viewport: $(window),
            adjust: {
                method: 'shift shift'
            },
        },
        show: {
            delay: 500,
        },
        hide: {
            inactive: 2000,
        },
    });


    $('.sense').qtip({
        content: {
            title: "Hard Dependency",
            text: function() {
                var dep = this.context.__data__;
                return dep_tip(enum_vals, dep);
            },
        },
        style: {
            classes: 'qtip-shadow'
        },
        position: {
            my: 'bottom center',
            at: 'top center',
            viewport: $(window),
            adjust: {
                y: -5,
                method: 'shift shift'
            },
            target: 'mouse',
        },
        show: {
            delay: 500,
        },
        hide: {
            inactive: 2000,
        },
    });
});
