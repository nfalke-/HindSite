function sendRequest(url) {
    var http = new XMLHttpRequest();
    http.open("GET", url, true);
    http.send( null )
    location.reload();
}

function updateTable(table_id, table_json) {
    var oldTable = document.getElementById(table_id),
        newTable = oldTable.cloneNode();
    for(var i = 0; i < table_json.length; i++){
        var tr = document.createElement('tr');
        for(var j = 0; j < table_json[i].length; j++){
            var td = document.createElement('td');
            td.appendChild((table_json[i][j]));
            tr.appendChild(td);
        }
        newTable.appendChild(tr);
    }
    oldTable.parentNode.replaceChild(newTable, oldTable);
}

function build_link(loc, text){
    var button = document.createElement("a");
    button.setAttribute("href", loc);
    button.innerHTML = text;
    return button
}

function build_button(value, click_action){
    var button = document.createElement("input");
    button.setAttribute("type", "button");
    button.setAttribute("value", value);
    button.setAttribute("onclick", click_action);
    return button
}

function build_span(text) {
    var span = document.createElement("span");
    span.innerHTML = text
    return span
}

function build_image(test_id, run_id, screenshot_name) {
    var screenshot_container = document.createElement("div");
    screenshot_container.setAttribute("class", "screenshot-container")
    var screenshot = document.createElement("img");
    screenshot.onclick = function(){
        modal.style.display = "block";
        modalImg.src = this.src;
    }
    screenshot.setAttribute("class", "screenshot")
    screenshot.setAttribute("src",
            "/static/" + test_id +
            "/" + run_id +
            "/" + screenshot_name +
            ".png");
    screenshot_container.append(screenshot);
    return screenshot_container
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

var http = new XMLHttpRequest();
async function update(url) {
    while(true){
      http.open("GET", url, true);
      http.send();
      await sleep(60000);
  }
};
