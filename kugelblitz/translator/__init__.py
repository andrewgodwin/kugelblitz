from kugelblitz.translator.base import ast, BaseTranslator
from kugelblitz.translator.exceptions import CompileError
from kugelblitz.translator.toplevel import ModuleTranslator, FunctionTranslator, LambdaTranslator, ClassTranslator
from kugelblitz.translator.expressions import ExprTranslator, BinOpTranslator, BoolOpTranslator, UnaryOpTranslator, CompareTranslator, SubscriptTranslator
from kugelblitz.translator.values import NumTranslator, ListTranslator, NameTranslator, DictTranslator, StrTranslator
from kugelblitz.translator.assignment import AssignTranslator, AugAssignTranslator
from kugelblitz.translator.control import IfTranslator, IfExprTranslator, RaiseTranslator, ReturnTranslator, CallTranslator

def wrap_old_translator(func):
    class WrappedTranslator(BaseTranslator):
        def translate(self):
            return func(self.node)
    return WrappedTranslator

def translate(node):
    return get_translator(node).translate()

def get_translator(node, **kwargs):
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
            ast.Dict: DictTranslator,
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
            ast.Str: StrTranslator,
            ast.Attribute: wrap_old_translator(translate_attribute),
            ast.Subscript: SubscriptTranslator,            
            ast.Name: NameTranslator,
            ast.List: ListTranslator,
            ast.Tuple: ListTranslator,
            
        }[node.__class__](node, **kwargs)
    except TypeError:
        raise CompileError("No translator available for %s." % node.__class__.__name__)

def translate_delete(node):
    return ';\n'.join('delete %s' % translate(n) for n in node.targets)

def translate_attribute(node):
    return "%(left)s.%(right)s" % {
        "left": translate(node.value),
        "right": node.attr,
    }

def translate_string(string):
    return get_translator(ast.parse(string+"\n")).translate()
