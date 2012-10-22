## -*- coding: utf-8 -*-

<%inherit file="sso.mako"/>

<form name="myform" method="post" action="${action}">
    <input type="hidden" name="SAMLResponse" value="${response}" />
    <input type="hidden" name="RelayState" value="${state}" />
</form>
