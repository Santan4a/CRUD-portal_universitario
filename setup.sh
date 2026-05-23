#!/bin/bash

#bash setup.sh, cod para rodar o script do setup.

if command -v python &> /dev/null; then
    PYTHON=python

elif command -v python3 &> /dev/null; then
    PYTHON=python3

else
    echo "Python não encontrado"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Ambiente virtual não encontrado! Criando ambiente virtual..."
    
    if ! $PYTHON -m venv .venv; then
        echo "Erro ao criar ambiente virtual"
        exit 1
    fi
fi

if [ -f ".venv/Scripts/python.exe" ]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
    VENV_PYTHON=".venv/bin/python"
else
    echo "Python do ambiente virtual não encontrado"
    exit 1
fi

$VENV_PYTHON -m pip install -r requirements.txt