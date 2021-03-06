from kugelblitz.translator.base import ast, BaseTranslator
from kugelblitz.translator.exceptions import CompileError
from kugelblitz.translator.toplevel import (
    ModuleTranslator,
    FunctionTranslator,
    LambdaTranslator,
    ClassTranslator,
)
from kugelblitz.translator.expressions import (
    ExprTranslator,
    BinOpTranslator,
    BoolOpTranslator,
    UnaryOpTranslator,
    CompareTranslator,
    SubscriptTranslator,
    AttributeTranslator,
    DeleteTranslator,
)
from kugelblitz.translator.values import (
    NumTranslator,
    ListTranslator,
    NameTranslator,
    DictTranslator,
    StrTranslator,
)
from kugelblitz.translator.assignment import (
    AssignTranslator,
    AugAssignTranslator,
)
from kugelblitz.translator.control import (
    IfTranslator,
    IfExprTranslator,
    RaiseTranslator,
    ReturnTranslator,
    CallTranslator,
    ForTranslator,
)

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
            
            ast.Delete: DeleteTranslator,
            ast.Assign: AssignTranslator,
            ast.AugAssign: AugAssignTranslator,
            
            ast.Print: None,
            
            ast.For: ForTranslator,
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
            ast.Attribute: AttributeTranslator,
            ast.Subscript: SubscriptTranslator,            
            ast.Name: NameTranslator,
            ast.List: ListTranslator,
            ast.Tuple: ListTranslator,
            
        }[node.__class__](node, **kwargs)
    except TypeError:
        raise CompileError("No translator available for %s." % node.__class__.__name__)

def translate_string(string, module_name=None):
    return get_translator(
        node = ast.parse(string+"\n"),
        module_name = module_name,
    ).translate()
