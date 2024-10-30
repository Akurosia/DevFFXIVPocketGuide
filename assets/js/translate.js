
translate_getSearchCategories();
translate_loadFromLocalStorage();

languages = ["_en","_de","_fr","_ja","_cn","_ko"]

function translate_loadFromLocalStorage(){
  if(localStorage.getItem('translate_ffxiv_term') !== null){
    document.getElementById("searchValue").value = localStorage.getItem('translate_ffxiv_term');
    document.getElementById("exactSearch").selectedIndex = localStorage.getItem('translate_ffxiv_exact');
    document.getElementById("filterValue").value = localStorage.getItem('translate_ffxiv_filter');
  }
}

// This will get all available search categories
function translate_getSearchCategories(){
  fetch('https://ffxiv.akurosiakamo.de/getTables.php')
    .then(response => response.json())
    .then(json => set_files(json))
}

function set_files(list_of_files){
    _select = document.getElementById("filterValue");
    for (var category in list_of_files){
        var _element = document.createElement('option');
        var value = list_of_files[category].replace('_all', '')
        _element.setAttribute("value", value);
        _element.text = value;
        _select.appendChild(_element);
    }
    translate_loadFromLocalStorage();
}

// Execute a function when the user releases a key on the keyboard
var input = document.getElementById("searchValue");
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("submitbtn").click();
    }
});

//saves last used search criteria to localstorage
function translate_SubmitToLocalStorage(){
    var inp = document.getElementById("searchValue").value;
    localStorage.setItem('translate_ffxiv_term', inp);

    var inp = document.getElementById("exactSearch").selectedIndex;
    localStorage.setItem('translate_ffxiv_exact', inp);

    var inp = document.getElementById("filterValue").value
    localStorage.setItem('translate_ffxiv_filter', inp);
}


async function translate_search(){
    remove_bodyDiv();
    var searchvalue = document.getElementById("searchValue").value;
    var filter = document.getElementById("filterValue")
    var filefilter = filter.value;
    var exactSearch = eval(document.getElementById("exactSearch").value);

    files = []
    for (var x = 1; x < filter.options.length; x++){
        files.push(filter.options[x].value)
    }

    if (filefilter == "all"){
        filefilter = null
    }

    console.log("Filefilter: " + String(filefilter))
    console.log("SearchValue: " + searchvalue)

    document.getElementById('search_spinner').classList.add("fa-spinner");
    promisses = []
    if (filefilter !== null) {
        p = getDataViaXMLHTTP(searchvalue.toLowerCase(), filefilter, exactSearch);
        promisses.push(p)
    }else {
        promisses = []
        files.forEach(file => {
            p = getDataViaXMLHTTP(searchvalue.toLowerCase(), file, exactSearch);
            promisses.push(p)
        });
    }
    await Promise.allSettled(promisses).then((xxx) => {
        //console.log(xxx)
        document.getElementById('search_spinner').classList.remove("fa-spinner")
        order_divs_at_the_end()
        // sort elements
    });
    console.log("Done")
}

function order_divs_at_the_end(){
    var mylist = document.getElementById('bodyDiv');
    var divs = mylist.getElementsByTagName('div');
    var listitems = [];
    for (i = 0; i < divs.length; i++) {
        if (divs.item(i).getAttribute('id').startsWith("mdiv")) {
            listitems.push(divs.item(i));
        }
    }
    listitems.sort(function(a, b) {
        var compA = a.getAttribute('id').toUpperCase();
        var compB = b.getAttribute('id').toUpperCase();
        return (compA < compB) ? -1 : (compA > compB) ? 1 : 0;
    });
    for (i = 0; i < listitems.length; i++) {
        mylist.appendChild(listitems[i]);
    }
}

// this will remove all old content from page except the header + searchbar
function remove_bodyDiv(){
    _body = document.getElementById("bodyDiv");
    _body.innerHTML = "";
}

function handleErrors(response) {
    if (!response.ok) {
        throw Error(JSON.stringify(response));
    }
    return response;
}

// get data from api via xmlhttprequest
async function getDataViaXMLHTTP(name, filefilter="", exact=false){
    if (!exact){
        name = name.trim();
    }

    urlparams = "?filterValue=" + filefilter
    urlparams = urlparams + "&searchValue=" + name
    //if (name){
    //    urlparams = urlparams + "&searchValue=" + name
    //}
    if (exact){
        urlparams = urlparams + "&exactSearch=" + exact
    }
    newurl = 'https://ffxiv.akurosiakamo.de/queryFFXIVtranslateDB.php' + urlparams
    console.log(newurl)
    return fetch(newurl)
        .then(handleErrors)
        .then(response => response.json())
        .then(json => addToBody(json, filefilter))
}

// this function will add content to the page (Beginning)
function addToBody(json, name){
    if (json == undefined || JSON.stringify(json) == "[]"){
        return
    }
    _body = document.getElementById("bodyDiv");

    var m_div = document.createElement('div');
    m_div.setAttribute("id", "mdiv_"+name);
    button = createTemplateButton(name);
    _div = createTemplateDIV(name, json);

    m_div.appendChild(button)
    m_div.appendChild(_div)
    _body.appendChild(m_div)
    window.dispatchEvent(new Event('resize'));
}

// this create a button to collapse or expand the table with content
function createTemplateButton(name){
    var button = document.createElement('button');
    var span_1 = document.createElement('span');
    var span_2 = document.createElement('span');

    var textnode_1 = document.createTextNode(name);
    var textnode_2 = document.createTextNode("▼");

    span_1.appendChild(textnode_1);
    span_2.appendChild(textnode_2);

    button.appendChild(span_1);
    button.appendChild(span_2);

    button.className = "collapsible bg-charcoal text-light";
    button.setAttribute("onclick","collapsOrExpand(this.children);");
    return button;
}

// this creates the container for the data that can be collapsed with the button
function createTemplateDIV(name, json){
    var _div = document.createElement('div');
    _table = createTemplateTable(name, json);
    _div.appendChild(_table);
    createTemplateScripts(name, _div);
    _div.className = "content table-responsive border-gold-metallic";
    _div.setAttribute("id", "div_"+name);
    _div.style.display = "none";
    return _div;
}

//this creates the actual table
function createTemplateTable(name, json){
    var _table = document.createElement('table');

    _thead = createTemplateTableHead(name, json)
    _tbody = createTemplateTableBody(name, json)
    _table.appendChild(_thead);
    _table.appendChild(_tbody);

    _table.setAttribute("id", "table_"+name);
    //_table.className = "table-striped table-dark table-hover bg-charcoal text-light border-gold-metallic";
    _table.className = "table table-bordered table-dark table-striped text-light patch_table";

    //_table.style.width = "1641px";
    _table.style["margin-bottom"] = "0px";
    return _table;
}

//this wil generate a propper set of header columns like i want it
function getTableColumns(header_json){
    columns = []
    // creates the base columns with unique values
    for (var prop in header_json) {
        if (languages.includes(prop.substring(prop.length -3))) {
            prop = prop.substring(0, prop.length - 2)
        }
        if (!columns.includes(prop)){
            columns.push(prop)
        }
    }
    // if an icon is available, make sure its at position [1]
    if (columns[1] != "Icon" && columns.includes("Icon")){
        columns = columns.filter(item => item !== "Icon")
        columns.splice(1, 0, "Icon")
    }
    // creates the final columns with all languages in order
    r_columns = []
    // first add non translateable columns
    for (var element in columns){
        if(columns[element].substring(columns[element].length - 1) != "_"){
            r_columns.push(columns[element])
        }
    }
    //remove elmeents
    for (var element in r_columns){
        columns = columns.filter(item => item !== r_columns[element])
    }
    //turn array around so description is always last and name/text/singular is first
    columns.reverse();
    for (var lang in languages){
        for (var element in columns){
            r_columns.push(columns[element].substring(0, columns[element].length - 1) + languages[lang])
        }
    }
    return r_columns
}

var header = []
function createTemplateTableHead(name, json){
    header_json = json[Object.keys(json)[0]]
    var _head = document.createElement('thead');
    var _tr = document.createElement('tr');
    _head.appendChild(_tr);

    // Add first Column ID
    var _th = document.createElement('th');
    _th.setAttribute("role", "columnheader");
    _th.setAttribute("aria-sort", "ascending");
    var textnode_1 = document.createTextNode("ID");
    _th.setAttribute("scope", "col");
    _th.appendChild(textnode_1);
    _tr.appendChild(_th);

    header = getTableColumns(header_json)
    // Add all coulmn fro file
    for (var prop in header) {
        var _th = document.createElement('th');
        _th.setAttribute("role", "columnheader");
        if (header[prop] == "_id"){
            continue;
        }
        var textnode_1 = document.createTextNode(header[prop]);
        _th.setAttribute("scope", "col");
        _th.setAttribute("class", getLanguageCode(header[prop]));
        _th.appendChild(textnode_1);
        _tr.appendChild(_th);
    }
    // Add copyRegexBtn
    var _th = document.createElement('th');
    _th.setAttribute("role", "columnheader");
    var textnode_1 = document.createTextNode("Get Values");
    _th.appendChild(textnode_1);
    _th.setAttribute("scope", "col");
    _tr.appendChild(_th);
    _head.appendChild(_tr);
    return _head;
}

function getLanguageCode(value){
    for (var lang in languages) {
        if (value.includes(languages[lang])) {
            return languages[lang];
        }
    }
    return ""
}

function createTemplateTableBody(name, json){
    var _body = document.createElement('tbody');
    counter = 0
    for (var json_key in json) {
        element = json[json_key]
        var _tr = document.createElement('tr');
        // Add first Column ID
        var _td = document.createElement('td');
        var textnode_1 = document.createTextNode(parseInt(element["0xID"], 16));
        _td.appendChild(textnode_1);
        _tr.appendChild(_td);
        // Add all coulmn fro file
        var e = ""
        for (var element_key in header) {
            if (header[element_key] == "_id"){
                continue;
            }
            e = element[header[element_key]]
            if (e == undefined){
                e = ""
            }else {
                // convert e to a string if it was maybe an integer
                e = String(e)
            }

            var _td = document.createElement('td');
            _td.setAttribute("class", getLanguageCode(header[element_key]));
            if (e.endsWith(".png")){
                // if e is an image
                e = e.replace(".png", "_hr1.png")
                var _img = document.createElement('img');
                // _img.setAttribute("src", "https://ffxiv.akurosia.de/extras/images/" + e);
                _img.setAttribute("src", "https://xivapi.com/i/" + e.replace("ui/icon/", ""));
                _img.setAttribute("alt", e);
                _img.setAttribute("loading", "lazy");
                _img.setAttribute("height", "30");
                _img.setAttribute("width", "30");
                _td.appendChild(_img);
            } else {
                var textnode_1 = document.createTextNode(e);
                _td.appendChild(textnode_1);
            }
            _tr.appendChild(_td);
        }

        // Add copyRegexBtn
        var _td = document.createElement('td');
        var _btn = document.createElement('input');
        _btn.setAttribute("type", "button");
        _btn.setAttribute("value", "GetRegex()");
        _btn.setAttribute("onclick", "getRegEx(this)");
        _td.appendChild(_btn);
        _tr.appendChild(_td);
        _body.appendChild(_tr);

        // code for limit purpose
        //counter += 1;
        //if (counter > 4){
        //    break;
        //}
    }
    return _body;
}

function createTemplateScripts(name, _div){
    var _script_1 = document.createElement('script');
    var _script_2 = document.createElement('script');
    var _script_3 = document.createElement('script');

    var textnode_1 = document.createTextNode("new Tablesort(document.getElementById('table_"+name+"'), {descending: true});");
    var textnode_2 = document.createTextNode("document.getElementById('table_"+name+"').children[0].children[0].children[0].click();");
    var textnode_3 = document.createTextNode("document.getElementById('table_"+name+"').children[0].children[0].children[0].click();");

    _script_1.appendChild(textnode_1);
    _script_2.appendChild(textnode_2);
    _script_3.appendChild(textnode_3);

    _div.appendChild(_script_1);
    _div.appendChild(_script_2);
    _div.appendChild(_script_3);
}

//WHEN SEARCH BUTTON IS PRESSED
function UserAction(file, folder = "translate") {
    var searchvalue = document.getElementById("searchValue").value;
    window.open("/py/" + folder + "/"+file+"?"+searchvalue,"_self")
}

//FUNCTION FOR THE COLLAPSE BUTTON
function collapsOrExpand(ele, state="none"){
    var colldiv = document.getElementById("div_"+ele[0].innerHTML);
    console.log(ele[0].innerHTML)
    //setTableWitdh(ele)
    if (colldiv.style.display === "table" || colldiv.style.display === "inline") {
        colldiv.style.display = "none";
        ele[1].innerHTML = "&#x25BC;";
    } else {
        if (state === "list"){
            colldiv.style.display = "inline";
        }else if (state === "flex"){
            colldiv.style.display = "flex";
        }else {
            colldiv.style.display = "table";
        }
        ele[1].innerHTML = "&#x25B2;";
    }
}

// Get the input field
$(document).ready(function(){
    $('#searchValue').keypress(function(e){
        if(e.keyCode==13)
        $('#submit').click();
    });
    window.dispatchEvent(new Event('resize'));
});

function setTableWitdh(ele) {
    try{
        document.getElementById("table_"+ele[0].innerHTML).style.width = ele[0].parentElement.clientWidth+2;
    }catch{
        console.log("Error on collapsOrExpand")
    }
}

function getRegEx(data) {
    line = data.parentElement.parentElement
    namedElements = line.getElementsByTagName("td")
    // namedElements[id_dec, id_hex, icon, german, english, franc, japanese, button]
    numberOfEntries = namedElements.length
    result = ""
    for(var i = 0; i<numberOfEntries; i++){
        if (namedElements[i].className == ""){
            continue;
        }
        result += "|" + namedElements[i].innerHTML
    }
    result = "(ID_" + namedElements[0].innerHTML + "|0xID_" + parseInt(namedElements[0].innerHTML, 16) + result + ")"
    result = result.replace("(|", "(").replace("||", "|").replace("||", "|").replace("||", "|").replace("|)", ")")
    var textarea = document.createElement("textarea");
    textarea.textContent = result;
    textarea.style.position = "fixed";
    document.body.appendChild(textarea);
    textarea.select();
    console.log(result);
    try {
       return document.execCommand("copy");  // Security exception may be thrown by some browsers.
    } catch (ex) {
        console.warn("Copy to clipboard failed.", ex);
        return false;
    } finally {
        document.body.removeChild(textarea);
    }
}
