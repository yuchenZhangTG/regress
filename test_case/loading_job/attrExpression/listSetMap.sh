#!/bin/bash
# Test Attribute expressions
# https://docs.tigergraph.com/gsql-ref/current/ddl-and-loading/creating-a-loading-job#_attributes_and_attribute_expressions

. $regress/setup/util.sh
echo "[GTEST_IB]"
#$regress/setup/setup.sh -nodata
gsql 'CLEAR GRAPH STORE -HARD'
echo "[GTEST_IE]"

echoTitle 'Test SET() LIST()'
ggsql 'DROP JOB load_list_set'
# GLE-3403 - Default value is not supported for fixed binary
# TUPLE in LIST/SET/MAP is not allowed LIST(TUP($1,$3,$5), TUP($2,$4,$6))
# 1,2 - INT | 3,4 - DOUBLE | 5,6 - DATETIME | 7,8 - STRING | 9 FB(4)
ggsql '
CREATE LOADING JOB load_list_set {
DEFINE FILENAME f;
LOAD f TO VERTEX listV VALUES ($0, LIST($1,$2), LIST($3,$4), LIST($5,$6), LIST($7,$8), _, _, $9) USING HEADER="true";
LOAD f TO VERTEX setV VALUES ($0, SET($1,$2), SET($3,$4), SET($5,$6), SET($7,$8), _, _) USING HEADER="true";
LOAD f TO VERTEX mapV VALUES ($0, MAP(($5 -> $7), ($6 -> $8)), MAP(($5 -> $7), ($6 -> $8)), _, _) USING HEADER="true";
}'
# check data
curl -s -X POST --data-binary @./data.csv 'http://localhost:9000/ddl/test_graph?tag=load_list_set&filename=f' | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/listV/0" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/listV/1" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/listV/2" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/setV/0" | sort_json # GLE-3406 - Duplicate element when loading SET attribute
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/setV/1" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/setV/2" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/mapV/0" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/mapV/1" | sort_json
curl -s -X GET "http://localhost:9000/graph/test_graph/vertices/mapV/2" | sort_json
