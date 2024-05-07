---
---

$(document).ready(() => {
    getTranslations();
});


function getTranslations(path = "/assets/translations") {
    // load data using navigator.language e.g. de-DE.json
    lang = window.localStorage.getItem('translation-language');
    if (lang == null || lang == undefined){
        lang = navigator.language
        window.localStorage.setItem('translation-language', lang);
    }
    fetch(`{{site.baseurl}}${path}/${lang}.json`)
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            return response.json();
        })
        .then(data => {
            //for normal translations
            elements = document.querySelectorAll('[data-translate]');
            for (var element of elements) {
                value = data[element.getAttribute('data-translate')]
                if (value == "" || value == undefined || value == null) {
                    console.log(`No Replace Value '${element.getAttribute('data-translate')}'`)
                    continue;
                }
                element.textContent = value
            }
            //for urls as hrefs
            elements = document.querySelectorAll('[data-href-translate]');
            for (var element of elements) {
                value = data[element.getAttribute('data-href-translate')]
                if (value == "" || value == undefined || value == null) {
                    console.log(`No Replace Value '${element.getAttribute('data-href-translate')}'`)
                    continue;
                }
                element.href = value
            }

            //for buttons
            elements = document.querySelectorAll('[data-value-translate]');
            for (var element of elements) {
                value = data[element.getAttribute('data-value-translate')]
                if (value == "" || value == undefined || value == null) {
                    console.log(`No Replace Value '${element.getAttribute('data-value-translate')}'`)
                    continue;
                }
                element.value = value
                element.name = value
            }
        })
        .catch(function () {this.dataError = true;})
    executeHandelingLanguages();
}


function changeLanguageTo(tag, languageCode) {
    window.localStorage.setItem('translation-language', languageCode);
    window.localStorage.setItem('primary-language', tag);
    getTranslations()
}


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
    if (setlangfields.length == 0){
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
