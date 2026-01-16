"""
Optional Streamlit Dashboard for ScopeSignal
Provides visual interface for classification and analysis.

Run with: streamlit run dashboard.py

Note: Install streamlit and pandas first:
    pip install streamlit pandas
"""

try:
    import streamlit as st
    import pandas as pd
    import json
    from pathlib import Path
    from datetime import datetime
except ImportError:
    print("Error: Dashboard requires streamlit and pandas")
    print("Install with: pip install streamlit pandas")
    exit(1)

from classifier import (
    ScopeSignalClassifier,
    ClassificationError,
    export_to_csv,
    export_summary_report
)
from evaluation import ClassificationMetrics


# Page config
st.set_page_config(
    page_title="ScopeSignal Dashboard",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if 'classifier' not in st.session_state:
    try:
        st.session_state.classifier = ScopeSignalClassifier()
    except ValueError as e:
        st.error(f"Failed to initialize classifier: {e}")
        st.info("Set DEEPSEEK_API_KEY environment variable and restart")
        st.stop()

if 'results' not in st.session_state:
    st.session_state.results = []


def main():
    st.title("🏗️ ScopeSignal Dashboard")
    st.markdown("**Conservative classification of NYC construction project updates**")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Single Classification", "Batch Processing", "Results Analysis", "Cache Management"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        ScopeSignal classifies construction project updates into:
        - **CLOSED** - No opportunity
        - **SOFT_OPEN** - Possible but uncertain
        - **CONTESTABLE** - Clear opportunity
        """)
    
    # Route to page
    if page == "Single Classification":
        page_single_classification()
    elif page == "Batch Processing":
        page_batch_processing()
    elif page == "Results Analysis":
        page_results_analysis()
    elif page == "Cache Management":
        page_cache_management()


def page_single_classification():
    st.header("Single Update Classification")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        update_text = st.text_area(
            "Project Update Text",
            placeholder="Enter the construction project update text here...",
            height=150
        )
    
    with col2:
        trade = st.selectbox("Trade", ["Electrical", "HVAC", "Plumbing"])
    
    if st.button("Classify", type="primary"):
        if not update_text:
            st.warning("Please enter update text")
            return
        
        with st.spinner("Classifying..."):
            try:
                result = st.session_state.classifier.classify_update(
                    update_text=update_text,
                    trade=trade
                )
                
                # Display result
                st.success("Classification Complete")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Classification", result['classification'])
                
                with col2:
                    st.metric("Confidence", f"{result['confidence']}%")
                
                with col3:
                    cache_status = "✓ Cache Hit" if result.get('_metadata', {}).get('cache_hit') else "API Call"
                    st.metric("Source", cache_status)
                
                st.markdown("---")
                st.markdown("**Reasoning:**")
                st.info(result['reasoning'])
                
                st.markdown("**Risk Note:**")
                st.warning(result['risk_note'])
                
                st.markdown("**Recommended Action:**")
                st.success(result['recommended_action'])
                
                # Store result
                result['text'] = update_text
                result['trade'] = trade
                result['timestamp'] = datetime.now().isoformat()
                st.session_state.results.append(result)
                
            except ClassificationError as e:
                st.error(f"Classification failed: {e}")


def page_batch_processing():
    st.header("Batch Processing")
    
    st.markdown("""
    Upload a JSON file with updates to classify. Format:
    ```json
    {
        "updates": [
            {"text": "Amendment 2 issued", "trade": "Electrical"},
            {"text": "RFP posted", "trade": "HVAC"}
        ]
    }
    ```
    """)
    
    uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
    
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            
            # Handle both array and object with "updates" key
            if isinstance(data, dict) and "updates" in data:
                updates = data["updates"]
            elif isinstance(data, list):
                updates = data
            else:
                st.error("JSON must be array or object with 'updates' key")
                return
            
            st.info(f"Loaded {len(updates)} updates")
            
            if st.button("Process Batch", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                
                for i, update in enumerate(updates):
                    status_text.text(f"Processing {i+1}/{len(updates)}...")
                    progress_bar.progress((i + 1) / len(updates))
                    
                    try:
                        result = st.session_state.classifier.classify_update(
                            update_text=update["text"],
                            trade=update["trade"]
                        )
                        result['text'] = update['text']
                        result['trade'] = update['trade']
                        results.append(result)
                    except Exception as e:
                        st.warning(f"Failed to classify update {i+1}: {e}")
                
                st.success(f"Processed {len(results)} updates")
                
                # Store results
                st.session_state.results.extend(results)
                
                # Show distribution
                dist = {}
                for r in results:
                    cls = r.get('classification', 'ERROR')
                    dist[cls] = dist.get(cls, 0) + 1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CLOSED", dist.get('CLOSED', 0))
                with col2:
                    st.metric("SOFT_OPEN", dist.get('SOFT_OPEN', 0))
                with col3:
                    st.metric("CONTESTABLE", dist.get('CONTESTABLE', 0))
                
        except json.JSONDecodeError:
            st.error("Invalid JSON file")


def page_results_analysis():
    st.header("Results Analysis")
    
    if not st.session_state.results:
        st.info("No results yet. Classify some updates first!")
        return
    
    results = st.session_state.results
    
    # Summary metrics
    st.subheader("Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Classified", len(results))
    
    with col2:
        closed = sum(1 for r in results if r.get('classification') == 'CLOSED')
        st.metric("CLOSED", closed)
    
    with col3:
        soft_open = sum(1 for r in results if r.get('classification') == 'SOFT_OPEN')
        st.metric("SOFT_OPEN", soft_open)
    
    with col4:
        contestable = sum(1 for r in results if r.get('classification') == 'CONTESTABLE')
        st.metric("CONTESTABLE", contestable)
    
    # Results table
    st.subheader("Detailed Results")
    
    df = pd.DataFrame([
        {
            'Text': r.get('text', 'N/A')[:60] + '...',
            'Trade': r.get('trade', 'N/A'),
            'Classification': r.get('classification', 'N/A'),
            'Confidence': r.get('confidence', 0),
            'Reasoning': r.get('reasoning', 'N/A')
        }
        for r in results
    ])
    
    st.dataframe(df, use_container_width=True)
    
    # Export options
    st.subheader("Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to CSV"):
            try:
                export_path = f"scopesignal_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                export_to_csv(results, export_path, include_metadata=True)
                st.success(f"Exported to {export_path}")
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        if st.button("Generate Summary Report"):
            try:
                report_path = f"scopesignal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                export_summary_report(results, report_path)
                st.success(f"Report saved to {report_path}")
            except Exception as e:
                st.error(f"Report generation failed: {e}")
    
    if st.button("Clear All Results", type="secondary"):
        st.session_state.results = []
        st.rerun()


def page_cache_management():
    st.header("Cache Management")
    
    from classifier.cache import ResultCache
    cache = ResultCache()
    
    stats = cache.stats()
    
    st.subheader("Cache Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Cache Entries", stats['entries'])
        st.metric("Cache Size", f"{stats['size_bytes'] / 1024:.1f} KB")
    
    with col2:
        if stats['entries'] > 0:
            st.metric("Oldest Entry", f"{stats['oldest_age_seconds'] // 60} min ago")
            st.metric("Newest Entry", f"{stats['newest_age_seconds']} sec ago")
    
    if st.button("Clear Cache", type="secondary"):
        count = cache.clear()
        st.success(f"Cleared {count} cache entries")
        st.rerun()


if __name__ == "__main__":
    main()
