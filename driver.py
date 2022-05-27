#!/usr/bin/python3
import argparse
from pathlib import Path
from glob import glob
import subprocess
from multiprocessing import Pool, cpu_count
import os
from time import time
import json
import shutil

parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test', type=str, help='directory name of the test')
parser.add_argument('--skip', '-s', action='store_true', help='skip parse and precompile')
parser.add_argument('--info', '-i', action='store_true', help='info mode, print output to terminal not log file')
parser.add_argument('--real', '-r', action='store_true', help='show difference in realtime')
parser.add_argument('--time', '-t', action='store_true', help='print parse, install and run time')
parser.add_argument('--mode', '-m', type=str, choices = ['udf', 'single', 'dist', 'all'], default = 'all', help='skip parse and precompile')

args = parser.parse_args()
# get directory of the script
root = Path(os.path.realpath(__file__)).parent
output_folder = root/'output'
threads = cpu_count()
modes = ['udf', 'single', 'dist'] if args.mode == 'all' else [args.mode]

def check(test_dir):
  # check the uniqueness of the test folder
  # check the uniqueness of the query name
  pass

def relative(file):
  return file.relative_to(root)

def getFiles(f, mode, filesInstall, filesRun):
  f = Path(f)
  names = f.name.split('.')
  if len(names) == 2 and names[-1] == 'gsql':
    filesInstall.append(f) 
  if len(names) >= 3:
    if names[-2] == mode:
      filesInstall.append(f)
    elif names[-2] == 'run':
      filesRun.append(f)

def parse(file):
  print(f'-- {file}')
  subprocess.run(["gsql", "-g", "test_graph", str(file)])

def parse_files(file_list):
  with Pool(processes=threads) as pool:
    pool.map(parse, file_list)

def installQueries(mode):
  if mode == 'udf':
      subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY ALL"])
  if mode == 'single':
    subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY -single ALL"])
  if mode == 'dist':
    subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY -distributed ALL"])

def dump_vset(json_dict):
  for k,v in json_dict.items():
    v.sort(key=lambda x: (x['v_type'],x['v_id'])) # vertex ids are sorted in alphebatic order
    return k + ':' + json.dumps(v, sort_keys=True)

def sort_json(json_str):
  json_dict = json.loads(json_str)
  if not json_dict['error']:
    rows = []
    for row in json_dict['results']:
      # If result is a Vertex Set
      if '"attributes"' in json_str and '"v_id"' in json_str and '"v_type"' in json_str:
        rows.append(dump_vset(row))
      else:
        rows.append(json.dumps(row, sort_keys=True))
    return '\n'.join(rows)
  else:
    return json_dict['message']

def getOutputFile(file):
  file = file.resolve()
  parent, name = file.parent, file.name
  output_parent = Path(str(parent).replace('test_case/', 'output/')) 
  output_parent.mkdir(parents=True, exist_ok=True)
  names = name.split('.')
  output_name = name.replace('.gsql', f'.{mode}.log') if len(name) == 2 else name.replace('.gsql', '.log')
  output_file = output_parent / output_name
  baseline_parent = Path(str(parent).replace('test_case/', 'baseline/'))
  baseline_parent.mkdir(parents=True, exist_ok=True)
  baseline_file = baseline_parent / name.replace('.gsql', '.base')
  return output_file,baseline_file

def runQuery(file, mode):
  print(f'-- {file}')
  output_file,baseline_file = getOutputFile(file)
  if not args.info:
    fo = open(output_file,'w')
  with open(file) as fi:
    for line in fi:
      cmd_out = subprocess.run(["gsql", "-g", "test_graph", line], stdout=subprocess.PIPE).stdout.decode()
      # if output is json
      if cmd_out.startswith('{'):
        cmd_out = sort_json(cmd_out)
      if args.info:
        print(line, end='')
        print(cmd_out)
      else:
        fo.write(line.strip()+'\n')
        fo.write(cmd_out.strip()+'\n\n')
  if args.info:
    return  
  fo.close()
  if not baseline_file.exists():
    shutil.copy(output_file, baseline_file)
    print(f'    Created baseline {f2}')
  elif args.real:
    compare(output_file, baseline_file)
  
def runQueries(file_list):
  with Pool(processes=threads) as pool:
    pool.map(runQuery, file_list)

def compare(output_file, baseline_file):
  cmd_out = subprocess.run(["diff", str(output_file), str(baseline_file)], stdout=subprocess.PIPE)
  r1 = relative(output_file)
  r2 = relative(baseline_file)
  if cmd_out.returncode:
    print(f'Wrong results in {r1}')
    print(f'To compare:')
    print(f'    vi -d {r1} {r2}')
    print(f'To update:')
    print(f'    cp {r1} {r2}')
    print()
  return cmd_out.returncode

def compare_files(file_list):
  num_diff = 0
  for file in file_list:
    output_file,baseline_file = getOutputFile(file)
    num_diff += compare(output_file, baseline_file)
  if num_diff == 0:
    print('-- PASS')
  else:
    print(f'-- {num_diff} files are differet')

def runTest(mode):
  filesInstall = []
  filesRun = []
  for f in Path('./').glob('**/*.gsql'):
    getFiles(f, mode, filesInstall, filesRun)
  if not args.skip:
    print('\n\n-------- Parse Query --------')
    start = time()
    parse_files(filesInstall)
    parse_time = time() - start
    print(f'\n\n------ Install Query : {mode} -------')
    start = time()
    installQueries(mode)
    install_time = time() - start
  print('\n\n--------- Run Query --------')
  start = time()
  for q in filesRun:
    runQuery(q, mode)
  run_time = time() - start
  print('\n\n--------- Compare Results --------')
  if not args.real:
    compare_files(filesRun)

  if args.time:
    print('============ Runtime Summary ============')
    if not args.skip:
      print(f'Parse:   {parse_time:.3f} s')
      print(f'Install: {install_time:.3f} s')
    print(f'Run:     {run_time:.3f} s')

os.chdir(root)
tests = glob(f'test_case/**/{args.test}', recursive=True) 
print('Tests to run:')
print('\t' + '\n\t'.join(tests) + '\n')

for test in tests:
  categories = test.split('/')
  print(f'====== {categories[-1]} =====')  
  for mode in modes:
    os.chdir(test)
    runTest(mode)
    os.chdir(root)