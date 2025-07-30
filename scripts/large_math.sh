#!/bin/bash


#Chart Cli Closure Codec Collections Compress Csv Gson JacksonCore JacksonDatabind JacksonXml Jsoup JxPath Lang Math Mockito Time

PROJECTS=("$@")

for PROJECT in "${PROJECTS[@]}"; do

	file=bugnums/"${PROJECT}".txt

	while IFS= read -r BUG_ID; do

		echo ""
		echo ""		
		echo "EVALUATING ${PROJECT} ${BUG_ID}"
		./prefix_exception_eval.sh ${PROJECT} ${BUG_ID}
		

	done < "$file"
done
	



