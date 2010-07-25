
class Context(object):
    """
    Represents a variable context.
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.items = {}
    
    def __getitem__(self, key):
        if key in self.items:
            return self.items[key]
        elif self.parent:
            return self.parent[key]
        else:
            raise KeyError("No variable %r in context." % key)
    
    def __setitem__(self, key, value):
        self.items[key] = value
    
    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True