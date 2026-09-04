(function () {
    var root = document.querySelector('.enemy-coverage');
    if (!root) return;

    var loading = document.getElementById('enemyCoverageLoading');
    var error = document.getElementById('enemyCoverageError');
    var content = document.getElementById('enemyCoverageContent');
    var search = document.getElementById('enemyCoverageSearch');
    var status = document.getElementById('enemyCoverageStatus');
    var pageBody = document.getElementById('enemyCoveragePages');
    var missingBody = document.getElementById('enemyCoverageMissing');
    var missingCount = document.getElementById('enemyCoverageMissingCount');
    var baseurl = (root.getAttribute('data-baseurl') || '').replace(/\/$/, '');
    var report;

    function label(id) {
        var element = document.getElementById(id);
        return element ? element.textContent : '';
    }

    function escapeHtml(value) {
        var element = document.createElement('div');
        element.textContent = String(value == null ? '' : value);
        return element.innerHTML;
    }

    function card(label, value, detail) {
        return '<article class="enemy-coverage__card"><span>' + escapeHtml(label) +
            '</span><strong>' + escapeHtml(value) + '</strong><small>' + escapeHtml(detail) + '</small></article>';
    }

    function siteUrl(path) {
        if (!path || /^(?:[a-z]+:)?\/\//i.test(path) || path.charAt(0) === '#') return path;
        return baseurl + (path.charAt(0) === '/' ? path : '/' + path);
    }

    function renderSummary() {
        var summary = report.summary;
        document.getElementById('enemyCoverageCards').innerHTML = [
            card(label('enemyCoverageLabelEntry'), summary.enemy_entry_coverage_percent + '%', summary.enemy_entries_covered + ' / ' + summary.enemy_entries_total),
            card(label('enemyCoverageLabelUnique'), summary.unique_enemy_id_coverage_percent + '%', summary.unique_enemy_ids_covered + ' / ' + summary.unique_enemy_ids),
            card(label('enemyCoverageLabelImages'), summary.matching_webp_images, label('enemyCoverageLabelOriginal')),
            card(label('enemyCoverageLabelWithoutId'), summary.enemy_entries_without_id, label('enemyCoverageLabelCannotMatch'))
        ].join('');
    }

    function render() {
        var term = search.value.toLowerCase().trim();
        var selectedStatus = status.value;
        var pages = report.pages.filter(function (page) {
            var complete = page.enemy_entries > 0 && page.entries_fully_covered === page.enemy_entries;
            var statusMatches = selectedStatus === 'all' ||
                (selectedStatus === 'complete' && complete) ||
                (selectedStatus === 'missing' && !complete);
            var textMatches = !term || (page.page_title + ' ' + page.post).toLowerCase().includes(term);
            return statusMatches && textMatches;
        });

        pageBody.innerHTML = pages.map(function (page) {
            return '<tr><td><a href="' + escapeHtml(siteUrl(page.url)) + '">' + escapeHtml(page.page_title) +
                '</a><small>' + escapeHtml(page.post) + '</small></td><td>' + page.entries_covered + ' / ' + page.enemy_entries +
                '</td><td>' + page.entries_without_id + '</td><td><progress max="100" value="' + page.coverage_percent +
                '"></progress><span>' + page.coverage_percent.toFixed(2) + '%</span></td></tr>';
        }).join('');

        var missing = report.uncovered_entries.filter(function (entry) {
            return !term || (entry.name + ' ' + entry.page_title + ' ' + entry.post + ' ' + entry.enemy_ids.join(' ')).toLowerCase().includes(term);
        });
        var shown = missing.slice(0, 500);
        missingCount.textContent = label('enemyCoverageLabelShowing')
            .replace('{shown}', shown.length)
            .replace('{total}', missing.length)
            .replace('{more}', missing.length > shown.length ? label('enemyCoverageLabelRefine') : '');
        missingBody.innerHTML = shown.map(function (entry) {
            return '<tr><td>' + escapeHtml(entry.name) + '</td><td>' + escapeHtml(entry.enemy_ids.join(', ')) +
                '</td><td>' + escapeHtml(entry.section) + '</td><td><a href="' + escapeHtml(siteUrl(entry.url)) + '">' +
                escapeHtml(entry.page_title) + '</a></td></tr>';
        }).join('');
    }

    fetch(root.getAttribute('data-report-url'))
        .then(function (response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
        })
        .then(function (data) {
            report = data;
            loading.hidden = true;
            content.hidden = false;
            renderSummary();
            render();
        })
        .catch(function (reason) {
            loading.hidden = true;
            error.hidden = false;
            error.textContent = label('enemyCoverageLabelLoadError') + ': ' + reason.message;
        });

    search.addEventListener('input', render);
    status.addEventListener('change', render);
    window.addEventListener('ffxiv-pocket-guide:translations-updated', function () {
        if (report) {
            renderSummary();
            render();
        }
    });
}());
