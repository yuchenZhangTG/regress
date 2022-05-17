#!/usr/bin/python3
import argparse
from pathlib import Path
from glob import glob
import subprocess

parser = argparse.ArgumentParser(description='GSQL regress test driver.')
parser.add_argument('test',  type=str, help='directory name of the test')
output = Path('./output')

def run_test(test_dir):
  test_dir = Path(test_dir)
  Qinstall = set(test_dir.glob('*.gsql'))
  Qrun = set(test_dir.glob('run*.gsql'))
  Qinstall = Qinstall - Qrun
  
  # install queries
  
  # run queries
  for q in Qrun:
    qstr = str(q)
    fout = output/qstr.replace('.gsql', '.log')
    fout.parent.mkdir(parents=True, exist_ok=True)
    f = open(fout,'w')
    subprocess.run(["gsql", qstr], stdout=f)
    f.close()
  

args = parser.parse_args()
tests = glob(f'*/*/{args.test}') 
print("Running tests:\n\t" + '\n\t'.join(tests))
for test in tests:
  c1, c2, name = test.split('/')
  print(c1,c2,name)
  run_test(test)
  