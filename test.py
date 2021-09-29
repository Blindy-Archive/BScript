from BScript_lite import Compiler
async def test(text):
  print(text)
with open("test.js","r",encoding="utf-8") as f:
    
  compiled = Compiler(f.read(),{"tester":test})()
  compiled.exporter.events["on_message"]("hello world")