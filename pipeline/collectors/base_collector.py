import os
import json
from abc import ABC, abstractmethod
from datetime import datetime

class BaseCollector(ABC):
    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.name = self.__class__.__name__

    @abstractmethod
    def fetch(self):
        """Fetch data from the source. Must return a list of dictionaries."""
        pass

    def save(self, data):
        """Save the collected data to the raw directory."""
        if not data:
            print(f"[{self.name}] No data to save.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[{self.name}] Saved {len(data)} items to {filepath}")

    def run(self):
        print(f"[{self.name}] Starting collection...")
        data = self.fetch()
        self.save(data)
        print(f"[{self.name}] Finished collection.")
