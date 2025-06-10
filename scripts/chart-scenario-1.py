#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np

from charts import generate_comparison_hist_chart

latency_data_path = "results/scenario-1/latency-data/"
perf_data_dir = "results/scenario-1/perf-data/"
latency_charts_dir = "results/scenario-1/latency-charts/"

tracked_function = "net_rx_action"

tests = [
    "control-firewall",
    "lkm-firewall",
    "ebpf-nf-firewall",
    "ebpf-xdp-firewall"
]

results = {}
for test in tests:
    filename = f"{latency_data_path}{test}.json"
    print(f"Loading {filename}...")
    with open(filename, "r") as f:
        results[test] = json.load(f)

print(f"Loaded JSON for the following tests: {list(results.keys())}")

print("Generating chart...")

chart_data = {
    "Test kontrolny": results['control-firewall'][tracked_function],
    "LKM z Netfilter": results['lkm-firewall'][tracked_function],
    "eBPF z Netfilter": results['ebpf-nf-firewall'][tracked_function],
    "eBPF z XDP": results['ebpf-xdp-firewall'][tracked_function],
}

generate_comparison_hist_chart(
        #(0, 0.00075),
        (0, 0.00025),
        (0, 10000),
        chart_data,
        f"{latency_charts_dir}comparison-chart.png"
)
