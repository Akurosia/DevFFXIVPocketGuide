(function () {
    'use strict';

    function normalizePath(pathname) {
        var path = pathname || '/';
        try { path = decodeURI(path); } catch (error) {}
        path = path.replace(/\/index\.html$/i, '/');
        if (path.length > 1) path = path.replace(/\/+$/, '');
        return path || '/';
    }

    function getLanguage() {
        var value = window.localStorage.getItem('translation-language') || navigator.language || 'en-US';
        var supported = { en: 'en-US', de: 'de-DE', fr: 'fr-FR', ja: 'ja-JP' };
        return supported[String(value).toLowerCase().slice(0, 2)] || 'en-US';
    }

    function sourceBase(source) {
        var marker = '/assets/generated/navigation.html';
        var index = source.indexOf(marker);
        return index >= 0 ? source.slice(0, index) : '';
    }

    function applyDictionary(root, dictionary) {
        root.querySelectorAll('[data-translate]').forEach(function (element) {
            var key = element.getAttribute('data-translate');
            if (Object.prototype.hasOwnProperty.call(dictionary, key) && dictionary[key] !== '') {
                element.innerHTML = dictionary[key];
            }
        });
    }

    async function translateNavigation(sidebar, source) {
        var language = getLanguage();
        var base = sourceBase(source);
        var paths = ['/assets/translations/navbar'];

        sidebar.querySelectorAll('[data-extra-translate]').forEach(function (element) {
            var path = element.getAttribute('data-extra-translate');
            if (path && paths.indexOf(path) === -1) paths.push(path);
        });

        var dictionaries = await Promise.all(paths.map(async function (path) {
            try {
                var response = await fetch(base + path + '/' + language + '.json', { credentials: 'same-origin' });
                if (!response.ok) return {};
                return await response.json();
            } catch (error) {
                console.warn('Navigation translation failed:', path, error);
                return {};
            }
        }));

        var merged = {};
        dictionaries.forEach(function (dictionary) { Object.assign(merged, dictionary); });
        applyDictionary(sidebar, merged);
    }

    function setToggleState(toggle, expanded) {
        if (!toggle) return;
        toggle.setAttribute('aria-expanded', String(expanded));
        var icon = toggle.querySelector('.sidebar__toggle-icon');
        if (icon) icon.textContent = expanded ? '▼' : '▶';
        var targetId = toggle.getAttribute('aria-controls');
        if (!targetId) return;
        var target = document.getElementById(targetId);
        if (target) target.style.display = expanded ? 'block' : 'none';
    }

    function openAncestorMenus(sidebar, activeLink) {
        var parent = activeLink.parentElement;
        while (parent && parent !== sidebar) {
            if (parent.tagName === 'UL' && parent.id) {
                var controller = Array.prototype.find.call(
                    sidebar.querySelectorAll('[aria-controls]'),
                    function (candidate) { return candidate.getAttribute('aria-controls') === parent.id; }
                );
                setToggleState(controller, true);
            }
            parent = parent.parentElement;
        }
    }

    function markCurrentNavigation(sidebar) {
        var currentPath = normalizePath(window.location.pathname);
        var links = sidebar.querySelectorAll('.sidebar__menu a[href]');
        links.forEach(function (link) {
            var linkUrl;
            try { linkUrl = new URL(link.getAttribute('href'), window.location.href); }
            catch (error) { return; }
            if (linkUrl.origin !== window.location.origin) return;
            if (normalizePath(linkUrl.pathname) !== currentPath) return;
            link.classList.add('active', 'is-active');
            link.setAttribute('aria-current', 'page');
            openAncestorMenus(sidebar, link);
        });
    }

    function loadNavigation() {
        var sidebar = document.querySelector('[data-sidebar-navigation]');
        if (!sidebar) return;
        var host = sidebar.querySelector('[data-sidebar-source]');
        if (!host) return;
        var source = host.getAttribute('data-sidebar-source');

        fetch(source, { credentials: 'same-origin' })
            .then(function (response) {
                if (!response.ok) throw new Error('Navigation request failed: ' + response.status);
                return response.text();
            })
            .then(async function (html) {
                host.innerHTML = html;
                markCurrentNavigation(sidebar);
                await translateNavigation(sidebar, source);

                if (typeof window.executeHandelingLanguages === 'function') {
                    window.executeHandelingLanguages();
                }
                document.dispatchEvent(new CustomEvent('pocketguide:navigation-ready'));
            })
            .catch(function () {
                host.innerHTML = '<p class="sidebar__load-error">Navigation could not be loaded. <a href="/">Return home</a>.</p>';
            });

        // Language switches happen after the fragment was injected. Translate the
        // fragment explicitly instead of depending on the page's initial DOM scan.
        window.addEventListener('ffxiv-pocket-guide:translations-updated', function () {
            translateNavigation(sidebar, source);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadNavigation, { once: true });
    } else {
        loadNavigation();
    }
})();
