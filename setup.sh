mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"you@example.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml

python -m nltk_setup.py
python -m textblob.download_corpora

#!/bin/bash
mkdir -p ~/.nltk_data
python -m nltk.downloader -d ~/.nltk_data punkt averaged_perceptron_tagger wordnet
