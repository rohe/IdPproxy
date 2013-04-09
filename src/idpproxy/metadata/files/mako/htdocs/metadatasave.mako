<%inherit file="root.mako"/>

<p class="description">
    Copy the partial XML below and paste it to your metadata file.
    The mdattr:EntityAttributes element should be pasted into a &lt;ns0:Extensions&gt;&lt;/ns0:Extensions&gt; element
    which must be placed directly after the &lt;SSODescription&gt; element.
    <textarea rows="20" cols="40" readonly="readonly">${xml}</textarea>
</p>
<a href="${home}">Click here to perform a new configuration.</a>
