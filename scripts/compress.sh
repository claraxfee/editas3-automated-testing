#!/bin/bash

PROJECT="$1"
BUG_ID="$2"

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <project> <bug_id>"
    exit 1
fi

BUG_STR="${PROJECT}${BUG_ID}"


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


	#FIND BUG TRIGGERING TESTS==============================================================================
	

	echo ""
	echo ""
	echo "RUNNING ON BUGGY"
	defects4j test -w checked_out/buggy/${BUG_STR} -s original_evotests/$EVOTEST_DIR/$EVOSUITE_TAR > logs/ran_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt 2>&1


	echo ""
	echo ""
	echo "RUNNING ON FIXED"
	defects4j test -w checked_out/fixed/${BUG_STR} -s original_evotests/$EVOTEST_DIR/$EVOSUITE_TAR > logs/ran_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt 2>&1

	echo ""
	echo ""
	echo "searching for failing tests in logs/ran_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt"
	awk '/^Failing tests:/ {n = $3; count = (n > 0) ? n : 0; next} count > 0 {print; count--}' logs/ran_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt > reports/failing_tests_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt

	echo ""
	echo ""
	echo "searching for failing tests in logs/ran_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt"
	awk '/^Failing tests:/ {n = $3; count = (n > 0) ? n : 0; next} count > 0 {print; count--}' logs/ran_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt > reports/failing_tests_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt

	echo ""
	echo ""
	echo "if a test passes on buggy but fails on fixed"
	echo "weve found a bug-triggering evosuite prefix"

	echo ""
	echo ""
	echo "DIFF:"
	diff reports/failing_tests_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt reports/failing_tests_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt > reports/diff_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt
	diff reports/failing_tests_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt reports/failing_tests_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt
	
	echo ""
	echo ""
	echo "BUG CATCHING TESTS"
	BUG_CATCHING_TESTS=$(comm -23 <(sort reports/failing_tests_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt) <(sort reports/failing_tests_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt) | sed 's/^  - //')
	comm -23 <(sort reports/failing_tests_fixed_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt) <(sort reports/failing_tests_buggy_${PROJECT}${BUG_ID}_${EVOTEST_DIR}.txt) | sed 's/^  - //'

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

    			# get the first line after the ---  
    			# assume if not AssertionFailedError, must be an exception
			EXC_LINE=$(awk -v test="--- $testname" '  $0 == test { getline; print; exit } ' "$FAILING_TESTS_FILE")

    			if [[ -n "$EXC_LINE" ]] && [[ "$EXC_LINE" != *"AssertionFailedError"* ]]; then
      				EXCEPTIONAL=1
      				EXCEPTION_TESTS+=("$testname")
      				# append exception message, remove newlines and commas
      				CLEAN_MSG=$(echo "$EXC_LINE" | tr -d '\n\r' | tr ',' ';')
      				if [[ -z "$EXCEPTION_MSGS" ]]; then
      					EXCEPTION_MSGS="$testname: $CLEAN_MSG"
      				else
        				EXCEPTION_MSGS="$EXCEPTION_MSGS; $testname: $CLEAN_MSG"
      				fi
    			fi

		done <<< "$BUG_CATCHING_TESTS" # feed in list of bug triggering tests



	    	break
	else
		echo ""
		echo ""
		echo "NO FAILING TESTS FOUND IN $EVOTEST_DIR . TRYING NEXT"
	fi
done



echo ""
echo ""
echo "WRITING TO RESULTS.CSV"
CSV="compress_result"
CSV_FILE="${CSV}.csv"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "project,bug_id,bug_catching_prefix?,bug_catching_tests,evosuite_dir,exceptional?,exception" > "$CSV_FILE"
fi

LINE="${PROJECT},${BUG_ID},${PREFIX_FLAG},\"${BUG_CATCHING_TESTS}\",${EVOTEST_DIR},${EXCEPTIONAL},${EXCEPTION_MSGS}"

# already exists in the results csv?
if grep -q "^${PROJECT},${BUG_ID}," ${CSV_FILE}; then
  # replace 
  awk -v proj="$PROJECT" -v bug="$BUG_ID" -v newline="$LINE" -F, '
    BEGIN { OFS="," }
    $1 == proj && $2 == bug { print newline; next }
    { print }
  ' ${CSV_FILE} > ${CSV}.tmp && mv ${CSV}.tmp ${CSV_FILE}
else
  # append 
  echo $LINE >> ${CSV_FILE}
fi



