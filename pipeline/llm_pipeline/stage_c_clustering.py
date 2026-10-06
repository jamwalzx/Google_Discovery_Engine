import os
import json
import numpy as np
import umap
import hdbscan
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

def run_stage_c(input_file="data/llm_output/stage_b_extracted.json", output_file="data/llm_output/stage_c_enriched.json"):
    print("=== Running Stage C: TF-IDF Embeddings & Clustering ===")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return []
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not data:
        print("No data to cluster.")
        return []
        
    print("1. Generating Embeddings locally (TF-IDF)...")
    texts = [item.get("original_text", "") for item in data]
    
    # We use TF-IDF because it runs purely on NumPy without needing heavy PyTorch C++ binaries
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    embeddings = vectorizer.fit_transform(texts).toarray()
    
    print("2. Running Dimensionality Reduction (PCA to 50d -> UMAP to 2d)...")
    if len(embeddings) > 50:
        pca = PCA(n_components=50)
        embeddings_reduced = pca.fit_transform(embeddings)
    else:
        embeddings_reduced = embeddings
        
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
    try:
        umap_result = reducer.fit_transform(embeddings_reduced)
    except Exception as e:
        print(f"UMAP failed (possibly too few samples): {e}")
        umap_result = np.zeros((len(embeddings), 2))
        
    print("3. Running HDBSCAN...")
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

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Stage C complete. Enriched {len(data)} records with TF-IDF clusters and UMAP coords.")
    return data
