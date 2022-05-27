# TigerGraph GSQL Integral test suites
## Usage
1. Pre-requisites: TigerGraph, python3 
1. load utility functions, this provide utilities `cdregress`, `cdtest`, `ggsql`
    ```
    . setup/util.sh
    ```
1. Set up the schema, and load data (require VPN connection)
    ```sh
    setup/setup.sh
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
Other usages of `./driver.py`    
* `--skip` or `-s` to skip parse and install, only run queries.
* `--mode [mode]` or `-m [mode]` to run only one mode.
* `--info` or `-i` print results to terminal not to log file.
* `--real` or `-r` show difference in realtime.

For example, I use  `./driver.py vSetAssign1 -rsim udf` to debug single query or test.

## Test case guidelines
1. test cases are located in `/*categories*/[test folder]/[query_name].gsql`, test folder name must be unique across different categories
1. The query name must be in format of `[test folder]_[query Name]###`
1. Please use attribute `creationDate` or `creationEpoch` to filter vertices. The creation date is between 2010-01-01 and 2013-01-01. For example,
    ```gsql
    S = SELECT s FROM tuplePerson:s WHERE s.creationDate < to_datetime("2010-01-02")
    ```
1. Length of each print statment is required to be less than 200. 
1. Utility function `check_stat` can check the data statistics. The data set has dominant number of `Comment` vertices. Writing queries on `Comment` vertices require preformance consideration.
1. About Comments in query. We use Github internal log to track the last author and modified date. Comments need to address 
    * The tested functionality or documentation link
    * The discovered or tested bug and ticket number 

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