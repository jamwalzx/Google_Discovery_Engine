import streamlit as st
import json
import os

st.set_page_config(page_title="RecallScope Labeler", layout="wide")

RAW_DATA_FILE = "../data/cleaned/cleaned_dataset.json"
GOLD_SET_FILE = "gold_set.json"

@st.cache_data
def load_data():
    if os.path.exists(RAW_DATA_FILE):
        with open(RAW_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_gold_set():
    if os.path.exists(GOLD_SET_FILE):
        with open(GOLD_SET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_gold_set(gold_data):
    with open(GOLD_SET_FILE, "w", encoding="utf-8") as f:
        json.dump(gold_data, f, indent=2, ensure_ascii=False)

def main():
    st.title("RecallScope: Gold Set Labeling Tool")
    
    data = load_data()
    gold_set = load_gold_set()
    
    if not data:
        st.warning(f"No data found at {RAW_DATA_FILE}. Run Phase 1 first.")
        return
        
    # Navigation
    if 'index' not in st.session_state:
        st.session_state.index = 0
        
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous") and st.session_state.index > 0:
            st.session_state.index -= 1
            st.rerun()
    with col2:
        st.write(f"Record {st.session_state.index + 1} of {len(data)} (Labeled: {len(gold_set)})")
    with col3:
        if st.button("Next") and st.session_state.index < len(data) - 1:
            st.session_state.index += 1
            st.rerun()

    # Current record
    record = data[st.session_state.index]
    record_id = record.get("url", str(st.session_state.index)) # Using URL as ID for simplicity
    
    st.markdown("### Source Text")
    st.info(record.get("original_text", ""))
    st.caption(f"Source: {record.get('source')} | Date: {record.get('date')} | Rating: {record.get('rating')}")
    
    st.markdown("---")
    st.markdown("### Labels")
    
    # Load existing labels if any
    existing_labels = gold_set.get(record_id, {})
    
    relevance = st.selectbox(
        "Relevance", 
        ["yes", "adjacent", "no"], 
        index=["yes", "adjacent", "no"].index(existing_labels.get("relevance", "yes")) if existing_labels.get("relevance") else 0
    )
    
    target_type = st.selectbox(
        "Target Type",
        ["trip_travel", "event_celebration", "document_id_receipt", "screenshot", "received_media", "other", "not_stated"],
        index=0 # Simplify for demo
    )
    
    failure_stage = st.selectbox(
        "Failure Stage",
        ["F1", "F2", "F3", "F4", "F5", "F6", "F0", "none"],
        index=0
    )
    
    if st.button("Save Label & Next", type="primary"):
        gold_set[record_id] = {
            "record": record,
            "labels": {
                "relevance": relevance,
                "target_type": target_type,
                "failure_stage": failure_stage
            }
        }
        save_gold_set(gold_set)
        st.success("Saved!")
        if st.session_state.index < len(data) - 1:
            st.session_state.index += 1
            st.rerun()

if __name__ == "__main__":
    main()
