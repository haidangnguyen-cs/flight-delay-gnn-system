import streamlit as st
import json
import pandas as pd
import time
from kafka import KafkaConsumer
from src.utils.config_loader import config

st.set_page_config(
    page_title="Flight Delay Dashboard",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    [data-testid="stMetricValue"] { color: #1f77b4 !important; }
    [data-testid="stMetricLabel"] { color: #495057 !important; }
    
    div[data-testid="stDataFrame"] { background-color: white; border: 1px solid #dee2e6; }
    
    .header-text { color: #212529; font-weight: 700; padding-bottom: 0px; }
    .sub-header { color: #6c757d; font-size: 1rem; padding-top: 0px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_consumer():
    return KafkaConsumer(
        config.get("kafka.topic_output"),
        bootstrap_servers=config.get("kafka.bootstrap_servers")[0],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=500
    )

def main():
    st.markdown('<h1 class="header-text">✈️ Flight Delay Prediction Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time GNN Inference Pipeline (GATv2)</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("System Status")
        st.info(f"Broker: {config.get('kafka.bootstrap_servers')[0]}")
        st.info(f"Topic: {config.get('kafka.topic_output')}")
        st.success("Model: GATv2 Ready")
        
        if st.button("Reset Dashboard"):
            st.session_state.data_log = []
            st.rerun()

    if 'data_log' not in st.session_state:
        st.session_state.data_log = []

    total = len(st.session_state.data_log)
    delayed = sum(1 for x in st.session_state.data_log if x['status'] == 'DELAYED')
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Scanned Flights", total)
    col2.metric("Delays Detected", delayed)
    col3.metric("Delay Rate", f"{(delayed/total*100):.1f}%" if total > 0 else "0.0%")

    st.subheader("Live Prediction Stream")
    table_placeholder = st.empty()

    consumer = get_consumer()
    messages = consumer.poll(timeout_ms=500)
    
    if messages:
        for tp, msgs in messages.items():
            for msg in msgs:
                st.session_state.data_log.insert(0, msg.value)
        
        st.session_state.data_log = st.session_state.data_log[:100]

    if st.session_state.data_log:
        df = pd.DataFrame(st.session_state.data_log)
        
        display_df = df[['airline', 'flight_num', 'origin', 'dest', 'probability', 'status']]
        display_df.columns = ['Airline', 'Flight No.', 'Origin', 'Dest', 'Prob.', 'Status']

        def highlight_status(row):
            if row['Status'] == 'DELAYED':
                return ['color: #d32f2f; font-weight: bold'] * len(row)
            return ['color: #2e7d32'] * len(row)

        table_placeholder.dataframe(
        display_df.style.apply(highlight_status, axis=1).format({"Prob.": "{:.2%}"}),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prob.": st.column_config.TextColumn(
                "Prob.",
                width="medium",
            ),
            "Airline": st.column_config.Column(width="small"),
            "Status": st.column_config.Column(width="small"),
        }
    )
    else:
        table_placeholder.warning("Waiting for data from Kafka stream...")

    time.sleep(1)
    st.rerun()

if __name__ == "__main__":
    main()