var ini_row = {},
    fst_yr = 14,
    lst_yr = 22,
    fst_date,
    lst_date,
    cols, rows,
    off = 380,
    yoff = 25,
    grpw = 90,
    cluw = 20,
    ragw = 0,
    rowh = 19,
    txth = 11,
    colw, // = (1000 - off) / cols,
    w, // = off + cols * colw,
    h; // = (rows+1) * rowh;

function ini_visible(ini) {
    if (ini === undefined) return false;
    //if (ini_row.length > 0 && ini_row[ini._id] === undefined) return false;

    if (!do_filter('INI', 'state', ini)) return false;
    if (!do_filter('INI', 'category', ini)) return false;

    if (!do_filter('INI', 'program_id', ini)) return false;
    if (!do_filter('INI', 'process_id', ini)) return false;

    if (!do_filter('INI', 'tracker_freq', ini)) return false;

    if (choice.view === 'year') {
        //if (ini.start_date === undefined) return false;
        if (ini.end_date === undefined) return false;
        if (ini.start_date !== undefined && cmp_date(lst_date, mk_date(ini.start_date)) < 0) return false;
        if (cmp_date(fst_date, mk_date(ini.end_date)) > 0) return false;
    }

    return true;
}
function dep_visible(dep) {
    if (!toggle.deps) return false;
    if (dep === undefined) return false;

    var ini1 = index.ini[dep.from_init_id],
        ini2 = index.ini[dep.to_init_id];

    if (!ini_visible(ini1)) return false;
    if (!ini_visible(ini2)) return false;

    if (ini1.end === undefined || ini2.start === undefined) return false;

    return true;
}
function group_inis(inis) {
    var grps,
        grp_ord;

    switch (choice.group) {
        case 'func':
            grps = _.groupBy(inis, 'function');
            grp_ord = _.keys(grps).sort();
            break;
        case 'proc':
            inis = _.filter(inis, function (ini) {
                return ini.process !== undefined;
            });
            inis = _.sortBy(inis, 'roadmap_ord');
            grps = _.groupBy(inis, function (ini) {
                return ini.process.title;
            });
            _.each(grps, function (v, k) {
                var val =_.sortBy(v, function (ini) {
                    return ini.cluster ? ini.cluster.roadmap_ord : 100;
                });
                grps[k] = val;
            });
            grp_ord = _.filter(_.pluck(_.sortBy(data.process, 'roadmap_ord'), 'title'), function (x) {
                return _.contains(_.keys(grps), x);
            });
            break;
        case 'clus':
            inis = _.filter(inis, function (ini) {
                return ini.cluster !== undefined;
            });
            inis = _.sortBy(inis, 'roadmap_ord');
            grps = _.groupBy(inis, function (ini) {
                return ini.cluster.name;
            });
            //grp_ord = _.keys(grps).sort();
            grp_ord = _.filter(_.pluck(_.sortBy(data.cluster, 'roadmap_ord'), 'name'), function (x) {
                return _.contains(_.keys(grps), x);
            });
            break;
    }

    return _.map(grp_ord, function (key) {
        return [key, grps[key]];
    });
}

function row_rect(d, i) {
    d3.select(this)
        .classed("row", true)
        .classed("odd", (i+1)%2)
        .classed("tipped", true)
        .attr({
            x: grpw,
            y: yoff + (i+1) * rowh,
            width: off + cols * colw + 3 * ragw - grpw,
            height: rowh,
            id: 'row' + i,
        })
        .on('click', function () {
            window.location.href = '/init/' + d.ini._id;
        });
}
function rag_rect(rect, i, d, f) {
    rect.classed("rag", true)
        .classed("rag-red", d[f] === 'red')
        .classed("rag-amber", d[f] === 'amber')
        .classed("rag-green", d[f] === 'green')
        .attr({
            x: off + (cols * colw) + (i * ragw) + 3,
            y: yoff + ini_row[d._id] * rowh + 3,
            width: ragw - 6,
            height: rowh - 6,
        })
        .on('click', function () {
          if (d[f] === 'red' || d[f] === 'amber' || d[f] === 'green') {
            //$('#ps-ini-name').text('Programme Status for ' + d.name);
            //$('#prog-status').modal();
            //$('#prog-status').attr('title', 'Programme Status for ' + d.name);
            $('#rag-ini-name').text("Initiative: " + d.name);
            $('#sg_supp_id').text(d.sg_supp ? d.sg_supp.name : '');
            $('#biz_pm_id').text(d.biz_pm ? d.biz_pm.name : '');

            if (d.tp_rag_t === 'green' && d.tp_rag_s === 'green' && d.tp_rag_c === 'green') {
                $('#tp_rag_desc').text('Progressing according to plan');
                $('#tp_rag_t_impact').html(mk('span.rag.rag-green', '&nbsp;'));
                $('#tp_rag_t_impact').append(' n/a');
                $('#tp_rag_s_impact').html(mk('span.rag.rag-green', '&nbsp;'));
                $('#tp_rag_s_impact').append(' n/a');
                $('#tp_rag_c_impact').html(mk('span.rag.rag-green', '&nbsp;'));
                $('#tp_rag_c_impact').append(' n/a');
                $('#tp_rag_act').text('No actions needed');
                $('#tp_rag_due').text('n/a');
                $('#tp_rag_resp').text('n/a');
            } else {
                $('#tp_rag_desc').text(d.tp_rag_desc || '');
                $('#tp_rag_t_impact').html(mk('span.rag.rag-' + d.tp_rag_t, '&nbsp;'));
                $('#tp_rag_t_impact').append(' ' + (d.tp_rag_t_impact || ''));
                $('#tp_rag_s_impact').html(mk('span.rag.rag-' + d.tp_rag_s, '&nbsp;'));
                $('#tp_rag_s_impact').append(' ' + (d.tp_rag_s_impact || ''));
                $('#tp_rag_c_impact').html(mk('span.rag.rag-' + d.tp_rag_c, '&nbsp;'));
                $('#tp_rag_c_impact').append(' ' + (d.tp_rag_c_impact || ''));
                $('#tp_rag_act').text(d.tp_rag_act || '');
                $('#tp_rag_due').text(d.tp_rag_due || '');
                $('#tp_rag_resp').text(d.tp_rag_resp ? d.tp_rag_resp.name : '');
            }
            $('#prog-status').dialog('open');
          }
        });
}

function init_bar(d, i) {
    var l = off + d.sc * colw,
        r = off + d.ec * colw,
        t = yoff + (i+1) * rowh + 3,
        b = t + rowh - 6,
        path;

    if (d.ec) {
        path = fmt("M {0} {1} {3} {1} {4} {5} {3} {2} {0} {2} {6}", l,t,b,r-rowh/2, r, t+(rowh-4)/2, d.ini.start ? 'Z' : '');
        if (choice.view === 'year' && d.ini.end_date !== undefined && cmp_date(lst_date, mk_date(d.ini.end_date)) < 0) {
            path = fmt("M {0} {1} {3} {1}  {3} {2} {0} {2} {4}", l,t,b,r, d.ini.start_date ? 'Z' : '');
        }

        d3.select(this)
            .append("path")
            .classed("bar", true)
            .classed("tipped", true)
            .classed(mk_class(d.ini.category), true)
            .attr('d', path)
            ;//.on("mouseover", function() {
            //    d3.select('#row'+i).classed('hilite', true);
            //})
            //.on("mouseout", function() {
            //    d3.select('#row'+i).classed('hilite', false);
            //})
            //.on('click', function () {window.location.href = '/init/'+d.ini._id;});
    } else if (d.sc) {
        r = off + cols * colw;
        path = fmt("M {0} {2} {1} {2} {1} {3} {0} {3}", r, l, t, b);

        d3.select(this)
            .append("path")
            .classed("bar", true)
            .classed("tipped", true)
            .classed(mk_class(d.ini.category), true)
            .attr('d', path)
            ;//.on("mouseover", function() {
            //    d3.select('#row'+i).classed('hilite', true);
            //})
            //.on("mouseout", function() {
            //    d3.select('#row'+i).classed('hilite', false);
            //});
    }
}
function dep_line_full(d) {
    var d1 = index.ini[d.from_init_id],
        d2 = index.ini[d.to_init_id],
        s = mk_fyt(d1.end, true),
        e = mk_fyt(d2.start, false),
        sc = s ? fyt_col(s,fst_yr) : undefined,
        ec = e ? fyt_col(e,fst_yr) : undefined,
        sr = ini_row[d1._id],
        er = ini_row[d2._id];

    if (sc && ec && sr && er) {
        d3.select(this)
            .classed("dep", true)
            //.classed("backward", sc > ec + .34)
            .attr({
                x1: off + sc * colw - colw/6,
                y1: yoff + sr * rowh + rowh/2,
                x2: off + ec * colw + colw/6,
                y2: yoff + er * rowh + rowh/2,
                "marker-start": "url(#circle)",
                "marker-end": "url(#arrow)",
            });
    }
}
function clamp(x, lo, hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}
function dep_line_year(d) {
    var d1 = index.ini[d.from_init_id],
        d2 = index.ini[d.to_init_id],
        s = mk_date(d1.end_date),
        e = mk_date(d2.start_date),
        fst_mnth = first_month(),
        sc = s ? clamp(date_col(s,fst_mnth,12),0,12) : undefined,
        ec = e ? clamp(date_col(e,fst_mnth,12),0,12) : undefined,
        sr = ini_row[d1._id],
        er = ini_row[d2._id];

    if (sc !== undefined && ec !== undefined && sr !== undefined && er !== undefined) {
        d3.select(this)
            .classed("dep", true)
            //.classed("backward", sc > ec + .34)
            .attr({
                x1: off + sc * colw - colw/6,
                y1: yoff + sr * rowh + rowh/2,
                x2: off + ec * colw + colw/6,
                y2: yoff + er * rowh + rowh/2,
                "marker-start": "url(#circle)",
                "marker-end": "url(#arrow)",
            });
    }
}
function year_text(d) {
    d3.select(this)
        .text(d.name)
        .classed("year", true)
        .attr({
            x: d.x + 2,
            y: yoff + 12,
        });
}
function rag_text(d) {
    d3.select(this)
        .text(d.name)
        .classed("rag", true)
        .attr({
            x: d.x + (ragw / 2),
            y: yoff + 12,
        });
}
function year_line(d) {
    d3.select(this)
        .classed("year", true)
        .attr({
            x1: d.x,
            y1: yoff + 0,
            x2: d.x,
            y2: yoff + (rows+1) * rowh,
        });
}
function month_text(d) {
    d3.select(this)
        .text(d.name)
        .classed("month", true)
        .attr({
            x: d.x + colw/2,
            y: h - 3, //10,
        });
}
function month_line(d) {
    d3.select(this)
        .classed("month", true)
        .attr({
            x1: d.x,
            y1: yoff + rowh,
            x2: d.x,
            y2: yoff + (rows+1) * rowh,
        });
}
function group_line(d) {
    d3.select(this)
        .classed("group", true)
        .attr({
            x1: 0,
            y1: yoff + (d.row + 0) * rowh,
            x2: off + cols * colw + 3 * ragw,
            y2: yoff + (d.row + 0) * rowh,
        });
}
function trunc_ini_name(name) {
    if (name.substr(0,7) === 'MHS TP ')
        name = name.substr(7);
    return name;
}
function init_text(d, i) {
    var g = d3.select(this).append('g'),
        rect = g.append('rect')
                .classed('init', true)
                .classed('tipped', true)
                .attr({
                    x: grpw,
                    y: yoff + (i+1) * rowh,
                    width: off - grpw,
                    height: rowh,
                    fill: 'none'
                }),
        text = g.append('text')
                .text(trunc_ini_name(d.ini.name))
                .classed("bar", true);

    d3plus.textwrap()
          .container(text)
          .padding(0)
          .valign("middle")
          //.rotate(-90)
          .draw();

    //rect.on('click', function () {
    //    window.location.href = '/init/' + d.ini._id;
    //});
}
function group_text(grp) {
    if (grp.rows > 0) {
        var g = d3.select(this),
            rect = g.append('rect')
                    .attr({
                        x: 0,
                        y: yoff + grp.row * rowh,
                        width: grpw-3,
                        height: grp.rows * rowh,
                        fill: 'none'
                    }),
            text = g.append('text')
                    .text(grp.name)
                    .classed("group", true);

        d3plus.textwrap()
              .container(text)
              .padding(0)
              .valign("middle")
              //.rotate(-90)
              .draw();
    }
}
function cluster_line(clu) {
    d3.select(this)
        .classed("cluster", true)
        .attr({
            x1: w - cluw,
            y1: yoff + clu.row * rowh,
            x2: w,
            y2: yoff + clu.row * rowh,
        });
}
function cluster_text(clu) {
    if (clu.rows > 0) {
        var g = d3.select(this),
            rect = g.append('rect')
                    .attr({
                        x: w - cluw,
                        y: yoff + clu.row * rowh,
                        width: cluw-3,
                        height: clu.rows * rowh,
                        fill: 'none'
                    }),
            text = g.append('text')
                    .text(clu.name.replace('&', 'and'))
                    .classed("cluster", true);

        d3plus.textwrap()
              .container(text)
              .padding(0)
              .valign("middle")
              .rotate(-90)
              .draw();
    }
}

function first_month() {
    var now = mk_date_now(),
        fst_mnth = Math.floor(now.getMonth() / 4) * 4;
    return mk_date(now.getFullYear(), fst_mnth, 1);
}

// This is called by the filter functions to re-draw the diagram
function render() {
    ini_row = {};
    var now = mk_date_now(),
        fst_mnth;

    if (choice.view === 'year') {
        ragw = rowh;
        cols = 12;
        fst_mnth = Math.floor(now.getMonth()); // / 4) * 4;
        fst_date = mk_date(now.getFullYear(), fst_mnth, 1);
        lst_date = mk_date(now.getFullYear()+1, fst_mnth, 1);
    } else {
        ragw = 0;
        cols = lst_yr - fst_yr + 1; //0;
    }
    colw = (900 - off) / cols;

    var inits = data.initiative.filter(ini_visible),
        grps = group_inis(inits),
        groups = [],
        clusters = [],
        i = 0,
        f = '-';

    inits = [];
    _.each(grps, function (grp) {
        var key = grp[0],
            inis = grp[1];

        groups.push({name: key, row: i+1, rows: inis.length});

        _.each(inis, function (ini) {
            ini_row[ini._id] = i+1;
            inits.push(ini);
            i++;
        });
    });
    groups.push({name: '', row: i+1, rows: 0});

    if (choice.group === 'proc') {
        var clu_id,
            clu;
        _.each(inits, function (ini) {
            if (clu !== undefined) {
                clu.rows++;
            }
            if ((ini.cluster === undefined && clu_id !== undefined) || (ini.cluster !== undefined && ini.cluster._id !== clu_id)) {
                if (clu !== undefined) {
                    clusters.push(clu);
                    clu_id = undefined;
                    clu = {name: '?', row: ini_row[ini._id], rows: 0};
                }
                if (ini.cluster !== undefined) {
                    clu_id = ini.cluster._id;
                    clu = {name: ini.cluster.name, row: ini_row[ini._id], rows: 0};
                }
            }
        });
        if (clu !== undefined) {
            clusters.push(clu);
        }
        clusters.push({name: '', row: i+1, rows: 0});
        cluw = 40;
    } else {
        cluw = 0;
    }

    rows = inits.length;
    w = off + cols * colw + (3 * ragw) + cluw;
    h = yoff + (rows+2) * rowh;
    $("#rag-text").width(w);

    d3.select("#diagram svg").remove();

    var svg = d3.select("#diagram")
                .append("svg")
                .attr("width", w+1+40)
                .attr("height", h+1),
        defs = svg.append("defs");

    d3_def_arrow(defs, 'black');
    d3_def_circle(defs, 'black');

    var bars = [],
        years = [],
        months = [];

    if (choice.view === 'year') {
        var mnth_name = [
                'Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec'
            ],
            year = now.getFullYear() - 2000,
            bar_inis = _.filter(inits, function (ini) {
                return ini.start_date !== undefined && ini.end_date !== undefined;
            });

        months = _.map(_.range(12), function (i) {
                        var m = (fst_mnth + i) % 12;
                        return {
                            x: off + i * colw,
                            name: mnth_name[m]
                        };
                    });

        years = [
            {x: off, name: 'FY' + year},
            {x: off + ((8 - fst_mnth) % 12) * colw, name: 'FY' + (year+1)},
        ];

        bars = _.map(inits, function (ini) {
            var s = mk_date(ini.start_date),
                e = mk_date(ini.end_date),
                f = mk_date(year, fst_mnth, 1);
            return {
                ini: ini,
                sc: s !== undefined ? Math.max(0, date_col(s,f,12)) : 0,
                ec: e !== undefined ? Math.min(cols, date_col(e,f,12)) : cols,
            };
        });
    } else {
        years = _.map(_.range(cols), function (i) {
                    return {
                        x: off + i * colw,
                        name: 'FY' + (fst_yr + i),
                    };
                });

        bars = _.map(inits, function (ini) {
            var s = mk_fyt(ini.start, false),
                e = mk_fyt(ini.end, true);
            return {
                ini: ini,
                sc: fyt_col(s,fst_yr),
                ec: fyt_col(e,fst_yr),
            };
        });
    }

    var ini_gs = d3_add(svg, "g", bars, "g");
    ini_gs.append("rect").each(row_rect);

    d3_add(svg, "text.month", months, "text", month_text);
    d3_add(svg, "line.month", months, "line", month_line);
    d3_add(svg, "text.year", years, "text", year_text);
    d3_add(svg, "line.year", years, "line", year_line);

    ini_gs.each(init_bar);
    ini_gs.each(init_text);

    d3_add(svg, "line.group", groups, "line", group_line);
    d3_add(svg, "text.group", groups, "g", group_text);

    d3_add(svg, "line.cluster", clusters, "line", cluster_line);
    d3_add(svg, "text.cluster", clusters, "g", cluster_text);

    //ini_gs.each(function (d,i) {
    //    mk_ini_rag_g(d, d3.select(this), off-30, (i+1) * rowh + 2);
    //});
    if (choice.view === 'year') {
        //ini_gs.append("rect").each(function (d) {rag_rect(d3.select(this),0,d,'tp_rag_t');});
        //ini_gs.append("rect").each(function (d) {rag_rect(d3.select(this),1,d,'tp_rag_s');});
        //ini_gs.append("rect").each(function (d) {rag_rect(d3.select(this),2,d,'tp_rag_c');});
        var rag_text_data = [
            {name: 'T', x: off + (cols * colw) + (0 * ragw)},
            {name: 'S', x: off + (cols * colw) + (1 * ragw)},
            {name: 'C', x: off + (cols * colw) + (2 * ragw)},
        ];
        d3_add(svg, "text.rag", rag_text_data, "text", rag_text);

        d3_add(svg, "rect.tp_rag_t", inits, "rect", function (d) {rag_rect(d3.select(this),0,d,'tp_rag_t');});
        d3_add(svg, "rect.tp_rag_s", inits, "rect", function (d) {rag_rect(d3.select(this),1,d,'tp_rag_s');});
        d3_add(svg, "rect.tp_rag_c", inits, "rect", function (d) {rag_rect(d3.select(this),2,d,'tp_rag_c');});

        svg.append('text')
          .text("Programme")
          .classed("rag-head", true)
          .attr({
              x: off + (cols * colw) + (1.5 * ragw),
              y: yoff - 16,
          });
        svg.append('text')
          .text("Status")
          .classed("rag-head", true)
          .attr({
              x: off + (cols * colw) + (1.1 * ragw),
              y: yoff - 2,
          });
        svg.append('text')
          .text("")
          .classed("info-icon", true)
          .attr({
              x: off + (cols * colw) + (2.7 * ragw),
              y: yoff - 2,
              id: 'prog-status-icon',
              cursor: 'pointer',
              //'data-toggle': 'modal',
              //'data-target': 'prog-status-info',
          })
          .on('click', function () {
            //$('#prog-status-info').modal();
            $('#prog-status-info').dialog('open');
          });
    }

    d3_add(svg, "line.dep", data.dependency.filter(dep_visible), "line", choice.view === 'year' ? dep_line_year : dep_line_full);

    function bar_tip(ini) {
        var c = ini.cluster,
            s = mk_fyt(ini.start, false),
            e = mk_fyt(ini.end, true),
            t = '<table class="tip">\n' +
                '  <tr><th>Status:</th><td>{0}</td></tr>\n' +
                '  <tr><th>Business Change Area:</th><td>{1}</td></tr>\n' +
                '  <tr><th>Start:</th><td>{2}</td></tr>\n' +
                '  <tr><th>End:</th><td>{3}</td></tr>\n' +
                '</table>\n';

        return fmt(t,
            enum_vals.ini_state[ini.state],
            c ? c.name : '',
            s ? s.fiscal_str() : '',
            e ? e.fiscal_str() : ''
        );
    }

    $('.tipped').qtip({
        content: {
            title: function() {
                var d = this.context.__data__.ini;
                return d.name;
            },
            text: function() {
                var d = this.context.__data__.ini;
                return bar_tip(d);
            },
        },
        style: {
            classes: 'qtip-cluetip qtip-shadow'
        },
        position: {
            my: 'bottom center',
            //at: 'top center',
            viewport: $(window),
            //adjust: {
            //    method: 'shift flip'
            //},
            target: 'mouse',
            adjust: {y:-5},
        },
        show: {
            delay: 300,
        },
        hide: {
            inactive: 2000,
        }
    });
}
