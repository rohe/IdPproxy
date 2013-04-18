//jQuery plugin used to serilize a form to JSON
//Example JSON.stringify($('#firstpageForm').serializeJSON())
//$('#firstpageForm') => Get the form object
//$('#firstpageForm').serializeJSON() => The form object as Javascript JSON object.
//JSON.stringify($('#firstpageForm').serializeJSON()) => String representation of the form object
(
    function( $ ){
        $.fn.serializeJSON=function() {
            var json = {};
            jQuery.map($(this).serializeArray(), function(n, i){
                json[n['name']] = n['value'];
            });
            return json;
        };
    }
    )( jQuery );