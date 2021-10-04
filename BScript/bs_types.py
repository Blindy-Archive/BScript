from functools import reduce
from BScript import exceptions
def raise_exception(exception):
  raise exception
class BS_type(object):
  name = ""
  def __sub_init__(cls,*args,**kwargs):
    cls.name = cls.__name__
    return cls()
undefined = type("undefined",(BS_type,),{
# "__init__":lambda self: raise_exception(TypeError("undefined is not a function")),
"__str__":lambda self: "undefined",
"__repr__":lambda self: "undefined",
"__name__":"undefined",
"__setattribute__":lambda self,name,value: raise_exception(TypeError("Cannot set property '{name}' of undefined")),
"__getattribute__":lambda self,name:  raise_exception(TypeError(f"Cannot read property '{name}' of undefined")) if name != "__class__" else undefined
})

def variable2BS(value):
      if isinstance(value,BS_type):
        return value
      elif isinstance(value,bool):
        return bool(value)
      elif isinstance(value,int):
        return BS_int(value)
      elif isinstance(value,dict):
        return BS_object(value)
      elif isinstance(value,str):
        return BS_string(value)
      elif isinstance(value,tuple):
        return BS_array(value)
      elif isinstance(value,list):
        return BS_array(value)
      return value
class AssignableObject():
  def __init__(self,obj,attr):
    self.obj = obj
    self.attr = attr
  def __call__(self,value):

    if isinstance(self.obj,BS_object):
      BS_object.setitem(self.obj,self.attr,value)
    else:
      self.obj[self.attr] = value

class required(BS_type):
  pass
def flatten(itemlist):
   """tests if itemlist is a list and how many dimensions it has
   returns -1 if it is no list at all, 0 if list is empty 
   and otherwise the dimensions of it"""
   flatten_list = []
   for item in itemlist:
    if isinstance(item,list) and not isinstance(item,BS_array):
      
      flatten_list.extend(flatten(item))
    else:
      flatten_list.append(item)
   return flatten_list
   
__reserveds__ = set(dict().__class__.__dict__.keys())
__reserveds__.add("__reserveds__")
__reserveds__.add("__private__")
__reserveds__.add("setattr")
__reserveds__.add("this")
__private__ = __reserveds__.copy()^{"clear","copy","fromkeys","get","items","keys","pop","popitem","setdefault","update","values"}

__reserved__keys__ = {"this","undefined","Infinity"}
__reserveds__.add("__private__")
__protected__ = {"__class__"}
class BS_object(BS_type,dict):
    
      
    
  def __init__(self, *args, **kwargs):
        super(BS_object, self).__init__(*args, **kwargs)
        self.this = self
        for i in {"clear","copy","fromkeys","get","items","keys","pop","popitem","setdefault","update","values","setitem","getitem"}:
          if hasattr(self,i):
            setattr(self,i,undefined())
  # def __init__(self, *args, **kwargs):
  #   self.__reserveds__ = set(dict().__class__.__dict__.keys())
  #   self.update(*args, **kwargs)
  #   self.this = self
  def __getattribute__(self,name):
    if name == "__class__":
      return super().__getattribute__(name)
    
    else:
      if name in self:
        return dict.__getitem__(self,name)
      else:
        return super().__getattribute__(name)
  
  
  def setitem(self,key,val):
    self[key] = val
  def getitem(self,key):
    return self[key]
NoneType = type(None)

class BS_int(BS_type,int):
  def toString(self):
    return BS_string(self.__str__())
slicer = {
(NoneType,BS_int):lambda obj,x,y: obj[:y],
(BS_int,NoneType):lambda obj,x,y: obj[x:],
(BS_int,BS_int):lambda obj,x,y: obj[x:y]

}
class BS_string(BS_type,str):
  def __new__(cls, *args, **kw):
    cls.toUpperCase = cls.upper
    cls.toLowerCase = cls.lower
    cls.trim = cls.strip
    cls.padStart = cls.rjust 
    cls.padEnd = cls.ljust
    cls.indexOf = cls.index
    cls.lastIndexOf = cls.rindex
    cls.search = cls.find
    cls.includes = lambda self,text: text in self
    cls.startsWith = cls.startswith
    cls.endsWith = cls.endswith
    return str.__new__(cls, *args, **kw)
  @property
  def length(self):
    return self.__len__()
  def slice(self, start=None,end=None):
    t = (type(start),type(end))
    return slicer.get(t)(self,start,end)
  def substring(self, start, end):
    assert start >= 0 and end >= 0, "substring method only can accept positive integers"
    assert  start <= end, "start must be smaller than end" 
    return self[start:end]
  def substr(self, start, length=0):
    return self[start:] if length == 0 else self[start:start+length]
  def concat(self, *other):
    return self+"".join(other)
  def charAt(self,position: int):
    return self[position]
  def charCodeAt(self,position: int):
    return ord(self[position])
  def split(self,seperator: str = None):
    if seperator == "":
      return list(self)
    elif seperator is None:
      raise ValueError("empty separator")
    else:
      return super().split(seperator)
      

class BS_array(BS_type,list):
  def toString(self):
    return ",".join(self)
  def join(self,chr):
    return chr.join(self)
  def push(self,element):
    self.append(element)
    return self.__len__()
  def shift(self,element=0):
    return self.pop(element)
  def unshift(self,element,index=0):
    self.insert(index,element)
    return self.__len__()
  @property
  def length(self):
    return self.__len__()
  def splice(self,start,delete,*args):
    removed_items = self[start:start+delete]
    del self[start:start+delete]
    for item in args:
      self.insert(start,item)
      start+=1
    return removed_items
  def concat(self,*args):
    new_list = self.copy()
    for item in args:
      new_list+=item
    return new_list
  def slice(self, start=None,end=None):
    t = (type(start),type(end))
    return slicer.get(t)(self,start,end)
  def toString(self):
    return BS_string(",".join(self))
  def sort(self,key=lambda x:x,reverse=False):
    super(BS_array, self).sort(key=key,reverse=reverse)
  def min(self):
    return variable2BS(min(self))
  def max(self):
    return variable2BS(max(self))
  def forEach(self,function):
    
    for index,value in enumerate(self):
      temp_kwargs = {"index":variable2BS(index),"value":variable2BS(value),"array":self.copy()}
      
      function(**{k:temp_kwargs[k] for k in function.args})
  def map(self,function):
    new_array = BS_array()
    for index,value in enumerate(self):
      temp_kwargs = {"index":variable2BS(index),"value":variable2BS(value),"array":self}
      
      new_array.append(variable2BS(function(**{k:temp_kwargs[k] for k in function.args})))
    return new_array
      
  def filter(self,function):
    new_array = BS_array()
    for index,value in enumerate(self):
      temp_kwargs = {"index":variable2BS(index),"value":variable2BS(value),"array":self}
      if variable2BS(function(**{k:temp_kwargs[k] for k in function.args})):
      
        new_array.append(value)
    return new_array

class BS_break: pass
class BS_continue: pass