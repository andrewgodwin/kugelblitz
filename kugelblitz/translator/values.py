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