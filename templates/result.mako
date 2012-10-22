<%def name="header(title)">
      <head><title>${title}</title></head>
      <body><h1>${title}</h1>
</%def>

<%def name="footer()">
    </body>
</%def>

<%def name="logout(action)">
<form method="logout" accept-charset="UTF-8" action="${action}">
    <input type="submit" value="Logout"/><br />
</form>
</%def>


<html>
    ${header(title)}
        
    ${result}
    <p>
    ${logout(action)}
    
    ${footer()}
</html>