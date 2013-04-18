/*
 * Contains functionality to present HTML popups.
 */

/**
 * Will cover the browser with a div so the user must close the popup before taking any actions.
 * Will position the popup in the middle of the browser window.
 */
function setupPopup() {
    paddingX = 40;
    paddingY = 40;
    $('#popupBackground').width($('html').width());
    marginLeft = ((($('#popupBackground').width()) / 2) - (($('#popup').width()) / 2));
    marginTop = (($('#popupBackground').height()) / 2) - (($('#popup').height())/2);
    $('#popup').css("margin-left",marginLeft+'px');
    $('#popup').css("margin-top",marginTop+'px');
    buttonLeft = ($('#popup').width() / 2) - ($('#popupClose').width() / 2) + parseInt($('#popup').css('padding-left'));
    $('#popupClose').css('margin-left', buttonLeft+'px');
}

/**
 * Will close the current popup.
 */
function closePopup() {
    $('#popup').hide();
    $('#popupBackground').hide();
}

/**
 * Will present a popup to the user.
 * @param text The text to show the user. This can actually contain any html.
 * @param buttonText Text for the button.
 */
function viewPopup(text, buttonText) {
    $('#popupClose').val(buttonText);
    $('#popupText').html(text);
    $('#popup').css('display','inline-block');
    setupPopup();
    $('#popupBackground').show();
}

/**
 * Will generate the html needed on a page to show the popup.
 */
function initPopup() {
    $('body').append("<div id='popupBackground'></div>");
    $('body').append("<div id='popup'>" +
        "<div id='popupText'>" +
        "</div><br /><br /><br />" +
        "<div id='popupClose'><input id='popupCloseButton' type='button' value='Close' onclick='closePopup();' /></div>" +
        "</div>");

    $(window).resize(function() {
        setupPopup();
    });
}

//Contains all code that must run when the pages is fully loaded.
$(document).ready(function() {
    initPopup();
});