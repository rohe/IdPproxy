## -*- coding: utf-8 -*-

<%inherit file="root.mako"/>

<%def name="idps()">
    % for eid, name in wayf_idplist:
      %if eid == selected_idp:
        <option value="${eid}" selected="true">${name}</option>
      %else:
        <option value="${eid}">${name}</option>
      %endif
    %endfor
</%def>

<p>
<h3>Välj en identitetsutgivare</h3>
Tjänsten du försöker nå kräver att du väljer en identitetsutgivare (t ex ditt universitet/högskola) från nedanstående lista innan du kan logga in.
</p>

<div id="idpform">
<form id="idp_selection_form" action="${action}" method="post">
  <select name="wayf_selected">
  ${idps()}.
  </select>
  <input type="submit" value="Confirm" /><br />
  <input type="hidden" name="save" value="true" />
  <input type="hidden" name="savetype" value="perm" />
</form>
</div>
