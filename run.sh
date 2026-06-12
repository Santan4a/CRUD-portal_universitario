#!/bin/bash
set -e


#bash run.sh, cod para rodar o script run.

if [ -f ".venv/Scripts/python.exe" ]; then
    VENV_PYTHON=".venv/Scripts/python.exe"

elif [ -f ".venv/bin/python" ]; then
    VENV_PYTHON=".venv/bin/python"

else
    echo "Ambiente virtual não encontrado"
    exit 1
fi

"$VENV_PYTHON" manage.py migrate
"$VENV_PYTHON" manage.py runserver
