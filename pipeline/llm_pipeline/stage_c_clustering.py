import os
import json
import numpy as np
import umap
import hdbscan
from google import genai

def run_stage_c(input_file="data/llm_output/stage_b_extracted.json", output_file="data/llm_output/stage_c_enriched.json"):
    print("=== Running Stage C: Embeddings & Clustering ===")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return []
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not data:
        print("No data to cluster.")
        return []
        
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    embedding_model = 'text-embedding-004'
    
    texts = [item.get("original_text", "") for item in data]
    
    print("1. Generating Embeddings...")
    embeddings = []
    # Batch embeddings if API allows, here doing sequentially for simplicity
    for idx, text in enumerate(texts):
        try:
            result = client.models.embed_content(
                model=embedding_model,
                contents=text
            )
            # Some versions return .embeddings[0].values, adapting for simplicity
            # Assuming result.embeddings[0].values
            embeddings.append(result.embeddings[0].values)
        except Exception as e:
            print(f"Error embedding item {idx}: {e}")
            # Fallback zero vector
            embeddings.append([0.0]*768)
            
    embeddings = np.array(embeddings)
    
    print("2. Running UMAP...")
    # Reduce to 2 dimensions for the UI
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
    try:
        umap_result = reducer.fit_transform(embeddings)
    except Exception as e:
        print(f"UMAP failed (possibly too few samples): {e}")
        umap_result = np.zeros((len(embeddings), 2))
        
    print("3. Running HDBSCAN...")
    # Cluster the 2D data (or high-D data depending on strategy)
    try:
        clusterer = hdbscan.HDBSCAN(min_cluster_size=3)
        cluster_labels = clusterer.fit_predict(umap_result)
    except Exception as e:
        print(f"HDBSCAN failed: {e}")
        cluster_labels = [-1] * len(embeddings)
        
    # Append to data
    for i, item in enumerate(data):
        item["umap_x"] = float(umap_result[i][0])
        item["umap_y"] = float(umap_result[i][1])
        item["cluster_id"] = int(cluster_labels[i])
        item["embedding"] = embeddings[i].tolist() # Optional, can be large

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Stage C complete. Enriched {len(data)} records with clusters and UMAP coords.")
    return data
