from kugelblitz.translator.base import ast, BaseTranslator
from kugelblitz.translator.exceptions import CompileError
from kugelblitz.translator.toplevel import ModuleTranslator, FunctionTranslator, LambdaTranslator, ClassTranslator
from kugelblitz.translator.expressions import ExprTranslator, BinOpTranslator, BoolOpTranslator, UnaryOpTranslator, CompareTranslator
from kugelblitz.translator.values import NumTranslator, ListTranslator, NameTranslator
from kugelblitz.translator.assignment import AssignTranslator, AugAssignTranslator
from kugelblitz.translator.control import IfTranslator, IfExprTranslator, RaiseTranslator, ReturnTranslator, CallTranslator

def wrap_old_translator(func):
    class WrappedTranslator(BaseTranslator):
        def translate(self):
            return func(self.node)
    return WrappedTranslator

def translate(node):
    return get_translator(node).translate()

def get_translator(node):
    try:
        return {
            # mod
            ast.Module: ModuleTranslator,
            ast.Expression: None,
            
            # stmt
            ast.FunctionDef: FunctionTranslator,
            ast.ClassDef: ClassTranslator,
            ast.Return: ReturnTranslator,
            
            ast.Delete: wrap_old_translator(translate_delete),
            ast.Assign: AssignTranslator,
            ast.AugAssign: AugAssignTranslator,
            
            ast.Print: None,
            
            ast.For: None,
            ast.While: None,
            ast.If: IfTranslator,
            ast.With: None,
            
            ast.Raise: RaiseTranslator,
            ast.TryExcept: None,
            ast.TryFinally: None,
            ast.Assert: None,
            
            ast.Import: None,
            ast.ImportFrom: None,
            
            ast.Exec: None,
            
            ast.Global: None,
            ast.Expr: ExprTranslator,
            ast.Break: None,
            ast.Continue: None,
            
            # expr
            ast.BoolOp: BoolOpTranslator,
            ast.BinOp: BinOpTranslator,
            ast.UnaryOp: UnaryOpTranslator,
            ast.Lambda: LambdaTranslator,
            ast.IfExp: IfExprTranslator,
            ast.Dict: None,
            #ast.Set: None, Not in 2.6
            ast.ListComp: None,
            #ast.SetComp: None, Not in 2.6
            #ast.DictComp: None, Not in 2.6
            ast.GeneratorExp: None,
            ast.Yield: None,
            ast.Compare: CompareTranslator,
            ast.Call: CallTranslator,
            ast.Repr: None,
            ast.Num: NumTranslator,
            ast.Str: None,
            ast.Attribute: wrap_old_translator(translate_attribute),
            ast.Subscript: wrap_old_translator(translate_subscript),            
            ast.Name: NameTranslator,
            ast.List: ListTranslator,
            ast.Tuple: ListTranslator,
            
        }[node.__class__](node)
    except TypeError:
        raise CompileError("No translator available for %s." % node.__class__.__name__)

def translate_delete(node):
    return ';\n'.join('delete %s' % translate(n) for n in node.targets)

def translate_attribute(node):
    return "%(left)s.%(right)s" % {
        "left": translate(node.value),
        "right": node.attr,
    }
    
def translate_subscript(node):
    if isinstance(node.slice, ast.Index):
        return "%(value)s[%(index)s]" % {
            "value": translate(node.value),
            "index": translate(node.slice.value),
        }
    elif isinstance(node.slice, ast.Slice):
        # Translate the endpoints
        if node.slice.lower:
            if isinstance(node.slice.lower, ast.Num):
                lower = node.slice.lower.n
            else:
                raise CompileError("Slice arguments must be numeric.")
        else:
            lower = 0
        if node.slice.upper:
            if isinstance(node.slice.upper, ast.Num):
                upper = node.slice.upper.n
            else:
                raise CompileError("Slice arguments must be numeric.")
        else:
            upper = None
        # Different cases for upper/lower
        if node.slice.upper is not None:
            return "%(value)s.slice(%(lower)s, %(upper)s)" % {
                "value": translate(node.value),
                "lower": lower,
                "upper": upper,
            }
        else:
            return "%(value)s.slice(%(lower)s)" % {
                "value": translate(node.value),
                "lower": lower,
            }
        
    else:
        raise CompileError("Unknown slice type %s" % type(node.slice))

if __name__ == "__main__":
    import sys
    print get_translator(ast.parse(sys.stdin.read()+"\n")).translate()
