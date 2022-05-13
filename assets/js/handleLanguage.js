$(document).ready(function() {
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
    // get the elements for the language
    setlangfields = document.getElementsByClassName(l1);
    // in case no elements can be found from localstorage
    if (setlangfields.length == 0){
        l1 = "lang-toogle-de"
        setlangfields = document.getElementsByClassName(l1);
    }
    // set all elements for the language to be displayed
    for (const box of setlangfields) {
        if (box.tagName == "SPAN"){
            box.style.display = 'inline';
        } else {
            box.style.display = 'block';
        }
    }

    // only show en_translation, if main language is not en
    if (l1 != "lang-toogle-en"){
        setlangfields = document.getElementsByClassName("lang-toogle-en-sub");
        for (const box of setlangfields) {
            if (box.tagName == "SPAN"){
                box.style.display = 'inline';
            } else {
                box.style.display = 'block';
            }
        }
    } else {
        setlangfields = document.getElementsByClassName("lang-toogle-en-sub");
        for (const box of setlangfields) {
            box.style.display = 'block';
            box.style.visibility = 'hidden';
        }
    }

});

function changeLanguageTo(tag) {
    window.localStorage.setItem('primary-language', tag);
    location.reload();
}
