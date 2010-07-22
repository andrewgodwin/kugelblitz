from kugelblitz.translator.base import BaseTranslator, ast


class NumTranslator(BaseTranslator):
    
    def translate(self):
        return str(self.node.n)
