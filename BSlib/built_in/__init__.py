class BS_builtin:
  pass
class KeywordArguments(BS_builtin):
  def __init__(self,obj):
    self.__obj = obj
  @property
  def kwargs(self):
    return self.__obj
    