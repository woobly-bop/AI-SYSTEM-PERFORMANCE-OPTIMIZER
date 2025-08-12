# main.py
import psutil
import time
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime

st.set_page_config(page_title="AI System Performance Optimizer", layout="wide")
st.title("⚡ AI System Performance Optimizer")
st.markdown("Real-time monitoring, bottleneck prediction, and optimization suggestions.")

# Initialize CSV logging file
LOG_FILE = "system_metrics.csv"
if not pd.io.common.file_exists(LOG_FILE):
    pd.DataFrame(columns=["Time", "CPU_Usage", "RAM_Usage", "Disk_Usage"]).to_csv(LOG_FILE, index=False)

# Function to log system metrics
def log_metrics(cpu, ram, disk):
    df = pd.read_csv(LOG_FILE)
    new_data = {"Time": datetime.now().strftime("%H:%M:%S"),
                "CPU_Usage": cpu,
                "RAM_Usage": ram,
                "Disk_Usage": disk}
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

# Function to predict bottleneck using linear regression
def predict_threshold(metric_list, threshold=80):
    if len(metric_list) < 5:
        return None
    X = np.arange(len(metric_list)).reshape(-1, 1)
    y = np.array(metric_list)
    model = LinearRegression()
    model.fit(X, y)
    future_time = np.array([[len(metric_list) + 5]])
    predicted = model.predict(future_time)[0]
    return predicted if predicted >= threshold else None

# Real-time dashboard loop
cpu_list, ram_list, disk_list = [], [], []

placeholder = st.empty()

while True:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    cpu_list.append(cpu)
    ram_list.append(ram)
    disk_list.append(disk)

    log_metrics(cpu, ram, disk)

    # Prediction
    cpu_alert = predict_threshold(cpu_list)
    ram_alert = predict_threshold(ram_list)

    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("🖥 CPU Usage (%)", f"{cpu}%")
        col2.metric("💾 RAM Usage (%)", f"{ram}%")
        col3.metric("📀 Disk Usage (%)", f"{disk}%")

        st.subheader("📊 Usage Trends")
        df = pd.read_csv(LOG_FILE)
        st.line_chart(df.set_index("Time"))

        st.subheader("🔮 AI Predictions & Suggestions")
        if cpu_alert:
            st.warning(f"⚠ CPU may exceed 80% soon (Predicted: {cpu_alert:.2f}%) - Close heavy apps.")
        if ram_alert:
            st.warning(f"⚠ RAM may exceed 80% soon (Predicted: {ram_alert:.2f}%) - Free up memory.")

    time.sleep(2)