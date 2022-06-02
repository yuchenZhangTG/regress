# TigerGraph GSQL Integral test suites
## Usage
1. Pre-requisites: TigerGraph, python3 
1. load utility functions, this provide [utility functions](#Utility-Functions)
    ```
    . setup/util.sh
    ```
1. Set up the schema, and load data.  
    ```sh
    setup/setup.sh
    ```
    Catalog, loading_job tests does not require the data to be loaded
    ```sh
    setup/setup.sh -nodata
    ```
1. Use the driver to
    * Run any category of tests
        ```sh
        ./driver.py catalog
        ./driver.py read_query
        ./driver.py accumClause
        ```
    * Single gsql file
        ```sh
        ./drivery userRole/userToken.sh
        ./driver.py setAccum1.gsql
        ./driver.py accumClause/setAccum1.gsql
        ```
1. The above two steps is equivalent to `gdriver [test] --setup`

Other usages of `./driver.py`    
* `--skip` or `-s` to skip query parse and compile, only run queries and compare.
* `--mode [mode]` or `-m [mode]` to run queries in a specified mode.
* `--info` or `-i` info mode, print results to terminal (default write to `output/` folder).

For example, I use  `./driver.py vSetAssign1 -sim udf` to debug single query or test.

## Test case guidelines
### Query tests (read_query, write_query)
1. Query tests are in `test_case/read_query` (Read-Only query, no data modification) and `test_case/write_query`. 
1. During the test, the driver will goes to the parent folder of GSQL files. The parent folder name must be unique. The query name must use format `[parent folder]_[query Name][Number]` so that the query name does not collide with each other.
1. Secondary extensions `udf`, `single` or `dist` can be used to make query to be installed in a certain mode. Files with a single extension `gsql` are installed in all three modes. The GSQL script to invoke query ends with `.run`. The output is `.out` and the baseline is `.base`. JSON outputs are sorted and formated before writing to `.out` files, the `.out` file should be exactly the same as the baseline file.
1. Utility function `check_stat` can check the data statistics. The data set has dominant number of `Comment` vertices. Writing queries on `Comment` vertices require preformance consideration.
1. Length of each print statment is recommended to be less than 500. Please use attribute `creationDate` or `creationEpoch` to filter vertices. The creation date for LDBC SNB data is nearly uniformly distributed between 2010-01-01 and 2013-01-01. For example, you can create a query as below and tune the parameter values to get the output length in a seasonale length. You can use `./driver.py [test folder]/[query_name].gsql -sim udf` to print results in terminal and tune the output length. To finish use use `./driver.py [test folder]/[query_name].gsql -sum udf` to update the baselines.
    ```gsql
    CREATE OR REPLACE QUERY q (datetime date) {
        S = SELECT s FROM tuplePerson:s WHERE s.creationDate < to_datetime(date)
    }
    RUN QUERY q("2010-01-02")
    ```
1. GSQL files should include comments to address 
    * The tested functionality or documentation link
    * The discovered or tested bug and ticket number

### Shell tests (catalog, loading_job, etc)
1. The shell tests can print Tags  `[GTEST_IB]`, `[GTEST_IE]` and `[GTEST_IL]`. The output is dumped to `.log` file first. Then the files is processed by `gclean file.log > file.out`. The contents between `[GTEST_IB]` and `[GTEST_IE]` are removed and the lines beginning with `GTEST_IL` are removed.
1. The json output in shells can be sorted using `sort_json` function. 

## Utility Functions
The following utility functions will be available after source `setup/util.sh`
* Utility functions for navitation
    * `cdregress` - go the regress home folder `regress`
    * `cdtc` - go to `regress/test_case`
    * `cdsetup` - go to `regress/setup`
    * `cddata` - go to the LDBC data set `regress/setup/ldbc_snb_data-sf0.1/social_network`
* Utility functions for processing the Log
    * `sort_json` - Sort json output, for exmple `echo '{"error":false, "results":[{"key":1}]}' | sort_json`
    * `gclean` - Remove contents between `[GTEST_IB]` and `[GTEST_IE]` and remove lines starting with `[GTEST_IL]`
* Utility functions for running tests
    * `ggsql` is equivalent to `gsql -g test_graph`
    * `gdriver` call the `./driver.py`
* Utility for test design
    * `check_stat` - print the statistics for the data, can be used with `check_stat | sort_json`
    * `echoTitle` and `echoNegative` - print formatted headers for postive and negative cases, respectively.
