#!/usr/bin/python3
import sys
import json
def json_to_tupList(x):
  if type(x) is dict:
    return ('__DICT__', [(k,json_to_tupList(v)) for k,v in x.items()])
  elif type(x) is list:
    return ('__LIST__',[json_to_tupList(v) for v in x])
  else:
    return x

def sort_tupleList(x):
  if type(x) is list:
    mylist = [sort_tupleList(v) for v in x]
    mylist.sort()
    return tuple(mylist)
  elif type(x) is tuple and len(x)==2:
    if x[0] == '__DICT__':
      mylist = [(k,sort_tupleList(v)) for k,v in x[1]]
      mylist.sort()
      return (x[0],tuple(mylist))
    elif x[0] == '__LIST__':
      mylist = [sort_tupleList(v) for v in x[1]]
      mylist.sort()
      return (x[0],tuple(mylist))
  return x

def decode_tupleList(x):
  if type(x) is tuple and len(x) == 2:
    if x[0] == '__LIST__':
      return [decode_tupleList(v) for v in x[1]]
    if x[0] == '__DICT__':
      return {k:decode_tupleList(v) for k,v in x[1]}
  return x

def sort_json(json_str):
  json_dict = json.loads(json_str)
  if not json_dict['error']:
    rows = []
    for row in json_dict['results']:
      if type(row) is dict:
        for k,v in row.items():
          tupleList = json_to_tupList(v)
          sorted_tuple = sort_tupleList(tupleList)
          sorted_json = decode_tupleList(sorted_tuple)
          rows.append(f'{k}:{sorted_json}')
    return '\n'.join(rows)
  else:
    code = json_dict['code'] if 'code' in json_dict else ''
    message = json_dict['message'] if 'message' in json_dict else ''
    return f'ERROR ({code}): {message}'

if __name__ == '__main__':
  for line in sys.stdin:
    if line.startswith('{'):
      print(sort_json(line))
    else:
      print(line)