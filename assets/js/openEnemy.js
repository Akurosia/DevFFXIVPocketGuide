function jumpToPosition() {
    if(window.location.hash) {
        const queryString = decodeURIComponent(window.location.hash.substring(1));
        const element = $('a[data-id]').filter(function () {
            return String($(this).data('id')) === queryString;
        });
        if (element.length) {
            element.trigger('click');
        }
    } else {
      // Fragment doesn't exist
    }
}
function myClick() {
  setTimeout( function(){}, 2000);
  setTimeout(jumpToPosition, 2000);
}

$(document).ready(myClick);
