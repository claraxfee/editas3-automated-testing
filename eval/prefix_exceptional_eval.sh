#!/bin/bash

PROJECT="$1"
BUG_ID="$2"

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <project> <bug_id>"
    exit 1
fi

BUG_ID_STR="${PROJECT}${BUG_ID}"

#STEP 1: CHECKOUT======================================================================================================= 

echo ""
echo ""
echo "REMOVING OLD CHECKOUTS"
rm -Rf checked_out/buggy/${PROJECT}${BUG_ID}
rm -Rf checked_out/fixed/${PROJECT}${BUG_ID}

echo ""
echo ""
echo "CHECKING OUT BUGGY AND FIXED VERSIONS"
defects4j checkout -p $PROJECT -v ${BUG_ID}b -w checked_out/buggy/${PROJECT}${BUG_ID} > logs/checkout_output_${PROJECT}${BUG_ID}b.txt 2>&1
defects4j checkout -p $PROJECT -v ${BUG_ID}f -w checked_out/fixed/${PROJECT}${BUG_ID} > logs/checkout_output_${PROJECT}${BUG_ID}f.txt 2>&1


#STEP 2: WGET=========================================================================================================== 

echo ""
echo ""
echo "WGETTING EVOSUITE TESTS FROM EDITAS2 DIRECTORY"

PREFIX_FLAG=0
JOINED_TESTS=""
EXCEPTIONAL=0
EXCEPTION_MSG=""

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

	#STEP 3: FIND BUG TRIGGERING TESTS==============================================================================
	

	echo ""
	echo ""
	echo "RUNNING ON BUGGY"
	defects4j test -w checked_out/buggy/${BUG_ID_STR} -s original_evotests/$EVOTEST_DIR/$EVOSUITE_TAR > logs/ran_buggy_${PROJECT}${BUG_ID}.txt 2>&1


	echo ""
	echo ""
	echo "RUNNING ON FIXED"
	defects4j test -w checked_out/fixed/${BUG_ID_STR} -s original_evotests/$EVOTEST_DIR/$EVOSUITE_TAR > logs/ran_fixed_${PROJECT}${BUG_ID}.txt 2>&1

	echo ""
	echo ""
	echo "searching for failing tests in logs/ran_buggy_${PROJECT}${BUG_ID}.txt"
	awk '/^Failing tests:/ {n = $3; count = (n > 0) ? n : 0; next} count > 0 {print; count--}' logs/ran_buggy_${PROJECT}${BUG_ID}.txt > logs/failing_tests_buggy_${PROJECT}${BUG_ID}.txt

	echo ""
	echo ""
	echo "searching for failing tests in logs/ran_fixed_${PROJECT}${BUG_ID}.txt"
	awk '/^Failing tests:/ {n = $3; count = (n > 0) ? n : 0; next} count > 0 {print; count--}' logs/ran_fixed_${PROJECT}${BUG_ID}.txt > logs/failing_tests_fixed_${PROJECT}${BUG_ID}.txt

	echo ""
	echo ""
	echo "if a test passes on buggy but fails on fixed"
	echo "weve found a bug-triggering evosuite prefix"

	echo ""
	echo ""
	echo "DIFF"
	diff logs/failing_tests_buggy_${PROJECT}${BUG_ID}.txt logs/failing_tests_fixed_${PROJECT}${BUG_ID}.txt > logs/diff_${PROJECT}${BUG_ID}.txt
	diff logs/failing_tests_buggy_${PROJECT}${BUG_ID}.txt logs/failing_tests_fixed_${PROJECT}${BUG_ID}.txt
	
	echo ""
	echo ""
	echo "BUG CATCHING TESTS"
	BUG_CATCHING_TESTS=$(comm -23 <(sort logs/failing_tests_fixed_${PROJECT}${BUG_ID}.txt) <(sort logs/failing_tests_buggy_${PROJECT}${BUG_ID}.txt) | sed 's/^  - //')
	comm -23 <(sort logs/failing_tests_fixed_${PROJECT}${BUG_ID}.txt) <(sort logs/failing_tests_buggy_${PROJECT}${BUG_ID}.txt) | sed 's/^  - //'

	#any tests found?
	if [[ -n "$BUG_CATCHING_TESTS" ]]; then
		PREFIX_FLAG=1
		JOINED_TESTS=$(echo "$BUG_CATCHING_TESTS" | paste -sd ";" -)
	    	echo ""
	    	echo ""
	    	echo "BUG TRIGGERING TEST FOUND!"
	    	echo ""
		echo ""
		echo "DETERMINING IF EXCEPTIONAL"
		
	    	FAILING_TESTS_FILE="checked_out/fixed/${PROJECT}${BUG_ID}/failing_tests"

  		EXCEPTION_TESTS=()

  		while IFS= read -r testname; do
    			testname_escaped=$(printf '%s\n' "$testname" | sed 's/\//\\\//g')

    			# Extract the first line after the --- testname header
    			# Check if it's an exception (not AssertionFailedError)
    			EXC_LINE=$(awk -v test="--- $testname" '  $0 == test { getline; print; exit } ' "$FAILING_TESTS_FILE")

    			if [[ -n "$EXC_LINE" ]] && [[ "$EXC_LINE" != *"AssertionFailedError"* ]]; then
      				EXCEPTIONAL=1
      				EXCEPTION_TESTS+=("$testname")
      				# Append exception message, remove newlines and commas (to keep CSV safe)
      				CLEAN_MSG=$(echo "$EXC_LINE" | tr -d '\n\r' | tr ',' ';')
      				if [[ -z "$EXCEPTION_MSGS" ]]; then
      					EXCEPTION_MSGS="$testname: $CLEAN_MSG"
      				else
        				EXCEPTION_MSGS="$EXCEPTION_MSGS; $testname: $CLEAN_MSG"
      				fi
    			fi

		done <<< "$BUG_CATCHING_TESTS"



	    	break
	else
		echo ""
		echo ""
		echo "NO FAILING TESTS FOUND IN $EVOTESTS_DIR . TRYING NEXT"
	fi
done



echo ""
echo ""
echo "WRITING TO RESULTS.CSV"
CSV_FILE="results.csv"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "project,bug_id,bug_catching_prefix?,bug_catching_tests,evosuite_dir,exceptional?,exception" > "$CSV_FILE"
fi

LINE="${PROJECT},${BUG_ID},${PREFIX_FLAG},\"${BUG_CATCHING_TESTS}\",${EVOTEST_DIR},${EXCEPTIONAL},${EXCEPTION_MSGS}"

# already exists in the results csv?
if grep -q "^${PROJECT},${BUG_ID}," results.csv; then
  # Replace the line
  awk -v proj="$PROJECT" -v bug="$BUG_ID" -v newline="$LINE" -F, '
    BEGIN { OFS="," }
    $1 == proj && $2 == bug { print newline; next }
    { print }
  ' results.csv > results.tmp && mv results.tmp results.csv
else
  # Append to the file
  echo $LINE >> results.csv
fi



