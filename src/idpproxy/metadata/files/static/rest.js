/*
This file contains all REST-calls performed.
 */

/**
 * General method that submits a form to a REST service instead of a web page.
 * @param formId Id for the form.
 * @param callback A callback function that will be called with the return json message.
 * @param errorMessage A error to be presented when the call is not successfull.
 * @param buttonText Text for the button.
 */
function submitForm(formId, callback, errorMessage, buttonText) {
    tmpForm=$('#'+formId).serializeJSON()
    url = $('#'+formId).attr('action')
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(tmpForm), //Serialize the form to an JSON string
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        //beforeSend: function (xhr) { xhr.setRequestHeader('Accept-Language', trans.lang) }, //Use to set language
        success: function(msg){
            callback(msg)
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            viewPopup(errorMessage, buttonText)
        }
    });
}