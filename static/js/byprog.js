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
        .data(data.softs.filter(dep_visible))
        .enter()
        .append("line")
        .classed("soft", true)
        .each(soft_line);

    svg.selectAll("line.hard")
        .data(data.hards.filter(dep_visible))
        .enter()
        .append("line")
        .classed("hard", true)
        .each(hard_line);

    var gs = svg.selectAll("g.init")
             .data(data.inits.filter(ini_visible))
             .enter()
             .append("g")
             .classed("init", true);

    gs.each(init_rect);
    gs.each(init_text);
    //gs.each(init_rag);

    $('.init').qtip({
        content: {
            title: function() {
                var d = this.context.__data__;
                return d.name;
            },
            text: function() {
                var d = this.context.__data__;
                $("#tt_stat").text(enum_vals.ini_state[d.state]);
                $("#tt_type").text(enum_vals.ini_type[d.type]);
                $("#tt_cat").text(enum_vals.ini_category[d.category]);
                $("#tt_prog").text(d.program.name);
                $("#tt_func").text(d['function']);
                $("#tt_start").text(d.start);
                $("#tt_end").text(d.end);
                var rslt = $("table.tooltip").html();
                return rslt;
            },
        },
        style: {
            classes: 'qtip-shadow'
        },
        position: {
            //my: 'left center',
            //at: 'center right',
            viewport: $(window),
            adjust: {
                method: 'shift shift'
            },
        },
    });
}

//function shorten(txt) {
//    if (txt.length > 30)
//        return mk('span', {title:txt}, txt.substr(0,28) + '...');
//    return txt;
//}
