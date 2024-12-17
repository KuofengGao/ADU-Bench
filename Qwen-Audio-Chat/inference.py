import os
import argparse
import json
from tqdm import tqdm
from http import HTTPStatus
import dashscope


def simple_multimodal_conversation_call():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--question_file", type=str, default=None,
        help="Path to the input file", required=True
    )
    parser.add_argument(
        "--response_file", type=str, default=None,
        help="Path to the output file", required=True
    )
    args = parser.parse_args()
    

    with open(args.question_file, "r") as fin, open(args.response_file, "w") as fout:
        for line in tqdm(fin):
            data = json.loads(line.strip())
            audio = data.get("audio", None)
            
            
            """Simple single round multimodal conversation call.
            """
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"text": "You are a helpful assistant. I will have a voice conversation with you."}
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {"audio": audio},
                        {"text": "Please answer the question."},
                    ]
                }
            ]
            response = dashscope.MultiModalConversation.call(model='qwen-audio-chat',
                                                            messages=messages)
            # The response status_code is HTTPStatus.OK indicate success,
            # otherwise indicate request is failed, you can get error code
            # and message from code and message.
            if response.status_code == HTTPStatus.OK:
                response_text = response["output"]["choices"][0]["message"]["content"][0]["text"]
            else:
                print(response.code)  # The error code.
                print(response.message)  # The error message.
            
            json_string = json.dumps(
                {
                    "response": response_text,
                    "audio": audio
                },
                ensure_ascii=False
            )
            fout.write(json_string + "\n")


if __name__ == '__main__':
    simple_multimodal_conversation_call()