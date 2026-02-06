var elements = undefined
var elements_translates = new Set();
var found_elements_translates = new Set();

async function getTranslations(path = "/assets/translations/navbar", olddata = {}) {
    // load data using navigator.language e.g. de-DE.json
    lang = window.localStorage.getItem('translation-language');
    if (lang == null || lang == undefined){
        lang = navigator.language
        window.localStorage.setItem('translation-language', lang);
    }
    if (path == "/assets/translations/navbar") {
        elements = {}
        elements['translate'] = Array.from(document.querySelectorAll('[data-translate]'));
        for (var ele of elements['translate']) {
            elements_translates.add(ele.getAttribute('data-translate'))
        }
        elements['href'] = Array.from(document.querySelectorAll('[data-href-translate]'));
        elements['value'] = Array.from(document.querySelectorAll('[data-value-translate]'));
        elements['extra'] = Array.from(document.querySelectorAll('[data-extra-translate]'));
    }
    await fetch(`${path}/${lang}.json`)
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            return response.json();
        })
        .then(newdata => {
            data = Object.assign({}, olddata, newdata);

            //for normal translations
            for (var element of elements['translate']) {
                value = data[element.getAttribute('data-translate')]
                if (value == "" || value == undefined || value == null) {
                    continue;
                }
                element.innerHTML  = value
                found_elements_translates.add(element.getAttribute('data-translate'))
            }

            //for urls as hrefs
            for (var element of elements['href']) {
                value = data[element.getAttribute('data-href-translate')]
                if (value == "" || value == undefined || value == null) {
                    //console.log(`No Replace Value '${element.getAttribute('data-href-translate')}'`)
                    continue;
                }
                element.href = value
            }

            //for buttons
            for (var element of elements['value']) {
                value = data[element.getAttribute('data-value-translate')]
                if (value == "" || value == undefined || value == null) {
                    //console.log(`No Replace Value '${element.getAttribute('data-value-translate')}'`)
                    continue;
                }
                element.value = value
                element.name = value
            }

            //for buttons
            if ( path != "/assets/translations/navbar" ){
                return;
            }

            for (var element of elements['extra']) {
                value = element.getAttribute('data-extra-translate')
                if (value === undefined) {
                    continue
                }
                console.log("Load extra: " + value)
                getTranslations(value, data)
            }
            if ( path == "/assets/translations/navbar" ){
                console.log(elements)
            }

        })
        .catch(e => {
            console.log(e)
        }
    )
    return
}

function validateArrays() {
    normal1 = Array.from(elements_translates)
    found1 = Array.from(found_elements_translates)
    for (k of found1){
        const index = normal1.indexOf(k);
        if (index > -1) { // only splice array when item is found
          normal1.splice(index, 1); // 2nd parameter means remove one item only
        }
    }
    console.log(normal1)
}

function changeLanguageTo(tag, languageCode) {
    window.localStorage.setItem('duckit_langs', languageCode.slice(0, 2));
    window.localStorage.setItem('translation-language', languageCode);
    window.localStorage.setItem('primary-language', tag);
    executeHandelingLanguages();
    getTranslationsWrapper()
}

async function getTranslationsWrapper() {
    prom = await getTranslations()
    Promise.all([prom]).then(() => {
        validateArrays()
    });
}


// is is only needed for a few things and is mostly way to overdone now...
function executeHandelingLanguages(){
    // set all language field to be not displayed
    const langfields = document.getElementsByClassName('lang-toggle');
    for (const box of langfields) {
        box.style.display = 'none';
    }

    // get the primary language from localstorage
    l1 = window.localStorage.getItem('primary-language');
    // if its null or undefined replace it with german
    if (l1 == null || l1 == undefined){
        l1 = "lang-toogle-de"
    }
    l2 = l1.replace("lang-toogle", "lang-toogle2");
    // get the elements for the language
    setlangfields = document.getElementsByClassName(l1);
    setlangfields2 = document.getElementsByClassName(l2);
    // in case no elements can be found from localstorage
    if (setlangfields == undefined){
        setlangfields = document.getElementsByClassName("lang-toogle-de");
        setlangfields2 = document.getElementsByClassName("lang-toogle2-de");
    }
    // set all elements for the language to be displayed
    doLanguageStuff(setlangfields, null)
    doLanguageStuff(setlangfields2, "block")

    // only show en_translation, if main language is not en
    if (l1 != "lang-toogle-en"){
        setlangfields = document.getElementsByClassName("lang-toogle-en-sub");
        for (const box of setlangfields) {
            if (box.tagName == "SPAN"){
                box.style.display = 'inline';
            } else {
                box.style.display = 'block';
            }
            box.style.visibility = 'inherit';
        }
    } else {
        setlangfields = document.getElementsByClassName("lang-toogle-en-sub");
        for (const box of setlangfields) {
            //box.style.display = 'none';
            box.style.visibility = 'hidden';
        }
    }
}


function doLanguageStuff(setlangfields, adj) {
    for (const box of setlangfields) {
        if (box.tagName == "SPAN"){
            box.style.display = adj || 'inline';
        } else {
            box.style.display = 'block';
        }
    }
}


$(document).ready(() => {
    getTranslationsWrapper()
});
