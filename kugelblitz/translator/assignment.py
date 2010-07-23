from kugelblitz.translator.base import BaseTranslator, ast
from kugelblitz.translator.exceptions import CompileError
from kugelblitz.translator.expressions import BinOpTranslator

class AssignTranslator(BaseTranslator):
    
    def translate_single_assign(self, target, value):
        context = {
            'target': self.sib_translate(target),
            'value': self.sib_translate(value),
            'module_name': self.module_name,
        }
        if isinstance(target, ast.Name):
            if self.module_name:
                return "%(module_name)s.%(target)s = %(value)s" % context
            else:
                return "var %(target)s = %(value)s" % context
        else:
            return "%(target)s = %(value)s" % context

    def translate(self):
        statements = []
        for target in self.node.targets:
            # Is it a tuple-to-tuple assignment?
            if isinstance(target, ast.Tuple):
                # Is the RHS a tuple?
                if isinstance(self.node.value, ast.Tuple):
                    # Make sure they're the same length
                    if len(target.elts) != len(self.node.value.elts):
                        raise CompileError("Assigning one tuple to another of different length.")
                    for t, v in zip(target.elts, self.node.value.elts):
                        statements.append(self.translate_single_assign(t, v))
                # No? Raise an error for now.
                else:
                    raise CompileError("Assigning a non-tuple to a tuple.")
            else:
                statements.append(self.translate_single_assign(target, self.node.value))
        return ";\n".join(statements)
    
    
class AugAssignTranslator(BaseTranslator):
    
    ops = BinOpTranslator.ops
    
    def translate(self):
        return '%(target)s %(op)s= %(value)s' % {
            'target': self.sub_translate(self.node.target),
            'op': self.ops[self.node.op.__class__],
            'value': self.sub_translate(self.node.value),
        }
