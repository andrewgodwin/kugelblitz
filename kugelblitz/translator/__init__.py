try:
    import ast
except ImportError:
    from kugelblitz.lib import ast

def translate(tree, **kwargs):
    return {
        ast.FunctionDef: translate_function,
        ast.Module: translate_module,
        ast.Return: translate_return,
        ast.Name: translate_name,
        ast.ClassDef: translate_class,
        ast.Assign: translate_assign,
        ast.Attribute: translate_attribute,
        ast.Num: translate_num,
        ast.BoolOp: translate_bool_op,
        ast.BinOp: translate_bin_op,
        ast.Expr: lambda n: translate(n.value),
        ast.And: lambda _: '&&',
        ast.Or: lambda _: '||',
        ast.Add: lambda _: '+',
        ast.Sub: lambda _: '-',
        ast.Mult: lambda _: '*',
        ast.Div: lambda _: '/',
        ast.Mod: lambda _: '%',
        ast.LShift: lambda _: '<<',
        ast.RShift: lambda _: '>>',
        ast.BitOr: lambda _: '|',
        ast.BitXor: lambda _: '',
    }[tree.__class__](tree, **kwargs)

def translate_module(node):
    return "\n\n".join(map(translate, node.body))

def translate_function(node, instance_method=False):
    """
    Translates a function. If self_var is not none, it behaves as
    an instance method.
    """
    # Generate argument definition
    body_def = "\n".join(map(translate, node.body))
    if instance_method:
        args_def = ", ".join([arg.id for arg in node.args.args[1:]])
        return "function (%(args_def)s) { %(body_def)s }" % {
            "args_def": args_def,
            "body_def": body_def,
        }
    else:
        args_def = ", ".join([arg.id for arg in node.args.args])
        return "function %(name)s (%(args_def)s) { %(body_def)s }" % {
            "args_def": args_def,
            "body_def": body_def,
            "name": node.name,
        }

def translate_return(node):
    return "return %s;" % translate(node.value)

def translate_name(node):
    if node.id == "self":
        return "this"
    else:
        return node.id
    
def translate_bool_op(node):
    return " ".join(map(translate, [node.values[0], node.op, node.values[1]]))

def translate_bin_op(node):
    if isinstance(node.op, ast.Pow):
        return "Math.pow(%s, %s)" % tuple(map(translate, [node.left, node.right]))
    return " ".join(map(translate, [node.left, node.op, node.right]))

def translate_attribute(node):
    return "%(left)s.%(right)s" % {
        "left": translate(node.value),
        "right": node.attr,
    }

def translate_assign(node):
    assert len(node.targets) == 1, "You can only assign to one thing at once"
    return "%(target)s = %(value)s" % {
        'value': translate(node.value),
        'target': translate(node.targets[0]),
    }

def translate_num(node):
    return str(node.n)

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
    
    
    return "%(name)s = %(init_def)s;\n%(name)s.prototype = { %(method_defs)s }" % {
        'name': node.name,
        'init_def': init_def,
        'method_defs': ",\n".join(body),
    }
