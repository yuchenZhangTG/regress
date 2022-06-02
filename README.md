# TigerGraph GSQL Integral test suites
## Usage
1. Pre-requisites: TigerGraph, python3 
1. load utility functions, this provide utilities `cdregress`, `cdtest`, `ggsql`
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
1. Test cases are located in `/*categories*/[test folder]/[query_name].gsql`, test folder name must be unique across different categories
1. `[query_name].gsql` will be installed in all modes. Secondary extensions `udf`, `single` or `dist` can be used to make query to be installed in a certain mode. The GSQL script to call query ends with `.run`. The output is `.log` and the baseline is `.base`.
1. The query name in `[query_name].run` must be in format of `[test folder]_[query Name]###`
1. Length of each print statment is required to be less than 500. Please use attribute `creationDate` or `creationEpoch` to filter vertices. The creation date for LDBC SNB data is nearly uniformly distributed between 2010-01-01 and 2013-01-01. For example, you can create a query as below and tune the parameter values to get the output length in a seasonale length. You can use `./driver.py [test folder]/[query_name].gsql -sim udf` to print results in terminal and tune the output length. To finish use use `./driver.py [test folder]/[query_name].gsql -sum udf` to update the baselines.
    ```gsql
    CREATE OR REPLACE QUERY q (datetime date) {
        S = SELECT s FROM tuplePerson:s WHERE s.creationDate < to_datetime(date)
    }
    RUN QUERY q("2010-01-02")
    ```
1. Utility function `check_stat` can check the data statistics. The data set has dominant number of `Comment` vertices. Writing queries on `Comment` vertices require preformance consideration.
1. About Comments in query. We use Github internal log to track the last author and modified date. Comments need to address 
    * The tested functionality or documentation link
    * The discovered or tested bug and ticket number

### Shell tests (catalog, loading_job, etc)
1. The shell tests can print Tags  `[GTEST_IB]`, `[GTEST_IE]` and `[GTEST_IL]`. The output is dumped to `.log` file first. Then the files is processed by `gclean file.log > file.out`. The contents between `[GTEST_IB]` and `[GTEST_IE]` are removed and the lines beginning with `GTEST_IL` are removed.
1. 