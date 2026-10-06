import os
import json
from groq import Groq
from dotenv import load_dotenv

def run_stage_a(input_file="data/cleaned/cleaned_dataset.json", output_file="data/llm_output/stage_a_filtered.json"):
    print("=== Running Stage A: Relevance Filter (via Groq) ===")
    load_dotenv()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return []
        
    # SLICED TO 200 FOR SPEED
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)[:200]
        
    prompt_path = "prompts/v1/stage_a_filter.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # We use llama3-8b-8192 for Stage A (Fast/Cheap)
    model = 'openai/gpt-oss-20b'
    
    filtered_data = []
    
    for idx, item in enumerate(data):
        print(f"Processing {idx+1}/{len(data)}...")
        text = item.get("original_text", "")
        if not text:
            continue
            
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
            item["stage_a"] = result
            
            if result.get("retrieval_related") in ["yes", "adjacent"]:
                filtered_data.append(item)
                
        except Exception as e:
            print(f"Error processing item {idx}: {e}")
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
    print(f"Stage A complete. Kept {len(filtered_data)} out of {len(data)} records.")
    return filtered_data
