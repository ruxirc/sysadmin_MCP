#!/bin/bash

ollama serve &

PID=$!

sleep 10

if ! ollama list | grep -q "llama3.2:3b"; then
    echo "nu am gasit modelul => il descarc"
    ollama pull llama3.2:3b
else
    echo "am deja modelul, nu il mai descarc"
fi

wait $PID