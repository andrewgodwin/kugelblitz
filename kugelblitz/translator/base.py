try:
    import ast
except ImportError:
    from kugelblitz.lib import ast

from kugelblitz.translator.context import Context

class BaseTranslator(object):
    
    """
    Base translator class. Instantiated for each node.
    
    indent_level says how far indented this node is. All nodes output without
    prefixing themselves with indent characters; only if they have a newline
    do they need to add them.
    
    module_name specifies the module prefix to append to all items in this
    node, if it contains any; it's lost as soon as you use sub_translate
    (since it's only needed for top-level things in modules)
    """
    
    INDENT_STRING = "    "
    
    def __init__(self, node, indent_level=0, module_name=None, context=None):
        self.node = node
        self.indent_level = indent_level
        self.module_name = module_name
        self.context = context or Context()
    
    @property
    def indent(self):
        return self.INDENT_STRING * self.indent_level
    
    @property
    def indent_child(self):
        return self.INDENT_STRING * (self.indent_level + 1)
    
    def get_translator(self, node, **kwargs):
        from kugelblitz.translator import get_translator
        return get_translator(node, **kwargs)
    
    def sub_translate(self, node):
        """
        Returns the node, indented the next level down.
        """
        return self.get_translator(
            node,
            indent_level = self.indent_level + 1,
            module_name = None,
            context = Context(self.context),
        ).translate()
    
    def sib_translate(self, node):
        """
        Returns the node, indented at the same level
        """
        return self.get_translator(
            node,
            indent_level = self.indent_level,
            module_name = self.module_name,
            context = self.context,
        ).translate()
