def Object(obj_array:list):
  
  return {k:v for k,v in obj_array}
def Object_get(obj,key):
  return dict.__getitem__(obj,key)
def Object_set(obj,key,value):
  dict.__setitem__(obj,key,value)

def log(text):
  print(text)
exports = {"__Object":Object,
          "__Object_get":Object_get,
          "__Object_set":Object_set,
          "__log":log
          }