#!/bin/bash

PROJECT="$1"
BUG_ID="$2"
EVOTEST_DIR="$3"
BUG_ID_STR="${PROJECT}${BUG_ID}"
EVOSUITE_TAR="${PROJECT}${BUG_ID}.$EVOTEST_DIR.tar.bz2"


echo ""
echo ""
echo "WGETTING EVOSUITE TESTS FROM EDITAS2 DIRECTORY"
cd original_evotests/${EVOTEST_DIR}
wget https://github.com/Lhy-apple/EditAs2/raw/refs/heads/main/evaluator/TEval-plus/data/evosuite_buggy_regression_all/${EVOTESTS_DIR}/generated/${PROJECT}/evosuite/${BUG_ID}/${PROJECT}-${BUG_ID}b-evosuite.${BUG_ID}00.tar.bz2
mv ${PROJECT}-${BUG_ID}b-evosuite.${BUG_ID}00.tar.bz2 ${PROJECT}${BUG_ID}.${EVOTEST_DIR}.tar.bz2
cd ../../
pwd


echo ""
echo ""
echo "CHECKING OUT BUGGY AND FIXED VERSIONS"
defects4j checkout -p $PROJECT -v ${BUG_ID}b -w checked_out/buggy/${BUG_ID_STR}
defects4j checkout -p $PROJECT -v ${BUG_ID}f -w checked_out/fixed/${BUG_ID_STR}


echo ""
echo ""
echo "REMOVING OLD EVOTESTS DIRECTORY  ${BUG_ID_STR}_evotests"
rm -Rf ${BUG_ID_STR}_evotests

echo ""
echo ""
echo "RUNNING ON BUGGY"
defects4j test -w checked_out/buggy/${BUG_ID_STR} -s original_evotests/$EVOTEST_DIR/$EVOSUITE_TAR


echo ""
echo ""
echo "RUNNING ON FIXED"
defects4j test -w checked_out/fixed/${BUG_ID_STR} -s original_evotests/$EVOTEST_DIR/$EVOSUITE_TAR


echo ""
echo ""
echo "if a test passes on buggy but fails on fixed"
echo "weve found a bug-triggering evosuite prefix"

echo ""
echo ""
echo "on the buggy version, these tests were failed TODO"
echo ""
echo ""
echo "on the fixed version, these tests were failed TODO" 






