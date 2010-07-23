try:
    import ast
except ImportError:
    from kugelblitz.lib import ast

class BaseTranslator(object):
    
    """
    Base translator class. Instantiated for each node.
    """
    
    INDENT_STRING = "    "
    
    def __init__(self, node, indent_level=0):
        self.node = node
        self.indent_level = indent_level
    
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
        ).translate()
    
    def sib_translate(self, node):
        """
        Returns the node, indented at the same level
        """
        return self.get_translator(
            node,
            indent_level = self.indent_level,
        ).translate()
