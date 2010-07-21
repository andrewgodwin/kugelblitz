import ast

def translate(tree):
    return {
        ast.FunctionDef: translate_function,
        ast.Module: translate_module,
        ast.Return: translate_return,
        ast.Name: translate_name,
    }[tree.__class__](tree)

def translate_module(node):
    return "\n\n".join(map(translate, node.body))

def translate_function(node):
    # Generate argument definition
    args_def = ", ".join([arg.id for arg in node.args.args])
    body_def = "\n".join(map(translate, node.body))
    return "function (%(args_def)s) { %(body_def)s }" % locals()

def translate_return(node):
    return "return %s;" % translate(node.value)

def translate_name(node):
    return node.id


        