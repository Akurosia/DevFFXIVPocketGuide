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
        let currentTimeout;

        links.forEach(link => {
            const scale = 300/link.getAttribute('data-size');
            link.addEventListener('mouseenter', (e) => {
                clearTimeout(currentTimeout); // Verhindert Race Condition
                const url = link.getAttribute('src');
                const size = link.getAttribute('data-size');
                preview.innerHTML = `<img style="height:${size}px;width:${size}px;" src="${url}" alt="Preview">`;
                preview.style.display = 'block';
                const rect = link.getBoundingClientRect();
                preview.style.width = `${size}px`;
                preview.style.height = `${size}px`;
                preview.style.top = `${e.pageY - link.getAttribute('data-size')/2}px`;
                preview.style.left = `${e.pageX - link.getAttribute('data-size') * scale}px`;

                requestAnimationFrame(() => {
                    preview.style.opacity = 1;
                });
            });

            link.addEventListener('mousemove', (e) => {
                preview.style.top = `${e.pageY - link.getAttribute('data-size')/2}px`;
                preview.style.left = `${e.pageX - link.getAttribute('data-size') * scale}px`;
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

        // FFXIV Guide Filters =================================================
        $("#guideFilter").keyup(function(e) {

            var input = this.value.toLowerCase().trim()
            var terms = input.split(" ");
            $(".index .index__list, \
              .index .index__list_quests, \
              .index .index__list_achivments, \
              .index_attack .index__list_attack, \
              .index_debuff .index__list_debuff, \
              .index_eureka .index__list_eureka, \
              .index_bozja .index__list_bozja, \
              .index_trait .index__list_trait, \
              .index_leve .index__list_leve, \
              .index_quest .index__list_quest").each(function(e) {

                $(this).find(".summary").each(function(e) {

                    var headingText  =  $(this).find(".index-item__title").data("terms").toLowerCase();

                    /*
                    This is currently setup for "OR" or "ANY" searching.
                    If any phrase matches the item will be shown. You can switch
                    this to "AND" or "ALL" searching by doing the following:
                    1. change the declaration of show to true by default.
                    2. negate the conditional in the forEach example:
                        if ( !(headingText.indexOf(term.trim()) >= 0) ) {
                    3. change the assignment inside the conditional to false
                    */

                    var show = true;

                    terms.forEach(function(term){
                        if ( !(headingText.indexOf(term.trim()) >= 0) ) {
                            show = false;
                        }
                    });

                    if (show) {
                        $(this).show();
                        $(this).addClass("show");
                    }
                    else {
                        $(this).hide();
                        $(this).removeClass("show");
                    }

                });

                if($(this).find(".summary.show").length) {
                    var expansion = $(this).attr("data-expansion");
                    $(this).show();
                    $(".index-divider").each(function(e) {
                        if ($(this).attr("data-expansion") == expansion) {
                            $(this).show();
                        }
                    });
                }
                else {
                    var expansion = $(this).attr("data-expansion");
                    $(this).hide();
                    $(".index-divider").each(function(e) {
                        if ($(this).attr("data-expansion") == expansion) {
                            $(this).hide();
                        }
                    });
                }

            });

            if(terms == "") {
                $("#shadowbringersTitle").show();
                $("#shadowbringersContent").show();
            }
            else {
                $("#shadowbringersTitle").hide();
                $("#shadowbringersContent").hide();
            }

            if($(".summary.show").length) {
                $(".index-null-state").hide();
            }
            else {
                $(".index-null-state").show();
            }

            // Prevents the user from submitting the form with the enter key.
            $('#guideFilter').on('keyup keypress', function(e) {
                var keyCode = e.keyCode || e.which;
                if (keyCode === 13) {

                    if ($(".site-grid__sidebar").hasClass("active")) {
                        $(".sidebar__trigger").removeClass("active");
                        $(".site-grid__sidebar-overlay").removeClass("active");
                        $(".site-grid__sidebar").removeClass("active");
                    }

                    var top = $('body').position().top;
                    $('html,body').scrollTop(top);

                    e.preventDefault();

                    document.activeElement.blur();

                    return false;

                }
            });

            e.preventDefault();

        });

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
                var headingText  =  $(this).find(".index-item__title").data("terms").toLowerCase();
                if (headingText.includes("finalcast:63")){
                    if (state) {
                        $(this).hide()
                    } else {
                        $(this).show()
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
                if (targetId.includes('-attack-') || targetId.includes('-debuff-') || targetId.includes('-map-') || targetId.includes('-fate-')) {
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

