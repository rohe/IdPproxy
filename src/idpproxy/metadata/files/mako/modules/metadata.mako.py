# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1365499656.315692
_enable_loop = True
_template_filename = '/Users/haho0032/githubFork/IdPproxy/src/idpproxy/metadata/files/mako/htdocs/metadata.mako'
_template_uri = 'metadata.mako'
_source_encoding = 'utf-8'
_exports = []


# SOURCE LINE 3

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


# SOURCE LINE 23

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


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'root.mako', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        action = context.get('action', UNDEFINED)
        sociallist = context.get('sociallist', UNDEFINED)
        spKeyList = context.get('spKeyList', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n')
        # SOURCE LINE 21
        __M_writer(u'\n\n')
        # SOURCE LINE 39
        __M_writer(u'\n\n<script>\n    //Has the social service name as key and {"secret": "mysecret", "key": "mykey"} as value.\n    var secretHash = {}\n    //Has the entity id as key and true or false as value.\n    //True = the entity id is from the list.\n    //False = the entity id is written by the user.\n    var spHash = {}\n\n    //Verifies if a hash is empty.\n    function isEmpty(obj) {\n        for (name in obj) {\n            return false;\n        }\n        return true;\n    }\n\n\n    //Verifies if the form is ready to be submitted.\n    function verifySubmit() {\n        if ((isEmpty(secretHash)) || (isEmpty(spHash))) {\n            $(\'#socialError\').show();\n            $(\'#spError\').show();\n            $(\'#submit\').attr(\'disabled\',\'disabled\');\n        } else {\n            $(\'#socialError\').hide();\n            $(\'#spError\').hide();\n            $(\'#submit\').removeAttr(\'disabled\');\n        }\n    }\n\n    //Will empty all options from the select with the given id.\n    //Then fill it again with all options in dataArr that have a text that matches the string str.\n    //The data array is constructed in python and represents a JSON list\n    // [{\'value\' : \'value1\',\'text\' : \'text1\'},{\'value\' : \'valuen\',\'text\' : \'textn\'}]\n    function filterOptions(str, id)\n    {\n        var dataArr = ')
        # SOURCE LINE 77
        __M_writer(unicode(setupJavaScriptEntityIdArray(spKeyList)))
        __M_writer(u'\n                $("#" + id + " option").remove();\n        $.each(dataArr,\n                function(i) {\n                    if (dataArr[i][\'text\'].match(\'.*\'+str+\'.*\') != null) {\n                        $("#"+id).append($("<option></option>")\n                                .attr("value",dataArr[i][\'value\'])\n                                .text(dataArr[i][\'text\']));\n                    }\n                }\n        )\n        $("#sp option:first").attr(\'selected\',\'selected\');\n    }\n\n    //Sort function, used for sorting option elements in a select element.\n    function NASort(a, b) {\n        if (a.innerHTML == \'NA\') {\n            return 1;\n        }\n        else if (b.innerHTML == \'NA\') {\n            return -1;\n        }\n        return (a.innerHTML > b.innerHTML) ? 1 : -1;\n    };\n\n    //Contains all code that must run when the pages is fully loaded.\n    $(document).ready(function() {\n\n        //Handles the action to add a new entity id for a sp given by the user.\n        $(\'#btn-add-sp-manual\').click(function(){\n            value = $(\'#manualSp\').val().trim();\n            if (value.length > 0) {\n                $(\'#sp_to\').append("<option value=\'"+value+"\'>"+value+"</option>");\n                spHash[value] = false;\n                $(\'#manualSp\').val(\'\');\n                $(\'#sp_to option\').sort(NASort).appendTo(\'#sp_to\');\n            }\n            verifySubmit();\n        });\n\n        //Handles the action to add a entity id for a sp from the list.\n        $(\'#btn-add-sp\').click(function(){\n            $(\'#sp_from option:selected\').each( function() {\n                $(\'#sp_to\').append("<option value=\'"+$(this).val()+"\'>"+$(this).text()+"</option>");\n                spHash[$(this).val()] = true;\n                $(this).remove();\n            });\n            $(\'#sp_to option\').sort(NASort).appendTo(\'#sp_to\');\n            verifySubmit();\n        });\n\n        //Handles the action to remove a entity id for a sp.\n        $(\'#btn-remove-sp\').click(function(){\n            $(\'#sp_to option:selected\').each( function() {\n                sort = false;\n                if (spHash[$(this).val()]) {\n                    $(\'#sp_from\').append("<option value=\'"+$(this).val()+"\'>"+$(this).text()+"</option>");\n                    sort = true;\n                }\n                try{\n                    delete spHash[$(this).val()];\n                } catch(e){}\n                $(this).remove();\n            });\n            if (sort)\n            {\n                $(\'#sp_from option\').sort(NASort).appendTo(\'#sp_from\');\n            }\n            verifySubmit();\n        });\n\n        //Handles the action to add a service with a given secret and key.\n        $(\'#btn-add-service\').click(function(){\n            $(\'#keysecretError\').hide();\n            if (($(\'#secrettmp\').val().trim().length == 0) || ($(\'#keytmp\').val().trim().length == 0)) {\n                $(\'#keysecretError\').show();\n            } else {\n                $(\'#service_from option:selected\').each( function() {\n                    $(\'#service_to\').append("<option value=\'"+$(this).val()+"\'>"+$(this).text()+"</option>");\n                    secrets = {"secret": $(\'#secrettmp\').val(), "key": $(\'#keytmp\').val()};\n                    secretHash[$(this).val()] = secrets;\n                    $(this).remove();\n                    $(\'#secrettmp\').val(\'\');\n                    $(\'#keytmp\').val(\'\');\n                });\n                $(\'#service_to option\').sort(NASort).appendTo(\'#service_to\');\n            }\n            verifySubmit();\n        });\n\n        //Handles the action to remove a service.\n        $(\'#btn-remove-service\').click(function(){\n            $(".hidden").css("visibility", "hidden");\n            $(\'#service_to option:selected\').each( function() {\n                $(\'#service_from\').append("<option value=\'"+$(this).val()+"\'>"+$(this).text()+"</option>");\n                try{\n                    delete secretHash[$(this).val()];\n                } catch(e){}\n                $(this).remove();\n            });\n            $(\'#service_from option\').sort(NASort).appendTo(\'#service_from\');\n            verifySubmit();\n        });\n\n        //Will show the key and secret for a added service.\n        $(\'#service_to\').click(function(){\n            $(".hidden").css("visibility", "hidden");\n            $(\'#service_to option:selected\').each( function() {\n                secrets = secretHash[$(this).val()];\n                $(\'#secret\').val(secrets["secret"]);\n                $(\'#key\').val(secrets["key"]);\n                $(".hidden").css("visibility", "visible");\n            });\n        });\n\n    });\n\n    //Action to be performed before the form is submitted.\n    //Will add a list of entity id\'s and socical services to be encrypted and added to an partial xml.\n    //Before the form is submitted is the input fields cleaned, to prevent the key(s) and secret(s) to be exposed\n    //by using the back button.\n    function setupInputFields() {\n        spList = [];\n        for(var key in spHash) {\n            spList.push(key)\n        }\n        $(\'form\').append("<input type=\'hidden\' id=\'entityId\' name=\'entityId\' value=\'" + JSON.stringify(spList) + "\' />");\n        $(\'form\').append("<input type=\'hidden\' id=\'secret\' name=\'secret\' value=\'" + JSON.stringify(secretHash) + "\' />");\n        $("select option").remove();\n        $(\'#secrettmp\').val(\'\');\n        $(\'#keytmp\').val(\'\');\n        spHash = {}\n        secretHash = {}\n    }\n</script>\n\n<p class="description">\n    You can use this tool if you want to include social service credentials in your metadata file.\n    All information will be encrypted with the public key for Social2Saml and included in an EntityAttributes XML element.\n    First you must add the entity id for all service providers that can use the same key(s) and secret(s)\n    for the social services. You can either use the list or add them manually.\n    Then you have to add key and secret for each social service you which to use for your service provider(s).\n    Follow the guide at <a href="https://portal.nordu.net/display/SWAMID/Social2SAML">SWAMID</a> to retrieve secret and key for the social service you which to configure.<br />\n</p>\n\n    <table style="width:100%">\n        <tr>\n            <td colspan="3">\n                Add Service Provider(s)\n            </td>\n        </tr>\n        <tr>\n            <td style="width:45%">\n                <select name=\'sp_from\' id="sp_from" size="10" multiple="multiple">\n                    ')
        # SOURCE LINE 231
        __M_writer(unicode(createSelectOptions(spKeyList)))
        __M_writer(u'\n                </select>\n            </td>\n            <td style="width:10%;text-align: center; vertical-align: middle">\n                <input type="button" id="btn-add-sp" value="Add &raquo;" />\n                <br>\n                <input type="button" id="btn-remove-sp" value="&laquo; Remove" />\n            </td>\n            <td  style="width:45%">\n                <select name=\'sp_to\' id="sp_to" size="10" multiple="multiple">\n                </select>\n            </td>\n        </tr>\n        <tr>\n            <td style="width:45%">\n                <div class="label">Filter:</div><input type=\'text\' class=\'inputValue\' onkeyup="filterOptions(this.value, \'sp_from\')" name=\'filter\' id=\'filter\' value=\'\'/>\n            </td>\n            <td style="width:10%;text-align: center; vertical-align: middle">\n                &nbsp;\n            </td>\n            <td  style="width:45%">\n                <div class="label">EntityId:</div><input type=\'text\' class=\'inputValueSmall\' name=\'manualSp\' id=\'manualSp\' value=\'\'/>\n                <input type="button" id="btn-add-sp-manual" value="Add" />\n            </td>\n        </tr>\n    </table>\n\n    <br>\n    <table style="width:100%">\n        <tr>\n            <td colspan="3">\n                Add key(s) and secret(s)\n            </td>\n        </tr>\n        <tr>\n            <td style="width:45%">\n                <select name=\'service_from\' id="service_from" size="5">\n                    ')
        # SOURCE LINE 268
        __M_writer(unicode(createSelectOptions(sociallist)))
        __M_writer(u'\n                </select>\n            </td>\n            <td style="width:10%;text-align: center; vertical-align: middle">\n                <input type="button" id="btn-add-service" value="Add &raquo;" />\n                <br>\n                <input type="button" id="btn-remove-service" value="&laquo; Remove" />\n            </td>\n            <td  style="width:45%">\n                <select name=\'service_to\' id="service_to" size="5">\n                </select>\n            </td>\n        </tr>\n        <tr>\n            <td style="width:45%; vertical-align: top;">\n                <div class="label">Secret:</div><input type=\'text\' class=\'inputValue\' name=\'secrettmp\' id=\'secrettmp\' value=\'\'/>\n                <div class="label">Key:</div><input type=\'text\' class=\'inputValue\' name=\'keytmp\' id=\'keytmp\' value=\'\'/>\n                <div id="keysecretError" class="labelError">You must have a value for both key and secret!</div>\n            </td>\n            <td style="width:10%;text-align: center; vertical-align: middle">\n                &nbsp;\n            </td>\n            <td  style="width:45%; vertical-align: top;">\n                <div class="label hidden">Secret:</div><input type=\'text\' readonly="readonly" class=\'inputView hidden\' name=\'secret\' id=\'secret\' value=\'\'/>\n                <div class="label hidden">Key:</div><input type=\'text\' readonly="readonly" class=\'inputView hidden\' name=\'key\' id=\'key\' value=\'\'/>\n            </td>\n        </tr>\n    </table>\n\n\n    <br />\n\n<form action="')
        # SOURCE LINE 300
        __M_writer(unicode(action))
        __M_writer(u'" method="post">\n    <input class="submit" id="submit" type="submit" disabled="disabled" onclick="setupInputFields();" value="Create XML >"/>\n    <div id="socialError" class="labelShowError">You must add at least one social service.</div>\n    <div id="spError" class="labelShowError">You must add the entity id for at lest one service provider.</div>\n</form>\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


