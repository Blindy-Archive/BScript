import js2py
from BSlib import requester
import asyncio
from js2py import base
import nest_asyncio
nest_asyncio.apply()

class Exports:
  events = {}
  commands = {}
  available_events = {"on_reaction_add","on_reaction_remove","on_message"}
  def export_events(self,__m:dict):
    __m = (__m.to_dict())

    for k,v in __m.items():
      if k not in self.available_events:
        raise TypeError(f"This {k} is not available yet")
      
      self.events[k] = v
  def export_event(self,event,function):
    if event not in self.available_events:
      raise TypeError(f"This {event} is not available yet")
    
    self.events[event] = function
  def export_functions(self,__m:dict):
     __m = (__m.to_dict())
     for k,v in __m.items():
        
        self.commands[k] = v
class Compiler():
    class async_compiler:
        loop = asyncio.get_event_loop()

        def Await(self, func):
            return self.loop.run_until_complete(func)

    def __init__(self, script,context={}):
        async_compiler = self.async_compiler()
        self.exporter = Exports() 
        self.__builtin__ = {
            "requester": requester,
            "await": async_compiler.Await,
            "exporter":self.exporter,
            "format":lambda text,kwargs: str(text).format(**base.to_dict(kwargs)),
            "Object_values":lambda obj: list(base.to_dict(obj).values())

        }
        self.__builtin__.update(context)
        self.script = script

    def __call__(self):
        context = js2py.EvalJs(self.__builtin__)
        context.execute(self.script)
        return context
