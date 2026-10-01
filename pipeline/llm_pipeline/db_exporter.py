import os
import json
import sqlite3

def export_to_sqlite(input_file="data/llm_output/stage_c_enriched.json", db_path="data/artifacts/recallscope.db"):
    print(f"=== Exporting to SQLite: {db_path} ===")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not data:
        print("No data to export.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create main records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            source TEXT,
            url TEXT,
            date TEXT,
            rating INTEGER,
            original_text TEXT,
            translated_text TEXT,
            
            relevance TEXT,
            relevance_confidence REAL,
            
            target_type TEXT,
            archetype TEXT,
            primary_stage TEXT,
            outcome TEXT,
            emotion_type TEXT,
            emotion_intensity INTEGER,
            
            umap_x REAL,
            umap_y REAL,
            cluster_id INTEGER,
            
            full_json TEXT
        )
    ''')
    
    # We clear the table on each run for simplicity (idempotent)
    cursor.execute('DELETE FROM records')
    
    count = 0
    for i, item in enumerate(data):
        # basic info
        record_id = str(i) # or item.get('url') if unique
        source = item.get("source", "")
        url = item.get("url", "")
        date = item.get("date", "")
        rating = item.get("rating")
        orig_text = item.get("original_text", "")
        trans_text = item.get("translated_text", "")
        
        # stage A
        stage_a = item.get("stage_a", {})
        relevance = stage_a.get("retrieval_related", "")
        rel_conf = stage_a.get("confidence", 0.0)
        
        # stage B
        stage_b = item.get("stage_b", {})
        target_type = stage_b.get("scenario", {}).get("target_type", "")
        archetype = stage_b.get("scenario", {}).get("archetype", "")
        primary_stage = stage_b.get("failure", {}).get("primary_stage", "")
        outcome = stage_b.get("outcome", "")
        emotion_type = stage_b.get("emotion", {}).get("type", "")
        emotion_intensity = stage_b.get("emotion", {}).get("intensity", 0)
        
        # stage C
        umap_x = item.get("umap_x", 0.0)
        umap_y = item.get("umap_y", 0.0)
        cluster_id = item.get("cluster_id", -1)
        
        full_json = json.dumps(item, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO records (
                id, source, url, date, rating, original_text, translated_text,
                relevance, relevance_confidence,
                target_type, archetype, primary_stage, outcome, emotion_type, emotion_intensity,
                umap_x, umap_y, cluster_id, full_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_id, source, url, date, rating, orig_text, trans_text,
            relevance, rel_conf,
            target_type, archetype, primary_stage, outcome, emotion_type, emotion_intensity,
            umap_x, umap_y, cluster_id, full_json
        ))
        count += 1
        
    conn.commit()
    conn.close()
    
    print(f"Exported {count} records to {db_path}")
