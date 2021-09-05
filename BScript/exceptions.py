class BaseException(Exception):
  pass
class SandBoxPrivilegesException(BaseException):
  """
  Raise: when sandbox doesn't have required privileges to do something
  """
class UnsupportedOperationException(BaseException):
  """
  Raise: when BinaryExpression tries executing the process with an unsupported operator
  """
class UnsupportedCallException(BaseException):
  """
  Raise: when An Unsupported Call happens to be called by executor
  """
class UnexpectedIdentifierException(BaseException):
  """
  Raise: when object created with a reserved attribute names
  """
class ThisExpressionException(BaseException):
  """
  Raise: when this expression used in outside of object
  """