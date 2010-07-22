try:
    import ast
except ImportError:
    from kugelblitz.lib import ast


class BaseTranslatorMetaclass(type):
    
    translators = {}
    
    def __new__(cls, name, bases, attrs):
        print cls, name, bases, attrs
        # Get the new class
        new_class = type(name, bases, attrs)
        # Attach it for any handlers
        for handler in attrs.get("translates", []):
            cls.translators[handler] = new_class
        return new_class
        

class BaseTranslator(object):
    
    """
    Base translator class. Instantiated for each node.
    """
    
    __metaclass__ = BaseTranslatorMetaclass
    
    def __init__(self, node):
        self.node = node

    @staticmethod
    def get_translator(node):
        return BaseTranslatorMetaclass.translators[node.__class__](node)
    

if __name__ == "__main__":
    import sys
    from kugelblitz.translator.toplevel import ModuleTranslator
    print ModuleTranslator(ast.parse(sys.stdin.read()+"\n")).translate()