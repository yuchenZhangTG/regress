#!/bin/bash
pushd . > /dev/null

cd ..
export regress="$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
alias cdregress="cd $regress"
alias cdsetup="cd $regress/setup"
alias cddata="cd $regress/setup/data_set/ldbc_snb_data-small/social_network"
alias ggsql="gsql -g test_graph"
cdtest() {
  dir=$(find $regress -name $1)
  cd $dir
}

# After 'gadmin start' done, GSQL#1 may be in WARMUP status, this may
# cause connection failure in tests.
wait_until_gsql_up () {
  # use gsql -v to check whether gsql is ready in order to avoid unexpected gsql slow startup
  # just like we did in gsql_server_util in 2.x
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

echoTitle() {
  echo '=============='
  echo $1
  echo '=============='
}

popd > /dev/null