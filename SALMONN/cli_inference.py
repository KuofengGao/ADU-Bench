# Copyright (2024) Tsinghua University, Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import re
import argparse
from tqdm import tqdm

import torch
from transformers import WhisperFeatureExtractor

from config import Config
from models.salmonn import SALMONN
from utils import prepare_one_sample


parser = argparse.ArgumentParser()
parser.add_argument("--cfg-path", type=str, required=True, help='path to configuration file')
parser.add_argument("--device", type=str, default="cuda:0")
parser.add_argument(
    "--question_file", type=str, default=None,
    help="Path to the input file"
)
parser.add_argument(
    "--response_file", type=str, default=None,
    help="Path to the output file"
)
parser.add_argument(
    "--options",
    nargs="+",
    help="override some settings in the used config, the key-value pair "
    "in xxx=yyy format will be merged into config file (deprecate), "
    "change to --cfg-options instead.",
)

args = parser.parse_args()
cfg = Config(args)

model = SALMONN.from_config(cfg.config.model)
model.to(args.device)
model.eval()

wav_processor = WhisperFeatureExtractor.from_pretrained(cfg.config.model.whisper_path)


with open(args.question_file, "r") as fin, open(args.response_file, "w") as fout:
    for line in tqdm(fin):
        data = json.loads(line.strip())
        audio = data.get("audio", None)

        wav_path = audio 
        prompt = "Please answer the question." 

        samples = prepare_one_sample(wav_path, wav_processor)
        prompt = [
            cfg.config.model.prompt_template.format("<Speech><SpeechHere></Speech> " + prompt.strip())
        ]
        with torch.cuda.amp.autocast(dtype=torch.float16):
            response = model.generate(samples, cfg.config.generate, prompts=prompt)[0]


        pattern = r'<s>(.*?)<\/s>'
        match = re.search(pattern, response, re.DOTALL)
        if match:
            extracted_text = match.group(1).strip()
        else:
            extracted_text = response

        json_string = json.dumps(
            {
                "response": extracted_text,
                "audio": audio
            },
            ensure_ascii=False
        )
        fout.write(json_string + "\n")

