<%inherit file="root.mako"/>

<%!
    def setupJavaScriptEntityIdArray(spList):
      """
      Creates a JSON list with a dictionary containing value and text.
      [{'value' : 'value1','text' : 'text1'},{'value' : 'valuen','text' : 'textn'}]
      The JSON list is created from a list of strings containing entityId's for sp's.
      :param spList: A list of entityId's.
      :return: A JSON list.
      """
      first = True
      entityIdArray = "["
      for entityId in spList:
        if not first:
            entityIdArray += ","
        entityIdArray += "{'value' : '" + entityId + "','text' : '" + entityId + "'}"
        first = False
      entityIdArray += "];"
      return entityIdArray
%>

<%!
    def createSelectOptions(list):
      """
      Creates option tags for a select tag.
      :param spList: A list of string.
      :return: A string with multiple option tags.
      """
      optionList = ""
      first = True
      for value in list:
        optionList += "<option value='" + value +"'"
        if first:
            optionList += " selected "
        optionList += ">" + value + "</option>"
        first = False
      return optionList
%>

<script>
    //Has the social service name as key and {"secret": "mysecret", "key": "mykey"} as value.
    var secretHash = {}
    //Has the entity id as key and true or false as value.
    //True = the entity id is from the list.
    //False = the entity id is written by the user.
    var spHash = {}

    //Verifies if a hash is empty.
    function isEmpty(obj) {
        for (name in obj) {
            return false;
        }
        return true;
    }


    //Verifies if the form is ready to be submitted.
    function verifySubmit() {
        if ((isEmpty(secretHash)) || (isEmpty(spHash))) {
            $('#socialError').show();
            $('#spError').show();
            $('#submit').attr('disabled','disabled');
        } else {
            $('#socialError').hide();
            $('#spError').hide();
            $('#submit').removeAttr('disabled');
        }
    }

    //Will empty all options from the select with the given id.
    //Then fill it again with all options in dataArr that have a text that matches the string str.
    //The data array is constructed in python and represents a JSON list
    // [{'value' : 'value1','text' : 'text1'},{'value' : 'valuen','text' : 'textn'}]
    function filterOptions(str, id)
    {
        var dataArr = ${setupJavaScriptEntityIdArray(spKeyList)}
                $("#" + id + " option").remove();
        $.each(dataArr,
                function(i) {
                    if (dataArr[i]['text'].match('.*'+str+'.*') != null) {
                        $("#"+id).append($("<option></option>")
                                .attr("value",dataArr[i]['value'])
                                .text(dataArr[i]['text']));
                    }
                }
        )
        $("#sp option:first").attr('selected','selected');
    }

    //Sort function, used for sorting option elements in a select element.
    function NASort(a, b) {
        if (a.innerHTML == 'NA') {
            return 1;
        }
        else if (b.innerHTML == 'NA') {
            return -1;
        }
        return (a.innerHTML > b.innerHTML) ? 1 : -1;
    };

    //Contains all code that must run when the pages is fully loaded.
    $(document).ready(function() {

        //Handles the action to add a new entity id for a sp given by the user.
        $('#btn-add-sp-manual').click(function(){
            value = $('#manualSp').val().trim();
            if (value.length > 0) {
                $('#sp_to').append("<option value='"+value+"'>"+value+"</option>");
                spHash[value] = false;
                $('#manualSp').val('');
                $('#sp_to option').sort(NASort).appendTo('#sp_to');
            }
            verifySubmit();
        });

        //Handles the action to add a entity id for a sp from the list.
        $('#btn-add-sp').click(function(){
            $('#sp_from option:selected').each( function() {
                $('#sp_to').append("<option value='"+$(this).val()+"'>"+$(this).text()+"</option>");
                spHash[$(this).val()] = true;
                $(this).remove();
            });
            $('#sp_to option').sort(NASort).appendTo('#sp_to');
            verifySubmit();
        });

        //Handles the action to remove a entity id for a sp.
        $('#btn-remove-sp').click(function(){
            $('#sp_to option:selected').each( function() {
                sort = false;
                if (spHash[$(this).val()]) {
                    $('#sp_from').append("<option value='"+$(this).val()+"'>"+$(this).text()+"</option>");
                    sort = true;
                }
                try{
                    delete spHash[$(this).val()];
                } catch(e){}
                $(this).remove();
            });
            if (sort)
            {
                $('#sp_from option').sort(NASort).appendTo('#sp_from');
            }
            verifySubmit();
        });

        //Handles the action to add a service with a given secret and key.
        $('#btn-add-service').click(function(){
            $('#keysecretError').hide();
            if (($('#secrettmp').val().trim().length == 0) || ($('#keytmp').val().trim().length == 0)) {
                $('#keysecretError').show();
            } else {
                $('#service_from option:selected').each( function() {
                    $('#service_to').append("<option value='"+$(this).val()+"'>"+$(this).text()+"</option>");
                    secrets = {"secret": $('#secrettmp').val(), "key": $('#keytmp').val()};
                    secretHash[$(this).val()] = secrets;
                    $(this).remove();
                    $('#secrettmp').val('');
                    $('#keytmp').val('');
                });
                $('#service_to option').sort(NASort).appendTo('#service_to');
            }
            verifySubmit();
        });

        //Handles the action to remove a service.
        $('#btn-remove-service').click(function(){
            $(".hidden").css("visibility", "hidden");
            $('#service_to option:selected').each( function() {
                $('#service_from').append("<option value='"+$(this).val()+"'>"+$(this).text()+"</option>");
                try{
                    delete secretHash[$(this).val()];
                } catch(e){}
                $(this).remove();
            });
            $('#service_from option').sort(NASort).appendTo('#service_from');
            verifySubmit();
        });

        //Will show the key and secret for a added service.
        $('#service_to').click(function(){
            $(".hidden").css("visibility", "hidden");
            $('#service_to option:selected').each( function() {
                secrets = secretHash[$(this).val()];
                $('#secret').val(secrets["secret"]);
                $('#key').val(secrets["key"]);
                $(".hidden").css("visibility", "visible");
            });
        });

    });

    //Action to be performed before the form is submitted.
    //Will add a list of entity id's and socical services to be encrypted and added to an partial xml.
    //Before the form is submitted is the input fields cleaned, to prevent the key(s) and secret(s) to be exposed
    //by using the back button.
    function setupInputFields() {
        spList = [];
        for(var key in spHash) {
            spList.push(key)
        }
        $('form').append("<input type='hidden' id='entityId' name='entityId' value='" + JSON.stringify(spList) + "' />");
        $('form').append("<input type='hidden' id='secret' name='secret' value='" + JSON.stringify(secretHash) + "' />");
        $("select option").remove();
        $('#secrettmp').val('');
        $('#keytmp').val('');
        $('html').remove(); //Delete all! :)
        spHash = {}
        secretHash = {}
    }
</script>

<p class="description">
    You can use this tool if you want to include social service credentials in your metadata file.
    All information will be encrypted with the public key for Social2Saml and included in an EntityAttributes XML element.
    First you must add the entity id for all service providers that can use the same key(s) and secret(s)
    for the social services. You can either use the list or add them manually.
    Then you have to add key and secret for each social service you which to use for your service provider(s).
    Follow the guide at <a href="https://portal.nordu.net/display/SWAMID/Social2SAML">SWAMID</a> to retrieve secret and key for the social service you which to configure.<br />
</p>

    <table style="width:100%">
        <tr>
            <td colspan="3">
                Add Service Provider(s)
            </td>
        </tr>
        <tr>
            <td style="width:45%">
                <select name='sp_from' id="sp_from" size="10" multiple="multiple">
                    ${createSelectOptions(spKeyList)}
                </select>
            </td>
            <td style="width:10%;text-align: center; vertical-align: middle">
                <input type="button" id="btn-add-sp" value="Add &raquo;" />
                <br>
                <input type="button" id="btn-remove-sp" value="&laquo; Remove" />
            </td>
            <td  style="width:45%">
                <select name='sp_to' id="sp_to" size="10" multiple="multiple">
                </select>
            </td>
        </tr>
        <tr>
            <td style="width:45%">
                <div class="label">Filter:</div><input type='text' class='inputValue' onkeyup="filterOptions(this.value, 'sp_from')" name='filter' id='filter' value=''/>
            </td>
            <td style="width:10%;text-align: center; vertical-align: middle">
                &nbsp;
            </td>
            <td  style="width:45%">
                <div class="label">EntityId:</div><input type='text' class='inputValueSmall' name='manualSp' id='manualSp' value=''/>
                <input type="button" id="btn-add-sp-manual" value="Add" />
            </td>
        </tr>
    </table>

    <br>
    <table style="width:100%">
        <tr>
            <td colspan="3">
                Add key(s) and secret(s)
            </td>
        </tr>
        <tr>
            <td style="width:45%">
                <select name='service_from' id="service_from" size="5">
                    ${createSelectOptions(sociallist)}
                </select>
            </td>
            <td style="width:10%;text-align: center; vertical-align: middle">
                <input type="button" id="btn-add-service" value="Add &raquo;" />
                <br>
                <input type="button" id="btn-remove-service" value="&laquo; Remove" />
            </td>
            <td  style="width:45%">
                <select name='service_to' id="service_to" size="5">
                </select>
            </td>
        </tr>
        <tr>
            <td style="width:45%; vertical-align: top;">
                <div class="label">Secret:</div><input type='text' class='inputValue' name='secrettmp' id='secrettmp' value=''/>
                <div class="label">Key:</div><input type='text' class='inputValue' name='keytmp' id='keytmp' value=''/>
                <div id="keysecretError" class="labelError">You must have a value for both key and secret!</div>
            </td>
            <td style="width:10%;text-align: center; vertical-align: middle">
                &nbsp;
            </td>
            <td  style="width:45%; vertical-align: top;">
                <div class="label hidden">Secret:</div><input type='text' readonly="readonly" class='inputView hidden' name='secret' id='secret' value=''/>
                <div class="label hidden">Key:</div><input type='text' readonly="readonly" class='inputView hidden' name='key' id='key' value=''/>
            </td>
        </tr>
    </table>


    <br />

<form action="${action}" method="post">
    <input class="submit" id="submit" type="submit" disabled="disabled" onclick="setupInputFields();" value="Create XML >"/>
    <div id="socialError" class="labelShowError">You must add at least one social service.</div>
    <div id="spError" class="labelShowError">You must add the entity id for at lest one service provider.</div>
</form>


