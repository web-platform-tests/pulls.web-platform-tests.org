(function() {

  function drawCumulativeChart() {
    var line_data = JSON.parse(window.WPTDASH.cumulativeData);

    var pctMultiplier = 100 / d3.max(line_data, function(d) { return d.sum; });


    var MARGIN = {top: 20, right: 20, bottom: 30, left: 50};
    var cumulativeChart = d3.select('#cumulative-chart');
    var width = +cumulativeChart.attr('width') - MARGIN.left - MARGIN.right;
    var height = +cumulativeChart.attr('height') - MARGIN.top - MARGIN.bottom;
    var g = cumulativeChart.append('g')
      .attr('transform', 'translate(' + MARGIN.left + ',' + MARGIN.top + ')')
    var xScale = d3.scaleLinear().rangeRound([0, width]);
    var yScale = d3.scaleLinear().rangeRound([height, 0]);
    var areaFn = d3.area()
      .x(function(d) { return xScale(d.minutes); })
      .y1(function(d) { return yScale(d.sum * pctMultiplier); })
      .curve(d3.curveStepAfter);


    xScale.domain([0, 60]).clamp(true);
    yScale.domain([0, 100]);

    areaFn.y0(yScale(0));

      g.append("path")
          .datum(line_data)
          .attr("fill", "steelblue")
          .attr("d", areaFn);

    g.append('g')
      .attr('transform', 'translate(0,' + height + ')')
      .call(d3.axisBottom(xScale).ticks(10, '.0s'));

    g.append('g')
      .call(d3.axisLeft(yScale))
      .append('text')
        .attr('fill', '#000')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end");
  }

  function drawHistogram(svg, data) {
    var formatCount = d3.format(",.0f");

    var margin = {top: 10, right: 30, bottom: 30, left: 30};
    var width = +svg.attr("width") - margin.left - margin.right;
    var height = +svg.attr("height") - margin.top - margin.bottom;
    var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var xScale = d3.scaleLinear()
        .domain([0, 60]).clamp(true)
        .range([0, width]);

    var bins = d3.histogram()
        .domain(xScale.domain())
        .thresholds(xScale.ticks(10))
        (data);

    var yScale = d3.scaleLinear()
        .domain([0, d3.max(bins, function(d) { return d.length; })])
        .range([height, 0]);

    var bar = g.selectAll(".bar")
      .data(bins)
      .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + xScale(d.x0) + "," + yScale(d.length) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", xScale(bins[0].x1) - xScale(bins[0].x0) - 1)
        .attr("height", function(d) { return height - yScale(d.length); });

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", 6)
        .attr("x", (xScale(bins[0].x1) - xScale(bins[0].x0)) / 2)
        .attr("text-anchor", "middle")
        .text(function(d) { return formatCount(d.length); });

    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale));
  }

  function drawBuildTimeHistogram() {
    drawHistogram(
      d3.select('#build-times'),
      JSON.parse(window.WPTDASH.buildTimes)
    );
  }

  function drawWaitTimeHistogram() {
    drawHistogram(
      d3.select('#wait-times'),
      JSON.parse(window.WPTDASH.waitTimes)
    );
  }

  drawCumulativeChart();
  drawWaitTimeHistogram();
  drawBuildTimeHistogram();
}());
