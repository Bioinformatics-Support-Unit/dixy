//this is all the d3.js stuff for drawing the chart
// size and margins for the chart
var margin = {top: 10, right: 10, bottom: 100, left: 100}
	, width = 850 - margin.left - margin.right
	, height = 750 - margin.top - margin.bottom;
var range = all_vals(data);

//scales 
//var xscale = d3.scale.linear()
//	.domain([0, d3.max(range)+(d3.max(range)*0.1)])  // the range of the values to plot
//	.range([ 0, width ]);        // the pixel range of the x-axis
//var yscale = d3.scale.linear()
//	.domain([0, d3.max(range)+(d3.max(range)*0.1)])
//	.range([ height, 0 ]);
arr = [];
for (d in data) {
    arr.push(data[d][x_files[current_data]]);
    arr.push(data[d][y_files[current_data]]);
}
var label_offset = d3.max(arr)*0.01;
xscale = d3.scale.linear()
    .domain([0, d3.max(arr)*1.05])  // the range of the values to plot
    .range([ 0, width ]);        // the pixel range of the x-axis
yscale = d3.scale.linear()
    .domain([0, d3.max(arr)*1.05])
    .range([ height, 0 ]);
var brush = d3.svg.brush()
	.x(xscale)
	.y(yscale)
	.on('brushstart', brushstart)
	.on('brush', brushmove)
	.on('brushend', brushend);
// the chart object, includes all margins
var chart = d3.select('#chart')
	.append('svg:svg')
	.attr('width', width + margin.right + margin.left)
	.attr('height', height + margin.top + margin.bottom)
	.attr('class', 'chart');
// the main object where the chart and axis will be drawn
var main = chart.append('g')
	.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
	.attr('width', width)
	.attr('height', height)
	.attr('class', 'main');
main.call(brush);
// draw the x axis
var xAxis = d3.svg.axis()
	.scale(xscale)
	.orient('bottom')
	.ticks(10);
var xAxisNodes = main.append('g')
    .attr('class', 'xaxis')
    .attr('transform', 'translate(0,' + height + ')')
    .style('fill', 'none')
    .style('stroke', 'black')
    .style('shape-rendering', 'crispEdges')
    .style('font-family', 'Helvetica')
    .style('font-size', '22px')
    .call(xAxis);
xAxisNodes.selectAll('text').style({ 'stroke-width': '0px'})
    .style('fill', 'black');
// draw the y axis
var yAxis = d3.svg.axis()
	.scale(yscale)
	.orient('left');
var yAxisNodes = main.append('g')
    .attr('class', 'yaxis')
    .attr('transform', 'translate(0,0)')
    .style('fill', 'none')
    .style('stroke', 'black')
    .style('shape-rendering', 'crispEdges')
    .style('font-family', 'Helvetica')
    .style('font-size', '22px')
    .call(yAxis);
yAxisNodes.selectAll('text').style({ 'stroke-width': '0px'})
    .style('fill', 'black');
// draw the graph object
var g = main.append('svg:g');
//add x-axis label
var xaxis_text = g.append('text')
	.text(metadata[metadata_labels[0]+".xlabel"])
	.style('font-family', 'Helvetica')
	.style('font-size', '24px')
	.attr('x', width/2)
	.attr('y', 720)
	.attr('text-anchor','middle');
//add y-axis label
var yaxis_text = g.append('text')
	.text(metadata[metadata_labels[0]+".ylabel"])
	.style('font-family', 'Helvetica')
	.style('font-size', '24px')
	.attr('x', 0)
	.attr('y', -10)
	.attr('dy', '-2.5em')
	.attr('text-anchor','middle')
	.attr('transform', 'rotate(-90) translate(-' + parseFloat(height / 2) + ',' + 0 + ')');
// add x=y line
var xeqy = g.append('svg:line')
	.attr('x1', xscale(0))
	.attr('y1', yscale(0))
	.attr('x2', xscale(d3.max(arr)*1.05))
	.attr('y2', yscale(d3.max(arr)*1.05))
	.style('stroke', 'rgb(6,120,155)');
// add regression line
current_slope1 = d3.max(arr)*1.05;
current_slope2 = metadata[metadata_labels[0]+".slope"]*current_slope1;
var reg = g.append('svg:line')
	.attr('x1', xscale(0))
	.attr('y1', yscale(0))
	.attr('x2', xscale(current_slope1))
	.attr('y2', yscale(current_slope2))
	.style('stroke', 'rgb(155,6,120)');
var dots = g.selectAll('scatter-dots')
	.data(data)  // using the values in the ydata array
	.enter().append('svg:circle')  // create a new circle for each value
	.attr('cx', function (d,i) { return xscale(parseFloat(data[i][x_files[current_data]])); } ) // translate x value
	.attr('cy', function (d,i) { return yscale(parseFloat(data[i][y_files[current_data]])); } ) // translate y value to a pixel
	.attr('r', 3) // radius of circle
	.attr('title', function (d,i) { return data[i].gene_name; })
	.attr('id', function (d,i) { return data[i].gene_name; })
	.on('click', function(d,i) { onClick(data[i].gene_name, i, d); })
    .attr('fill-opacity', function(d,i) { return getOpacity(i, this); })
	.style('fill', function(d,i) { return getColor(i, this); }); // color of circle
var labels = g.selectAll('labels')
	.data(data)
	.enter().append('svg:text')
	//.attr('x', function(d,i) { return xscale(parseFloat(data[i][x_files[current_data]])-0.9) } )
	//.attr('y', function(d,i) { return yscale(parseFloat(data[i][y_files[current_data]])+1.25) } )
	.attr('x', function(d,i) { return xscale(parseFloat(data[i][x_files[current_data]])-label_offset) } )
	.attr('y', function(d,i) { return yscale(parseFloat(data[i][y_files[current_data]])+label_offset) } )
	.text(function(d,i) { return getText(i); });


jQuery('button[id^="chart_"]').click(function() {
	var id = parseInt(jQuery(this).attr('id').split('_').slice(-1));
	highlight_button(id);
	current_data = id;
	current_slope1 = d3.max(range)+(d3.max(range)*0.1);
	current_slope2 = metadata[metadata_labels[id]+".slope"]*current_slope1;
	//move_data(current_slope1, current_slope2, false, 1);
	scale_axis()
    return false;
});
