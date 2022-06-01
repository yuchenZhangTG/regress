#!/bin/bash
# ========================
# Usage:
# ./setup.sh
# ./setup.sh -nodata # only schema without any data 
# ========================
pushd . > /dev/null
cd "$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
echo '=============================='
echo 'Pre-set configurations'
echo '=============================='
gadmin config set GSQL.BasicConfig.LogConfig.LogLevel debug
gadmin config set RESTPP.Factory.DefaultQueryTimeoutSec 600
gadmin config apply -y

echo '=============================='
echo 'Set up Schema'
echo '=============================='
gsql schema.gsql
if [ "$1" = "-nodata" ]; then exit 0; fi

echo '=============================='
echo 'Load data'
echo '=============================='
if [ ! -d "ldbc_snb_data-sf0.1" ]; then
  echo 'Downloading LDBC SNB SF-0.1 data.'
  wget https://storage.googleapis.com/tigergraph/ldbc_snb_data-sf0.1.tar.gz --no-check-certificate
  tar -xf ldbc_snb_data-sf0.1.tar.gz
  rm ldbc_snb_data-sf0.1.tar.gz
fi
gsql load.gsql

echo '=============================='
echo 'User defined Functions'
echo '=============================='
gsql PUT TokenBank FROM \"$(pwd)/TokenBank.cpp\"
gsql PUT ExprFunctions FROM \"$(pwd)/ExprFunctions.hpp\"