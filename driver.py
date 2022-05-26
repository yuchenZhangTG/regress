#!/usr/bin/python3
import argparse
from pathlib import Path
from glob import glob
import subprocess
from multiprocessing import Pool, cpu_count
import os
from time import time
parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test',  type=str, help='directory name of the test')
cwd = Path(os.path.realpath(__file__)).parent
output = cwd/'output'
threads = cpu_count()

def check(test_dir):
  # check the uniqueness of the test folder
  # check the uniqueness of the query name
  pass

def parse(file):
  subprocess.run(["gsql", "-g", "test_graph", str(file)])

def parse_files(file_list):
  with Pool(processes=threads) as pool:
    pool.map(parse, file_list)

def runQuery(file):
  output_file = output/str(file).replace('.gsql', '.log')
  output_file.parent.mkdir(parents=True, exist_ok=True)
  with open(file) as fi, open(output_file,'w') as fo:
    for line in fi:
      fo.write(line)
      subprocess.run(["gsql", "-g", "test_graph", line], stdout=fo)

def runQueries(file_list):
  with Pool(processes=threads) as pool:
    pool.map(runQuery, file_list)
        
def runTest():
  # catogorize the files
  modes = ['all', 'udf', 'gpr', 'interp']
  files = {'all':[], 'udf':[], 'gpr':[], 'interp':[], 'gsql':[], 'sh':[]}
  for f in Path('.').iterdir():
    name = f.name.split('.')
    if len(name) >= 3 and name[-2] in modes:
      files[name[-2]].append(f)
    elif name[-1] == 'gsql':
      files['gsql'].append(f)
    elif name[-1] == 'sh':
      files['sh'].append(f)
  # parse queries
  start = time()
  #for m in ['all', 'udf', 'gpr']:
  #  parse_files(files[m])  
  parse_time = time() - start
  # install queries
  start = time()
  #subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY ALL"])
  install_time = time() - start
  # run queries
  start = time()
  for f in files['gsql']:
    runQuery(f)
  run_time = time() - start
  print('===============')
  print(f'parse:   {parse_time:.4f} s')
  print(f'install: {install_time:.4f} s')
  print(f'run:     {run_time:.4f} s')


args = parser.parse_args()
os.chdir(cwd)
tests = glob(f'*/{args.test}') 
print('============= Tests to run =============')
print('\n'.join(tests) + '\n')

for test in tests:
  print(f'============= {test} =============')
  c, name = test.split('/')
  os.chdir(test)
  runTest()
  os.chdir(cwd)
  