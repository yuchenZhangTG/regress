#!/usr/bin/python3
import argparse
from pathlib import Path
from glob import glob
import subprocess

parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test',  type=str, help='directory name of the test')
output = Path('./output')

def check(test_dir):
  # check the uniqueness of the test folder
  # check the uniqueness of the query name
  pass

def run_test(test_dir):
  test_dir = Path(test_dir)
  # catogorize the files
  modes = ['all', 'udf', 'gpr', 'interp']
  files = {'all':[], 'udf':[], 'gpr':[], 'interp':[], 'gsql':[], 'sh':[]}
  for f in test_dir.iterdir():
    name = f.name.split('.')
    if len(name) >= 3 and name[-2] in modes:
      files[name[-2]].append(f)
    elif name[-1] == 'gsql':
      files['gsql'].append(f)
    elif name[-1] == 'sh':
      files['sh'].append(f)
  # install queries
  with open('/tmp/tmp.gsql', 'w') as ftmp:
    for m in ['all', 'udf', 'gpr']:
      for f in files[m]:
        with open(f) as f:
          for line in f: ftmp.write(line)
  subprocess.run(["gsql", "-g", "test_graph", "/tmp/tmp.gsql"])
  subprocess.run(["gsql", "-g", "test_graph", "INSTALL QUERY ALL"])
  # run queries
  for q in Qrun:
    qstr = str(q)
    fout = output/qstr.replace('.gsql', '.log')
    fout.parent.mkdir(parents=True, exist_ok=True)
    f = open(fout,'w')
    subprocess.run(["gsql", "-g", "test_graph", qstr], stdout=f)
    f.close()

args = parser.parse_args()
tests = glob(f'*/{args.test}') 
print("Running tests:\n\t" + '\n\t'.join(tests))
for test in tests:
  c, name = test.split('/')
  print(c,name)
  run_test(test)
  