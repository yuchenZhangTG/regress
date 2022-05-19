# TigerGraph GSQL Integral test suites
## Usage
To run test
```
./setup.sh
./driver.py selectStar # Run tests in ./read/e2e/selectStar/
```

## Migrate old tests
| Old test  | new test |
| ------------- | ------------- |
| end2end/gquery/regress1  | read_query/buildIn/selectStar  |
| end2end/gquery/regress804  | read/e2e/select1  |

regress44