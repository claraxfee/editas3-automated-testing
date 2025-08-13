import csv
import sys
import time
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")


def prompt_chatgpt(prompt):
    response=client.chat.completions.create(
            model="gpt-4", 
            messages = [
                {"role":"system", "content": "You are an expert Java software developer. You will be given a line from a CSV containing 3 fields as follows: label,test,fm,docstring,project,bug_num,full_test_name. The second field represents a prefix, ie. an incomplete unit test. The 3rd field represents the method under test. The 4th field represents the Java docstring for that method under test. Based on this information, your job is to determine if the developer who wrote the method under test intended for an exception to occur under the conditions of the prefix."  },
                {"role":"user", "content": prompt}
        ],
        temperature = 0.0
    )
    return response.choices[0].message.content.strip() # model's answer as string 

if len(sys.argv) < 2:
    print("pass in input and output files as command line arguements")

input_csv = sys.argv[1]

output_csv = sys.argv[2]


with open(input_csv, newline='', encoding='utf-8') as infile, \
        open(output_csv, newline='', mode='w', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader)
            writer.writerow(header + ["chatgpt_response"])

            for idx, row in enumerate(reader):
                
                prompt = f"Based on the following information, is an exception expected to occur when the unit test is executed? If an exception is expected to occur, reply only with the number '0'. If no exception is expected to occur, reply only with the number 1.'\n\nHere is the information: \n\n {row}"

                response = prompt_chatgpt(prompt)

                time.sleep(1)

                writer.writerow(row + [response])



