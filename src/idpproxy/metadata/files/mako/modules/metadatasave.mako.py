# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1365430482.195919
_enable_loop = True
_template_filename = '/Users/haho0032/IdPproxy/src/idpproxy/metadata/files/mako/htdocs/metadatasave.mako'
_template_uri = 'metadatasave.mako'
_source_encoding = 'utf-8'
_exports = []


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
        xml = context.get('xml', UNDEFINED)
        home = context.get('home', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n<p class="description">\n    Copy the partial XML below and paste it to your metadata file.\n    The mdattr:EntityAttributes element should be pasted into a &lt;ns0:Extensions&gt;&lt;/ns0:Extensions&gt; element\n    which must be placed directly after the &lt;SSODescription&gt; element.\n    <textarea rows="20" cols="40" readonly="readonly">')
        # SOURCE LINE 7
        __M_writer(unicode(xml))
        __M_writer(u'</textarea>\n</p>\n<a href="')
        # SOURCE LINE 9
        __M_writer(unicode(home))
        __M_writer(u'">Click here to perform a new configuration.</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


