import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

class StageAOutput(BaseModel):
    retrieval_related: str = Field(description="Must be 'yes', 'adjacent', or 'no'")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reason: str = Field(description="Short reason for classification")

def run_stage_a(input_file="data/cleaned/cleaned_dataset.json", output_file="data/llm_output/stage_a_filtered.json"):
    print("=== Running Stage A: Relevance Filter ===")
    load_dotenv()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return []
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_path = "prompts/v1/stage_a_filter.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # We use gemini-1.5-flash for Stage A (Fast/Cheap)
    model = 'gemini-1.5-flash'
    
    filtered_data = []
    
    for idx, item in enumerate(data):
        print(f"Processing {idx+1}/{len(data)}...")
        text = item.get("original_text", "")
        if not text:
            continue
            
        try:
            response = client.models.generate_content(
                model=model,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=StageAOutput,
                    temperature=0.1
                )
            )
            
            result = json.loads(response.text)
            item["stage_a"] = result
            
            if result.get("retrieval_related") in ["yes", "adjacent"]:
                filtered_data.append(item)
                
        except Exception as e:
            print(f"Error processing item {idx}: {e}")
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
    print(f"Stage A complete. Kept {len(filtered_data)} out of {len(data)} records.")
    return filtered_data
