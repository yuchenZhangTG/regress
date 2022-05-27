#!/bin/bash
pushd . > /dev/null
cd "$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
cd ..
export regress=$(pwd)
export testCase=$regress/test_case
alias cdregress="cd $regress"
alias cdtc="cd $regress/test_case"
alias cdsetup="cd $regress/setup"
alias cddata="cd $regress/setup/ldbc_snb_data-sf0.1/social_network"
alias ggsql="gsql -g test_graph"
cdtest() {
  dir=$(find $regress/test_case -name $1)
  cd $dir
}

# After 'gadmin start' done, GSQL#1 may be in WARMUP status, wait until gsql is up
wait_until_gsql_up () {
  local NUM_RETRY=0
  local RETRY_MAX=10
  echo "[GTEST_IB]"
  while [ $NUM_RETRY -lt $RETRY_MAX ]; do
    gsql -v &>/dev/null
    if [ $? -eq 0 ]; then
      break
    else
      (( NUM_RETRY++ ))
      if [ $NUM_RETRY -ge $RETRY_MAX ]; then
        echo "[GTEST_IE]"
        echo "GSQL is not ready after $RETRY_MAX retries!"
        exit 1
      else
        echo "Wait until GSQL is ready to serve... ($NUM_RETRY)"
      fi
    fi
  done
  echo "[GTEST_IE]"
}

# check statistics of vertices and edges
check_stat() {
  echo "Wait for the database to rebuild delta..."
  curl -s -H "GSQL-TIMEOUT:2500000" "http://127.0.0.1:9000/rebuildnow" > /dev/null
  echo "Vertex statistics:"
  curl -X POST "http://127.0.0.1:9000/builtins/test_graph" -d  '{"function":"stat_vertex_number","type":"*"}'
  echo
  echo
  echo "Edge statistics:"
  curl -X POST "http://127.0.0.1:9000/builtins/test_graph" -d  '{"function":"stat_edge_number","type":"*"}'
  echo
}

echoTitle() {
  echo '======================='
  echo $1
  echo '======================='
}

popd > /dev/null