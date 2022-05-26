# TigerGraph GSQL Integral test suites
## Usage
1. Pre-requisites: TigerGraph, python3 
1. Set up the schema and data using
    ```sh
    ./setup.sh
    ``` 
1. Use to driver to
    * run single test
        ```sh
        ./driver.py globalAccum
        ``` 
    * A category of tests
        ```sh
        ./driver.py read_query
        ```
    * All tests
        ```sh
        ./driver.py all
        ```

## About the schema and data
The 

## Usage of the test driver `./driver.py`
./driver.py globalAccum
```


```
./setup.sh
./driver.py globalAccum



## Migrate old tests
| Old test  | new test |
| ------------- | ------------- |
| end2end/gquery/regress1  | read_query/buildIn/selectStar  |
| end2end/gquery/regress804  | read/e2e/select1  |

regress44