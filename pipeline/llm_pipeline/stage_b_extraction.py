import os
import json
from groq import Groq
from dotenv import load_dotenv

def run_stage_b(input_file="data/llm_output/stage_a_filtered.json", output_file="data/llm_output/stage_b_extracted.json"):
    print("=== Running Stage B: Structured Extraction (via Groq) ===")
    load_dotenv()
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return []
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_path = "prompts/v1/stage_b_extraction.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # We use llama3-70b-8192 for Stage B (Complex Extraction)
    model = 'openai/gpt-oss-120b'
    
    extracted_data = []
    
    for idx, item in enumerate(data):
        print(f"Processing {idx+1}/{len(data)}...")
        text = item.get("original_text", "")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Merge with original item
            item["stage_b"] = result
            extracted_data.append(item)
            
        except Exception as e:
            print(f"Error processing item {idx}: {e}")
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        
    print(f"Stage B complete. Extracted {len(extracted_data)} records.")
    return extracted_data
