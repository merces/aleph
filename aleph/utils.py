import os, sys, logging
from copy import deepcopy
from functools import partial

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
# Get path as a function - for PluginBase
get_path = partial(os.path.join, CURRENT_DIR)

def error(msg):
    # print help information and exit:
    logging.error(msg)
    sys.stderr.write(str(msg+"\n"))
    sys.exit(2)

def dict_merge(target, *args):

    # Merge multiple dicts
    if len(args) > 1:
        for obj in args:
            dict_merge(target, obj)
        return target
 
    # Recursively merge dicts and set non-dict values
    obj = args[0]
    if not isinstance(obj, dict):
        return obj

    for k, v in obj.iteritems():
        if k in target and isinstance(target[k], dict):
            dict_merge(target[k], v)
        else:
            target[k] = deepcopy(v)

    return target

import pytz, datetime
import dateutil.parser

utc = pytz.utc

def get_timezone_by_name(tz_name):

    try:
        timez = pytz.timezone(tz_name)
        return timez
    except Exception, e:
        return None

def to_iso8601(when=None, tz=utc):
  if not when:
    when = datetime.datetime.now(tz)
  if not when.tzinfo:
    when = tz.localize(when)
  _when = when.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
  return _when[:-8] + _when[-5:] # remove microseconds

def from_iso8601(when=None, tz=utc):
  _when = dateutil.parser.parse(when)
  if not _when.tzinfo:
    _when = tz.localize(_when)
  return _when

def in_string(tokens, string):
    return any(token in str(string).lower() for token in tokens)

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

