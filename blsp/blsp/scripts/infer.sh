export PYTHONPATH="./:$PYTHONPATH"
export TORCH_HOME="/your/path"

CUDA_VISIBLE_DEVICES=0 python3 blsp/generate.py \
    --question_file input/ADU-Skill/physics.jsonl \
    --response_file your/path/response_file.jsonl \
    --blsp_model "/your/path/blsp_lslm_7b" \
    --instruction ""
