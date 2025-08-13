# for http requesting qwen, already started via vllm in cli

import openai
import json
import csv
import os
import sys
import time



client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)




json_format= {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "Your full thought process."
        },
        "answer": {
            "type":"integer",
            "enum": [0,1],
            "description": "1 if an exception is expected to occur in this prefix. 0 if an exception is NOT expected to occur in this prefix."
        },
        "exception_type": {
            "type":"string",
            "description": "The exception type, if it is expected. An empty string if not expected."
        }
    },
    "required": ["reasoning", "answer"]
}




system_prompt = """
You are an expert Java software developer specializing in unit testing. 
Given a method, docstring, and test prefix, your task is to determine if the developer who wrote the method under test intended for an exception to occur under the conditions of the prefix.


You will output your answer in a Json scheme with three fields: one for your reasoning, one for your answer, and one for the exception type if it is expected.

First, think through the task step by step. Then, output your full thought process into the reasoning field. Ensure you output your full thought process, but keep it short and concise--remember that each output token comes with a cost.

Second, output your answer as either a 1 or 0 in the answer field:
    If an exception is expected to occur when the prefix is executed, output a 1. 
    If an exception is NOT expected to occur when the prefix is executed, output a 0. 
    No other answers are accepted for the "answer" field.

Third, output the expected exception type into the "exception-type" field:
    If an exception is expected to occur when the prefix is executed, specify the exception type (e.g. NullArguementException).
    If an exception is NOT expected to occur when the prefix is executed, output an empty string.
    

Here are two brief examples of the task. 

Example #1:

    Information:
        Test prefix:                                                                                                                    public void test49()  throws Throwable  {       ClosureCodingConvention closureCodingConvention0 = new ClosureCodingConvention();       SimpleErrorReporter simpleErrorReporter0 = new SimpleErrorReporter();       JSTypeRegistry jSTypeRegistry0 = new JSTypeRegistry(simpleErrorReporter0);       ObjectType objectType0 = jSTypeRegistry0.createAnonymousObjectType();       SemanticReverseAbstractInterpreter semanticReverseAbstractInterpreter0 = new SemanticReverseAbstractInterpreter(closureCodingConvention0, jSTypeRegistry0);       semanticReverseAbstractInterpreter0.getRestrictedByTypeOfResult(objectType0, ""function"", false);   }

  Method under test:                                                                                                              JSType getRestrictedByTypeOfResult(JSType type, String value,                                      boolean resultEqualsValue) {     if (type == null) {       if (resultEqualsValue) {         JSType result = getNativeTypeForTypeOf(value);         return result == null ? getNativeType(CHECKED_UNKNOWN_TYPE) : result;       } else {         return null;       }     }     return type.visit(         new RestrictByOneTypeOfResultVisitor(value, resultEqualsValue));   }

        Docstring:                                                                                                                      /**    * Returns a version of {@code type} that is restricted by some knowledge    * about the result of the {@code typeof} operation.    * <p>    * The behavior of the {@code typeof} operator can be summarized by the    * following table:    * <table>    * <tr><th>type</th><th>result</th></tr>    * <tr><td>{@code undefined}</td><td>""undefined""</td></tr>    * <tr><td>{@code null}</td><td>""object""</td></tr>    * <tr><td>{@code boolean}</td><td>""boolean""</td></tr>    * <tr><td>{@code number}</td><td>""number""</td></tr>    * <tr><td>{@code string}</td><td>""string""</td></tr>    * <tr><td>{@code Object} (which doesn't implement [[Call]])</td>    *     <td>""object""</td></tr>    * <tr><td>{@code Object} (which implements [[Call]])</td>    *     <td>""function""</td></tr>    * </table>    * @param type the type to restrict    * @param value A value known to be equal or not equal to the result of the    *        {@code typeof} operation    * @param resultEqualsValue {@code true} if the {@code typeOf} result is known    *        to equal {@code value}; {@code false} if it is known <em>not</em> to    *        equal {@code value}    * @return the restricted type or null if no version of the type matches the    *         restriction    */

    Reasoning based on this information:
        "The method getRestrictedByTypeOfResult is designed to return a restricted JSType based on the result of a typeof operation. The test case passes an ObjectType, the string ""function"", and false for resultEqualsValue. According to the docstring, when resultEqualsValue is false, the method should return null if no version of the type matches the restriction. Since the ObjectType does not implement [[Call]], its typeof result is ""object"", which does not equal ""function"". Therefore, the method should return null, and no exception is expected."

    Final answer: 0
    
    Exception type: "" 


Example #2:
                                                                                                                                Information:                                                                                                                                                                                                                                                Test prefix:                                                                                                                    public void test03()  throws Throwable  {       Frequency frequency0 = new Frequency();       Object object0 = new Object();                        frequency0.addValue(object0);         ;       }    }

        Method under test:
            public void addValue(Object v) {             addValue((Comparable<?>) v);                 },                                                                                                                                                        Docstring for method under test:                                                                                                /**      * Adds 1 to the frequency count for v.      * <p>      * If other objects have already been added to this Frequency, v must      * be comparable to those that have already been added.      * </p>      *       * @param v the value to add.      * @throws IllegalArgumentException if <code>v</code> is not Comparable,       *         or is not comparable with previous entries      * @deprecated use {@link #addValue(Comparable)} instead      */                                                                                                                                                                 Reasoning based on this information:                                                                                            "The method addValue(Object v) calls addValue((Comparable<?>) v), which expects v to be a Comparable. The test passes an Object, which is not Comparable, leading to a MockIllegalArguementException. The docstring warns of IllegalArgumentException, but the actual exception is a MockIllegalArgumentException, indicating an unexpected exception."

    Final answer: 1
    
    Exception type: "MockIllegalArgumentException"
"""


def prompt_model(client, prompt):

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0,
        extra_body={
            "guided_json":json_format
        }
    )
    return response.choices[0].message.content.strip()





#main


if len(sys.argv) < 3:
    print("pass in input and output files as command line arguements")

input_csv = sys.argv[1]

output_csv = sys.argv[2]

with open(input_csv, newline='', encoding='utf-8') as infile, \
        open(output_csv, newline='', mode='w', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader)
            writer.writerow(header + ["chatgpt_response"] + ["reasoning"])
            
            idx = 0

            for idx, row in enumerate(reader):

                test_prefix, fm, docstring = row[1:4]

                prompt = f"Based on the following information, is an exception expected to occur when the unit test is executed? \n\nHere is the information: \n\n Method: {fm} \n\n Docstring: {docstring} \n\n Test prefix: {test_prefix}"

                response = prompt_model(client, prompt)

                try: 
                    parsed_response = json.loads(response)
                    reasoning_only = parsed_response["reasoning"]
                    answer_only = parsed_response["answer"]
                    exception_type = parsed_response["exception_type"]
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Raw response: {repr(response)}")
                    answer_only = "JSON_ERROR"
                    reasoning_only = "JSON_ERROR"
                    #input("Press Enter to continue...")
                except KeyError as e:
                    print(f"Missing field in JSON: {e}")
                    print(f"Parsed response: {parsed_response}")
                    answer_only = "MISSING_FIELD"
                    #input("Press Enter to continue...")
                
                time.sleep(1)
                print()
                print()
                print(idx)
                print()
                writer.writerow(row + [answer_only] + [reasoning_only] + [exception_type])
                idx += 1
                

