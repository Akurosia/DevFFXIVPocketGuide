// =============================================================================

    // APP JS

    // Authored by:
        // - Josh Beveridge

// =============================================================================

function openFullscreen(imgElement) {
    const overlay = document.getElementById("fullscreenOverlay");
    const fullscreenImg = document.getElementById("fullscreenImg");

    fullscreenImg.src = imgElement.src; // Set the clicked image as fullscreen image
    overlay.style.display = "flex"; // Show the overlay
}

function closeFullscreen() {
    document.getElementById("fullscreenOverlay").style.display = "none";
}

function debounce(func, wait) {
    let timeoutId;

    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), wait);
    };
}

function handleExpansionAssetError(expansion) {
    if (!expansion) {
        return;
    }

    window.disabledExpansions = window.disabledExpansions || {};
    var disabledExpansions = window.disabledExpansions;
    disabledExpansions[expansion] = true;

    document.querySelectorAll("[data-expansion='" + expansion + "']").forEach((element) => {
        element.style.display = "none";
    });

    document.querySelectorAll(".expansion-toggle[data-expansion='" + expansion + "']").forEach((button) => {
        button.classList.add("inactive");
        button.style.display = "none";
    });

    if (typeof window.runGuideFilter === "function") {
        window.runGuideFilter();
    }
}

function scrollToElement(element) {
    var container = $('html, body');

    $("[class*='guide__accordion-trigger']").removeClass("active");
    $("[class*='guide__accordion-content']").removeClass("active");

    // Activate all parent accordions
    element.parents("[class*='guide__accordion-content']").each(function () {
        $(this).addClass("active");
        $(this).prev("[class*='guide__accordion-trigger']").addClass("active");
    });

    // Activate target element itself if necessary
    element.addClass("active");
    element.next("[class*='guide__accordion-content']").addClass("active");

    // Scroll to target
    var offSet = element.offset().top;
    container.animate({
        scrollTop: offSet
    }, 'slow');
}

(function($) {

    $(document).ready(function() {
        $(document).on('click', '.guide__attack-image-item img', function() {
            openFullscreen(this);
        });

        const links = document.querySelectorAll('.preview-link');
        const preview = document.getElementById('mapimagepreview');
        const filterableListSelector = ".index .index__list, .index .index__list_quests, .index .index__list_achivments, .index_attack .index__list_attack, .index_debuff .index__list_debuff, .index_eureka .index__list_eureka, .index_bozja .index__list_bozja, .index_trait .index__list_trait, .index_leve .index__list_leve, .index_quest .index__list_quest";
        const $guideFilter = $("#guideFilter");
        const $indexNullState = $(".index-null-state");
        const $filterableLists = $(filterableListSelector);
        const dividerCache = {};
        let currentTimeout;

        links.forEach(link => {
            const size = Number(link.getAttribute('data-size'));
            const scale = 300 / size;
            link.addEventListener('mouseenter', (e) => {
                clearTimeout(currentTimeout); // Verhindert Race Condition
                const url = link.getAttribute('src');
                preview.innerHTML = `<img style="height:${size}px;width:${size}px;" src="${url}" alt="Preview">`;
                preview.style.display = 'block';
                preview.style.width = `${size}px`;
                preview.style.height = `${size}px`;
                preview.style.top = `${e.pageY - size / 2}px`;
                preview.style.left = `${e.pageX - link.getAttribute('data-size') * scale}px`;

                requestAnimationFrame(() => {
                    preview.style.opacity = 1;
                });
            });

            link.addEventListener('mousemove', (e) => {
                preview.style.top = `${e.pageY - size / 2}px`;
                preview.style.left = `${e.pageX - size * scale}px`;
            });

            link.addEventListener('mouseleave', () => {
                preview.style.opacity = 0;
                currentTimeout = setTimeout(() => {
                    preview.style.display = 'none';
                    preview.innerHTML = '';
                }, 200); // Gleiche Zeit wie die Animation
            });
        });

        $(document).on('click', '.sidebar__menu li ', function () {
            arrow = $(this).children('span').children('span')[0]
            if (arrow.textContent == "▶") {
                arrow.textContent = "▼";
            } else {
                arrow.textContent = "▶";
            }
            $(this).next('ul').toggle();
        })

        var $root = $('html, body');

        // Disabled Button Clicks ==============================================
        $('.disabled').on('click', function(e){
            e.preventDefault();
            e.stopPropagation();
            return false;
        });

        // Input Focus =========================================================
        if($(".search").length) {
            $("#guideFilter").focus();
        }

        // Menu Trigger ========================================================
        $(".sidebar__trigger").on("click", function(e) {

            if ($(".sidebar").hasClass("active")) {
                $("body").css("overflow-y", "visible");
            }
            else {
                $("body").css("overflow-y", "hidden");
            }

            $(this).toggleClass("active");
            $(".site-grid__sidebar-overlay").toggleClass("active");
            $(".sidebar").toggleClass("active");

        });

        $(".site-grid__sidebar-overlay").on("click", function(e) {
            if ($(".sidebar").hasClass("active")) {
                $(".sidebar__trigger").removeClass("active");
                $(this).removeClass("active");
                $(".sidebar").removeClass("active");
                $("body").css("overflow-y", "visible");
            }
        });

        // FFXIV Issue Link ====================================================
        $("#issueSubmissionLink").on("click", function(e) {

            e.preventDefault();

            var dataObject = $('#'+$(this).data('id'));
            var container = $('html,body');
            var offSet = container.scrollTop() + dataObject.offset().top;

            container.animate({
                scrollTop : offSet
            }, 'slow');

        });

        // Keep track of disabled expansions
        var disabledExpansions = window.disabledExpansions || {};
        window.disabledExpansions = disabledExpansions;

        function getDividerForExpansion(expansion) {
            if (!expansion) {
                return $();
            }

            if (!dividerCache[expansion]) {
                dividerCache[expansion] = $(".index-divider[data-expansion='" + expansion + "']");
            }

            return dividerCache[expansion];
        }

        function getCachedTerms($summary) {
            var cachedTerms = $summary.data("searchTermsCache");
            if (!cachedTerms) {
                cachedTerms = String($summary.find(".index-item__title").data("terms") || "").toLowerCase();
                $summary.data("searchTermsCache", cachedTerms);
            }
            return cachedTerms;
        }

        function runGuideFilter() {
            var input = String($guideFilter.val() || "").toLowerCase().trim();
            var terms = input ? input.split(/\s+/).filter(Boolean) : [];
            var visibleSummaryCount = 0;

            $filterableLists.each(function () {
                var $list = $(this);
                var listExpansion = $list.attr("data-expansion");
                var hasVisibleSummary = false;

                $list.find(".summary").each(function () {
                    var $summary = $(this);
                    var itemExpansion = $summary.data("expansion") || listExpansion;
                    var isDisabledByExpansion = !!disabledExpansions[itemExpansion];
                    var headingText = getCachedTerms($summary);
                    var show = !isDisabledByExpansion;

                    if (show && terms.length > 0) {
                        show = terms.every(function (term) {
                            return headingText.indexOf(term) !== -1;
                        });
                    }

                    $summary.toggle(show).toggleClass("show", show);

                    if (show) {
                        hasVisibleSummary = true;
                        visibleSummaryCount += 1;
                    }
                });

                $list.toggle(hasVisibleSummary);
                if (listExpansion) {
                    getDividerForExpansion(listExpansion).toggle(hasVisibleSummary);
                }
            });

            $("#shadowbringersTitle, #shadowbringersContent").toggle(!input);
            $indexNullState.toggle(visibleSummaryCount === 0);
        }

        window.runGuideFilter = runGuideFilter;

        $(document).on("click", ".expansion-toggle", function () {
            var $btn = $(this);
            var expansion = $btn.data("expansion");

            $btn.toggleClass("inactive");

            if ($btn.hasClass("inactive")) {
                disabledExpansions[expansion] = true;
            } else {
                delete disabledExpansions[expansion];
            }

            runGuideFilter();
        });

        $guideFilter.on("keydown", function (e) {
            if (e.key !== "Enter") {
                return;
            }

            if ($(".site-grid__sidebar").hasClass("active")) {
                $(".sidebar__trigger").removeClass("active");
                $(".site-grid__sidebar-overlay").removeClass("active");
                $(".site-grid__sidebar").removeClass("active");
            }

            $('html,body').scrollTop($('body').position().top);
            e.preventDefault();
            document.activeElement.blur();
            return false;
        });

        $guideFilter.on("input", debounce(runGuideFilter, 120));



        // FFXIV Guide Accordions only arrow ==============================================
        $("[class*='Dropdown material-icons']").on("click", function(e) {
            $(this).parents("[class*='guide__accordion-trigger']").toggleClass("active");
            $(this).parents("[class*='guide__accordion-trigger']").next("[class*='guide__accordion-content']").toggleClass("active");
            e.preventDefault();
        });

        // FFXIV Guide Accordions rest of the element ==============================================
        $("[class*='guide__accordion-trigger']").on("click", function(e) {
            const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);

            if (e.shiftKey || e.ctrlKey || isMobile) {
                $(this).toggleClass("active");
                $(this).next("[class*='guide__accordion-content']").toggleClass("active");
                e.preventDefault();
            }
        });

        $(".guide__attack-image-item").each(function () {
            $(this).find("img").attr("onclick", "openFullscreen(this)");
        });

        // Guide Only display final skills ====================================================
        $("#onlyfinalskills").on("click", function(e) {
            let state = $("#onlyfinalskills").is(':checked')
            $(".summary").each(function(e) {
                var $summary = $(this);
                var headingText  =  getCachedTerms($summary);
                if (headingText.includes("finalcast:63")){
                    if (state) {
                        $summary.hide()
                    } else {
                        $summary.show()
                    }
                }
            });
        });

        // FFXIV Guide Menu ====================================================
        $('.guide-metadata__menu-link').on("click", function (e) {
            e.preventDefault();
            // get the correct element
            var targetId = $(this).data("id");
            if (targetId === undefined) {
                targetId = $(this)[0].id;
            }
            var dataObject = $('#' + targetId);

            var newHash = '';
            if (dataObject.length) {
                if (targetId.includes('-attack-') || targetId.includes('-debuff-') || targetId.includes('map-') || targetId.includes('fate-')) {
                    // do nothing
                } else {
                    scrollToElement(dataObject);
                }
                newHash = '#' + targetId;
            }
            history.pushState(null, null, newHash);
        });

        // Check URL on page load /must be executed last, otherwise page does not function properly
        if (window.location.hash) {
            var hashParts = window.location.hash.substring(1).split('/');
            $.each(hashParts, function (_, part) {
                var target = $('#' + part);
                if (target.length) {
                    scrollToElement(target);
                }
            });
        }

    });

})(jQuery);



// Modernization repair: keep the original mobile sidebar behavior, but make it robust
// even if the trigger/overlay are injected or previous handlers fail.
(function () {
    function setSidebarState(open) {
        var body = document.body;
        var sidebar = document.querySelector('.sidebar');
        var trigger = document.querySelector('.sidebar__trigger');
        var overlay = document.querySelector('.site-grid__sidebar-overlay');

        if (sidebar) sidebar.classList.toggle('active', open);
        if (trigger) trigger.classList.toggle('active', open);
        if (overlay) overlay.classList.toggle('active', open);
        if (body) {
            body.classList.toggle('sidebar-active', open);
            body.classList.toggle('xiv-sidebar-open', open);
            body.style.overflowY = open ? 'hidden' : 'visible';
        }
    }

    document.addEventListener('click', function (event) {
        var trigger = event.target.closest && event.target.closest('.sidebar__trigger');
        var overlay = event.target.closest && event.target.closest('.site-grid__sidebar-overlay');

        if (trigger) {
            event.preventDefault();
            event.stopPropagation();
            var sidebar = document.querySelector('.sidebar');
            setSidebarState(!(sidebar && sidebar.classList.contains('active')));
            return;
        }

        if (overlay) {
            event.preventDefault();
            setSidebarState(false);
        }
    }, true);

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') setSidebarState(false);
    });
})();
