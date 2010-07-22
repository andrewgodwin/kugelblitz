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
            var x = function (a, b) {
                return a;
            };
            """,
        )
    
    def test_bool_op(self):
        self.assertCompilesTo('a and b', '(a && b);')
        self.assertCompilesTo('a or b', '(a || b);')
    
    def test_bin_op(self):
        for o in ['+', '-', '*', '%', '<<', '>>', '|', '^', '&']:
            self.assertCompilesTo('a %s b' % o, '(a %s b);' % o)
        self.assertCompilesTo('a // b', '(a / b);')
    
    def test_grouped_bin_op(self):
        self.assertCompilesTo('a * (b + c)', '(a * (b + c));')
    
    def test_power(self):
        self.assertCompilesTo('a**b', 'Math.pow(a, b);')
    
    def test_unary_op(self):
        for o in ['~', '+', '-']:
            self.assertCompilesTo('%sa' % o, '%sa;' % o)
        self.assertCompilesTo('not a', '!a;')
    
    def test_lambda(self):
        self.assertCompilesTo(
            """
            lambda: 1
            """,
            """
            function() {
                return 1;
            };
            """
        )
        self.assertCompilesTo(
            """
            lambda a: a + 1
            """,
            """
            function(a) {
                return (a + 1);
            };
            """
        )
    
    def test_if(self):
        self.assertCompilesTo(
            """
            if x and y:
                return 1
            """,
            """
            if ((x && y)) {
                return 1;
            }
            """
        )
        self.assertCompilesTo(
            """
            if x:
                return 1
            else:
                return 0
            """,
            """
            if (x) {
                return 1;
            }
            else {
                return 0;
            }
            """
        )
        self.assertCompilesTo(
            """
            if x:
                if y:
                    return y
                else:
                    return x
            else:
                return 0
            """,
            """
            if (x) {
                if (y) {
                    return y;
                }
                else {
                    return x;
                }
            }
            else {
                return 0;
            }
            """
        )
        self.assertCompilesTo(
            """
            if x:
                return x
            elif y:
                return y
            else:
                return 0
            """,
            """
            if (x) {
                return x;
            }
            else {
                if (y) {
                    return y;
                }
                else {
                    return 0;
                }
            }
            """
        )
    
    def test_if_exp(self):
        self.assertCompilesTo(
            """
            a = x if y else z
            """,
            """
            a = y ? x : z;
            """
        )
    
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
            var Foo = function (a) { this.a = a; };
            Foo.prototype = {
                'CONST': 45,
                'bar': function () { return this.a; },
                'baz': function () { return 2; }
            };
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
    
    def test_bracketing(self):
        self.assertCompilesTo(
            """
            (1 + 2) * (3 + 4)
            """,
            """
            ((1 + 2) * (3 + 4));
            """,
        )
    
    def test_function_call(self):
        self.assertCompilesTo(
            """
            def foo(x, y, z):
                return x + y
            foo(1, 2, 3)
            """,
            """
            var foo = function (x, y, z) {
                return (x + y);
            };
            foo(1, 2, 3);
            """,
        )
    
    def test_is_instance(self):
        self.assertCompilesTo(
            """
            isinstance(x, Foo)
            """,
            """
            x instanceof Foo;
            """
        )
        # self.assertCompilesTo(
        #     """
        #     isinstance(x, (Foo, Bar))
        #     """,
        #     """
        #     x instanceof Foo || x instanceof Bar;
        #     """
        # )
        # self.assertCompilesTo(
        #     """
        #     isinstance(x, [Foo, Bar])
        #     """,
        #     """
        #     x instanceof Foo || x instanceof Bar;
        #     """
        # )
    
    def test_compare(self):
        self.assertCompilesTo(
            """
            3 == 4
            """,
            """
            3 == 4;
            """,
        )
        
    def test_slice(self):
        self.assertCompilesTo(
            """
            x = [1,2,3]
            y = x[1:2]
            """,
            """
            x = [1, 2, 3];
            y = x.slice(1, 2);
            """,
        )
        
    def test_complex_class(self):
        self.assertCompilesTo(
            """
            class Vector(object):
    
                '''
                A 2D vector class.
                '''
                
                def __init__(self, x, y=None):
                    if y == None:
                        if isinstance(x, Vector):
                            self.x, self.y = x.x, x.y
                        elif len(x) == 2:
                            self.x, self.y = x[0], x[1]
                        else:
                            raise ValueError("Please pass either a tuple of (x, y), a Vector, or two parameters.")
                    else:
                        self.x = x
                        self.y = y
                
                def __add__(self, other):
                    return Vector(self.x+other.x, self.y+other.y)
            """,
            """
            var Vector = function (x, y) {
                if (y == None) {
                    if (isinstance(x, Vector)) {
                        this.x = x.x;
                        this.y = x.y;
                    }
                    else {
                        if (len(x) == 2) {
                            this.x = x[0];
                            this.y = x[1];
                        }
                        else {
                            throw;
                        }
                    }
                }
                else {
                    this.x = x;
                    this.y = y;
                }
            };
            Vector.prototype = {
                '__add__': function (other) {
                    return Vector((this.x + other.x), (this.y + other.y));
                }
            };
            """,
        )
        

if __name__ == "__main__":
    unittest.main()
