<%def name="pre()" filter="trim">
</%def>
<%def name="post()" filter="trim">
    <div>
        <div class="footer">
            <p>&#169; Copyright 2013 Ume&#229; Universitet &nbsp;</p>
        </div>
    </div>
</%def>

<html>
<head><title>Social service - Metadata generation</title>
    <link rel="stylesheet" type="text/css" href="/metadata/style.css" media="screen" />
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js" ></script>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body>
<div id="formContainer">
    <h2>Generate Social2Saml metadata for your Service provider</h2>
    ${pre()}
    ${next.body()}
    ${post()}
</div>
</body>
</html>