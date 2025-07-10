#!/bin/bash
set -e  # exit on any error (?)

BUG_ID="$1"
PROJECT="$2"
BUG_ID_STR="${PROJECT}${BUG_ID}"
EVOSUITE_TAR="${PROJECT}-${BUG_ID}b-evosuite.100.tar.bz2"

echo "checking out buggy and fixed versions"
defects4j checkout -p $PROJECT -v ${BUG_ID}b -w checked_out/buggy/${BUG_ID_STR}
defects4j checkout -p $PROJECT -v ${BUG_ID}f -w checked_out/fixed/${BUG_ID_STR}

echo "running original EvoSuite tests"
echo "if a test passes on buggy but fails on fixed, we've found a bug-triggering evosuite prefix"
defects4j test -w checked_out/buggy/${BUG_ID_STR} -s original_tars/$EVOSUITE_TAR
defects4j test -w checked_out/fixed/${BUG_ID_STR} -s original_tars/$EVOSUITE_TAR

echo "extracting EvoSuite tests"
mkdir -p ${PROJECT}${BUG_ID}_evotests
cd all_original_evotests
tar xjvf $EVOSUITE_TAR
mv org ../${PROJECT}${BUG_ID}_evotests
cd ..

echo "make changes in ${PROJECT}${BUG_ID}_evotests/org/..."
read -p "press Enter to continue after editing..."

echo "tarring and bzip2-ing modified tests"
cd ${PROJECT}${BUG_ID}_evotests
tar cvjf ../${PROJECT}${BUG_ID}.tar.bz2 .
cd ..

echo "running modified test suite on buggy version"
defects4j test -w checked_out/buggy/${BUG_ID_STR} -s ${PROJECT}${BUG_ID}.tar.bz2

echo "running modified test suite on fixed version"
defects4j test -w checked_out/fixed/${BUG_ID_STR} -s ${PROJECT}${BUG_ID}.tar.bz2

echo "done! check failed_tests/ in fixed version directory to see failing test output"

