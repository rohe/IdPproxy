<%def name="header(title)">
      <head><title>${title}</title></head>
      <body><h1>${title}</h1>
</%def>

<%def name="footer()">
    </body>
</%def>

<%def name="matrix(action, choices)">
    <div id="verify-matrix">
        <table border="1"><tr>
        % for key, label, img in choices:
            <td><a href="${action}?${label}=on&sessionid=${sessionid}">
            %if img:
                <img alt="${label}" src="${img}"/>
            %else:
                <label for="${key}">${label}</label>
            %endif
            </a></td>
        %endfor
        </tr></table>
    </div>
</%def>

<html>
    ${header(title)}
    
    ${matrix(action, choices)}
    
    %if last:
        <em>When you last used this service you authenticated using: ${last}</em>
    %endif
    
    ${footer()}
</html>