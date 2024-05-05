function getTranslations() {
        // load data using navigator.language e.g. de-DE.json
        fetch(`assets/translations/${navigator.language}.json`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("HTTP error " + response.status);
                }
                return response.json();
            })
            .then(data => {
                elements = document.querySelectorAll('[data-translate]');
                for (var element of elements) {
                    element.textContent = data[element.getAttribute('data-translate')]
                }
            })
            .catch(function () {this.dataError = true;})
    }

getTranslations()
window.onload = (event) => {
    getTranslations()
};
