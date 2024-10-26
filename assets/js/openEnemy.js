function jumpToPosition() {
    if(window.location.hash) {
        const queryString = window.location.hash.substring(1);
        element = $('a[data-id="'+queryString+'"]');
        element.click();
        console.log(queryString);
    } else {
      // Fragment doesn't exist
    }
}
function myClick() {
  setTimeout( function(){}, 2000);
  setTimeout( jumpToPosition(), 2000);
}

$(document).ready(myClick());
