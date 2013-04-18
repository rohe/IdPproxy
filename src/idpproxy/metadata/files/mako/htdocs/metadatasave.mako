<%inherit file="root.mako"/>
<h2>&nbsp;&nbsp;&nbsp;&nbsp;- Result</h2>
<p class="description">
    Copy the partial XML below and paste it in your metadata file.
    The mdattr:EntityAttributes element should be pasted into an Extensions element
    which must be placed directly after the SSODescription element.
    <a href="#" onclick="showExampleMetadata()">View an example.</a>
    Please make sure your metadata file is constructed correct before submitting it to the IdP. You can do that by
    performing the next step, <a href="${action}">"Validate metadata file".</a>
    <textarea rows="30" readonly="readonly" >${xml}</textarea>
<form action="${action}" method="post">
    <input class="submit" id="submit" type="submit" value="Validate metadata file >"/>
</form>

</p>
<a href="${home}">Click here to perform a new configuration.</a>
