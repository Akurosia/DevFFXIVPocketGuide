// =============================================================================

    // APP JS

    // Authored by:
        // - Josh Beveridge

// =============================================================================

(function($) {

    $(document).ready(function() {

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

        // FFXIV Guide Menu ====================================================
        $('.guide-metadata__menu-link').on("click", function(e) {

            e.preventDefault();

            var dataObject = $('#'+$(this).data('id'));
            var container = $('html,body');

            $("[class*='guide__accordion-trigger']").removeClass("active");
            $("[class*='guide__accordion-content']").removeClass("active");

            $(dataObject).parents("[class*='guide__accordion-content']").prev("[class*='guide__accordion-trigger']").addClass("active");
            $(dataObject).parents("[class*='guide__accordion-content']").addClass("active");
            $(dataObject).addClass("active");
            $(dataObject).next("[class*='guide__accordion-content']").addClass("active");

            var offSet = dataObject.offset().top;

            container.animate({
                scrollTop : offSet
            }, 'slow');

        });

        // FFXIV Guide Menu Temp ===============================================
        $('.guide-metadata__menu-link--new').on("click", function(e) {

            e.preventDefault();

            var dataTrigger = $(this).attr("data-menu-trigger");
            var dataObject = $("[data-menu-target='"+dataTrigger+"']");
            var container = $('html,body');

            $("[class*='guide__accordion-trigger']").removeClass("active");
            $("[class*='guide__accordion-content']").removeClass("active");

            $(dataObject).parents("[class*='guide__accordion-content']").prev("[class*='guide__accordion-trigger']").addClass("active");
            $(dataObject).parents("[class*='guide__accordion-content']").addClass("active");
            $(dataObject).addClass("active");
            $(dataObject).next("[class*='guide__accordion-content']").addClass("active");

            var offSet = dataObject.offset().top;

            container.animate({
                scrollTop : offSet
            }, 'slow');

        });


        // FFXIV Guide Accordions ==============================================
        $("[class*='guide__accordion-trigger']").on("click", function(e) {
            $(this).toggleClass("active");
            $(this).next("[class*='guide__accordion-content']").toggleClass("active");
            e.preventDefault();
        });

        // Guide Image Zoom ====================================================
        //$(".guide__attack-image-item").on("click", function(e) {
        //    if($(this).hasClass("active")) {
        //        $(this).removeClass("active")
        //    }
        //    else {
        //        $(this).addClass("active")
        //    }
        //});
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



    });

})(jQuery);


function openFullscreen(imgElement) {
    const overlay = document.getElementById("fullscreenOverlay");
    const fullscreenImg = document.getElementById("fullscreenImg");

    fullscreenImg.src = imgElement.src; // Set the clicked image as fullscreen image
    overlay.style.display = "flex"; // Show the overlay
}

function closeFullscreen() {
    document.getElementById("fullscreenOverlay").style.display = "none";
}


const links = document.querySelectorAll('.preview-link');
const preview = document.getElementById('mapimagepreview');
let currentTimeout;

links.forEach(link => {
    link.addEventListener('mouseenter', (e) => {
        clearTimeout(currentTimeout); // Verhindert Race Condition
        const url = link.href;
        preview.innerHTML = `<img src="${url}" alt="Preview">`;
        preview.style.display = 'block';

        const rect = link.getBoundingClientRect();
        preview.style.top = `${window.scrollY + rect.top}px`;
        preview.style.left = `${window.scrollX + rect.left - preview.offsetWidth - 10}px`;

        requestAnimationFrame(() => {
            preview.style.opacity = 1;
        });
    });

    link.addEventListener('mouseleave', () => {
        preview.style.opacity = 0;
        currentTimeout = setTimeout(() => {
            preview.style.display = 'none';
            preview.innerHTML = '';
        }, 200); // Gleiche Zeit wie die Animation
    });
});
