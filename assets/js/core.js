// =============================================================================

    // CORE JS

    // Authored by:
        // - Josh Beveridge

// =============================================================================

    // *** This file is not to be edited on a per project basis. ***

// =============================================================================

(function($) {

    $(document).ready(function() {

        var $root = $('html, body');

        // User Agent Data Attributes ==========================================
        var ua = navigator.userAgent;
        ua = ua.toString();
        $('body').attr('id', ua);

        // Smooth Scrolling ====================================================
        $('a[href*="#"]:not([href="#"])').on('click',function(e) {
            var targetSelector = $(this).attr('href');
            var hashIndex = targetSelector.indexOf('#');

            if (hashIndex > -1) {
                targetSelector = targetSelector.substring(hashIndex);
            }

            var target = targetSelector.substring(1);
            var $target = target ? $(document.getElementById(decodeURIComponent(target))) : $();

            if (!$target.length) {
                return true;
            }

            e.preventDefault();

            $root.animate({
                scrollTop: $target.offset().top
            }, 500); // change the duration of your animation in ms

            return false;

         });

    });

})(jQuery);
