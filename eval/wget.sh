#!/bin/bash

PROJECT="$1"
BUG_ID="$2"

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <project> <bug_id>"
    exit 1
fi

BUG_ID_STR="${PROJECT}${BUG_ID}"


#STEP 2: WGET===========================================================================================================

echo ""
echo ""
echo "WGETTING EVOSUITE TESTS FROM EDITAS2 DIRECTORY"


#loop over editas2 evosuite sets 1 thru 10

for EVOTEST_DIR in {1..10}; do

        echo ""
        echo ""
        echo "TRYING EVOSUITE SET ${EVOTEST_DIR}"

        EVOSUITE_TAR="${PROJECT}${BUG_ID}.${EVOTEST_DIR}.tar.bz2"

        cd original_evotests/${EVOTEST_DIR}

	 wget https://github.com/Lhy-apple/EditAs2/raw/refs/heads/main/evaluator/TEval-plus/data/evosuite_buggy_regression_all/${EVOTEST_DIR}/generated/${PROJECT}/evosuite/${BUG_ID}/${PROJECT}-${BUG_ID}b-evosuite.${BUG_ID}00.tar.bz2 || { echo "wget failed for test set $EVOTEST_DIR"; cd ../../; continue; }

        mv ${PROJECT}-${BUG_ID}b-evosuite.${BUG_ID}00.tar.bz2 ${PROJECT}${BUG_ID}.${EVOTEST_DIR}.tar.bz2 || { echo "mv failed for test set $EVOTEST_DIR"; cd ../../; continue; }
                                                                                                                                    cd ../../


															
															    done
