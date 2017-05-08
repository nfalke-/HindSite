var table = document.getElementById('StepTable')
    tbody = table.getElementsByTagName('tbody')[0],
    clone = tbody.rows[0].cloneNode(true);
window.onload = renumber;

function renumber(){
    var i = 1;
    while (table.rows[i]) {
        updateRow(table.rows[i], i, false);
        i++;
    }
}

function deleteRow(el) {
    var i = el.parentNode.parentNode.rowIndex;
    table.deleteRow(i);
    renumber()
}

function insRow(el) {
    var i = el.parentNode.parentNode.rowIndex;
    var new_row = updateRow(clone.cloneNode(true), ++tbody.rows.length, true);
    tbody.insertBefore(new_row, tbody.children[i]);
    renumber()
}

function updateRow(row, i, reset) {
    row.cells[0].innerHTML = i;

    var inp1 = row.cells[1].getElementsByTagName('select')[0];
    var inp2 = row.cells[2].getElementsByTagName('input')[0];
    var inp3 = row.cells[3].getElementsByTagName('input')[0];
    var inp4 = row.cells[4].getElementsByTagName('input')[0];
    var inp5 = row.cells[5].getElementsByTagName('input')[0];
    //var inp6 = row.cells[6].getElementsByTagName('input')[0];
    inp1.name = 'action';
    inp2.name = 'arguments';
    inp3.name = 'screenshot';
    inp4.name = 'screenshot_name';
    inp5.name = 'threshold';
    if (!inp3.checked) {
        inp4.disabled = true;
        inp5.disabled = true;
    }
    inp3.onclick = function() {
        inp4.disabled = !(this.checked);
        inp5.disabled = !(this.checked);
    }
    inp3.value = i;
    if (reset) {
        inp1.value = 'click';
        inp2.value = inp4.value =  '';
        inp5.value = .10;
        inp3.checked = false;
    }
    return row;
}

function activateAll(){
    var i = 1;
    while (table.rows[i]) {
        var inp4 = table.rows[i].cells[4].getElementsByTagName('input')[0].disabled=false;
        var inp5 = table.rows[i].cells[5].getElementsByTagName('input')[0].disabled=false;
        i++;
    }
}

