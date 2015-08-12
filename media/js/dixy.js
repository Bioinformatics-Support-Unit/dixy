var shift_pressed = 0;
var current_data = 0;
var current_signames;
var current_slope1;
var current_slope2;
var selected = [];

//functions
var oc = function(a) {
	//extracts elements from array one at a time, 
    //allows for iteration over elements, not keys
    var o = {};
	for (var i = 0; i < a.length; i++) {
		o[a[i]]='';
	}
	return o;
};

var setSelectedText = function() {
    //sets the text of the 'Selected Genes' box on RHS of plot
	var str = "<strong>Selected Genes Info</strong><br/><br/>"
	for (s in selected) {
		var sel_name = data[selected[s]].gene_name;
		var key = data[selected[s]].orf_name;
		var description = descriptions[key];
		str = str + "Gene: "+sel_name+"<br/>"+description+"<br/><br/>";
	}
	$("#selected-info").html(str);
};

var onClick = function(d, i, point) {
    //respond to a click event (on point in plot)
    if (shift_pressed === 1) {
        shift_pressed = 0;
        var urlStub = 'http://www.yeastgenome.org/cgi-bin/locus.fpl?locus=';
        var url = urlStub + d;
        window.open(url, '_blank');
    } else {
        if (i in oc(selected)) {
            //deselect it
            search.value = '';
            for (s in selected) {
                if (selected[s] == i) {
                    selected.splice(s, 1);
                }
            }
            for (s in selected) {
                this_index = selected[s];
                search.value = search.value+data[this_index].gene_name+',';
            }
        } else {
            //select the point
            genename = data[i].gene_name;
            selected.push(i);
            search.value = '';
            for (s in selected) {
                this_index = selected[s];
                search.value = search.value+data[this_index].gene_name+',';
            }
        }
        //modify the text of the selected genes box
        setSelectedText();
        //move_data call to actually colour the newly selected points
        //or uncolour deselected ones
        move_data(current_slope1, current_slope2, true, true);
    }
    $(".ui-tooltip").hide();
};

var is_significant = function (o) {
    //test for significant q-values (single point)
	x = x_files[current_data].substring(0, x_files[current_data].length-2);
	y = y_files[current_data].substring(0, y_files[current_data].length-2);
	if (x !== y) {
		return 0;
	} else {
		if (o[x+".q"] <= 0.05) {
			return 1;
		} else {
			return 0;
		}
	}
};

var getColor = function(i, current) {
    //determine required colour for current point
	d = data[i];
	orfname = data[i].orf_name
	if (i in oc(selected)) {
  		var sel = d3.select(current);
  		sel.moveToFront();	
		if (is_significant(d)) {
			return 'rgb(152,78,163)';
		}
		else {
			return 'rgb(77,175,74)';
		}
	} else if (is_significant(d)) {
  		var sel = d3.select(current);
  		//move selected points on top of everything else
        sel.moveToFront();	
		line_slope = metadata[metadata_labels[current_data]+".slope"];
		current_position = d[y_files[current_data]]/d[x_files[current_data]];
		if (current_position > line_slope) {
			if ($('#reverse').is(':checked')) {
				return 'rgb(228,26,28)';
			} else {
				return 'rgb(55,126,184)';
			}
		} else if (current_position < line_slope) {
			if ($('#reverse').is(':checked')) {
				return 'rgb(55,126,184)';
			} else {
				return 'rgb(228,26,28)';
			}
		}
	} else {
		return 'rgb(143,148,152)';
	}
};
var getOpacity = function(i, current) {
	//currently, everything is opaque
    //(transparency slows things down too much)
    d = data[i];
    orfname = data[i].orf_name$                                                
    if (i in oc(selected)) {
        return 1.0;
    } else if (is_significant(d)) {
        return 1.0;
    } else {
		return 0.5;
	}
};
var getText = function(i) {
    //retrieves the gene names for selected points (in order to make label visible)
	if (i in oc(selected)) {
		return data[i].gene_name;
	}
	else {
		return "";
	}
};
d3.selection.prototype.moveToFront = function() {
    //moves selection to 'end' of data - meaning they're drawn last
	return this.each(function() {
		this.parentNode.appendChild(this);
	});
};

var move_data = function(linex, liney, instant, sw) {
    //moves the data points to a new location (via timed transitions)
    //also used to colour stuff in when it's selected etc
    //Destroy any persisting tooltips?
    //$(".ui-tooltip").tooltip("destroy");
    var delay;
	if (sw) {
		delay = 0
	}
	else {
		delay = function(d, i) { return i * 2; };
	}
    if (instant) {
        dur = 0;
    }
    else {
	    dur = parseInt($("#timing option:selected").val());
    }
	if ($('#disable').is(':checked')) {
		dur = 0;
		delay = 0;
	}
    //move the dots
	dots
        .data(data)
        .transition()
		.delay(delay)
        .duration(dur)
        .attr('cx', function(d,i) { return xscale(parseFloat(data[i][x_files[current_data]])); } )
        .attr('cy', function(d,i) { return yscale(parseFloat(data[i][y_files[current_data]])); } )
        .attr('fill-opacity', function(d,i) { return getOpacity(i, this); })
        .style('fill', function(d,i) { return getColor(i, this); }); // color of circle
    //move the regression line
    reg
        .transition()
        .duration(dur)
        .attr('x2', xscale(linex))
        .attr('y2', yscale(liney));
    xeqy
        .transition()
        .duration(dur)
        .attr('x2', xscale(d3.max(arr)*1.05))
        .attr('y2', yscale(d3.max(arr)*1.05))
	//move the labels too, otherwise they get orphaned from their points
    labels
		.data(data)
		.transition()
		.duration(dur)
        //.attr('x', function(d,i) { return xscale(parseFloat(data[i][x_files[current_data]])-0.9) } )
        //.attr('y', function(d,i) { return yscale(parseFloat(data[i][y_files[current_data]])+1.25) } )
        .attr('x', function(d,i) { return xscale(parseFloat(data[i][x_files[current_data]])-label_offset) } )
        .attr('y', function(d,i) { return yscale(parseFloat(data[i][y_files[current_data]])+label_offset) } )
		.text(function(d, i) { return getText(i); });
    //relabel the axes
	xaxis_text
		.text(metadata[metadata_labels[current_data]+".xlabel"]);
	yaxis_text
		.text(metadata[metadata_labels[current_data]+".ylabel"]);
    //move labels on top of points - otherwise they get obscured
    labels.moveToFront()
};

function brushstart() {
    // Clear the previously-active brush, if any.
	main.call(brush.clear());
};

function brushmove() {
    //currently unused
};

function brushend() {
    //once you finish drawing a box, this will work out its extent, and any
    //points it captures
    var e = brush.extent();
	//need to deal with margins here
	var x0 = e[0][0],
        y0 = e[0][1],
        x1 = e[1][0],
        y1 = e[1][1];
	for (d in data) {
		p_x = data[d][x_files[current_data]];
		p_y = data[d][y_files[current_data]];
		if (x0 <= p_x && p_x <= x1 && y0 <= p_y && p_y <= y1) {
			if (d in oc(selected)) {
			} else {			
				selected.push(d);
			}
		}
    };
    search.value = "";
    for (s in selected) {
		this_index = selected[s];
		search.value = search.value+data[this_index].gene_name+',';
	}
	setSelectedText();
	move_data(current_slope1, current_slope2, true, true);
	main.call(brush.clear())
};

var make_json = function() {
    //turns gene/orf names into structure required for search interface
    var empty_list = [];
    for (var i=0; i<data.length; i++) {
        var obj = {}
        obj.label = data[i]['orf_name']+", "+data[i]['gene_name'];
        obj.value = data[i]['gene_name'];
		empty_list.push(obj);
    }
	return empty_list;
};

var highlight_button = function(i) {
    //highight the button for the currently selected dataset
	//clear all previous selections
	$('.run').removeClass('selected_button');
	$('.run').addClass('unselected_button');
	var chart = "#chart_"+i;
	$(chart).removeClass('unselected_button');
	$(chart).addClass('selected_button');
};

function isInArray(value, array) {
    //used in navigating the gene sets
    return array.indexOf(value) > -1;
};

function getGenelistJson(index) {
    //used in navigating the gene sets
    if (index == 0) {
        list_json = benschop;
    } else if (index == 1) {
        list_json = goann;
    }
    return list_json
};

function populateGenelist(name) {
    //used in navigating the gene sets
    $('#geneset_lists').empty();
    list_json = getGenelistJson(name);
    $.each(list_json, function (index, value) {
        $('#geneset_lists').append($('<option>', { 
           value: index,
           text : value.name
        }));
    });
};

function highlightGenelist(element, list) {
    //used in navigating the gene sets
    var count = 0;
    selected = [];
    $("#search").val("");
    list_json = getGenelistJson(list);
    genes = list_json[element].orfs;
    $.each(data, function (index, value) {
        if (isInArray(value.orf_name,genes)) {
            count++;
            onClick(value.orf_name, index, null);
        };
    });
    if (count === 0) {
        move_data(current_slope1, current_slope2, true, true);
    }
};

function scale_axis() {
    d3.select('.xaxis').remove();
    d3.select('.yaxis').remove();
    arr = [];
    for (d in data) {
        arr.push(data[d][x_files[current_data]]);
        arr.push(data[d][y_files[current_data]]);
    }
    current_slope1 = d3.max(arr)*1.05;
    current_slope2 = metadata[metadata_labels[current_data]+".slope"]*current_slope1;
    label_offset = d3.max(arr)*0.01;
    xscale = d3.scale.linear()
        .domain([0, d3.max(arr)*1.05])  // the range of the values to plot
        .range([ 0, width ]);        // the pixel range of the x-axis
    yscale = d3.scale.linear()
        .domain([0, d3.max(arr)*1.05])
        .range([ height, 0 ]);
    // update the brush
    brush.x(xscale).y(yscale);
    var xAxisNew = d3.svg.axis().scale(xscale).orient('bottom').ticks(10);
    var yAxisNew = d3.svg.axis().scale(yscale).orient('left').ticks(10);
    var newx = main.append('g')
        .attr('class', 'xaxis')
        .attr('transform', 'translate(0,' + height + ')')
        .style('fill', 'none')
        .style('stroke', 'black')
        .style('shape-rendering', 'crispEdges')
        .style('font-family', 'Helvetica')
        .style('font-size', '22px')
        .call(xAxisNew);
    newx.selectAll('text').style({ 'stroke-width': '0px'})
        .style('fill', 'black');
    //xnodes.selectAll('text').style({ 'stroke-width': '0px'})
    //    .style('fill', 'black');
    // draw the y axis
    var newy = main.append('g')
        .attr('class', 'yaxis')
        .attr('transform', 'translate(0,0)')
        .style('fill', 'none')
        .style('stroke', 'black')
        .style('shape-rendering', 'crispEdges')
        .style('font-family', 'Helvetica')
        .style('font-size', '22px')
        .call(yAxisNew);
    newy.selectAll('text').style({ 'stroke-width': '0px'})
        .style('fill', 'black');
    move_data(current_slope1, current_slope2, false, true);
    /*var yAxisNodes = main.append('g')
        .attr('transform', 'translate(0,0)')
        .style('fill', 'none')
        .style('stroke', 'black')
        .style('shape-rendering', 'crispEdges')
        .style('font-family', 'Helvetica')
        .style('font-size', '22px')
        .call(yAxis);
    yAxisNodes.selectAll('text').style({ 'stroke-width': '0px'})
        .style('fill', 'black');
    */
    //move_data(current_slope1, current_slope2, true, true);
};

//A bunch of jQuery
$(document).ready(function(){
    $("#scaleaxis").click(function(){
        scale_axis();
    });
    $("#reverse").click(function(){
        //handled before the box is checked, so reverse of expected
        if ($('#reverse').is(':checked')) {
			$(".key_up").css("background-color", "#e41a1c");
            $(".key_down").css("background-color", "#377eb8");
		} else {
			$(".key_up").css("background-color", "#377eb8");
            $(".key_down").css("background-color", "#e41a1c");
		}
    });
    populateGenelist(0);
    jQuery("select[name='genesets']").change(function(){
        populateGenelist(parseInt(jQuery("select[name='genesets']").val()));
    });
    jQuery("select[name='geneset_lists']").change(function(){
        highlightGenelist(parseInt(jQuery("select[name='geneset_lists']").val()), parseInt(jQuery("select[name='genesets']").val()));
    });
    $("#saveas").click(function(){
		var html = d3.select("svg")
			.attr("title", "test2")
			.attr("version", 1.1)
			.attr("xmlns", "http://www.w3.org/2000/svg")
			.node().parentNode.innerHTML;
		d3.select("body").append("div")
			.attr("id", "download")
			.html("Right-click on this preview and choose Save as<br />")
			.append("img")
			.attr("src", "data:image/svg+xml;base64,"+ btoa(html));
	});
    $(function() {
    $(document).tooltip({position: {
                        my: "right",
                        at: "left-10 top-10"}});
	var json_genenames = make_json();
	function split( val ) {
      return val.split( /,\s*/ );
    }
    function extractLast( term ) {
      return split(term).pop();
    }
    $(document).bind("keydown", function(event) {
        if ( event.keyCode === 16) {
            //SHIFT IS PRESSED
            shift_pressed = 1;
        } else if (event.keyCode === 67) {
            //c is pressed
            if ($(document.activeElement).attr("type") == "text") {
            } else {
                selected = [];
                move_data(current_slope1, current_slope2, true, true);
                setSelectedText();
                $("#search").val("");
            }
        } else if (event.keyCode === 188) {
	    	//comma (move left) pressed
            if ($(document.activeElement).attr("type") == "text") {
            } else {
            var id = current_data - 1;
		    if (id < 0) {
			    id = metadata_labels.length - 1; 
		    }
		    highlight_button(id);
		    current_data = id;
            label_offset = d3.max(arr)*0.01;
		    //current_slope1 = d3.max(range)+10;
		    //current_slope2 = metadata[metadata_labels[id]+".slope"]*current_slope1;
		    //move_data(current_slope1, current_slope2, false, true);
            scale_axis()
            }
        } else if (event.keyCode === 190) {
		    //period (move right) pressed
            if ($(document.activeElement).attr("type") == "text") {
            } else {
            var id = current_data + 1;
		    if (id === metadata_labels.length) {
			    id = 0;
		    }
		    highlight_button(id);
		    current_data = id;
		    //current_slope1 = d3.max(range)+10;
		    //current_slope2 = metadata[metadata_labels[id]+".slope"]*current_slope1;
		    //move_data(current_slope1, current_slope2, false, true);
            scale_axis()
            }
        } else if (event.keyCode === 38) {
		    //alert('Up Arrow Pressed');
        } else if (event.keyCode === 40) {
		    //alert('Down Arrow Pressed');
	    } else if (event.keyCode === 78) {
            /*
            var sel_names = []
            for (s in selected) {
                 sel_names.push(data[selected[s]].orf_name);
            }
            var d = sel_names.join('|')
            var urlStub = 'http://bsu-srv.ncl.ac.uk/dixy/network/';
            var url = urlStub + d;
            window.open(url, '_blank');
            */
        }
    });
    $(document).bind("keyup", function(event) {
        if ( event.keyCode === 16) {
            //SHIFT IS RELEASED
            shift_pressed = 0;
        }
    });
    $( "#search" )
      // don't navigate away from the field on tab when selecting an item
      .bind( "keydown", function( event ) {
        if ( event.keyCode === $.ui.keyCode.TAB &&
            $( this ).data( "ui-autocomplete" ).menu.active ) {
          event.preventDefault();
        }
      })
      .autocomplete({
        minLength: 0,
        source: function( request, response ) {
          // delegate back to autocomplete, but extract the last term
            response( $.ui.autocomplete.filter(
            json_genenames, extractLast( request.term ) ) );
        },
        focus: function() {
          // prevent value inserted on focus
          return false;
        },
        select: function( event, ui ) {
          var terms = split( this.value );
          // remove the current input
          terms.pop();
          // add the selected item
          terms.push(ui.item.value);
          indexes = [];
          for (term in terms) {
            //select genes in 'terms'
            //get index of gene in data
	    for (d in data) {
	        if (data[d]['gene_name'] == terms[term].toUpperCase()) {
		    var this_index = d;
		}
	    }
            indexes.push(this_index);
          }
          selected = indexes;
          move_data(current_slope1, current_slope2, true, true);
          setSelectedText();
		  // add placeholder to get the comma-and-space at the end
          terms.push( "" );
          this.value = terms.join( ", " );
          return false;
        },
        open: function(event, ui) {
		  var terms = split( this.value );
          indexes = [];
		  for (term in terms) {
            //select genes in 'terms'
			for (d in data) {
				if (data[d]['gene_name'] == terms[term].toUpperCase()) {
					var this_index = d;
				}
			}
            //var this_index = genenames.indexOf(terms[term].toUpperCase());
            indexes.push(this_index);
          }
          selected = indexes;
          move_data(current_slope1, current_slope2, true, true);
		  setSelectedText();
        }
      });
  });
});

function all_vals(d) {
	values = [];
	for (i in d) {
		o = d[i];
		for (k in o) {
			if (/x$/.test(k)) {
				values.push(o[k]);
			}
			if (/y$/.test(k)) {
				values.push(o[k]);
			}
		}
	}
	return values;
};

