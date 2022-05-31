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
import uuid
from functools import partial
from setup.sort_json import sort_json
parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test', type=str, help='directory name of the test')
parser.add_argument('--skip', '-s', action='store_true', help='skip query parse and compile, only run queries and compare')
parser.add_argument('--info', '-i', action='store_true', help='info mode, print results to terminal (default write to `output/` folder).')
parser.add_argument('--time', '-t', action='store_true', help='print parse, install and run time')
parser.add_argument('--update', '-u', action='store_true', help='force update baselines')
parser.add_argument('--mode', '-m', type=str, choices = ['udf', 'single', 'dist', 'all'], default = 'all', help='run queries in a specified mode')

args = parser.parse_args()
# get directory of the script
root = Path(os.path.realpath(__file__)).parent
output_folder = root/'output'
threads = cpu_count()
modes = ['udf', 'single', 'dist'] if args.mode == 'all' else [args.mode]
dist_tmp = Path('/tmp/distQuery/')

class bcolor:
  FAIL = '\033[91m'
  GREEN = '\033[92m'
  WARNING = '\033[93m'
  ENDC = '\033[0m'

def check(test_dir):
  # check the uniqueness of the test folder
  # check the uniqueness of the query name
  pass

def relative(file: Path):
  return file.relative_to(root)

# collect files in certain mode, files are collected in filesInstall, filesRun
def filterFiles(f:Path, mode, filesInstall, filesRun):
  names = f.name.split('.')
  if names[-1] == 'run':
      filesRun.append(f)
  elif len(names) == 2 and names[-1] == 'gsql':
    filesInstall.append(f) 
  if len(names) >= 3:
    if mode in names[1:-1]:
      filesInstall.append(f)

def parseDist(file):
  print(f'-- {file}')
  file = Path(file)
  tmp_file = dist_tmp / (file.stem + '-' + str(uuid.uuid4()) + file.suffix)
  with open(tmp_file, 'w') as fo, open(file, 'r') as fi:
    for line in fi:
      fo.write(line
        .replace('CREATE OR REPLACE QUERY', 'CREATE OR REPLACE DISTRIBUTED QUERY')
        .replace('CREATE QUERY', 'CREATE DISTRIBUTED QUERY')
        .replace('create or replace query', 'create or replace distributed query')
        .replace('create query', 'created distributed query')
        )
  subprocess.run(["gsql", "-g", "test_graph", str(tmp_file)])

"""
================ GSQL file handlers =======================
Parse, install, run,
===========================================================
"""
def parse(file):
  print(f'-- {file}')
  subprocess.run(["gsql", "-g", "test_graph", str(file)])

def getOutputFile(file, mode=''):
  file = file.resolve()
  parent, name = file.parent, file.name
  output_parent = Path(str(parent).replace('test_case/', 'output/')) 
  output_parent.mkdir(parents=True, exist_ok=True)
  names = name.split('.')
  if name.endswith('.run'):
    output_name = name.replace('.run', f'.{mode}.out') if len(name) == 2 else name.replace('.run', f'.{mode}.out')
  elif name.endswith('.sh'):
    output_name = name.replace('.sh', '.out')
  output_file = output_parent / output_name
  baseline_parent = Path(str(parent).replace('test_case/', 'baseline/'))
  baseline_parent.mkdir(parents=True, exist_ok=True)
  baseline_file = baseline_parent / name.replace('.run', '.base').replace('.sh', '.base')
  # overwrite the generic baseline
  baseline_file2 = baseline_parent / name.replace('.run', f'.{mode}.base')
  if baseline_file2.is_file():
    baseline_file = baseline_file2
  
  diff_file = Path(str(output_file).replace('test_case/', 'diff/'))
  return output_file, baseline_file, diff_file

def compare(output_file, baseline_file, diff_file):
  cmd_out = subprocess.run(["diff", str(output_file), str(baseline_file)], stdout=subprocess.PIPE)
  r1 = relative(output_file)
  r2 = relative(baseline_file)
  if cmd_out.returncode == 0:
    return cmd_out.returncode
  if args.update:
    shutil.copy(output_file, baseline_file)
    print(f'Updated {r2}')
    return cmd_out.returncode
  diff_file.parent.mkdir(exist_ok=True, parents=True)
  with open(diff_file,'w') as f:
    f.write(cmd_out.stdout.decode())
  print(f'Wrong results in {r1}')
  print(f'To compare:')
  print(f'    vi -d {r1} {r2}')
  print(f'To update:')
  print(f'    cp {r1} {r2}')
  print()
  return cmd_out.returncode

def runQuery(mode, file):
  print(f'-- {file}')
  output_file, baseline_file, diff_file = getOutputFile(file, mode)
  if not args.info:
    print(f'Writing results to output/')
    fo = open(output_file,'w')
  with open(file) as fi:
    for line in fi:
      cmd_out = subprocess.run(["gsql", "-g", "test_graph", line], stdout=subprocess.PIPE).stdout.decode()
      # if output is json
      if cmd_out.startswith('{'):
        cmd_out = sort_json(cmd_out)
      if args.info:
        print(line.rstrip('\n'))
        print(cmd_out.rstrip('\n')+'\n')
      else:
        fo.write(line.rstrip('\n')+'\n')
        fo.write(cmd_out.rstrip('\n')+'\n\n')
  if not args.info:
    fo.close()
  if not baseline_file.exists():
    shutil.copy(output_file, baseline_file)
    print(f'    Created baseline {relative(baseline_file)}')
  return compare(output_file, baseline_file, diff_file)
   
def parseFiles(file_list, mode):
  print(f'{bcolor.GREEN}------------ {mode.upper()}: Parse  ------------{bcolor.ENDC}')    
  start = time()
  if mode == 'dist':
    dist_tmp.mkdir(parents=True, exist_ok=True)  
    with Pool(processes=threads) as pool:
      pool.map(parseDist, file_list)
    #shutil.rmtree(dist_tmp)
  else:
    with Pool(processes=threads) as pool:
      pool.map(parse, file_list)
  return time() - start
  
def installQueries(mode):
  print(f'\n\n{bcolor.GREEN}------------ {mode.upper()}: Install ------------{bcolor.ENDC}')
  start = time()
  if mode == 'single':
    subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY -SINGLE ALL"])
  else:
    subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY ALL"])
  return time() - start
  
def runQueries(file_list, mode):
  print(f'\n\n{bcolor.GREEN}------------ {mode.upper()}: Run GSQL----------{bcolor.ENDC}')
  start = time()
  with Pool(processes=threads) as pool:
    num_diffs = pool.map(partial(runQuery, mode), file_list)
  num_diff = sum(num_diffs)
  if num_diff == 0:
    print(f'    {bcolor.GREEN}{mode.upper()} : PASS{bcolor.ENDC}\n')
  else:
    print(f'    {bcolor.FAIL}{mode.upper()} : FAIL - {num_diff} files are differet{bcolor.ENDC}\n')
  return time() - start
  
def runShells(file_list, mode):
  print(f'\n\n{bcolor.GREEN}------------ {mode.upper()}: Run Shell----------{bcolor.ENDC}')
  start = time()
  for shell_file in file_list:
    output_file, baseline_file, diff_file = getOutputFile(shell_file)
    log_file = str(output_file).replace('.out', '.log')
    subprocess.run(f"""
      . {root}/setup/util.sh; 
      bash {shell_file} > {log_file}; 
      gclean {log_file} > {output_file}""",
      shell=True, executable="/bin/bash")
    
    num_diff = 0
    if not baseline_file.exists():
      shutil.copy(output_file, baseline_file)
      print(f'    Created baseline {relative(baseline_file)}')
    num_diff += compare(output_file, baseline_file, diff_file)
  
  if num_diff == 0:
    print(f'    {bcolor.GREEN}{mode.upper()} : PASS{bcolor.ENDC}\n')
  else:
    print(f'    {bcolor.FAIL}{mode.upper()} : FAIL - {num_diff} files are differet{bcolor.ENDC}\n')
  return time() - start

def runTest(mode, query):
  if query and query.endswith('.gsql'):
    filesInstall.append(Path(query))
    filesRun.append(Path(query.replace('.gsql','.run')))
    filesShell = []
  if query and query.endswith('.sh'):
    filesInstall = []
    filesRun = []
    filesShell = [Path(query)]
  else:
    filesInstall = []
    filesRun = []
    filesShell = list(Path('./').glob('*.sh'))  
    for f in Path('./').glob('**/*'):
      filterFiles(f, mode, filesInstall, filesRun)
  
  if len(filesRun) > 0:
    if not args.skip:
      timeParse = parseFiles(filesInstall, mode)
      timeInstall = installQueries(mode)  
    timeRun = runQueries(filesRun, mode)

  if len(filesShell) > 0:
    runShells(filesShell, mode)

  if args.time:
    print(f'\n{bcolor.GREEN}============ {mode.upper()}: Summary ============{bcolor.ENDC}')
    if len(filesRun) > 0:
      if not args.skip:
        print(f'Parse:\t{timeParse:.3f} s')
        print(f'Install:\t{timeInstall:.3f} s')
      print(f'Query:\t{timeRun:.3f} s')
    if len(filesShell) > 0:
      print(f'Shell:\t{timeShell:.3f} s')

"""
================ Main Program =======================
./driver.py read_query
./driver.py test_case
./driver.py test_case/test1.gsql
./driver.py test_case/test1.sh
===========================================================
"""
os.chdir(root)
tests = glob(f'test_case/**/{args.test}', recursive=True) 
print(f'{bcolor.GREEN}Tests to run:')
print(f'  --' + '\n  --'.join(tests) + bcolor.ENDC)

for test in tests:
  if Path(test).is_file():
    test_file = Path(test)
    test, query = str(test_file.parent), test_file.name
  else:
    query = None
  categories = test.split('/')
  print(f'\n{bcolor.GREEN}=========== Run test: {categories[-1]} ============{bcolor.ENDC}')
  if categories[0] not in ['read_query']:
    modes = ['udf']
  for mode in modes:
    os.chdir(test)
    runTest(mode, query)
    os.chdir(root)