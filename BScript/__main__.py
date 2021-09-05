import sys,json
from BScript import execute
from pyjsparser import parse
import os
def test(text=1): print(text)
class console():
  text = "selami"
  @staticmethod
  def log(*args):
    print(*args)
  
  class a:
    test = "selamet"
    
executor = execute.BS_executor({"console":console},sandbox_mode=False)
def main(filename):
  
  
  with open(filename, 'r',encoding="utf8") as f:
    read = f.read()
    with open("test.json", "w") as j:
      json.dump(parse(read),j,indent=2)
    
    executor(parse(read))
    print(executor.variables)
if __name__ == '__main__':
  
    main(*sys.argv[1:])
    