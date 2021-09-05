import js2py
esprima = js2py.require("esprima@4.0.1")
from pyjsparser import parse

with open("test.bs","r",encoding="utf8") as f:
  read = f.read()
  print(esprima.parse(read))
