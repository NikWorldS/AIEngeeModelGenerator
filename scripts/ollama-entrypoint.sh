#!/bin/bash

/bin/ollama serve &

pid=$!

sleep 5

echo "Retrieve Target model..."
ollama pull ${OLLAMA_MODEL_NAME}
echo "Done!"

wait $pid