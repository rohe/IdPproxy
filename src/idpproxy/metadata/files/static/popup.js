function setupPopup() {
    paddingX = 40;
    paddingY = 40;
    $('#popupBackground').width($('html').width());
    marginLeft = ((($('#popupBackground').width()) / 2) - (($('#popup').width()) / 2));
    marginTop = (($('#popupBackground').height()) / 2) - (($('#popup').height())/2);
    $('#popup').css("margin-left",marginLeft+'px');
    $('#popup').css("margin-top",marginTop+'px');
    buttonLeft = ($('#popup').width() / 2) - ($('#popupClose').width() / 2) + parseInt($('#popup').css('padding-left'));
    //buttonTop = ($('#popup').height()) - ($('#popupClose').height()) + parseInt($('#popup').css('padding'));
    $('#popupClose').css('margin-left', buttonLeft+'px');
    //$('#popupClose').css("top",buttonTop+'px');
}

function closePopup() {
    $('#popup').hide();
    $('#popupBackground').hide();
}

function viewPopup(text, buttonText) {
    $('#popupClose').val(buttonText);
    $('#popupText').html(text);
    $('#popup').css('display','inline-block');
    setupPopup();
    $('#popupBackground').show();
}

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