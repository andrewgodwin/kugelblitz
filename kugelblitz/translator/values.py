from kugelblitz.translator.exceptions import CompileError
from kugelblitz.translator.base import BaseTranslator, ast


class NumTranslator(BaseTranslator):
    def translate(self):
        return str(self.node.n)

class NameTranslator(BaseTranslator):
    def translate(self):
        if self.node.id == "self":
            return "this"
        elif self.node.id == "None":
            return "null"
        elif self.node.id == "False":
            return "false"
        elif self.node.id == "True":
            return "true"
        else:
            return self.node.id

class ListTranslator(BaseTranslator):
    def translate(self):
        return "[%s]" % ", ".join(map(self.sub_translate, self.node.elts))

class DictTranslator(BaseTranslator):
    def str_translate(self, value):
        if isinstance(value, ast.Str):
            return self.sub_translate(value)
        elif isinstance(value, ast.Num):
            node = ast.Str()
            node.s = str(value.n)
            return self.sub_translate(node)
        else:
            raise CompileError("Invalid value for dict key: %r" % value)
    
    def translate(self):
        return "{%s}" % ",\n".join([
            "%s: %s" % (self.str_translate(k), self.sub_translate(v))
            for k, v in zip(self.node.keys, self.node.values)
        ])

class StrTranslator(BaseTranslator):
    def translate(self):
        return repr(self.node.s)
    
