import argparse
import json
from tqdm import tqdm


def inference():
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
            
            ########### Load Your Model ###########
            response_text = your_model(audio)
            ########### Load Your Model ###########

            json_string = json.dumps(
                {
                    "response": response_text,
                    "audio": audio
                },
                ensure_ascii=False
            )
            fout.write(json_string + "\n")


if __name__ == '__main__':
    inference()
