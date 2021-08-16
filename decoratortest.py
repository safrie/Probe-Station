# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

class Length:
    """Taken from https://github.com/python/cpython/blob/bb3e0c240bc60fe08d332ff5955d54197f79751c/Doc/howto/descriptor.rst
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        # print('test = ', test)
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self._name = ''
        print('initting')
        print('self.fget = ', fget)
        print('self.fset = ', fset, '\n')
        #self._name = fget.__name__
        # print(self._name)
        
    def __set_name__(self, owner, name):
        self._name = name
        print(f'using __set_name__, name = {self._name}\n')
        
    def __get__(self, obj, objtype=None):
        print('calling __get__')
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f'unreadable attribute {self._name}')
        print(f'using __get__, self._name = {self._name}')
        return self.fget(obj)
    
    def __set__(self, obj, value):
        print('calling __set__')
        if self.fset is None:
            raise AttributeError(f"can't set attribute {self._name}")
        if value <= 0:
            raise ValueError("Length must be positive")
        print(f'in __set__, self._name = {self._name}')
        self.fset(obj, value)
        
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError(f"can't delete attribute {self._name}")
        self.fdel(obj)
        
    def getter(self, fget):
        print('calling getter')
        prop = type(self)(fget, self.fset, self.fdel, self.__doc__)
        prop._name = self._name
        return prop
    
    def setter(self, fset):
        print('calling setter')
        prop = type(self)(self.fget, fset, self.fdel, self.__doc__)
        prop._name = self._name
        return prop
    
    def deleter(self, fdel):
        prop = type(self)(self.fget, self.fset, fdel, self.__doc__)
        prop._name = self.name
        return prop
    
        
class Circle:
    def __init__(self, radius):
        print('init circle')
        self.radius = radius
        
    @Length
    def radius(self):
        print('setting up radius')
        return self._radius
    
    @radius.setter
    def radius(self, value):
        print('setting up setter')
        self._radius = value
        
    @property
    def diameter(self):
        print('diametering')
        return self._radius * 2



#%%
from abc import ABC, abstractmethod
from functools import wraps

class Info:
    fixed = {'txt': {0: 'a',
                     1: 'b',
                     2: 'c'},
             'def': 0}
    def __init__(self):
        self.t = {'lim': range(-5, 6),
                  'def': 2}
        self.v = {'vim': (-30, 30),
                  'def': 15.5}
        self.w = {'txt': {0: 'aa',
                          1: 'bb',
                          2: 'cc'},
                  'def': 0,
                  'mess': {'big': {0: 'messy',
                                   1: 'messier',
                                   2: 'messiest'},
                           'small': {3: "neat",
                                     4: 'neater',
                                     5: 'neatest'}}
                  }

class Info0(Info):
    def __init__(self):
        super().__init__()
        self.t['lim'] = range(-6, 7)
        self.t['def'] = -4

class Info1(Info):
    def __init__(self):
        super().__init__()
        self.v['vim'] = (-25, 25)
        self.v['def'] =  -12

class Info2(Info):
    def __init__(self):
        super().__init__()
        self.t['lim'] = range (-10, 11)
        self.t['def'] = 7
        self.v['vim'] = (-10, 10)
        self.v['def'] = 0


ivinfo = {'dic': {0: Info0,
                  1: Info1,
                  2: Info2}}


class ValABC(ABC):
    def __init__(self, fget, fset):
        print('ABC __init__\n')
        self.fget = fget
        self.fset = fset
        self.public_name = ''
        self.private_name = ''
        self.valkey = ''

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, func, owner):
        print('using __get__')
        return self.fget(func)

    def __set__(self, func, value):
        """"Validate the value we're tyring to set instance to, then execute.
        
        The way this works is first, get the 'key' var from fset ('key' was
        assigned to fset by the decorator infoset).  Then, get the bounds by
        looking up the value of 'key' in the info attribute associated
        with the function being set.  If the key leads to a dict object, set
        the bounds to info.name[key].keys().  Pass these bounds and the
        proposed value to validate to see if it raises a ValueError.  If it
        doesn't, go ahead and set the value. Done!
        """
        name = self.public_name
        limkey = self.fget.key
        print('limkey type = ', type(limkey))
        lims = getattr(func.info, name)[limkey]
        print('old lims = ', lims)

        def unpack(dct):
            for key, val in dct.items():
                if isinstance(val, dict):
                    yield from unpack(val)
                else:
                    yield key

        if isinstance(lims, dict):
            lims = list(unpack(lims))
        print('new lims = ', lims)
        self.validate(value, lims)
        self.fset(func, value)

    def setter(self, fset):
        """Reinitialize valABC with the given fset function."""
        prop = type(self)(self.fget, fset)
        prop.private_name = self.private_name
        return prop

    def getter(self, fget):
        prop = type(self)(fget, self.fset)
        prop.private_name = self.private_name
        return prop

    @abstractmethod
    def validate(self, value, lims):
        # This will involve the kwarg from init
        pass


class OneOf(ValABC):
    """Validator for dropdown menu options"""
    def __init__(self, fget=None, fset=None):
        super().__init__(fget, fset)

    def validate(self, value, lims):
        print('value = ', value, '\n', 'lims = ', lims)
        if value not in lims:
            raise ValueError(f'Expected {value!r} to be in {lims!r}')


class Number(ValABC):
    """Validator for continuous variables, such as current"""
    def __init__(self, fget=None, fset=None):
        super().__init__(fget, fset)

    def validate(self, value, lims):
        if not lims[0] <= value <= lims[1]:
            raise ValueError(f'Expected {value!r} to be between {lims}')


def infoset(key):
    """Decorator to set the dictionary """
    def wrapper(func):
        # TODO: Deterime if want to return the key in a tuple..? public a
        func.key = key
        return func
    return wrapper


class Test:
    """This class tests whether my validator with varying keys works"""
    measkey = ivinfo['dic'].keys()
    fixed = Info().fixed['def']

    def __init__(self, meas_idx, tval=0, vval=0):
        print('Test initting')
        self.info = ivinfo['dic'][meas_idx]()
        self._meas_idx = meas_idx
        self.v = vval
        self.t = tval
        self.w = self.info.w['def']
        # self.v = vval
        # print('tkey = ', self.t.key)

    @property
    def meas_idx(self):
        return self._meas_idx

    @OneOf
    @infoset('lim')
    def t(self):
        print('setting up t')
        return self._t

    @t.setter
    @infoset('lim')
    def t(self, value):
        print('using t setter in Test')
        self._t = value

    @Number
    @infoset('vim')
    def v(self):
        return self._v

    @v.setter
    @infoset('vim')
    def v(self, value):
        self._v = value

    @infoset('mess')
    def w(self):
        return self._w

    @w.setter
    @infoset('mess')
    def w(self, value):
        self._w = value

    @property
    def tbyv(self):
        return self._t * self._v


test = Test(0, 0, 10)


#%%
w = {'txt': {0: 'aa',
             1: 'bb',
             2: 'cc'},
     'def': 0,
     'mess': {'big': {0: 'messy',
                      1: 'messier',
                      2: 'messiest'},
              'small': {3: "neat",
                        4: 'neater',
                        5: 'neatest'}}
     }


def unpack(dct):
    for key, val in dct.items():
        if isinstance(val, dict):
            yield from unpack(val)
        else:
            yield key
# def unpack(data):
#     try:
#         for k, value in data.items():
#             print('k = ', k)
#             yield from unpack(value)
#     except AttributeError:
#         yield k


data = w['mess']
print('dataype = ', type(data))
unpacked = list(unpack(data))
print(2 in unpacked)
print(unpacked)

data2 = w['txt']
print(list(unpack(data2)))

#%%


def basic(a, b):
    return a, b
