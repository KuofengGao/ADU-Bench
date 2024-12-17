import re
import json
import argparse
from tqdm import tqdm
from openai import OpenAI 
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument(
    "--question_file", type=str, default=None,
    help="Path to the input file", required=True
)
parser.add_argument(
    "--response_file", type=str, default=None,
    help="Path to the response file", required=True
)
parser.add_argument(
    "--output_file", type=str, default=None,
    help="Path to the output file", required=True
)
args = parser.parse_args()


if 'pause' in args.question_file or 'intonation' in args.question_file:
    PROMPT_TEMPLATE = \
    '''Please evaluate the following predicted answer in response to the user question and a referenced answer is provided.

    Question: {question}
    Referenced answer: {answer}
    Predicted answer: {pred}

    Please rate the correctness of the predicted answer.
    If the predicted answer matches the referenced answer totally, provide a score of 10 else a score of 0.
    DO NOT PROVIDE ANY OTHER OUTPUT TEXT OR EXPLANATION. Only provide the score.

    Output:
    '''
else:
    PROMPT_TEMPLATE = \
    '''Please evaluate the following LALMs' response for the user query and a reference is provided.

    Query: {query}
    Reference: {reference}
    Response: {response}

    Please rate the helpfulness, relevance, accuracy, and comprehensiveness of the LALMs' response.
    Please provide an overall score on a scale of 0 to 10, where a higher score indicates better overall performance.
    DO NOT PROVIDE ANY OTHER OUTPUT TEXT OR EXPLANATION. Only provide the score.

    Output:
    '''


def gpt_crawler(prompt, retry=5):
    content = prompt
    messages_l = [{'role': 'system', 'content': 'You are a helpful and precise assistant for checking the quality of the predicted answer.'}, {"role": "user", "content": content}]

    for _ in range(retry):
        try:
            client = OpenAI(api_key=your_api_key)
            completion = client.chat.completions.create(
                model="gpt-4-0613",
                messages=messages_l
            )
            response = completion["choices"][0]["message"]["content"]
            break
        except Exception as e:
            # print(e)
            response = ""

    return response


pattern = r'(\d+(?:\.\d+)?)'

def generate_score():
    score_list = []
    with open(args.question_file, "r") as fin1, open(args.response_file, "r") as fin2, open(args.output_file, "w") as fout:
        for line1, line2 in tqdm(zip(fin1, fin2)):
            data1, data2 = json.loads(line1.strip()), json.loads(line2.strip())
            
            question, answer, source, category = data1["question"], data1["answer"], data1["source"], data1["category"]
            response, audio = data2["response"], data2["audio"]

            prompt_content = PROMPT_TEMPLATE.format(query=question, reference=answer, response=response)
            generated_text = gpt_crawler(prompt_content)

            match = re.search(pattern, generated_text)
            if match:
                score = float(match.group(1))
            else:
                score = float(0)

            score_list.append(score)
            json_string = json.dumps(
                {
                    "question": question,
                    "answer": answer,
                    "response": response,
                    "audio": audio,
                    "source": source,
                    "category": category,
                    "score": score
                },
                ensure_ascii=False
            )
            fout.write(json_string + "\n")
            print('Evaluation score: ', np.mean(score_list))


if __name__ == '__main__':
    generate_score()

