from kugelblitz.translator.base import ast, BaseTranslator
from kugelblitz.translator.exceptions import CompileError
from kugelblitz.translator.toplevel import ModuleTranslator, FunctionTranslator
from kugelblitz.translator.expressions import ExprTranslator, BinOpTranslator, BoolOpTranslator, UnaryOpTranslator, CompareTranslator
from kugelblitz.translator.values import NumTranslator, ListTranslator, NameTranslator

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
            ast.ClassDef: wrap_old_translator(translate_class),
            ast.Return: wrap_old_translator(translate_return),
            
            ast.Delete: wrap_old_translator(translate_delete),
            ast.Assign: wrap_old_translator(translate_assign),
            ast.AugAssign: wrap_old_translator(translate_aug_assign),
            
            ast.Print: None,
            
            ast.For: None,
            ast.While: None,
            ast.If: wrap_old_translator(translate_if),
            ast.With: None,
            
            ast.Raise: wrap_old_translator(translate_raise),
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
            ast.Lambda: wrap_old_translator(translate_lambda),
            ast.IfExp: wrap_old_translator(translate_if_exp),
            ast.Dict: None,
            #ast.Set: None, Not in 2.6
            ast.ListComp: None,
            #ast.SetComp: None, Not in 2.6
            #ast.DictComp: None, Not in 2.6
            ast.GeneratorExp: None,
            ast.Yield: None,
            ast.Compare: CompareTranslator,
            ast.Call: wrap_old_translator(translate_call),
            ast.Repr: None,
            ast.Num: NumTranslator,
            ast.Str: None,
        
            ast.Attribute: wrap_old_translator(translate_attribute),
            ast.Subscript: wrap_old_translator(translate_subscript),
            
            #ast.Attribute: translate_attribute,
            #ast.Subscript: translate_subscript,
            ast.Name: NameTranslator,
            ast.List: ListTranslator,
            ast.Tuple: ListTranslator,
            
            # cmpop
        }[node.__class__](node)
    except TypeError:
        raise CompileError("No translator available for %s." % node.__class__.__name__)

def translate_body(body, line_separator='\n'):
    s = []
    for node in body:
        if isinstance(node, (ast.If,)):
            s.append(translate(node))
        else:
            s.append('%s;' % translate(node))
    return '\n'.join(s)

def translate_function(node, instance_method=False):
    """
    Translates a function. If self_var is not none, it behaves as
    an instance method.
    """
    # Generate argument definition
    if instance_method:
        args_def = ", ".join([arg.id for arg in node.args.args[1:]])
        return "function (%(args_def)s) { %(body_def)s }" % {
            "args_def": args_def,
            "body_def": translate_body(node.body),
        }
    else:
        args_def = ", ".join([arg.id for arg in node.args.args])
        return "var %(name)s = function (%(args_def)s) { %(body_def)s }" % {
            "args_def": args_def,
            "body_def": translate_body(node.body),
            "name": node.name,
        }

def translate_class(node):
    
    # Is there an __init__?
    functions = {}
    assigns = {}
    classes = {}
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            functions[item.name] = item
        elif isinstance(item, ast.Assign):
            assert len(item.targets) == 1, "You can only assign to a single item."
            assert isinstance(item.targets[0], ast.Name), "You can only assign to simple names in classes"
            assigns[item.targets[0].id] = item.value

    # Make constructor def
    if "__init__" in functions:
        init_def = translate_function(functions['__init__'], instance_method=True)
    else:
        init_def = "function () {}"
    
    # Make other defs
    body = []
    for aname, anode in sorted(assigns.items()):
        body.append("'%s': %s" % (
            aname,
            translate(anode),
        ))
    
    # Make method defs
    for fname, fnode in sorted(functions.items()):
        if fname != "__init__":
            body.append("'%s': %s" % (
                fname,
                translate_function(fnode, instance_method=True),
            ))
    
    return "var %(name)s = %(init_def)s;\n%(name)s.prototype = { %(method_defs)s }" % {
        'name': node.name,
        'init_def': init_def,
        'method_defs': ",\n".join(body),
    }

def translate_return(node):
    return "return %s" % translate(node.value)

def translate_delete(node):
    return ';\n'.join('delete %s' % translate(n) for n in node.targets)

def translate_single_assign(target, value):
    if isinstance(target, ast.Name):
        return "var %(target)s = %(value)s" % {
            'target': translate(target),
            'value': translate(value),
        }
    else:
        return "%(target)s = %(value)s" % {
            'target': translate(target),
            'value': translate(value),
        }
    
def translate_assign(node):
    # For each target...
    statements = []
    for target in node.targets:
        # Is it a tuple-to-tuple assignment?
        if isinstance(target, ast.Tuple):
            # Is the RHS a tuple?
            if isinstance(node.value, ast.Tuple):
                # Make sure they're the same length
                if len(target.elts) != len(node.value.elts):
                    raise CompileError("Assigning one tuple to another of different length.")
                for t, v in zip(target.elts, node.value.elts):
                    statements.append(translate_single_assign(t, v))
            # No? Raise an error for now.
            else:
                raise CompileError("Assigning a non-tuple to a tuple.")
        else:
            statements.append(translate_single_assign(target, node.value))
    return ";\n".join(statements)

def translate_aug_assign(node):
    return '%(target)s %(op)s= %(value)s' % {
        'target': translate(node.target),
        'op': translate(node.op),
        'value': translate(node.value),
    }

def translate_lambda(node):
    return "function (%(args_def)s) {\nreturn %(body_def)s\n}" % {
        'args_def': ", ".join([arg.id for arg in node.args.args]),
        'body_def': translate_body([node.body]),
    }

def translate_if(node):
    s = ["if (%(test_def)s) { %(body_def)s }" % {
        'test_def': translate(node.test),
        'body_def': translate_body(node.body),
    }]
    if node.orelse:
        s.append("else { %(orelse_def)s }" % {
            's': s,
            'orelse_def': translate_body(node.orelse),
        })
    return '\n'.join(s)

def translate_if_exp(node):
    return '%(test)s ? %(body)s : %(orelse)s' % {
        'test': translate(node.test),
        'body': translate(node.body),
        'orelse': translate(node.orelse),
    }

def translate_attribute(node):
    return "%(left)s.%(right)s" % {
        "left": translate(node.value),
        "right": node.attr,
    }

def translate_num(node):
    return str(node.n)

def translate_call(node):
    func = translate(node.func)
    if func == 'isinstance':
        if len(node.args) != 2:
            raise TypeError("isinstance expected 2 arguments, got %s" % len(args))
        s = []
        if isinstance(node.args[1], (ast.List, ast.Tuple)):
            for n in node.args[1].elts:
                s.append("%s instanceof %s" % (
                    translate(node.args[0]),
                    translate(n),
                ))
        else:
            s.append("%s instanceof %s" % tuple(map(translate, node.args)))
        return " || ".join(s)
    elif func == 'len':
        if len(node.args) != 1:
            raise TypeError("len() takes exactly one argument (%s given)" % len(args))
        return "%s.length" % translate(node.args[0])
    args_def = ", ".join(map(translate, node.args))
    return "%(func)s(%(args_def)s)" % {
        "func": func,
        "args_def": args_def,
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

def translate_raise(node):
    return "throw"

if __name__ == "__main__":
    import sys
    print get_translator(ast.parse(sys.stdin.read()+"\n")).translate()
