try:
    import ast
except ImportError:
    from kugelblitz.lib import ast

class BaseTranslator(object):
    
    """
    Base translator class. Instantiated for each node.
    """
    
    def __init__(self, node):
        self.node = node
    
    def get_translator(self, node):
        from kugelblitz.translator import get_translator
        return get_translator(node)
    
    def sub_translate(self, node):
        return self.get_translator(node).translate()
