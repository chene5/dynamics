function flow_graph(flow_data, full_word_list, margin) {
	var word_list = full_word_list.slice(1);
  var data_length = flow_data.length;
  var words_length = word_list.length;
  if (words_length != data_length) {
  	console.log("Word list and flow list not of same length.");
  }
  if (words_length < data_length) {
  	data_length = words_length;
  }
	//  alert("hi");
  var data = [];
  var ticks = [0];
  for (var i = 0; i < data_length; i++) {
  	// data.push({"word": word_list[i+1], "flow": flow_data[i]});
  	data.push({"word": word_list[i], "flow": flow_data[i]});
  	ticks.push(i+1);
  }
	// console.log(data);
	// set the ranges
	var x = d3.scaleLinear().range([0, width]);
	var y = d3.scaleLinear().range([height, 0]);

  // Scale the range of the data
  x.domain([0, word_list.length]);

  if (d3.min(data, function(d) { return d.flow}) > 0) {
	  // y.domain([0, d3.max(data, function(d) { return d.flow})])
		y_range = d3.extent(data, function(d) { return d.flow});
		y_range[0] = y_range[0] - .1;
		y_range[1] = y_range[1] + .1;
		y.domain(y_range);
  }
  else {
	  y.domain(d3.extent(data, function(d) { return d.flow}));
	}

	// define the line
	var valueline = d3.line()
    .x(function(d, i) { return x(i+1); })
    // .x(function(d, i) { return x(i); })
    .y(function(d) { return y(d.flow); });

  // Add the valueline path.
  svg.append("path")
      .data([data])
      .attr("class", "line")
      .attr("d", valueline);

  xAxis = d3.axisBottom(x).tickValues(ticks).tickFormat(function(d,i) { return full_word_list[i] });

  /*
  // This is for a wider view of the graph.
	if (data_length == 0) {
	  // Add the X Axis
	  svg.append("g")
      .style("font-size", "14px")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
  } 
  else {
	  // Add the X Axis
	  svg.append("g")
      .style("font-size", "14px")
      .attr("transform", "translate(0," + y(0) + ")")
      .call(xAxis);
  }
  */
  // Add the X Axis
  svg.append("g")
     .style("font-size", "14px")
     .attr("transform", "translate(0," + height + ")")
     .call(xAxis);

  // text label for the x axis
  /*
  svg.append("text")             
      .attr("transform",
            "translate(" + (width/2) + " ," + 
                           (height + margin.top + 20) + ")")
      .style("text-anchor", "middle")
      .text("Your words");
  */

  // Add the Y Axis
  svg.append("g")
      .style("font-size", "14px")
      .call(d3.axisLeft(y));

  // text label for the y axis
  svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x",0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "20px")
      .text("Forward flow");  
	/*
  svg.append("circle")
  		.attr("stroke", "black")
         .attr("fill", function(d, i) { return "black" })
         .attr("cx", function(d, i) { return x(i) })
         .attr("cy", function(d, i) { return y(data.flow) })
         .attr("r", function(d, i) { return 3 });
	*/
}

function flow_graph_remove() {
	svg.selectAll("*").remove();
	// d3.select("svg").remove();
}
