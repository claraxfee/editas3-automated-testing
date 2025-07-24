#!/bin/bash



PROJECTS=(Cli)

for PROJECT in "${PROJECTS[@]}"; do

	file=bugnums/"${PROJECT}".txt

	while IFS= read -r BUG_ID; do

		echo ""
		echo ""		
		echo "EVALUATING ${PROJECT} ${BUG_ID}"
		./checkout.sh ${PROJECT} ${BUG_ID}
		

	done < "$file"
done
	



