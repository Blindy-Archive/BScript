from colorama import Fore, Back, Style
from colorama import init
init()
class failure:
  def __init__(self,case):
    self.case = case
class success:
  def __init__(self,case):
    self.case = case
class unsettest:
  def __init__(self,case):
    self.case = case
class test:
  def __init__(self,live=False):
    self.test_cases = []
    self.test_case = 0
    self.live = live
  def assertion(self,condition=None):
    if condition is None:
      self.test_cases.append(unsettest(self.test_case))
    elif condition:
      self.test_cases.append(success(self.test_case))
      if self.live:
        print(Fore.GREEN + f'[{self.test_case}] test case ran successfuly! ✔️')
        print(Style.RESET_ALL,end="")
    else:
      self.test_cases.append(failure(self.test_case))
      
    self.test_case += 1
  def finalize(self):
    for test_case in self.test_cases:
      if isinstance(test_case, success):
        print(Fore.GREEN + f'[{test_case.case}] test case ran successfuly! ✔️')
        print(Style.RESET_ALL,end="")
      elif isinstance(test_case,unsettest):
        print(Fore.YELLOW + f'? [{test_case.case}] test case is not set!')
        print(Style.RESET_ALL,end="")
      else:
        print(Fore.RED + f'[{test_case.case}] test case failed! ❌')
        print(Style.RESET_ALL,end="")
