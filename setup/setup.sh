#!/bin/bash
pushd . > /dev/null

download_and_extract () {
  remote_file_path="$1"
  extract_path="$2"
  tar_opt=''
  if [[ "${remote_file_path}" == *.gz ]]; then
    tar_opt='--gzip'
  fi

  mkdir -p "${extract_path}"
  curl --silent --fail "ftp://ftp.graphsql.com${remote_file_path}" \
    | tar "${tar_opt}" -xf - -C "${extract_path}"
}

download_ldbc_snb_small () {
  remote_file_path='/data_set/ldbc/ldbc_snb_data-small.tar.gz'
  default_extract_path='./data_set/'
  extract_path="${1:-${default_extract_path}}"

  if [ ! -d "${extract_path}/ldbc_snb_data-small" ]; then
    echo 'Downloading LDBC SNB SF-0.1 data.'
    download_and_extract "${remote_file_path}" "${extract_path}"
  else
    echo 'Already have LDBC SNB SF-0.1 data; skipping download.'
  fi
}

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

echo '=============================='
echo 'Load data'
echo '=============================='
download_ldbc_snb_small
gsql load.gsql

echo '=============================='
echo 'User defined Functions'
echo '=============================='
gsql PUT TokenBank FROM \"$(pwd)/TokenBank.cpp\"
gsql PUT ExprFunctions FROM \"$(pwd)/ExprFunctions.hpp\"
popd > /dev/null