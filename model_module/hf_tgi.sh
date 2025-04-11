
# Set model path to the correct location inside the container
model="/data/models/mistral/weights"

# Ensure the model directory is mounted correctly
volume="$PWD"

docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
    ghcr.io/huggingface/text-generation-inference:latest --model-id $model

