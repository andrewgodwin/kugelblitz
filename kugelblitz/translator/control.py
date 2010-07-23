from kugelblitz.translator.base import BaseTranslator, ast
from kugelblitz.translator.toplevel import BodyTranslator
from kugelblitz.translator.exceptions import CompileError

class IfTranslator(BodyTranslator):

    def translate(self):
        s = ["if (%(test_def)s) {\n%(indent_child)s%(body_def)s\n%(indent)s}" % {
            'test_def': self.sub_translate(self.node.test),
            'body_def': self.translate_body(self.node.body),
            'indent': self.indent,
            'indent_child': self.indent_child,
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

class RaiseTranslator(BodyTranslator):
    def translate(self):
        return "throw"

class ReturnTranslator(BodyTranslator):
    def translate(self):
        return "return %s" % self.sub_translate(self.node.value)
    
class CallTranslator(BodyTranslator):
    def translate(self):
        func = self.sub_translate(self.node.func)
        if func == 'isinstance':
            if len(self.node.args) != 2:
                raise TypeError("isinstance expected 2 arguments, got %s" % len(args))
            s = []
            if isinstance(self.node.args[1], (ast.List, ast.Tuple)):
                for n in self.node.args[1].elts:
                    s.append("%s instanceof %s" % (
                        self.sub_translate(self.node.args[0]),
                        self.sub_translate(n),
                    ))
            else:
                s.append("%s instanceof %s" % tuple(map(self.sub_translate, self.node.args)))
            return " || ".join(s)
        elif func == 'len':
            if len(self.node.args) != 1:
                raise TypeError("len() takes exactly one argument (%s given)" % len(args))
            return "%s.length" % self.sub_translate(self.node.args[0])
        args_def = ", ".join(map(self.sub_translate, self.node.args))
        return "%(func)s(%(args_def)s)" % {
            "func": func,
            "args_def": args_def,
        }

class ForTranslator(BodyTranslator):
    """
    Translates for loops.
    """
    
    def translate(self):
        return "for (var _i = 0; _i < %(iter)s.length; _i++) {\n%(indent_child)svar %(target)s = %(iter)s[_i];\n%(indent_child)s%(body)s\n%(indent)s}" % {
            "iter": self.sib_translate(self.node.iter),
            "target": self.sib_translate(self.node.target),
            "indent": self.indent,
            "indent_child": self.indent_child,
            "body": self.translate_body(self.node.body),
        }
