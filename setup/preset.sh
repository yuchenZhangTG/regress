echo '=============================='
echo 'Pre-set configurations'
echo '=============================='

#gadmin config set GSQL.EnableStringCompress true
gadmin config set GSQL.BasicConfig.LogConfig.LogLevel debug
gadmin config set RESTPP.Factory.DefaultQueryTimeoutSec 600

# set segment size
gsql "set segsize_in_bits = 15"

gadmin config apply -y
gadmin restart gsql -y