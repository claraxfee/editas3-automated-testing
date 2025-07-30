#!/bin/bash



#PROJECTS=(Chart Cli Closure Codec Collections Compress Csv Gson JacksonCore JacksonDatabind JacksonXml Jsoup JxPath Lang Math Mockito Time)

PROJECTS=(Collections, Cli)

for PROJECT in "${PROJECTS[@]}"; do

	file=bugnums/"${PROJECT}".txt

	while IFS= read -r BUG_ID; do

		echo ""
		echo ""		
		echo "EVALUATING ${PROJECT} ${BUG_ID}"
		./wget.sh ${PROJECT} ${BUG_ID}
		

	done < "$file"
done
	



