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