function translate_getSearchCategories() {
    var Http = new XMLHttpRequest();
    var url = encodeURI('https://ff14.akurosiakamo.de/extras/json/list_files.php');

    Http.open("GET", url, true);
    Http.send();

    Http.onreadystatechange = (e) => {
        if (Http.readyState === 4 && Http.status === 200) {
            _select = document.getElementById("filterValue");

            // Parse text instead of JSON
            let raw = Http.responseText.trim();

            // Support newline OR comma separated formats
            let files = raw.includes("\n")? raw.split("\n"): raw.split(",");

            files = files
                .map(s => s.trim())
                .filter(Boolean);

            var collator = new Intl.Collator(undefined, {
                numeric: true,
                sensitivity: 'base',
                ignorePunctuation: true
            });

            files = files.sort(collator.compare);

            for (let file of files) {
                // Remove wrapping quotes if present
                file = file.replace(/^"+|"+$/g, '');

                let _element = document.createElement('option');
                _element.value = file;
                _element.text = file;
                _select.appendChild(_element);
            }

            translate_loadFromLocalStorage();
        }
    };
}



function translate_SubmitToLocalStorage(){
    var inp = document.getElementById("filterValue").selectedIndex;
    localStorage.setItem('ffxiv_aku_filterValue', inp);
    var inp = document.getElementById("fieldfilter").value;
    localStorage.setItem('ffxiv_aku_fieldfilter', inp);
    var inp = document.getElementById("filterterm").value
    localStorage.setItem('ffxiv_aku_filterterm', inp);
}


function translate_loadFromLocalStorage(){
    if(localStorage.getItem('translate_ffxiv_term') !== null){
        document.getElementById("filterValue").selectedIndex = localStorage.getItem('ffxiv_aku_filterValue');
        document.getElementById("fieldfilter").value = localStorage.getItem('ffxiv_aku_fieldfilter');
        document.getElementById("filterterm").value = localStorage.getItem('ffxiv_aku_filterterm');
        //document.getElementById("exactSearch").selectedIndex = localStorage.getItem('ffxiv_aku_filterValue');
    }
}


async function UserAction2(caller){
    remove_bodyDiv();
    await load_data(caller)
    console.log("Done")
}


function remove_bodyDiv(){
    _body = document.getElementById("workspace");
    _body.innerHTML = "";
}


async function load_data(caller){
    _select = document.getElementById("filterValue")
    _input = document.getElementById("fieldfilter")
    _filterterm = document.getElementById("filterterm").value.toLowerCase();
    _input = _input.value.split(/,\s*/)
    if (_input == ""){
        _input = "*"
    }else {
        _input = [..._input].map(c => c.trim().toLowerCase());
    }
    var Http = new XMLHttpRequest();
    if (caller == "example"){
        url = "https://ff14.akurosiakamo.de/extras/json/xivapi_data/" + _select.value;
    } else {
        url = "https://ff14.akurosiakamo.de/extras/json/xivapi_data/" + _select.value;
    }
    url = encodeURI(url)
    console.log(url)

    Http.open("GET", url, true);
    Http.send();
    Http.onreadystatechange = (e) => {
        if (Http.readyState == 4 && Http.status == 200){
            let json = JSON.parse(Http.responseText);
            addToBody(json, caller, _filterterm, _input);
            translate_SubmitToLocalStorage();
        }
    }
}


function addToBody(json, caller, _filterterm, _input){
    _body = document.getElementById("workspace");
    //button = createTemplateButton(name, icon);
    _table = createTemplateTable(json, caller, _filterterm, _input);
    //_body.appendChild(button)
    _body.appendChild(_table)
}


function createTemplateTable(json, caller, _filterterm, _input){
    var _table = document.createElement('table');


    if (caller == "data"){
        console.log("data");
        _thead = createTemplateTableHead(json)
        _tbody = createTemplateTableBody(json, _filterterm, _input)
    } else {
        console.log("example");
        _thead = createTemplateTableHead2(json)
        _tbody = createTemplateTableBody2(json)

    }
    _table.appendChild(_thead);
    _table.appendChild(_tbody);
    _table.className = "table table-bordered table-dark table-striped text-light patch_table";
    return _table;
}


function createTemplateTableHead2(json){
    var _head = document.createElement('thead');
    var _tr = document.createElement('tr');
    _head.appendChild(_tr);

    var _th = document.createElement('th');
    var textnode_1 = document.createTextNode("Column");
    _th.appendChild(textnode_1);
    _tr.appendChild(_th);
    var _th2 = document.createElement('th');
    var textnode_2 = document.createTextNode("ExampleData");
    _th2.appendChild(textnode_2);
    _tr.appendChild(_th2);

    _head.appendChild(_tr);

    return _head;
}


function createTemplateTableBody2(json){
    var _body = document.createElement('tbody');
    var collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
    var keys = Object.keys(json);
    console.log(keys);
    keys = keys.sort(collator.compare)
    for (var json_key in keys) {
        _tr = document.createElement('tr');
        var _td = document.createElement('td');
        var textnode_1 = document.createTextNode(keys[json_key]);
        _td.appendChild(textnode_1);
        _tr.appendChild(_td);

        var _td2 = document.createElement('td');
        if (typeof json[keys[json_key]] === 'object'){
            var textnode_2 = document.createTextNode(JSON.stringify(json[keys[json_key]]));
        } else {
            var textnode_2 = document.createTextNode(json[keys[json_key]]);
        }
        _td2.appendChild(textnode_2);

        _tr.appendChild(_td2);
        _body.appendChild(_tr);
    }
    return _body;
}


function addHeadElement(_tr, prop){
    var _th = document.createElement('th');
    _th.setAttribute("role", "columnheader");
    _th.setAttribute("scope", "col");
    var textnode_1 = document.createTextNode(prop);
    _th.appendChild(textnode_1);
    _tr.appendChild(_th);
    return _tr
}


function createTemplateTableHead(json){
    header_json = json
    var _head = document.createElement('thead');
    var _tr = document.createElement('tr');
    _head.appendChild(_tr);

    var textnode_1 = document.createTextNode("key");
    var _th = document.createElement('th');
    _th.appendChild(textnode_1);
    _tr.appendChild(_th);

    // Add all coulmn fro file
    for (var firstelement in header_json) {
        for (var prop in header_json[firstelement]) {
            if (_input != "*") {
                if (!_input.includes(prop.toLocaleLowerCase())){
                    continue
                }
            }
            if (typeof header_json[firstelement][prop] == "object") {
                for (var sub_element_key in header_json[firstelement][prop]) {
                    _tr = addBodyElement(_tr, prop + "[" + sub_element_key + "]")
                }
            } else {
                _tr = addHeadElement(_tr, prop)
            }
        }
        break;
    }

    _head.appendChild(_tr);

    return _head;
}


function addBodyElement(_tr, element){
    var _td = document.createElement('td');
    if (typeof element == "object") {
        element = JSON.stringify(element);
    }
    if (element.startsWith("ui") && element.endsWith(".tex")){
        var value = element.replace(".tex", "_hr1.png")
        var textnode_1 = document.createElement('img');
        textnode_1.setAttribute("src", "https://ff14.akurosiakamo.de/extras/images/" + value);
        textnode_1.setAttribute("alt", value);
        textnode_1.setAttribute("style", "max-height: 40px; max-width: fit-content;");
    } else{
        var textnode_1 = document.createTextNode(element);
    }
    _td.appendChild(textnode_1);
    _tr.appendChild(_td);
    return _tr
}


function createTemplateTableBody(json, _filterterm, _input){
    var _body = document.createElement('tbody');
    var collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
    var keys = Object.keys(json);
    keys = keys.sort(collator.compare)
    for (var json_key of keys) {
        element = json[json_key]
        if (_filterterm != ""){
            if (!(JSON.stringify(element)+json_key).toLowerCase().includes(_filterterm)){
                continue
            }
        }
        var _tr = document.createElement('tr');
        var _td = document.createElement('td');
        // add json key to list
        var textnode_1 = document.createTextNode(json_key);
        _td.appendChild(textnode_1);
        _tr.appendChild(_td);

        // Add all coulmn fro file
        found_item = false
        for (var element_key in element) {
            if (_input != "*") {
                if (!_input.includes(element_key.toLocaleLowerCase())){
                    continue
                }
            }
            found_item = true
            // if element is a dict do it for all subkeys
            if (typeof element[element_key] == "object") {
                //_tr = addBodyElement(_tr, JSON.stringify(element[element_key]))
                for (var sub_element_key in element[element_key]) {
                    _tr = addBodyElement(_tr, element[element_key][sub_element_key])
                }
            } else {
                _tr = addBodyElement(_tr, element[element_key])
            }
            //_tr.appendChild(_td);
        }

        // if a filterterm is set and the final result does not include the filterterm, pretent to have not found the item at all
        if (_filterterm != "") {
            if (!_tr.outerHTML.toLowerCase().includes(_filterterm)){
                found_item=false
            }
        }
        // only print result if flag is true
        if (found_item){
            _body.appendChild(_tr);
        }
    }
    return _body;
}


translate_getSearchCategories();

