#!/bin/bash

PROJECT="$1"
BUG_ID="$2"

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <project> <bug_id>"
    exit 1
fi

BUG_ID_STR="${PROJECT}${BUG_ID}"

# STEP 1: CHECKOUT
echo ""
echo "REMOVING OLD CHECKOUTS"

rm -Rf checked_out/buggy/${PROJECT}${BUG_ID}
rm -Rf checked_out/fixed/${PROJECT}${BUG_ID}

echo ""
echo "CHECKING OUT BUGGY AND FIXED VERSIONS"

defects4j checkout -p $PROJECT -v ${BUG_ID}b -w checked_out/buggy/${PROJECT}${BUG_ID} > logs/checkout_output_${PROJECT}${BUG_ID}b.txt 2>&1
defects4j checkout -p $PROJECT -v ${BUG_ID}f -w checked_out/fixed/${PROJECT}${BUG_ID} > logs/checkout_output_${PROJECT}${BUG_ID}f.txt 2>&1

