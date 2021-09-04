class cached_class_property(object):
    r'''A read-only @property that is only evaluated once per class.
        May be read from the class level, as well as from instances.
        
        >>> class A(object):
        ...   @class_property
        ...   def b(self):
        ...     print "Calculating."
        ...     return 42
        >>> type(A.__dict__["b"]) is class_property
        True
        >>> a = A()
        >>> a.__dict__
        {}
        >>> a.b
        Calculating.
        42
        >>> a.__dict__
        {}
        >>> A.b
        42
        >>> A().b
        42
        >>> A.__dict__["b"]
        42
        >>> type(A.__dict__["b"]) is int
        True
    '''#"""#'''
    
    def __init__(self, method):
        self.fget = method
        self.__doc__ = method.__doc__
        self.__name__ = method.__name__
    
    def __get__(self, instance, cls=None):
        result = self.fget(cls)
        setattr(cls, self.__name__, result)
        return result
