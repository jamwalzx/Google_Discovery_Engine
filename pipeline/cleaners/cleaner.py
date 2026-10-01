import os
import json
import glob
from langdetect import detect, LangDetectException
import hashlib

class Cleaner:
    def __init__(self, raw_dir="data/raw", cleaned_dir="data/cleaned"):
        self.raw_dir = raw_dir
        self.cleaned_dir = cleaned_dir
        os.makedirs(self.cleaned_dir, exist_ok=True)

    def load_raw_data(self):
        all_data = []
        # Find all json files in raw_dir
        pattern = os.path.join(self.raw_dir, "*.json")
        for filepath in glob.glob(pattern):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                except json.JSONDecodeError:
                    print(f"[Cleaner] Error reading {filepath}")
        print(f"[Cleaner] Loaded {len(all_data)} raw records across all files.")
        return all_data

    def get_hash(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def process(self):
        raw_data = self.load_raw_data()
        
        seen_hashes = set()
        cleaned_data = []
        
        for item in raw_data:
            text = item.get("original_text", "").strip()
            
            # Skip empty
            if not text:
                continue
                
            # Skip short generic reviews
            if len(text.split()) < 3 and item.get("rating", 0) in [4, 5]:
                continue
                
            # Deduplication
            text_hash = self.get_hash(text)
            if text_hash in seen_hashes:
                continue
            seen_hashes.add(text_hash)
            
            # Language detection
            lang = item.get("language_original", "en")
            try:
                detected_lang = detect(text)
                lang = detected_lang
            except LangDetectException:
                pass
            
            item["language_original"] = lang
            
            # For MVP, we keep the original_text as is. 
            # In a full run, we would call a translation API here for non-en.
            item["translated_text"] = text if lang == "en" else "[PENDING TRANSLATION] " + text
            
            cleaned_data.append(item)
            
        print(f"[Cleaner] Cleaned data: {len(cleaned_data)} records remaining after deduplication & filtering.")
        
        # Save cleaned dataset
        out_filepath = os.path.join(self.cleaned_dir, "cleaned_dataset.json")
        with open(out_filepath, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
            
        print(f"[Cleaner] Saved cleaned dataset to {out_filepath}")
        return cleaned_data
