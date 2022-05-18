pushd . > /dev/null

cd ..
regress="$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" >/dev/null 2>&1 && pwd )"
alias cdregress="cd $regress"
alias cdsetup="cd $regress/setup"
alias cddata="cd $regress/setup/data_set/ldbc_snb_data-small/social_network"
alias ggsql="gsql -g test_graph"
cdtest() {
  dir=$(find $regress -name $1)
  cd $dir
}

popd > /dev/null