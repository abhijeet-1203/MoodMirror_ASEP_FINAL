import nltk
import os
from pathlib import Path

class NLTKDataLoader:
    def __init__(self):
        self.data_dir = Path(__file__).parent / "nltk_data"
        self.ensure_data()

    def ensure_data(self):
        self.data_dir.mkdir(exist_ok=True)
        nltk.data.path.append(str(self.data_dir))
        
        required_data = [
            ('tokenizers/punkt', 'punkt'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
            ('corpora/brown', 'brown')
        ]
        
        for path, package in required_data:
            if not (self.data_dir / path).exists():
                try:
                    nltk.download(package, download_dir=str(self.data_dir), quiet=True)
                except:
                    print(f"Failed to download {package}")

# Initialize when imported
loader = NLTKDataLoader()
