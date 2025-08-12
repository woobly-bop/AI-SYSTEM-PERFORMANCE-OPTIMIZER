import psutil
import time
import pandas as pd
import streamlit as st
import plotly.express as px

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(page_title="AI System Performance Optimizer",
                   layout="wide")

st.title("⚡ AI System Performance Optimizer")
st.markdown("Live system monitoring for CPU, RAM, Disk, and Network usage.")

# --------------------------
# Data Storage
# --------------------------
data = {
    "Time": [],
    "CPU (%)": [],
    "RAM (%)": [],
    "Disk (%)": [],
    "Upload (KB/s)": [],
    "Download (KB/s)": []
}

# --------------------------
# Main Monitoring Loop
# --------------------------
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 10, 2)
duration = st.sidebar.number_input("Monitoring duration (seconds)", 10, 300, 60)

start_time = time.time()
prev_net = psutil.net_io_counters()

status_placeholder = st.empty()
graph_placeholder = st.empty()

while time.time() - start_time < duration:
    current_time = time.strftime("%H:%M:%S")

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    net = psutil.net_io_counters()
    upload_speed = (net.bytes_sent - prev_net.bytes_sent) / 1024
    download_speed = (net.bytes_recv - prev_net.bytes_recv) / 1024
    prev_net = net

    # Append data
    data["Time"].append(current_time)
    data["CPU (%)"].append(cpu)
    data["RAM (%)"].append(ram)
    data["Disk (%)"].append(disk)
    data["Upload (KB/s)"].append(upload_speed)
    data["Download (KB/s)"].append(download_speed)

    df = pd.DataFrame(data)

    # Status display
    status_placeholder.markdown(
        f"⏳ Monitoring...** {len(df)} data points collected out of {duration // refresh_rate}"
    )

    # Graphs
    fig = px.line(df, x="Time", y=["CPU (%)", "RAM (%)", "Disk (%)"],
                  title="System Resource Usage")
    fig_net = px.line(df, x="Time", y=["Upload (KB/s)", "Download (KB/s)"],
                      title="Network Usage")

    graph_placeholder.plotly_chart(fig, use_container_width=True)
    graph_placeholder.plotly_chart(fig_net, use_container_width=True)

    time.sleep(refresh_rate)

st.success("✅ Monitoring Complete!")