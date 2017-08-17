
function make_row(row){
    //order doesn't matter here, put them wherever you want
    $button = $('<button/>')
        .text('x')
        .attr("class", "deleteb")
        .click(
            function() {
                $.get('/suites/'+row.id+'/delete/')
                update()
            }
        )
    $name = $('<a/>')
        .attr('href', '/suites/'+row.id)
        .attr("class", "suitename")
        .text(row.name)
    $lastRan = $('<div/>')
        .attr("id", "lastran")
        .text("Last Ran: " + row.last_ran)
    $browser = $('<div/>')
        .attr("class", "linline")
        .attr("id", "capbrow")
        .text(row.browser)
    $dims = $('<div/>')
        .attr("class", "rinline")
        .text(row.width+'x'+row.height)
    $description = $('<div/>')
        .attr("id", "des")
        .text("Description: " + row.description)
    $testCount = $('<div/>')
        .attr("class", "linline")
        .text('Test Count: ' + row.test_count)
    $failCount = $('<div/>')
        .attr("class", "rinline")
        .text('Fail Count: ' + 0)

    //move these around to put things where you like them
    $row = $('<div/>').attr('class', 'suite'); 
    $top = $('<div/>').html($name)
    $top.append($button)
    $row.append($top)
    $row.append($lastRan)
    $settings = $('<div/>')
    $settings.append($browser)
    $settings.append($dims)
    $row.append($settings)
    $row.append($testCount)
    $row.append($failCount)
    $row.append($description)

    return $row
}

function make_divs(data) {
    $table = $('<div>').attr("id", "suites")
    data.forEach(function(row) {
        $table.append(make_row(row))
    })
    return $table
}

function make_select(data) {
    $select = $('<select/>').attr('id', 'suite_select').attr('name', 'suite')
    $select.append($('<option\>').attr('value', 0).text("Suite Name"))
    data.forEach(function(row) {
        $select.append($('<option\>').attr('value', row.id).text(row.name))
    })
    return $select
}

function update() {
    $.get("/data/", function(data) {
        $('#suites').replaceWith(make_divs(data));
        $('#suite_select').replaceWith(make_select(data));
    })
    setTimeout(update, 30000)
}

