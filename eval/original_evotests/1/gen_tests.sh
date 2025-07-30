#!/bin/bash


PROJECTS = ("@")


for PROJECT in "${PROJECTS[@]}"; do
	
	file=bugnums/"${PROJECT}".txt

        while IFS= read -r BUG_ID; do

                echo ""
                echo ""
                echo "GEN TESTS FOR ${PROJECT} ${BUG_ID}"
                gen_tests.pl -g evosuite -p ${PROJECT} -v {$BUG_ID}b -n 1 -o out_${PROJECT}_{$BUG_ID} -b 180


        done < "$file"
done


