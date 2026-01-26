# manual call with a prompt to OpenAI's API

# to run make sure to execute the following
# set OPENAI_API_KEY=x
# configure your openAI project to be able to use model gpt-5-nano
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from openai import OpenAI
import os

prompt_A = """Product description: A pair of shoes that can fit any foot size.
Seed words: adaptable, fit , onmi-fit
Product names:"""

test_prompts = [prompt_A]

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],    
)

def get_response(prompt):
    response = client.chat.completions.create(
        model = "gpt-5-nano",
        messages = [
            {
                "role": "system", 
                "content": "You are a helpful assistant"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
    )
    return response.choices[0].message.content

def main():
    responses = []
    num_tests = 5

    for idx, prompt in enumerate(test_prompts):
        # prompt number as a leter
        var_name = chr(ord('A') + idx)

        for i in range(num_tests):
            # get a response from the model
            response = get_response(prompt)

            data = {
                'variant': var_name,
                'prompt': prompt,
                'response': response
            }
            responses.append(data)

    # convert responses into a dataframe
    df = pd.DataFrame(responses)

    # save dataframe to csv
    df.to_csv('prompt_responses.csv', index=False)
    print(df)

if __name__ == "__main__":
    main()