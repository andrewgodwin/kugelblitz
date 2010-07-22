from kugelblitz.translator.base import BaseTranslator, ast
from kugelblitz.translator.toplevel import BodyTranslator
from kugelblitz.translator.exceptions import CompileError

class IfTranslator(BodyTranslator):

    def translate(self):
        s = ["if (%(test_def)s) { %(body_def)s }" % {
            'test_def': self.sub_translate(self.node.test),
            'body_def': self.translate_body(self.node.body),
        }]
        if self.node.orelse:
            s.append("else { %(orelse_def)s }" % {
                's': s,
                'orelse_def': self.translate_body(self.node.orelse),
            })
        return '\n'.join(s)

class IfExprTranslator(BodyTranslator):

    def translate(self):
        return '%(test)s ? %(body)s : %(orelse)s' % {
            'test': self.sub_translate(self.node.test),
            'body': self.sub_translate(self.node.body),
            'orelse': self.sub_translate(self.node.orelse),
        }