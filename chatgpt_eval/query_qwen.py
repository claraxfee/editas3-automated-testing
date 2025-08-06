import csv
import sys
import time
import os

import openai

client = openai.OpenAI(
    # Use a custom endpoint compatible with OpenAI API
    base_url='http://localhost:8000/v1',  # api_base
    api_key="EMPTY"
)

def prompt_chatgpt(client, prompt):
    system = "You are an expert Java software developer. Given a method, docstring, and test prefix, determine if the developer who wrote the method under test intended for an exception to occur under the conditions of the prefix." 
    prompt = system + "\n" + prompt 
    #prompt = "Hello who are you?"
    print(prompt)
    messages = [{'role': 'user', 'content': prompt}]

    response = client.chat.completions.create(
            #model=deepseek-ai/DeepSeek-V3,
            #model="Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8",
            model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            #model="Qwen/Qwen1.5-72B",
            messages=messages,
            #prompt=prompt
            max_tokens=1024
            )

    #print(response.choices[0].message)
    return response.choices[0].message.content.strip()

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

                test_prefix, fm, docstring = row[1:4]

                prompt = f"Based on the following information, is an exception expected to occur when the unit test is executed? '\n\nHere is the information: \n\n Method: {fm} \n\n Docstring: {docstring} \n\n Test prefix: {test_prefix}"

                response = prompt_chatgpt(client, prompt)
                print(response)

                input()
                #time.sleep(1)
                print()
                print()
                print("==="*50)
                print()
                print()
                writer.writerow(row + [response])



