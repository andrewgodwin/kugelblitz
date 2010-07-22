from kugelblitz.translator.base import BaseTranslator, ast


class ExprTranslator(BaseTranslator):
    
    def translate(self):
        return self.sub_translate(self.node.value)
    

class BoolOpTranslator(BaseTranslator):
    
    ops = {
        ast.And: '&&',
        ast.Or: '||',
    }
    
    def translate(self):
        return "(%(left)s %(op)s %(right)s)" % {
            'left': self.sub_translate(self.node.values[0]),
            'op': self.ops[self.node.op.__class__],
            'right': self.sub_translate(self.node.values[1]),
        }
    

class UnaryOpTranslator(BaseTranslator):
    
    ops = {
        ast.Invert: '~',
        ast.Not: '!',
        ast.UAdd: '+',
        ast.USub: '-',
    }
    
    def translate(self):
        return "%(op)s%(operand)s" % {
            'op': self.ops[self.node.op.__class__],
            'operand': self.sub_translate(self.node.operand),
        }


class BinOpTranslator(BaseTranslator):
    
    ops = {
        ast.Add: '+',
        ast.Sub: '-',
        ast.Mult: '*',
        ast.Div: '/', # TODO: Handle integers
        ast.Mod: '%',
        ast.LShift: '<<',
        ast.RShift: '>>',
        ast.BitOr: '|',
        ast.BitXor: '^',
        ast.BitAnd: '&',
        ast.FloorDiv: '/',
    }
    
    def translate(self):
        # The ** operator isn't in JavaScript.
        if isinstance(self.node.op, ast.Pow):
            return "Math.pow(%s, %s)" % (
                self.sub_translate(self.node.left),
                self.sub_translate(self.node.right),
            )
        else:
            return "(%(left)s %(op)s %(right)s)" % {
                'left': self.sub_translate(self.node.left),
                'op': self.ops[self.node.op.__class__],
                'right': self.sub_translate(self.node.right),
            }


class CompareTranslator(BaseTranslator):
    
    ops = {
        ast.Eq: '==',
        ast.NotEq: '!=',
        ast.Lt: '<',
        ast.LtE: '<=',
        ast.Gt: '>',
        ast.GtE: '>=',
        ast.Is: None,
        ast.IsNot: None,
        ast.In: None,
        ast.NotIn: None,
    }
    
    def translate(self):
        assert len(self.node.ops) == 1, "Cannot have multiple comparison"
        assert len(self.node.comparators) == 1, "Cannot have multiple comparison"
        return "%(left)s %(op)s %(comparator)s" % {
            "left": self.sub_translate(self.node.left),
            "op": self.ops[self.node.ops[0].__class__],
            "comparator": self.sub_translate(self.node.comparators[0]),
        }
