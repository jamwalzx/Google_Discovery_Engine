import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Define strict Pydantic schemas corresponding to Stage B requirements
class Scenario(BaseModel):
    target_type: str = Field(description="trip_travel, event_celebration, person_family, child_growth, pet, screenshot, document_id_receipt, medical_health, whiteboard_notes, received_media, video, food_place, product_shopping, work_study, nostalgia_old, other, or not_stated")
    target_age: str = Field(description="days, weeks, months, about_1_year, several_years, or not_stated")
    vagueness_level: str = Field(description="0_exact_known, 1_some_clues, 2_few_clues, or 3_only_feelings")
    archetype: str = Field(description="A1, A2, A3, A4, A5, A6, A7, A8, new_candidate, or none")
    description_mode: list[str] = Field(description="List of modes: content, context, purpose, feeling, time, source")

class Clue(BaseModel):
    clue_type: str
    value: str
    confidence: str

class Memory(BaseModel):
    remembered: list[Clue]
    forgotten: list[str]

class SearchAttempt(BaseModel):
    query: str
    style: str
    result: str

class Failure(BaseModel):
    primary_stage: str = Field(description="F1, F2, F3, F4, F5, F6, F0, or none")
    secondary_stage: str = Field(description="F1-F6 or none")
    mechanism: list[str]

class Emotion(BaseModel):
    type: str
    intensity: int = Field(description="1 to 5 scale")

class EvidenceQuote(BaseModel):
    text: str = Field(description="Must be verbatim from source")

class StageBOutput(BaseModel):
    scenario: Scenario
    memory: Memory
    search_attempts: list[SearchAttempt]
    failure: Failure
    workarounds: list[str]
    outcome: str
    emotion: Emotion
    stakes: str
    evidence_quotes: list[EvidenceQuote]
    extraction_confidence: float
    notes: str

def validate_quotes(original_text, quotes):
    valid_quotes = []
    text_lower = original_text.lower()
    for q in quotes:
        if q.text.lower() in text_lower:
            valid_quotes.append(q.model_dump())
        else:
            print(f"  [Warning] Quote dropped, not verbatim: '{q.text}'")
    return valid_quotes

from dotenv import load_dotenv

def run_stage_b(input_file="data/llm_output/stage_a_filtered.json", output_file="data/llm_output/stage_b_extracted.json"):
    print("=== Running Stage B: Structured Extraction ===")
    load_dotenv()
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return []
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_path = "prompts/v1/stage_b_extraction.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # We use gemini-1.5-pro for Stage B (Complex Extraction)
    model = 'gemini-1.5-pro'
    
    extracted_data = []
    
    for idx, item in enumerate(data):
        print(f"Processing {idx+1}/{len(data)}...")
        text = item.get("original_text", "")
        
        try:
            response = client.models.generate_content(
                model=model,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=StageBOutput,
                    temperature=0.1
                )
            )
            
            result = json.loads(response.text)
            
            # Reconstruct result with pydantic to use model_dump
            pydantic_res = StageBOutput(**result)
            
            # Post-process: Validate quotes deterministically
            validated_quotes = validate_quotes(text, pydantic_res.evidence_quotes)
            
            output_dict = pydantic_res.model_dump()
            output_dict["evidence_quotes"] = validated_quotes
            
            # Merge with original item
            item["stage_b"] = output_dict
            extracted_data.append(item)
            
        except Exception as e:
            print(f"Error processing item {idx}: {e}")
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        
    print(f"Stage B complete. Extracted {len(extracted_data)} records.")
    return extracted_data
