#! /bin/sh

case $1 in
updater | retriever | api | asker) echo "Application sélectionnée : $1";;
*) echo "Application non reconnue" && exit;;
esac

SEPARATOR="- - - - - - - - - - - - - -"

echo "--- Update $1 libraries.---"
pip install --no-cache-dir -r requirements.txt 1> /dev/null  2> /dev/stdout

case $1 in
updater | asker) python -m spacy download en_core_web_sm;;
esac

python app_$1.py
