#!/bin/bash

echo "🔧 Setting up MoodMirror App Environment..."

# Install dependencies (Streamlit Cloud already does this via requirements.txt)
pip install -r requirements.txt

# Create data folder and journal CSV if not exists
mkdir -p data
if [ ! -f data/journal_entries.csv ]; then
    echo "date,text,sentiment,score" > data/journal_entries.csv
    echo "🗂️ Initialized empty journal_entries.csv"
fi

echo "✅ Setup Complete!"
