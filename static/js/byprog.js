init_grid.cols = 1; //5;
init_grid.rows = 1; //12;
init_grid.colw = 170;
init_grid.rowh = 65;

var w = init_grid.cols * init_grid.colw + 20,
    h = init_grid.rows * init_grid.rowh + init_grid.rowh/2;


function ini_visible(ini) {
    if (ini === undefined) return false;

    if (ini.byprog_col === undefined || ini.byprog_row === undefined) {
        console.warn('Cannot draw', ini.name);
        return false;
    }

    if (!do_filter('INI', 'state', ini)) return false;
    if (!do_filter('INI', 'category', ini)) return false;

    if (!do_filter('INI', 'program_id', ini)) return false;
    if (!do_filter('INI', 'process_id', ini)) return false;

    if (!do_filter('INI', 'tracker_freq', ini)) return false;

    return true;
}

function dep_visible(dep) {
    if (dep === undefined) return false;

    var ini1 = index.ini[dep.from_init_id],
        ini2 = index.ini[dep.to_init_id];

    if (!ini_visible(ini1)) return false;
    if (!ini_visible(ini2)) return false;

    return true;
}

function soft_line(d) {
    var d1 = index.ini[d.from_init_id],
        d2 = index.ini[d.to_init_id];

    if (ini_visible(d1) && ini_visible(d2)) {
        var line = d3.select(this)
                     .attr({
                        x1: d1.byprog_col * init_grid.colw + init_grid.colw/2,
                        y1: d1.byprog_row * init_grid.rowh + init_grid.rowh,
                        x2: d2.byprog_col * init_grid.colw + init_grid.colw/2,
                        y2: d2.byprog_row * init_grid.rowh + init_grid.rowh,
                     });

        d1.lines.push(line);
        d2.lines.push(line);
    }
}

function hard_line(d) {
    var d1 = index.ini[d.from_init_id],
        d2 = index.ini[d.to_init_id];

    if (ini_visible(d1) && ini_visible(d2)) {
        var r1 = mk_init_rect(d1),
            xk = r1.cx, yk = r1.cy,
            r2 = mk_init_rect(d2),
            xl = r2.cx, yl = r2.cy,
            xm = r2.l, ym = r2.t,
            xn = r2.r, yn = r2.t,
            xp = r2.r, yp = r2.b,
            xq = r2.l, yq = r2.b,
            p = intersect_lineseg_rect(xk,yk, xl,yl, xm,ym, xn,yn, xp,yp, xq,yq),
            line;

        if (p !== undefined) {
            line = d3.select(this)
                         .attr({x1: xk, y1: yk,
                                x2: p.x, y2: p.y,
                                "marker-end": "url(#arrow)",
                         });

            d1.lines.push(line);
            d2.lines.push(line);
        }
    }
}

// This is called by the filter functions to re-draw the diagram
function render() {
    d3.select("#diagram svg").remove();

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
            //d: "M2,2 L2,13 L8,7 L2,2",
            //d: "M0,0 L-13,7 L-13,-7 L0,0",
            d: "M-20,-8L0,0L-20,8",
            fill: "black",
        });

    var progs = svg.selectAll("g.prog")
                    .data(data.programme)
                    .enter()
                    .append("g")
                    .classed("prog", true);

    progs.append("rect")
        .attr({
            x: function(d) { return d.byprog_col * init_grid.colw + 10; },
            y: function(d) { return d.byprog_row * init_grid.rowh + 0; },
            width: function(d) { return d.byprog_cols * init_grid.colw - 20; },
            height: function(d) { return d.byprog_rows * init_grid.rowh - 0 + init_grid.rowh/2; },
            //fill: function(d) { return d.color; },
            rx: 10,
            ry: 10,
        });

    progs.append("text")
        .text(function(d) { return d.name; })
        .attr({
            x: function(d) { return d.byprog_col * init_grid.colw + 20; },
            y: function(d) { return d.byprog_row * init_grid.rowh + 10 + 12; },
        });

    svg.selectAll("line.soft")
        //.data(data.softs.filter(dep_visible))
        .data(_.where(data.dependency, {type: 'soft'}).filter(dep_visible))
        .enter()
        .append("line")
        .classed("soft", true)
        .each(soft_line);

    svg.selectAll("line.hard")
        .data(_.where(data.dependency, {type: 'hard'}).filter(dep_visible))
        .enter()
        .append("line")
        .classed("hard", true)
        .each(hard_line);

    var gs = svg.selectAll("g.init")
             .data(data.inits.filter(ini_visible))
             .enter()
             .append("g")
             .classed("init", true);


    init_rect.hover = function (on, rect) {
        if (rect) {
            var _id = rect.__data__._id,
                deps_from = _.pluck(_.where(data.dependency, {to_init_id: _id}), 'from_init_id'),
                deps_to = _.pluck(_.where(data.dependency, {from_init_id: _id}), 'to_init_id'),
                non_faded = [_id].concat(deps_from.concat(deps_to));

            gs.classed('faded', function (d) {
                return on && !_.contains(non_faded, d._id);
            });
        } else {
            gs.classed('faded', on);
        }
    };

    gs.each(init_rect);
    gs.each(init_text);
    //gs.each(init_rag);

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
            my: 'bottom center', // 'bottom center',
            at: 'center center',
            viewport: $(window),
            //adjust: {
            //    method: 'shift flip'
            //},
            //target: 'mouse', // $('#diagram svg'), //
            //adjust: {
                //x:-15,
                //method: 'shift shift'
            //},
        },
        show: {
            delay: 500,
        },
        hide: {
            //fixed: true,
            inactive: 2000,
            //event: 'click',
            //distance: 100
        }
    });
}
