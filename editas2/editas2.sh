#!/bin/bash

set -euo pipefail

# === Step 1: Copy txt files and cd to IR directory ===
cp txt/*.txt ../../Artifact-of-Assertion-ICSE22/
cd ../../Artifact-of-Assertion-ICSE22/
echo "finished cp .txt files over to IR directory" 

# === Step 2–4: Loop over bugs 1–87 ===
for i in $(seq 1 87); do
    echo "[Bug $i] Starting"

    # Step 3: Clean input file
    python clean_data.py "$i.txt" > "query_${i}.txt"

    # Step 4.1: Update config.txt (line 2)
    sed -i "2s|.*|query_${i}.txt|" config.txt

    # Step 4.2: Run IR
    mkdir -p "out_${i}"
    python Retrieval/IR.py config.txt "out_${i}"

    # Step 4.3: Copy result to EditAs2 dataset dir
    cp "out_${i}/IRResultTest.txt" ../EditAs2/dataset

    # Step 4.4: Run EditAs2
    cd ../EditAs2/dataset

    python prepare_data.py > sample.jsonl

    cd ../scripts/
    bash test.sh > out.txt
    cp out.txt ../dataset
    cd ../dataset

    # Step 4.5: Append result to results.csv
    tail -n 2 out.txt | head -n 1 >> results.csv

    echo "[Bug $i] Done"
    cd ../../Artifact-of-Assertion-ICSE22/
done

echo "[All Done] Results appended to EditAs2/dataset/results.csv"

