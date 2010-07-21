import unittest
try:
    import ast
except ImportError:
    from kugelblitz.lib import ast
from kugelblitz.translator import translate

class SimpleTests(unittest.TestCase):
    
    def num_spaces_left(self, line):
        """
        Returns the number of blank spaces on the left of a line.
        """
        for i, char in enumerate(line):
            if char != " ":
                return i
        return 0
    
    def unindent_code(self, code):
        """
        Given a string that's got extra indenting (because it's an intended
        multi-line test input or docstring) unindent it so python's parser
        is happy.
        """
        min_space_run = min([
            self.num_spaces_left(line) 
            for line in code.split("\n")
            if line.strip(" ")
        ])
        return "\n".join([
            line[min_space_run:]
            for line in code.split("\n")
        ])
    
    def assertCompilesTo(self, source, output):
        """
        Assertion that the source compiles to the output.
        Doesn't fail horribly on whitespace differences.
        """
        compiled = translate(ast.parse(self.unindent_code(source)))
        self.assertEqual(
            " ".join(compiled.split()),
            " ".join(output.split()),
        )
    
    def test_function(self):
        self.assertCompilesTo(
            """
            def x(a, b):
               return a
            """,
            """
            function x (a, b) {
                return a;
            }
            """,
        )
    
    def test_bool_op(self):
        self.assertCompilesTo('a and b', 'a && b')
        self.assertCompilesTo('a or b', 'a || b')
    
    def test_bin_op(self):
        for o in ['+', '-', '*', '%', '<<', '>>', '|', '^', '&']:
            expr = 'a %s b' % o
            self.assertCompilesTo(expr, expr)
        self.assertCompilesTo('a // b', 'a / b')
    
    def test_power(self):
        self.assertCompilesTo('a**b', 'Math.pow(a, b)')
    
    def test_unary_op(self):
        for o in ['~', '+', '-']:
            expr = '%sa' % o
            self.assertCompilesTo(expr, expr)
        self.assertCompilesTo('not a', '!a')
    
    def test_lambda(self):
        self.assertCompilesTo(
            """
            lambda: 1
            """,
            """
            function() {
                return 1;
            }
            """
        )
        self.assertCompilesTo(
            """
            lambda a: a + 1
            """,
            """
            function(a) {
                return a + 1;
            }
            """
        )
    
    def test_class(self):
        self.assertCompilesTo(
            """
            class Foo(object):
                def __init__(self, a):
                    self.a = a
                def bar(self):
                    return self.a
                def baz(self):
                    return 2
            """,
            """
            Foo = function (a) { this.a = a };
            Foo.prototype = {
                'bar': function () { return this.a; },
                'baz': function () { return 2; }
            }
            """,
        )

if __name__ == "__main__":
    unittest.main()
