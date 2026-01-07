#!/bin/bash
set -e

ollama serve &
sleep 10 
ollama pull llama3.2:3b

wait $!