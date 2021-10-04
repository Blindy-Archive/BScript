from itertools import chain
import itertools
import os,requests
import tkinter as tk
import importlib
from BScript import exceptions
import sys,asyncio
from BScript.bs_types import *
import BScript.reserved_functions as rf
import BSlib
import traceback,time
from js2py import require
import nest_asyncio
import sys
import sys
import gc
nest_asyncio.apply()
escodegen = require('escodegen')
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
  "in":lambda x,y: x in y,
}
unary_expressions = {
  "-":lambda x: x*-1,
  "delete":lambda x: x,
  "--":lambda x: x-1,
  "++":lambda x: x+1,
  "!":lambda x: not x
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
__private__ = __reserveds__.copy()^{"clear","copy","fromkeys","get","items","keys","pop","popitem","setdefault","update","values","__delitem__"}

__reserved__keys__ = {"this","undefined","Infinity"}
__reserveds__.add("__private__")
__protected__ = {"__class__"}
class scope:
  parent_scope = None
  child = False
  constants = set()

  def __init__(self,*args,**kwargs):
    self.variables = {}
    self.variables.update(kwargs)
  def get_variable(self,name):
    if name in self.variables:
      return self.variables[name]
    elif self.child and (value:=self.parent_scope.get_variable(name)) is not None:

      return variable2BS(value)
    else:
      raise NameError(f"name '{name}' is not defined")

  def check_constant(self,name):
    if name in self.constants:
      return True
    
  def has_variable(self,name):
    if name in self.variables:
      return self
    elif self.child:
      return self.parent_scope.has_variable(name)
    else:
      return self
      
  def create_variable(self,kind,name,value=undefined):
    if self.check_constant(name):
      raise TypeError("Assignment to constant variable.")
    if kind == "const":
      self.constants.add(name)
      self.variables[name] = variable2BS(value)

    elif kind == "var":
      self.variables[name] = variable2BS(value)
    elif kind == "let":
      self.variables[name] = variable2BS(value)
  def unsafe_set_variables(self,kwargs):
    for k,v in kwargs.items():
      kwargs[k] = variable2BS(v)
    self.variables.update(kwargs)
  def unsafe_set_variable(self, name, value):
    if self.check_constant(name):
      raise TypeError("Assignment to constant variable.")
    self.variables[name] = variable2BS(value)
  def set_variable_value(self, name, value):
    if self.check_constant(name):
      raise TypeError("Assignment to constant variable.")
    self.has_variable(name).variables[name] = variable2BS(value)
    


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
        self.variables = dict({k["name"]:executor.calls[v.get("type")](**v) if v else required() for k,v in list(itertools.zip_longest(script["params"], script["defaults"]))})
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
      variables = scope()
            
      variables.unsafe_set_variables(self.variables)
      k_words = {k:v for k,v in zip(self.kwargs[:abs(self.args_len - len(args))],args[abs(self.args_len - len(args)):])}
      self_args = [arg for arg in self.args if arg not in kwargs.keys()]
      value = { k : kwargs[k]  for k in set(kwargs) - set(k_words) if k in self.args  }
      kwargs = self.__difference__dict__(kwargs,value)
      variables.unsafe_set_variables(value)
      args_len = len(self_args) 
      args = args[:args_len]
      variables.unsafe_set_variables(k_words)
      args_length = len(args)
      if args_length < args_len:
        raise TypeError(f"{self.__name__}() missing {args_len -args_length} required positional argument: {'and'.join(self.args[args_len - args_length:])}")
      for x,y in zip(self.args,args):
        variables.unsafe_set_variable(x,y)

      for k, (k2,v2) in zip(self.kwargs,kwargs.items()):
        if k2 not in self.kwargs:
          raise TypeError(f"{self.__name__}() got an unexpected keyword argument: {k2}")
        else:
          variables.unsafe_set_variable(k,v2)
      variables.child = True
      variables.parent_scope = self.executor.scope
      return BS_executor(self.get_env_name(),variables,sandbox_mode=self.executor.sandbox_mode)(self.body,terminal=self.executor.terminal,env_name=self.get_env_name())
      return self.executor(self.body,temporary=True,env_name=self.get_env_name(),env=variables)
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
      return super(BS_async_function,self).__call__(*args,**kwargs)
    def get_env_name(self):
      return self.executor.env_name+"."+getattr(self,"__name__")
    def __str__(self):
      return self.get_env_name()
    def get_as_async():
      pass
      
class Exports:
  events = {}
  commands = {}
  available_events = {"on_reaction_add","on_reaction_remove","on_message"}
  def export_events(self,__m:dict):
    for k,v in __m.items():
      if k not in self.available_events:
        raise TypeError(f"This {k} is not available yet")
      if not isinstance(v,(BS_function,BS_async_function)):
        raise TypeError(f"Only allowed function types in exports")
      self.events[k] = v
  def export_event(self,event,function):
    if event not in self.available_events:
      raise TypeError(f"This {k} is not available yet")
    if not isinstance(function,(BS_function,BS_async_function)):
      raise TypeError(f"Only allowed function types in exports")
    self.events[event] = function
  def export_functions(self,__m:dict):
     for k,v in __m.items():
        if not isinstance(v,(BS_function,BS_async_function)):
          raise TypeError(f"Only allowed function types in exports")
        self.commands[k] = v
class BS_executor(object):
    def __init__(self,env_name="__main__",scope=scope(),sandbox_mode=True,__importables__=__importables__,mem_size=8000,parent=None,max_loop=500,use_reserved=False,variables={}):
        self.exports = Exports()
        self.scope = scope
        if not self.scope.child:
          original = {"p_import":self.p_import,
          "async":self.Async,
          "await":self.Await,
          "Object":BS_object,
          "Object_get":lambda obj,key: dict.get(obj,key),
          "Object_set":lambda obj,key,value: dict.__setitem__(obj,key,value),
          "undefined":undefined(),
          "Exports":self.exports,
          "bimport":self.bimport,
          "Number":BS_int,
          "String":BS_string,
          "Array":BS_array
          }
          self.scope.unsafe_set_variables(original)
          self.scope.unsafe_set_variables(variables)
          
          if not sandbox_mode:
            self.scope.unsafe_set_variable("__main__",self)
        self.mem_size = mem_size
        self.mem_usage = 0
        self.variable_mem_size = 0
        self.env_name = env_name
        self.parent = parent
        self.sandbox_mode = sandbox_mode
        self.__importables__ = __importables__
        self.max_loop = max_loop
        self.reserved_functions = rf.exports
        self.use_reserved = use_reserved
        # if env_name != "__main__":
        #   print(env_name)
        #   print(self.variables.self.__globals__)
        #   print(self.variables["txt"])
        self.before_var_mem = {}
        self.terminal = False
        self.async_loop = asyncio.get_event_loop()
        self.code_block = 1
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
        "BlockStatement":self.__call__,
        "ForStatement":self.ForStatement
        }
        import threading
        t1 = threading.Thread(target=self.ProfileMemory)
        t1.daemon = True
        t1.start()
    
    
    def actualsize(self,input_obj):
        memory_size = 0
        ids = set()
        objects = [input_obj]
        while objects:
            new = []
            for obj in objects:
                if id(obj) not in ids:
                    ids.add(id(obj))
                    memory_size += sys.getsizeof(obj)
                    new.append(obj)
            objects = gc.get_referents(*new)
        return memory_size
    
    def ProfileMemory(self):
      
      while 1:
        
        size = self.actualsize(self)
        
        self.mem_usage = size
        time.sleep(0.6)
        
    def bimport(self,library):
      
      if library in BSlib.__modules__:
        return BSlib.__modules__[library] 
      else:
        raise exceptions.UndefinedBSlibModuleException(f"BSlib doesn't have a module named as '{library}'")
    def Await(self,func):
      
      return self.async_loop.run_until_complete(func)
    def Async(self,func: BS_function):
      return func.get_as_async()
    def variable2mem(self,variable):
      pass
      if self.variable_mem_size > self.mem_size:
        raise MemoryError("Sandbox reached its memory limit")
    def variable2BS(self,value):
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
      if self.scope.child:
        raise exceptions.ScopeException("Can only import in global scope")
      if self.sandbox_mode:
        if module in self.__importables__:
          return __importables__[module]
        else:
          raise exceptions.SandBoxPrivilegesException(f"Sandbox doesn't have required privileges to import '{module}' module") 
      else:
          
        return importlib.import_module(module)
    def ForStatement(self,**kwargs):
      self.calls[kwargs["init"]["type"]](**kwargs["init"])
      
      loop = 0
      while self.calls[kwargs["test"]["type"]](**kwargs["test"]) :
        state = self.__call__(kwargs["body"],self.terminal,temporary=True)
        self.calls[kwargs["update"]["type"]](**kwargs["update"])
        loop+=1
        if state is BS_break:
          break
        elif state is BS_continue:
          continue
        if loop>=self.max_loop:
          raise Exception("System reached maximum loop limit")
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
          self.scope.set_variable_value(variable, operator(value))
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
        BS_object.setitem(obj,key,value)
      return obj
    def BinaryExpression(self,**kwargs):
      
      expression = binary_expressions.get(kwargs["operator"])
      if expression:
        return expression(self.calls[kwargs["left"]["type"]](assignment=True,**kwargs["left"]),self.calls[kwargs["right"]["type"]](assignment=True,**kwargs["right"]))
      else:
        raise exceptions.UnsupportedOperationException(f"'{kwargs['operator']}' operator is not supported by BScript")
    def Identifier(self,**kwargs):
      if kwargs.get("delete",False):
        # TODO: Add delete function in scope
        self.delete(self.variables,kwargs["name"])
      elif kwargs.get("assignment"):
        
        return self.scope.get_variable(kwargs["name"])
      
      else:
        return kwargs["name"]
    def VariableDeclaration(self,**kwargs):
      kind = kwargs["kind"]
      for declaration in kwargs["declarations"]:
        name = self.calls[declaration["id"]["type"]](**declaration["id"])
        
        value = self.calls[declaration["init"]["type"]](assignment=True,**declaration["init"]) if declaration["init"] else undefined
        
        self.scope.create_variable(kind,name,value)
    def ThisExpression(self,**kwargs):
      if self.parent:
        return self.parent
      else:
        raise exceptions.ThisExpressionException("this expression cannot be used outside of an object")
    def delete(self,parent,child):
      if isinstance(parent,(list,BS_object)):
        parent[child] = self.scope.get_variable("undefined")
      elif isinstance(parent,scope):
        
        pass
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
            func_callable = self.scope.get_variable(func)
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
            func_callable = self.scope.get_variable(func)
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
          
          
          return AssignableObject(self.scope.get_variable(flatten_expressions[0]),self.scope.get_variable(flatten_expressions[1]))
        
        else:

          try:
            if isinstance(flatten_expressions[0], BS_object):
              return flatten_expressions[0][flatten_expressions[1]]
              
            return variable2BS(self.scope.get_variable(flatten_expressions[0])[self.calls[kwargs["property"]["type"]](assignment=True,**kwargs["property"])])
          except IndexError:
            return self.scope.get_variable("undefined")
      
      elif kwargs["property"]["type"] == "Identifier":
        func_callable = None
        if isinstance(expressions,list):
          funcs = flatten(expressions)
          
          for func in funcs:
            if func_callable is None and isinstance(func,BS_string):
              func_callable = func
            elif func_callable is None and isinstance(func,str):
              func_callable = self.scope.get_variable(func)
              
            elif func_callable is not None and isinstance(func,str) and not isinstance(funcs,BS_string):
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
        else:
          self.scope.set_variable_value(variable,value)
        
        return value
      elif (expression:=assignment_expressions.get(kwargs["operator"])):
        variable = self.calls[kwargs["left"]["type"]](**kwargs["left"])
        value = self.calls[kwargs["right"]["type"]](assignment=True,**kwargs["right"])
        result = expression(self.scope.get_variable(variable),value)
        self.scope.set_variable_value(variable,result)
        # TODO: Test here
        return result

      else:
        raise exceptions.UnsupportedOperationException(f"'{kwargs['operator']}' operator is not supported by BScript")
    def ArgumentParser(self,*arguments):
      args = []
      kwargs = {}
      for arg in arguments:
        
        if (func:=self.calls.get(arg["type"])):
          value = func(assignment=True,**arg)
          if isinstance(value,BSlib.built_in.KeywordArguments):
            
            kwargs.update({k:(variable2BS(v)) for k,v in value.kwargs.items()})
          else :
            args.append(variable2BS(value))
           
            
          
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
            func_callable = self.scope.get_variable(func)
          elif func_callable is not None and isinstance(func,str):
            func_callable = getattr(func_callable, func)
          elif func_callable is None and not isinstance(func,str):
            func_callable = func
      
      elif isinstance(funcs,str) and not isinstance(funcs,BS_string):
        func_callable = self.scope.get_variable(funcs)
      else:
        func_callable = funcs
        
      if (isinstance((result:=func_callable(*args,**k_args)),dict)) and not isinstance(result,BS_object): 
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
      if self.use_reserved and kwargs["id"]["name"] in self.reserved_functions:
        pass
      else:
        self.scope.create_variable("var",kwargs["id"]["name"],BS_function(kwargs,executor=self))
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
    
    
    def __call__(self,script,terminal=False,temporary=False,env_name=None,env={}):
      try:
        self.env_name = env_name if env_name else self.env_name 
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
          if self.mem_usage>=self.mem_size:
            raise exceptions.SandboxMemoryOverflowException(f"Memory usage is too big for sandbox's privileges")
          if body_type == "ReturnStatement":
            return_val = self.ReturnStatement(**body) 
            return return_val
          elif body_type == "BreakStatement":
            return BS_break
          elif body_type == "ContinueStatement":
            return BS_continue
          elif (func:=self.calls.get(body_type)) :
            return_val = func(**body)
          self.code_block+=1
          # if body_type == "ExpressionStatement" and isinstance(return_val,dict):
          #   self.variables.update(return_val)
          
      except Exception as e:
        code = escodegen.generate(body)
        
        raise type(e)(str(e) +
                      f' code block: block {self.code_block}:\n   \'%s\'' % code).with_traceback(sys.exc_info()[2])