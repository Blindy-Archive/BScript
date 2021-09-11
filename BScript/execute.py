from itertools import chain
import itertools
import os,requests
import tkinter as tk
import importlib
from BScript import exceptions
import sys,asyncio
from BScript.bs_types import *
string_indicators = {
'"',
"'"
}
binary_expressions = {
  "+":lambda x,y: x + y,
  "-":lambda x,y: x - y,
  "*":lambda x,y: x * y,
  "/":lambda x,y: x / y,
  "==":lambda x,y: x == y,
  "===": lambda x,y: type(x) is type(y) and x==y,
  "!=":lambda x,y: x != y,
  "^":lambda x,y: x^y,
  ">":lambda x,y: x > y,
  "<":lambda x,y: x < y,
  ">=":lambda x,y: x >= y,
  "<=":lambda x,y: x <= y,
}
unary_expressions = {
  "-":lambda x: x*-1,
  "delete":lambda x: x,
  "--":lambda x: x-1,
  "++":lambda x: x+1
}
assignment_expressions = {
  "*=":lambda x,y: x * y,
  "-=":lambda x,y: x - y,
  "/=":lambda x,y: x / y,
  "+=":lambda x,y: x + y,
  "^=":lambda x,y: x^y

}

bool_indicators = {"true":True,"false":False,"False":False,"True":True}

__importables__ = \
{
"os":os,
"tk":tk
}
__reserveds__ = set(dict().__class__.__dict__.keys())
__reserveds__.add("__reserveds__")

__reserveds__.add("__private__")
__private__ = __reserveds__.copy()^{"clear","copy","fromkeys","get","items","keys","pop","popitem","setdefault","update","values"}

__reserved__keys__ = {"this","undefined","Infinity"}
__reserveds__.add("__private__")
__protected__ = {"__class__"}
__globals__ = {}

class environment(dict):
  
  def __init__(self, *args,locked=False, **kwargs):
    _args = []
    _kwargs = {}
    for arg in args:
      temp_dict = {}
      for k,v in arg.items():
        temp_dict[k] = variable2BS(v)
      _args.append(temp_dict)
    for k,v in kwargs.items():
      _kwargs[k] = variable2BS(v)
    
    self.locked = locked
    super(environment, self).__init__(*_args, **_kwargs)
    dict.__setitem__(self,"this",self)
    self.__class__ = environment
    self.__constants__ = set()
    self.locked = locked


    dict.__setitem__(self,"Infinity",float("inf"))
  def get_env(self):
    if self.locked:
      return self
  def __getitem__(self,key):
    if key in __globals__:
      return dict.__getitem__(__globals__,key)
    return dict.__getitem__(self, key)
  def get(self,key,default=None):
    if key in self.__globals__:
      return self.__globals__.get(key)
    return super(environment,self).get(key,default)
  def __contains__(self, key):
    return dict.__contains__(self,key) or dict.__contains__(__globals__,key)
  def __setitem__(self,key,value):
    if key in __reserved__keys__:
      raise ValueError(f"'{key}' cannot be set due to its protection level")
    elif key in self.__constants__:
      raise TypeError("Assignment to constant variable.")
    elif key in __globals__:
      dict.__setitem__(__globals__,key,variable2BS(value))
    else:
      dict.__setitem__(self,key,variable2BS(value))
  def __getattribute__(self,name):
    if name in __private__:
      raise ValueError(f"'{name}' is inaccessible due to its protection level")
    elif name in __protected__:
      return self
    return super(environment,self).__getattribute__(name)
  def __add_global__(self,kwargs):
    for name,value in kwargs.items():
      if name in __globals__ or name in self:
        raise SyntaxError(f"Identifier '{name}' has already been declared")

      __globals__[name] = variable2BS(value)
      
  def __add_const__(self,kwargs):
    for name,value in kwargs.items():
      if name in self.__constants__ or name in self or name in __globals__:
        raise SyntaxError(f"Identifier '{name}' has already been declared")
      self[name] = variable2BS(value)
      self.__constants__.add(name)
  def __setattr__(self,name,value):
    if name in __reserveds__ or name in __private__:
      raise ValueError(f"'{name}' cannot be set due to its protection level")
    super(environment,self).__setattr__(name,variable2BS(value))


def raise_exception(exception):
  raise exception
class BS_function(object):
    def __init__(self, script,executor,parent=None):
        self.executor = executor
        if (ids:=script.get("id")) and (name:=ids.get("name")):
          setattr(self,"__name__",name) 
        else:
          setattr(self,"__name__","function")
        self.script = script
        self.executor = executor
        self.variables = environment({k["name"]:executor.calls[v.get("type")](**v) if v else required() for k,v in list(itertools.zip_longest(script["params"], script["defaults"]))})
        self.parent = parent
        # if parent is not None:
        #   self.variables["this"] = parent
        # else:
        #   self.variables["this"] = self
        self.args = [k for k,v in self.variables.items() if isinstance(v,required) ]
        self.kwargs = [k for k,v in self.variables.items() if not isinstance(v,required)]
        self.args_len = len(self.args)
        self.body = script["body"]
    def __raise_exception__(self,exception):
      raise exception
    def __difference__dict__(self,first,other):
      return {k:v   for k,v in first.items() if  k not in other}
    def __call__(self,*args,**kwargs):
      
      variables = environment()
      variables.update(self.executor.variables.copy())
      variables.update(self.variables)
      k_words = {k:v for k,v in zip(self.kwargs[:abs(self.args_len - len(args))],args[abs(self.args_len - len(args)):])}
      self_args = [arg for arg in self.args if arg not in kwargs.keys()]
      value = { k : kwargs[k]  for k in set(kwargs) - set(k_words) if k in self.args  }
      kwargs = self.__difference__dict__(kwargs,value)
      variables.update(value)
      args_len = len(self_args) 
      args = args[:args_len]
      variables.update(k_words)
      args_length = len(args)
      if args_length < args_len:
        raise TypeError(f"{self.__name__}() missing {args_len -args_length} required positional argument: {'and'.join(self.args[args_len - args_length:])}")
      for x,y in zip(self.args,args):
        variables[x] = y

      for k, (k2,v2) in zip(self.kwargs,kwargs.items()):
        if k2 not in self.kwargs:
          raise TypeError(f"{self.__name__}() got an unexpected keyword argument: {k2}")
        else:
          variables[k] = v2
      return BS_executor(env_name=self.get_env_name(),variables=variables,parent=self.parent)(self.body)
    def get_env_name(self):
      return self.executor.env_name+"."+getattr(self,"__name__")
    def __str__(self):
      return self.get_env_name()
    def get_as_async(self):
      return BS_async_function(self.script,self.executor,self.parent)
      
class BS_async_function(BS_function):
    def __init__(self, script,executor,parent):
        super(BS_async_function,self).__init__(script,executor,parent)
    async def __call__(self,*args,**kwargs):
      variables = self.variables.copy()
      args_length = len(args)
      for k1,k2 in  itertools.zip_longest(kwargs.keys(),self.kwargs):
        if k1 is not None and k1 != k2:
          raise TypeError(f"{self.__name__}() got unexpected keyword argument '{k1}'")
      if args_length < (args_len:=len([i for i in self.args if i not in kwargs])):
        raise TypeError(f"{self.__name__}() missing {args_len -args_length} required positional argument: {'and'.join(self.args[args_len - args_length:])}")
      # elif args_length > (args_len:=len([i for i in self.args if i  in kwargs])):
      #   raise TypeError(f"{self.__name__}() waited for {args_len} required positional argument, but given '{args_length}' positional argument")
      
        
      for x,y in zip(self.args,args):
        variables[x] = y
      for k, (k2,v2) in  zip(self.kwargs,kwargs.items()):
        if k2 not in self.kwargs:
          raise TypeError(f"{self.__name__}() got an unexpected keyword argument: {k2}")
        else:
          variables[k] = v2
      variables.update(self.executor.variables)
      return BS_executor(env_name=self.get_env_name(),variables=variables,parent=self.parent)(self.body)
    def get_env_name(self):
      return self.executor.env_name+"."+getattr(self,"__name__")
    def __str__(self):
      return self.get_env_name()
    def get_as_async():
      pass
class BS_executor(object):
    def __init__(self,env_name="__main__",variables={},sandbox_mode=True,__importables__=__importables__,mem_size=8000,parent=None):
        original = {"p_import":self.p_import,
        "async":self.Async,
        "await":self.Await,
        "Object":BS_object,
        "undefined":undefined()
        }
        if not sandbox_mode:
          original.update({"__main__":self})
        self.mem_size = mem_size
        self.variable_mem_size = 0
        self.env_name = env_name
        self.parent = parent
        self.sandbox_mode = sandbox_mode
        self.__importables__ = __importables__
        variables.update(original)
        self.variables = variables if isinstance(variables, environment) else environment(variables) 
        
        # if env_name != "__main__":
        #   print(env_name)
        #   print(self.variables.__globals__)
        #   print(self.variables["txt"])
        self.before_var_mem = {}
        self.terminal = False
        self.async_loop = asyncio.get_event_loop()
        self.calls = {
        "VariableDeclaration":self.VariableDeclaration,
        "ExpressionStatement":self.ExpressionStatement,
        "AssignmentExpression":self.AssignmentExpression,
        "Literal":self.Literal,
        "CallExpression":self.CallExpression,
        "Identifier":self.Identifier,
        "MemberExpression":self.MemberExpression,
        "ReturnStatement":self.ReturnStatement,
        "FunctionDeclaration":self.FunctionDeclaration,
        "BinaryExpression":self.BinaryExpression,
        "FunctionExpression":self.FunctionExpression,
        "ObjectExpression":self.ObjectExpression,
        "ThisExpression":self.ThisExpression,
        "UnaryExpression":self.UnaryExpression,
        "ArrayExpression":self.ArrayExpression,
        "UpdateExpression":self.UpdateExpression,
        "LogicalExpression":self.LogicalExpression,
        "IfStatement":self.IfStatement,
        "BlockStatement":self.__call__
        }
    def Await(self,func,*args,**kwargs):
      return self.async_loop.run_until_complete(func(*args,**kwargs))
    def Async(self,func: BS_function) -> BS_async_function:
      return func.get_as_async()
    def variable2mem(self,variable):
      pass
      if self.variable_mem_size > self.mem_size:
        raise MemoryError("Sandbox reached its memory limit")
    def variable2BS(self,value):
      print(value,"hehe")
      if isinstance(value,int):
        return BS_int(value)
      elif isinstance(value,dict):
        return BS_object(value)
      elif isinstance(value,str):
        return BS_string(value)
      return value
    def raw2value(self,raw):
      # TODO: Add regex support
      if raw[0] in string_indicators and raw[-1] in string_indicators:
        return BS_string(raw[1:-1])
      elif "." in raw:
        return float(raw)
      elif raw in bool_indicators:
        
        return bool_indicators.get(raw)
      elif raw.isnumeric():
        return BS_int(raw)
      elif raw == "null":
        return None
      else:
        
        raise TypeError(f"{raw} value is not supported by BScript")
    def p_import(self,module,module_as=None):
      if self.sandbox_mode:
        if module in self.__importables__:
          
          self.variables.update({module_as if module_as else module:__importables__[module]})
          self.variable2mem(module)
        else:
          raise exceptions.SandBoxPrivilegesException(f"Sandbox doesn't have required privileges to import '{module}' module") 
      else:
        if module_as:
          
          self.variables[module_as] = importlib.import_module(module)
        else:
          self.variables[module] = importlib.import_module(module)
    def IfStatement(self,**kwargs):
      
      if self.calls[kwargs["test"]["type"]](**kwargs["test"]):
        self.__call__(kwargs["consequent"],self.terminal)
      elif kwargs["alternate"]:
        if kwargs["alternate"]["type"] == "BlockStatement":
          self.__call__(kwargs["alternate"],self.terminal)
        else:
          self.calls[kwargs["alternate"]["type"]](**kwargs["alternate"])

        
    def LogicalExpression(self,**kwargs):
      if kwargs["operator"] == "&&":
        if (result:=self.calls[kwargs["left"]["type"]](**kwargs["left"])):
          return result and self.calls[kwargs["right"]["type"]](**kwargs["right"])
        else:
          return False
      elif kwargs["operator"] == "||":
        if (result:=self.calls[kwargs["left"]["type"]](**kwargs["left"])):
          return True
        else:
          return result or self.calls[kwargs["right"]["type"]](**kwargs["right"])
      # print(kwargs["left"])
    def UpdateExpression(self,**kwargs):
      operator = unary_expressions.get(kwargs["operator"])
      if operator:
        if kwargs["argument"]["type"] == "Identifier":
          variable = self.Identifier(**kwargs["argument"])
          value = self.Identifier(assignment=True,**kwargs["argument"])
          self.variables[variable] = operator(value)
        else:
          kwargs["argument"]["computed"] = True
          assignable_object = self.calls[kwargs["argument"]["type"]](as_variable=True,**kwargs["argument"])
          assignable_object(operator(self.calls[kwargs["argument"]["type"]](assignment=True,**kwargs["argument"])))
        # return self.calls[kwargs]
    def ArrayExpression(self,**kwargs):
      array = []
      for arg in kwargs.get("elements"):
        array.append(self.calls[arg["type"]](assignment=True,**arg))
      return BS_array(array)
    def UnaryExpression(self,**kwargs):
      
      expression = unary_expressions.get(kwargs["operator"])
      delete = True if kwargs["operator"] == "delete" else False
      if expression:
        return expression(self.calls[kwargs["argument"]["type"]](assignment=True,delete=delete,**kwargs["argument"]))
      else:
        raise exceptions.UnsupportedOperationException(f"'{kwargs['operator']}' operator is not supported by BScript")
    def ObjectExpression(self,**kwargs):
      properties = kwargs["properties"]
      obj = BS_object({})
      for property in properties:
        key = self.calls[property["key"]["type"]](assignment=property["computed"],**property["key"])
        value = self.calls[property["value"]["type"]](assignment=True,parent=obj,**property["value"])
        if property["method"]:
          obj.setattr(**{key:value})
        else:
          obj.update({key:value})
      return obj
    def BinaryExpression(self,**kwargs):
      
      expression = binary_expressions.get(kwargs["operator"])
      if expression:
        return expression(self.calls[kwargs["left"]["type"]](assignment=True,**kwargs["left"]),self.calls[kwargs["right"]["type"]](assignment=True,**kwargs["right"]))
      else:
        raise exceptions.UnsupportedOperationException(f"'{kwargs['operator']}' operator is not supported by BScript")
    def Identifier(self,**kwargs):
      if kwargs.get("delete",False):
        self.delete(self.variables,kwargs["name"])
      elif kwargs.get("assignment"):
        
        if kwargs["name"] in self.variables:
          return self.variables[kwargs["name"]]
        else:
          raise NameError(f"name '{kwargs['name']}' is not defined")
      
      else:
        return kwargs["name"]
    def VariableDeclaration(self,**kwargs):
      skwargs = {}
      kind = kwargs["kind"]
      for declaration in kwargs["declarations"]:
        name = self.calls[declaration["id"]["type"]](**declaration["id"])
        value = self.calls[declaration["init"]["type"]](assignment=True,**declaration["init"]) if declaration["init"] else None
        
        skwargs[name] = value
      if kind == "const":
        self.variables.__add_const__(skwargs)
      elif kind == "let":
        self.variables.__add_global__(skwargs)
      else:
        self.variables.update(skwargs)
    def ThisExpression(self,**kwargs):
      if self.parent:
        return self.parent
      else:
        raise exceptions.ThisExpressionException("this expression cannot be used outside of an object")
    def delete(self,parent,child):
      if isinstance(parent,(list,environment,BS_object)):
        parent[child] = self.variables["undefined"]
      else:
        raise TypeError(f"BScript delete method doesn't support '{type(parent)}'")
    def MemberExpression(self,**kwargs):
      expressions = []
      expressions.append(self.calls[kwargs["object"]["type"]](as_variable=kwargs.get("as_variable",False),**kwargs["object"]))
      expressions.append(self.calls[kwargs["property"]["type"]](**kwargs["property"]))
      if expressions[0] is None:
        raise AttributeError("'NullType' object has no any attribute")
      if kwargs.get("delete"):
        funcs = flatten(expressions)
        
        child = funcs.pop()
        func_callable = None
        for func in funcs:
          if func_callable is None and isinstance(func,BS_string):
            func_callable = func
          elif func_callable is None and isinstance(func,str):
            func_callable = self.variables[func]
          elif func_callable is not None and isinstance(func,str):
                
            func_callable = variable2BS(getattr(func_callable, func))
          elif func_callable is None and not isinstance(func,str):
            func_callable = func
        self.delete(func_callable,child)
        return 
        
      if kwargs["object"]["type"] == "ThisExpression":
        funcs = flatten(expressions)
        this = funcs.pop(0)
        if kwargs.get("as_variable",False):
          attr = funcs.pop()

        func_callable = self.parent
        for func in funcs:
          if func_callable is None and isinstance(func,BS_string):
            func_callable = func
          elif func_callable is None and isinstance(func,str):
            func_callable = self.variables[func]
          elif func_callable is not None and isinstance(func,str):
                
            func_callable = variable2BS(getattr(func_callable, func))
          elif func_callable is None and not isinstance(func,str):
            func_callable = func
          
        if kwargs.get("as_variable",False):
          return AssignableObject(func_callable,attr)
        return func_callable
      if isinstance(flatten(expressions)[0],AssignableObject):
        funcs = flatten(expressions)
        funcs[0] = funcs[0].obj[funcs[0].attr]
        return AssignableObject(funcs[0],funcs[1])
      if kwargs["computed"]:
        flatten_expressions = flatten(expressions)
        if kwargs.get("as_variable",False):
          return AssignableObject(self.variables[flatten_expressions[0]],flatten_expressions[1])
        
        else:
          try:
            if isinstance(flatten_expressions[0], BS_object):
              return flatten_expressions[0][flatten_expressions[1]]
              
            return variable2BS(self.variables[flatten_expressions[0]][flatten_expressions[1]])
          except IndexError:
            return self.variables["undefined"]
      
      elif kwargs["property"]["type"] == "Identifier":
        func_callable = None
        if isinstance(expressions,list):
          funcs = flatten(expressions)
          for func in funcs:
            if func_callable is None and isinstance(func,BS_string):
              func_callable = func
            elif func_callable is None and isinstance(func,str):
              func_callable = self.variables[func]
              
            elif func_callable is not None and isinstance(func,str):
              # FIX
              func_callable = variable2BS(getattr(func_callable, func))
            elif func_callable is None and not isinstance(func,str):
              func_callable = func
          return func_callable
      else:
        expressions.append(self.calls[kwargs["property"]["type"]](**kwargs["property"]))
      return  expressions
    def Literal(self,**kwargs):
      assert not kwargs.get("regex"),raise_exception(NotImplementedError("text regex is not supported by BScript")) 
      return self.raw2value(kwargs["raw"])
    
    def AssignmentExpression(self,**kwargs):
      if kwargs["operator"] == "=":
        variable = self.calls[kwargs["left"]["type"]](as_variable=True,left=True,**kwargs["left"])
        value = self.calls[kwargs["right"]["type"]](assignment=True,**kwargs["right"])
        if isinstance(variable,AssignableObject):
          variable(value)
          return value
        elif not kwargs.get("func_caller",False):
          self.variables[variable] = value
        
        
        return value
      elif (expression:=assignment_expressions.get(kwargs["operator"])):
        variable = self.calls[kwargs["left"]["type"]](**kwargs["left"])
        value = self.calls[kwargs["right"]["type"]](assignment=True,**kwargs["right"])
        result = expression(self.variables[variable],value)
        self.variables[variable] = result
        self.variable2mem(variable)
        return {variable:result}

      else:
        raise exceptions.UnsupportedOperationException(f"'{kwargs['operator']}' operator is not supported by BScript")
    def ArgumentParser(self,*arguments):
      args = []
      kwargs = {}
      args_lock = False
      for arg in arguments:
        
        if (func:=self.calls.get(arg["type"])):
          value = func(func_caller=True,assignment=True,**arg)
          if isinstance(value,BS_object):
            if not args_lock:
              args.append(value)
            else:
              raise SyntaxError("positional argument follows keyword argument")
          elif isinstance(value,dict):
            kwargs.update(value)
            args_lock = True
            
          else:
            if not args_lock:
              args.append(variable2BS(value))
            else:
              raise SyntaxError("positional argument follows keyword argument")
        else:
          raise exceptions.UnsupportedOperationException(f"'{arg['type']}' is not supported by BScript")
      return args,kwargs
      
    def CallExpression(self,**kwargs):
      args,k_args = self.ArgumentParser(*kwargs["arguments"])
      funcs = self.calls[kwargs["callee"]["type"]](**kwargs["callee"])
      func_callable = None
      if isinstance(funcs,list):
        funcs = flatten(funcs)
        for func in funcs:
          if func_callable is None and isinstance(func,str):
            func_callable = self.variables[func]
          elif func_callable is not None and isinstance(func,str):
            func_callable = getattr(func_callable, func)
          elif func_callable is None and not isinstance(func,str):
            func_callable = func
      
      elif isinstance(funcs,str):
        func_callable = self.variables[funcs]
      else:
        func_callable = funcs
      if (isinstance((result:=func_callable(*args,**k_args)),dict)): 
        return BS_object(**result)
      else:
        return result
    def ExpressionStatement(self,**kwargs):
      if self.terminal:
        return_value =  self.calls[kwargs["expression"]["type"]](assignment=True,**kwargs["expression"])
        if return_value:
          # protected print ability
          print(return_value)
        
        return return_value
      
      return_value =  self.calls[kwargs["expression"]["type"]](assignment=True,**kwargs["expression"])
      
      return return_value
    def FunctionExpression(self,**kwargs):
      return BS_function(kwargs,executor=self,parent=kwargs.get("parent"))
    def FunctionDeclaration(self,**kwargs):
      self.variables[kwargs["id"]["name"]] = BS_function(kwargs,executor=self)
    def ReturnStatement(self,**kwargs):
      """
      {
            "type": "ReturnStatement",
            "argument": {
              "type": "Identifier",
              "name": "a"
            }
          }
      """
      args,k_args = self.ArgumentParser(kwargs["argument"])
      args.extend(k_args.values())
      return args[0]
      
      
    def __call__(self,script,terminal=False):
      self.terminal = terminal
      if not self.terminal:
        for index,body in enumerate(script["body"]):
          body_type = body["type"]
          if body_type == "FunctionDeclaration":
            del script["body"][index]
            
            # body = script["body"].pop(index)
            self.calls["FunctionDeclaration"](**body)
  
      for body in script["body"]:
        body_type = body["type"]
          
        if body_type == "ReturnStatement":
          return self.ReturnStatement(**body) 
        if (func:=self.calls.get(body_type)) :
          return_val = func(**body)
          # if body_type == "ExpressionStatement" and isinstance(return_val,dict):
          #   self.variables.update(return_val)
