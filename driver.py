#!/usr/bin/python3
import argparse
from pathlib import Path
from glob import glob
import subprocess
import os

parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test',  type=str, help='directory name of the test')
cwd = Path(os.path.realpath(__file__)).parent
output = cwd/'output'

def check(test_dir):
  # check the uniqueness of the test folder
  # check the uniqueness of the query name
  pass

def runQuery(query_file):
  print(query_file)
  output_file = output/str(query_file).replace('.gsql', '.log')
  output_file.parent.mkdir(parents=True, exist_ok=True)  
  with open(query_file) as fi, open(output_file,'w') as fo:
    for line in fi:
      line = line.rstrip()
      print('\t' + line)
      subprocess.run(["echo", f"[IL] {line}"], stdout=fo)
      subprocess.run(["gsql", "-g", "test_graph", line], stdout=fo)

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
  # install queries
  
  for m in ['all', 'udf', 'gpr']:
    with open('/tmp/tmp.gsql', 'w') as ftmp:
      for f in files[m]:
          with open(f) as f:
            for line in f: ftmp.write(line)
    subprocess.run(["gsql", "-g", "test_graph", "/tmp/tmp.gsql"])
  subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY ALL"])
  
  # run queries
  for f in files['gsql']:
    runQuery(f)
  
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
  