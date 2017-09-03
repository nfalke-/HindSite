function make_step_row(row, row_number){
    $row = $('<div/>', {class: 'suite'});

    $('<label/>', {text: row_number}).appendTo($row)
    $('<label />', {'for': 'action', text: 'action'}).appendTo($row);
    $select = $('<select/>', {name: 'action'})
    $('<option/>', {value: 'visit', text: 'Visit'}).appendTo($select)
    $('<option/>', {value: 'click', text: 'Click'}).appendTo($select)
    $('<option/>', {value: 'input', text: 'Input'}).appendTo($select)
    $('<option/>', {value: 'sleep', text: 'Sleep'}).appendTo($select)
    $('<option/>', {value: 'refresh', text: 'Refresh'}).appendTo($select)
    $('<option/>', {value: 'execute', text: 'Execute Javascript'}).appendTo($select)
    $('<option/>', {value: 'assert', text: 'Assert'}).appendTo($select)
    $select.appendTo($row);

    $('<label />', {'for': 'arguments', text: 'arguments'}).appendTo($row);
    $('<input/>', {name: 'arguments', value: row.arguments}).appendTo($row);

    $('<label />', {'for': 'screenshot', text: 'screenshot'}).appendTo($row);
    $('<input/>', {
        name: 'screenshot', type: "checkbox",
        checked: row.screenshot, value: row_number}).appendTo($row);

    $('<label />', {'for': 'name', text: 'Screenshot Name'}).appendTo($row);
    $('<input/>', {name: 'screenshot_name', value: row.screenshot_name}).appendTo($row)

    $('<label />', {'for': 'threshold', text: 'threshold'}).appendTo($row);
    $('<input/>', {name: 'threshold', value: row.threshold}).appendTo($row)

    $('<input/>', {
        name: 'add_row', type: 'button', value: "add new row",
        onclick: "make_step_row({threshold:0}).insertAfter(this.parentElement)"
    }).appendTo($row)

    $('<input/>', {
        name: 'remove_row', type: 'button', value: "remove this row",
        onclick: "this.parentElement.remove()"
    }).appendTo($row)
    return $row
}

function make_table(data, id, make_row) {
    $table = $('<div>').attr("id", id)
    count = 0
    data.forEach(function(row) {
        $table.append(make_row(row, count))
        count += 1
    })
    return $table
}

function update(suite_id, test_id) {
    $.get("/suites/"+suite_id+"/tests/"+test_id+"/data/", function(data) {
        $('#suites').replaceWith(
            make_table(data.steps, "suites", make_step_row));
    })
}
