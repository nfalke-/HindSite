function make_row(row, suite_id){
    $button = $('<button/>').text('x').click(
        function() {
            $.get('/suites/'+row.id+'/delete/')
            update()
        }
    ).attr("class", "deleteb")

    $lastRan = $('<div/>').text(row.last_ran)
    $name = $('<a/>').attr('href', '/suites/' + suite_id + '/tests/'+row.id).text(row.name)
    $testPassed = $('<div/>').text('Test Passed: ' + row.passed)
    $screenshotPassed = $('<div/>').text('Screenshot Passed' + row.screenshot_passed)


    $row = $('<div/>').attr('class', 'suite'); 
    $top = $('<div/>').html($name)
    $top.append($button)
    $row.append($top)

    $row.append($testPassed)
    $row.append($screenshotPassed)

    return $row
}

function make_divs(data, suite_id) {
    $table = $('<div>').attr("id", "suites")
    data.forEach(function(row) {
        $table.append(make_row(row, suite_id))
    })
    return $table
}
function make_select(data, select_id, select_name, default_option) {
    $select = $('<select/>').attr('id', select_id).attr('name', select_name)
    $select.append($('<option\>').attr('value', 0).text(default_option))
    data.forEach(function(row) {
        $select.append($('<option\>').attr('value', row.id).text(row.name))
    })
    return $select
}


function update(suite_id) {
    $.get("/suites/suite_id/data/", function(data) {
        $('#suites').replaceWith(make_divs(data, suite_id));
        $('#suite_select').replaceWith(make_select(data));
    })
    $.get("/suites/" + suite_id + "/copy/data/", function(data) {
        console.log(data)
        $('#test_to_copy').replaceWith(make_select(data.tests, "test_to_copy", "test", "Test Name"));
        $('#suite_to_copy_to').replaceWith(make_select(data.suites, "suite_to_copy_to", "suite", "Suite Name"));
    })
    setTimeout(update, 30000)
}

