---
---

var elements = undefined
var elements_translates = new Set();
var found_elements_translates = new Set();
var translationLoadGeneration = 0;
var translationData = {};

function getTranslationLanguage() {
    var language = window.localStorage.getItem('translation-language');
    if (language == null || language == undefined) {
        language = navigator.language || "en-US";
    }

    var supportedLanguages = {
        en: "en-US",
        de: "de-DE",
        fr: "fr-FR",
        ja: "ja-JP"
    };
    language = supportedLanguages[String(language).toLowerCase().slice(0, 2)] || "en-US";
    window.localStorage.setItem('translation-language', language);
    return language;
}

function collectTranslationElements() {
    elements = {};
    elements['translate'] = Array.from(document.querySelectorAll('[data-translate]'));
    elements['href'] = Array.from(document.querySelectorAll('[data-href-translate]'));
    elements['value'] = Array.from(document.querySelectorAll('[data-value-translate]'));
    elements['placeholder'] = Array.from(document.querySelectorAll('[data-placeholder-translate]'));
    elements['extra'] = Array.from(document.querySelectorAll('[data-extra-translate]'));

    elements_translates.clear();
    for (var element of elements['translate']) {
        elements_translates.add(element.getAttribute('data-translate'));
    }
}

function applyTranslations(data) {
    for (var element of elements['translate']) {
        var value = data[element.getAttribute('data-translate')];
        if (value == "" || value == undefined || value == null) {
            continue;
        }
        element.innerHTML = value;
        found_elements_translates.add(element.getAttribute('data-translate'));
    }

    for (var hrefElement of elements['href']) {
        var hrefValue = data[hrefElement.getAttribute('data-href-translate')];
        if (hrefValue == "" || hrefValue == undefined || hrefValue == null) {
            continue;
        }
        hrefElement.href = hrefValue;
    }

    for (var valueElement of elements['value']) {
        var translatedValue = data[valueElement.getAttribute('data-value-translate')];
        if (translatedValue == "" || translatedValue == undefined || translatedValue == null) {
            continue;
        }
        valueElement.value = translatedValue;
        valueElement.name = translatedValue;
    }

    for (var placeholderElement of elements['placeholder']) {
        var placeholderValue = data[placeholderElement.getAttribute('data-placeholder-translate')];
        if (placeholderValue == "" || placeholderValue == undefined || placeholderValue == null) {
            continue;
        }
        placeholderElement.placeholder = placeholderValue;
    }
}

async function loadTranslationFile(path, language, generation) {
    var response = await fetch(`{{site.baseurl}}${path}/${language}.json`);
    if (!response.ok) {
        throw new Error("HTTP error " + response.status + " loading " + path);
    }

    var newdata = await response.json();
    if (generation != translationLoadGeneration) {
        return false;
    }

    Object.assign(translationData, newdata);
    applyTranslations(translationData);
    return true;
}

async function getTranslations(path = "/assets/translations/navbar", olddata = {}) {
    if (elements == undefined || path == "/assets/translations/navbar") {
        collectTranslationElements();
    }
    translationData = Object.assign({}, olddata);
    return loadTranslationFile(path, getTranslationLanguage(), translationLoadGeneration);
}

function scheduleDeferredTranslations(extraElements, language, generation) {
    var loadNext = async function () {
        if (generation != translationLoadGeneration || extraElements.length == 0) {
            return;
        }

        var element = extraElements.shift();
        var path = element.getAttribute('data-extra-translate');
        if (path) {
            try {
                await loadTranslationFile(path, language, generation);
                window.dispatchEvent(new CustomEvent('ffxiv-pocket-guide:translations-updated'));
            } catch (error) {
                console.error(error);
            }
        }

        if (generation == translationLoadGeneration && extraElements.length > 0) {
            if (window.requestIdleCallback) {
                window.requestIdleCallback(loadNext, { timeout: 1000 });
            } else {
                window.setTimeout(loadNext, 0);
            }
        }
    };

    if (window.requestIdleCallback) {
        window.requestIdleCallback(loadNext, { timeout: 1000 });
    } else {
        window.setTimeout(loadNext, 0);
    }
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
}

function changeLanguageTo(tag, languageCode) {
    window.localStorage.setItem('duckit_langs', languageCode.slice(0, 2));
    window.localStorage.setItem('translation-language', languageCode);
    window.localStorage.setItem('primary-language', tag);
    executeHandelingLanguages();
    getTranslationsWrapper()
}

async function getTranslationsWrapper() {
    var generation = ++translationLoadGeneration;
    var language = getTranslationLanguage();
    collectTranslationElements();
    found_elements_translates.clear();
    translationData = {};

    try {
        await loadTranslationFile("/assets/translations/navbar", language, generation);

        var priorityElements = elements['extra'].filter(function (element) {
            return element.getAttribute('data-translation-priority') == 'high' || !element.closest('.sidebar');
        });
        var deferredElements = elements['extra'].filter(function (element) {
            return element.getAttribute('data-translation-priority') != 'high' && element.closest('.sidebar');
        });

        for (var element of priorityElements) {
            var path = element.getAttribute('data-extra-translate');
            if (path) {
                try {
                    await loadTranslationFile(path, language, generation);
                } catch (error) {
                    console.error(error);
                }
            }
        }

        if (generation != translationLoadGeneration) {
            return;
        }

        window.dispatchEvent(new CustomEvent('ffxiv-pocket-guide:translations-updated'));
        validateArrays();
        scheduleDeferredTranslations(deferredElements, language, generation);
    } catch (error) {
        console.error(error);
    }
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
