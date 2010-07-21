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
    
    def test_bin_op(self):
        self.assertCompilesTo('a and b', 'a && b')
        self.assertCompilesTo('a or b', 'a || b')
    
    def test_power(self):
        self.assertCompilesTo('a**b', 'Math.pow(a, b)')
    
    def test_class(self):
        self.assertCompilesTo(
            """
            class Foo(object):
                CONST = 45
                def __init__(self, a):
                    self.a = a
                def bar(self):
                    return self.a
                def baz(self):
                    return 2
            """,
            """
            Foo = function (a) { this.a = a; };
            Foo.prototype = {
                'CONST': 45,
                'bar': function () { return this.a; },
                'baz': function () { return 2; }
            }
            """,
        )
    
    def test_tuple_assignment(self):
        self.assertCompilesTo(
            """
            x, y = 1, 2
            """,
            """
            x = 1;
            y = 2;
            """,
        )
    
    def test_multi_assignment(self):
        self.assertCompilesTo(
            """
            x = y = 1
            """,
            """
            x = 1;
            y = 1;
            """,
        )

if __name__ == "__main__":
    unittest.main()
