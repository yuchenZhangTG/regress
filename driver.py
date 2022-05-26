#!/usr/bin/python3
import argparse
from pathlib import Path
from glob import glob
import subprocess
from multiprocessing import Pool, cpu_count
import os
from time import time
import json

parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test', type=str, help='directory name of the test')
parser.add_argument('--skip', '-s', action='store_true', help='skip parse and precompile')
parser.add_argument('--info', '-i', action='store_true', help='info mode, print output to terminal not log file')
parser.add_argument('--mode', '-m', type=str, choices = ['udf', 'single', 'dist', 'all'], default = 'all', help='skip parse and precompile')

args = parser.parse_args()
# get directory of the script
cwd = Path(os.path.realpath(__file__)).parent
output_folder = cwd/'output'
threads = cpu_count()

def check(test_dir):
  # check the uniqueness of the test folder
  # check the uniqueness of the query name
  pass

def parse(file):
  print(f'-- {file}:')
  subprocess.run(["gsql", "-g", "test_graph", str(file)])

def parse_files(file_list):
  with Pool(processes=threads) as pool:
    pool.map(parse, file_list)

def dump_vset(json_dict):
  for k,v in json_dict.items():
    v.sort(key=lambda x: (x['v_type'],x['v_id'])) # vertex ids are sorted in alphebatic order
    return k + ':' + json.dumps(v, sort_keys=True)

def sort_json(json_str):
  json_dict = json.loads(json_str)
  if not json_dict['error']:
    # printed results is a Vertex Set
    rows = []
    for row in json_dict['results']:
      if '"attributes"' in json_str and '"v_id"' in json_str and '"v_type"' in json_str:
        rows.append(dump_vset(row))
      else:  
        rows.append(json.dumps(row, sort_keys=True))
    return '\n'.join(rows)
  else:
    return json_dict['message']

def runQuery(file):
  print(f'-- {file}')
  cwd = os.getcwd()
  output_parent = Path(cwd.replace('test_case/', 'output/')) 
  output_parent.mkdir(parents=True, exist_ok=True)
  output_file = output_parent / str(file).replace('.gsql', '.log')
  if not args.info:
    fo = open(output_file,'w')
  with open(file) as fi:
    for line in fi:
      print('\n'+line, end='')
      cmd_out = subprocess.run(["gsql", "-g", "test_graph", line], stdout=subprocess.PIPE).stdout.decode()
      # output is json
      if cmd_out.startswith('{'):
        cmd_out = sort_json(cmd_out)
      if args.info:
        print(cmd_out)
      else:
        fo.write(line)
        fo.write(cmd_out)

def runQueries(file_list):
  with Pool(processes=threads) as pool:
    pool.map(runQuery, file_list)
        
def runTest(mode):
  # catogorize the files
  filesInstall = []
  filesRun = []
  for f in Path('.').iterdir():
    name = f.name.split('.')
    if len(name) == 2 and name[-1] == 'gsql':
      filesInstall.append(f) 
    if len(name) >= 3:
      if name[-2] == mode:
        filesInstall.append(f)
      elif name[-2] == 'run':
        filesRun.append(f)
  print('\n\n-------- Parse Query --------')
  start = time()
  if not args.skip:
    parse_files(filesInstall)  
  parse_time = time() - start
  print('\n\n-------- Install Query --------')
  start = time()
  if not args.skip:
    subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY ALL"])
  install_time = time() - start
  print('\n\n--------- Run Query --------')
  start = time()
  for q in filesRun:
    runQuery(q)
  run_time = time() - start
  print('================= Summary =================')
  print(f'Parse:   {parse_time:.3f} s')
  print(f'Install: {install_time:.3f} s')
  print(f'Run:     {run_time:.3f} s')

os.chdir(cwd)
tests = glob(f'test_case/**/{args.test}', recursive=True) 
print('Tests to run:')
print('\t' + '\n\t'.join(tests) + '\n')

for test in tests:
  categories = test.split('/')
  print(f'====== {categories[-1]} =====')  
  modes = ['udf', 'single', 'dist'] if args.mode == 'all' else [args.mode]
  for mode in modes:
    os.chdir(test)
    runTest(mode)
    os.chdir(cwd)
  