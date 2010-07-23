from kugelblitz.translator.base import BaseTranslator, ast


class BodyTranslator(BaseTranslator):
    
    separator = '\n'
    
    def translate_body(self, body, sib=False):
        trans_method = self.sib_translate if sib else self.sub_translate
        s = []
        for node in body:
            if isinstance(node, ast.Pass):
                continue
            if isinstance(node, ast.If):
                s.append(trans_method(node))
            else:
                s.append('%s;' % trans_method(node))
        if sib:
            return (self.separator + self.indent).join(s)
        else:
            return (self.separator + self.indent_child).join(s)


class ModuleTranslator(BodyTranslator):
    """
    Responsible for translating a module.
    """
    
    separator = '\n\n'
    
    def translate(self):
        return self.translate_body(self.node.body, sib=True)


class FunctionTranslator(BodyTranslator):
    """
    Translates a function. Includes function name in output.
    """
    
    def get_body(self):
        """
        Returns the body, and a possible docstring.
        """
        if self.node.body and isinstance(self.node.body[0], ast.Expr) and isinstance(self.node.body[0].value, ast.Str):
            docstring = ("\n%s" % self.indent).join([
                "// %s" % line.strip()
                for line in self.node.body[0].value.s.strip().split("\n")
            ])
            body = self.node.body[1:]
        else:
            docstring = None
            body = self.node.body
        return docstring, body
    
    def translate(self):
        docstring, body = self.get_body()
        args_def = ", ".join([arg.id for arg in self.node.args.args])
        context = {
            "args_def": args_def,
            "body_def": self.translate_body(body),
            "name": self.node.name,
            "indent": self.indent,
            "indent_child": self.indent_child,
            "docstring": docstring,
            'module_name': self.module_name,
        }
        if self.module_name:
            if docstring:
                return "%(docstring)s\n%(indent)s%(module_name)s.%(name)s = function (%(args_def)s) {\n%(indent_child)s%(body_def)s\n%(indent)s}" % context
            else:
                return "%(module_name)s.%(name)s = function (%(args_def)s) {\n%(body_def)s\n%(indent)s}" % context
        else:
            if docstring:
                return "%(docstring)s\n%(indent)svar %(name)s = function (%(args_def)s) {\n%(indent_child)s%(body_def)s\n%(indent)s}" % context
            else:
                return "var %(name)s = function (%(args_def)s) {\n%(body_def)s\n%(indent)s}" % context


class LambdaTranslator(BodyTranslator):
    """
    Translates a function. Includes function name in output.
    """
    
    def translate(self):
        return "function (%(args_def)s) {\nreturn %(body_def)s\n}" % {
            'args_def': ", ".join([arg.id for arg in self.node.args.args]),
            'body_def': self.translate_body([self.node.body]),
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


class ClassTranslator(FunctionTranslator):
    """
    Translates methods (doesn't include name in output)
    """
    
    def translate(self):
        # Is there an __init__?
        functions = {}
        assigns = {}
        classes = {}
        for item in self.node.body:
            if isinstance(item, ast.FunctionDef):
                functions[item.name] = item
            elif isinstance(item, ast.Assign):
                assert len(item.targets) == 1, "You can only assign to a single item."
                assert isinstance(item.targets[0], ast.Name), "You can only assign to simple names in classes"
                assigns[item.targets[0].id] = item.value
    
        # Make constructor def
        if "__init__" in functions:
            init_def = MethodTranslator(functions['__init__']).translate()
        else:
            init_def = "function () {}"
        
        # Make other defs
        body = []
        for aname, anode in sorted(assigns.items()):
            body.append("'%s': %s" % (
                aname,
                self.sub_translate(anode),
            ))
        
        # Make method defs
        for fname, fnode in sorted(functions.items()):
            if fname != "__init__":
                body.append("'%s': %s" % (
                    fname,
                    MethodTranslator(fnode).translate(),
                ))
        
        return "var %(name)s = %(init_def)s;\n%(name)s.prototype = { %(method_defs)s }" % {
            'name': self.node.name,
            'init_def': init_def,
            'method_defs': ",\n".join(body),
        }