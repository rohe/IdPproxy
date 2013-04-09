# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1365430591.651148
_enable_loop = True
_template_filename = u'/Users/haho0032/IdPproxy/src/idpproxy/metadata/files/mako/templates/root.mako'
_template_uri = u'root.mako'
_source_encoding = 'utf-8'
_exports = ['pre', 'post']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def pre():
            return render_pre(context.locals_(__M_locals))
        def post():
            return render_post(context.locals_(__M_locals))
        next = context.get('next', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 9
        __M_writer(u'\n\n<html>\n<head><title>Social service - Metadata generation</title>\n    <link rel="stylesheet" type="text/css" href="/metadata/style.css" media="screen" />\n    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js" ></script>\n    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n</head>\n<body>\n<div id="formContainer">\n    <h2>Generate Social2Saml metadata for your Service provider</h2>\n    ')
        # SOURCE LINE 20
        __M_writer(unicode(pre()))
        __M_writer(u'\n    ')
        # SOURCE LINE 21
        __M_writer(unicode(next.body()))
        __M_writer(u'\n    ')
        # SOURCE LINE 22
        __M_writer(unicode(post()))
        __M_writer(u'\n</div>\n</body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_pre(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        context._push_buffer()
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


def render_post(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        context._push_buffer()
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n    <div>\n        <div class="footer">\n            <p>&#169; Copyright 2013 Ume&#229; Universitet &nbsp;</p>\n        </div>\n    </div>\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


