<%inherit file="root.mako"/>
<script>
    function verifyResponse(msg) {
        if (msg.ok == "True") {
            services = "";
            first = true;
            for(i = 0; i < msg.services.length; i++)
            {
                if (!first) {
                    services += ", ";
                }else{
                    first = false;
                }
                services += msg.services[i];
            }
            if (msg.services.length > 0) {
                viewPopup("<b>The metadata is correct!</b><br /><i>You have configured the following services:" + services + "</i>", "OK")
            } else {
                viewPopup("<b>Fails to find any configured social services.</b><br /><i>" +
                        "Your metadata file is correct, but you are missing the mdattr:EntityAttributes element" +
                        " or have it on the wrong place in the xml.<br />" +
                        "Note, when you generate the social service element you must match the entity id with the entity id for your SP!<br >" +
                        "Please <a href='#' onclick='showExampleMetadata()'>view the example</a></i>", "OK");
            }
        } else {
            viewPopup("<b>Your metadata file is incorrect!</b><br /><i>" +
                    "First verify that your metadata file is correct without the social services extension.<br />" +
                    "When your metadata file is correct, please <a href='#' onclick='showExampleMetadata()'>view the example</a> " +
                    "to add the social services to your metadata file correct.</i>", 'OK');
        }
    }
</script>
<h2>&nbsp;&nbsp;&nbsp;&nbsp;- Verification</h2>
<p class="description">
    Copy your metadata XML to the textarea below and click on the button verify.
    View the example <a href="#" onclick="showExampleMetadata()">metadata file</a> to get a hint how the XML should be
    constructed.
</p>
<form id="xmlForm" action="${action}" class="big">
    <textarea id="xml" name="xml" rows="30" ></textarea>
    <input type="button" onclick="submitForm('xmlForm', function(msg){verifyResponse(msg);}, 'The metadata validation is currently not working.', 'Close')" value="Verify" />
</form>
<br />
<a href="${home}">Click here to perform a new configuration.</a>
