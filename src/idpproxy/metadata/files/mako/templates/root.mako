<%def name="pre()" filter="trim">
</%def>
<%def name="post()" filter="trim">
    <div xmlns="http://www.w3.org/1999/html">
        <div class="footer">
            <p>&#169; Copyright 2013 Ume&#229; Universitet &nbsp;</p>
        </div>
    </div>
</%def>

<html>
<head><title>Social service - Metadata generation</title>
    <link rel="stylesheet" type="text/css" href="/metadata/style.css" media="screen" />
    <link rel="stylesheet" type="text/css" href="/metadata/popup.css" media="screen" />
    <script type="text/javascript" src="/metadata/jquery.min.1.9.1.js" ></script>
    <script type="text/javascript" src="/metadata/popup.js" ></script>
    <script type="text/javascript" src="/metadata/serializeJSON.js" ></script>
    <script type="text/javascript" src="/metadata/rest.js" ></script>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <script language="JavaScript">
        function showExampleMetadata() {
            viewPopup($('#exampleMetadata').html(), "Close")
        }
    </script>
    <script language="JavaScript">

    </script>
</head>
<body>
<div id="exampleMetadata"  style="display: none">
<div style="padding-right:20px;width:800px;height:640px;overflow-x: hidden;overflow-y: auto;word-wrap: break-word;">
&lt;?xml&nbsp;version='1.0'&nbsp;encoding='UTF-8'?&gt;<br />
&lt;ns0:EntityDescriptor&nbsp;xmlns:ns0="urn:oasis:names:tc:SAML:2.0:metadata"&nbsp;xmlns:ns1="http://www.w3.org/2000/09/xmldsig#"&nbsp;entityID="http://localhost:8087/sp.xml"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:SPSSODescriptor&nbsp;AuthnRequestsSigned="false"&nbsp;WantAssertionsSigned="true"&nbsp;protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:Extensions&gt;<br />
<b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;mdattr:EntityAttributes&nbsp;xmlns:mdattr="urn:oasis:names:tc:SAML:metadata:attribute"&nbsp;xmlns:samla="urn:oasis:names:tc:SAML:2.0:assertion"&nbsp;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;samla:Attribute&nbsp;Name="http://social2saml.nordu.net/customer"&nbsp;NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;samla:AttributeValue&nbsp;xsi:type="xs:string"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;eyJhbGciOiAiUlNBLU9BRVAiLCAiZW5jIjogIkEyNTZHQ00ifQ.ZQirC33tA6x0_1_utl1N3KCItRnymJ3nl8tGZgf1-asSZkrTq1ZFLcavXvrGXAPWCh5rGRFAbIWWeGemtX62VjB_i54v8xqfPzamwiMAyqCA_AxCE6qhjnP92h2mpikjlqjPivG3xIhbWuAi4szr8fqgbvlh3HmmXjvuisod03w.F7XOQWE3nm1H2BGV.LREJkSMe2dkbzaYR8THvIjdOMV6O4-EvD3jN2Uh4-6bfnx-TJyQtenmAFdzjkTWY1gGFSy9egCL6DlnXRGcejbmPMlPqf-i588sFAL6lk8AGsn489kplBvkkqnQFAGqF9bzLpbvh6Wv57ax5HIYq4wPsCrii-1O3TkGiqdwANiAbE6wVUPKWp4sx09OUCBiez1AcuFWJjNgIT2iPbxWLscyYtBLHlMvYkTMAE8LhbM2qCcqcR5PvxSTkeubvPQtDcjS4uGlo0vg0K9bXEIC8tl6d2GM24NolIfAlEUCC4gygQHDXmmEE4_0xkb3LkRSw6b5glI9E_Q-gY1SOiZ4M11mN6Zk4T0f8EcOmZ0NJvMBuqgzkQEW2HBJCCxgXJCrlpx6Yff3L0X9TJ7iDj1TetWR40YJfms6SLKJ6qAHC9vxJ0rbQ6nYzpaA.UCSrAPuRrNuUMOUr7gN5vg<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/samla:AttributeValue&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/samla:Attribute&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/mdattr:EntityAttributes&gt;<br /></b>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns0:Extensions&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:KeyDescriptor&nbsp;use="signing"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns1:KeyInfo&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns1:X509Data&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns1:X509Certificate&gt;MIIC8jCCA...&lt;/ns1:X509Certificate&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns1:X509Data&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns1:KeyInfo&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns0:KeyDescriptor&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:SingleLogoutService&nbsp;Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"&nbsp;Location="http://localhost:8087/slo"&nbsp;/&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:AssertionConsumerService&nbsp;Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"&nbsp;Location="http://localhost:8087"&nbsp;index="1"&nbsp;/&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns0:SPSSODescriptor&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:Organization&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:OrganizationName&nbsp;xml:lang="en"&gt;Exempel&nbsp;AB&lt;/ns0:OrganizationName&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:OrganizationDisplayName&nbsp;xml:lang="se"&gt;Exempel&nbsp;AB&lt;/ns0:OrganizationDisplayName&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:OrganizationDisplayName&nbsp;xml:lang="en"&gt;Example&nbsp;Co.&lt;/ns0:OrganizationDisplayName&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:OrganizationURL&nbsp;xml:lang="en"&gt;http://www.example.com&lt;/ns0:OrganizationURL&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns0:Organization&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:ContactPerson&nbsp;contactType="technical"&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:GivenName&gt;John&lt;/ns0:GivenName&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:SurName&gt;Smith&lt;/ns0:SurName&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;ns0:EmailAddress&gt;john.smith@example.com&lt;/ns0:EmailAddress&gt;<br />
&nbsp;&nbsp;&nbsp;&nbsp;&lt;/ns0:ContactPerson&gt;<br />
&lt;/ns0:EntityDescriptor&gt;<br />
</div>
</div>
<div id="formContainer">
    <h1>Social2Saml metadata for your Service provider</h1>
    ${pre()}
    ${next.body()}
    ${post()}
</div>

</body>
</html>