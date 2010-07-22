from kugelblitz.translator.base import BaseTranslator, ast


class BodyTranslator(BaseTranslator):
    
    separator = '\n'
    
    def translate_body(self, body):
        s = []
        for node in body:
            if isinstance(node, ast.Pass):
                continue
            translator = self.get_translator(node)
            if isinstance(node, ast.If):
                s.append(translator.translate())
            else:
                s.append('%s;' % translator.translate())
        return self.separator.join(s)


class ModuleTranslator(BodyTranslator):
    """
    Responsible for translating a module.
    """
    
    separator = '\n\n'
    translates = [ast.Module]
    
    def translate(self):
        return self.translate_body(self.node.body)


class FunctionTranslator(BodyTranslator):
    """
    Translates a function. Includes function name in output.
    """
    
    translates = [ast.FunctionDef]
    
    def translate(self):
        args_def = ", ".join([arg.id for arg in self.node.args.args])
        return "var %(name)s = function (%(args_def)s) { %(body_def)s }" % {
            "args_def": args_def,
            "body_def": self.translate_body(self.node.body),
            "name": self.node.name,
        }
    

class MethodTranslator(FunctionTranslator):
    """
    Translates methods (doesn't include name in output)
    """
    
    def translate(self):
        args_def = ", ".join([arg.id for arg in self.node.args.args[1:]])
        return "function (%(args_def)s) { %(body_def)s }" % {
            "args_def": args_def,
            "body_def": self.translate_body(self.node.body),
        }

