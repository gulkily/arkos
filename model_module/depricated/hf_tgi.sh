
# Set model path to the correct location inside the container
model=Qwen/Qwen2.5-7B-Instruct""

# Ensure the model directory is mounted correctly
volume="$PWD/data"

docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
    ghcr.io/huggingface/text-generation-inference:latest --model-id $model  --quantize gptq
