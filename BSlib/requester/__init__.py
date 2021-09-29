"""
This library is made for BScript and the main purpose of this library is making requests libraries
more suitable for BScript sandbox

"""

import re
import requests
from BSlib.requester import exceptions
# This regex created to validate urls
URL_RE = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
         # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# This function is used to check if given string is a valid url or not.
def is_url_valid(url):
  return re.match(URL_RE, url) is not None

#This decorator is used to check if parameters is suitable 
def _param_check(func):
  def __check(
    url: str,
    params: dict = None,
    data: object = None,
    headers: object = None,
    cookies:  object = None,
    files: object = None,
    auth: object = None,
    timeout: object = None,
    allow_redirects: bool = False,
    proxies: object = None,
    hooks: object = None,
    stream: object = None,
    verify: object = None,
    cert: object = None,
    json: dict = None):
      if is_url_valid(url):
        return func(
        url=url,
        params=params,
        verify=verify,
        data=data,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        hooks=hooks,
        stream=stream,
        cert=cert,
        json=json
        )
      else:
        raise exceptions.InvalidURLException("'%s' is not a valid URL" % url)
  return __check

# This function is used to make a get request to specified url.
@_param_check
def get(**kwargs):
  return requests.get(**kwargs)

# This function is used to make a post request to specified url.
@_param_check
def post(**kwargs):
  return requests.post(**kwargs)

# This function is used to make a put request to specified url.
@_param_check
def put(**kwargs):
  return requests.put(**kwargs)

# This function is used to make a delete request to specified url.
@_param_check
def delete(**kwargs):
  return requests.delete(**kwargs)



# SIGNALS: Signals are used to enable using methods via dict

# SIGNAL: get
GET = lambda obj: get(**obj)
# SIGNAL: post
POST = lambda obj: post(**obj)
# SIGNAL: put
PUT = lambda obj: put(**obj)
# SIGNAL: delete
DELETE = lambda obj: delete(**obj)
