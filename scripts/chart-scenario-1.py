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
    "ebpf-nojit-nf-firewall",
    "ebpf-nojit-xdp-firewall",
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
    "Test kontrolny": results['control-firewall'][tracked_function]["latencies"],
    "LKM z Netfilter": results['lkm-firewall'][tracked_function]["latencies"],
    "eBPF z Netfilter": results['ebpf-nf-firewall'][tracked_function]["latencies"],
    "eBPF bez JIT z Netfilter": results['ebpf-nojit-nf-firewall'][tracked_function]["latencies"],
    "eBPF z XDP": results['ebpf-xdp-firewall'][tracked_function]["latencies"],
    "eBPF bez JIT z XDP": results['ebpf-nojit-xdp-firewall'][tracked_function]["latencies"],
}

generate_comparison_hist_chart(
        #(0, 0.00075),
        (0, 0.0005),
        (0, 20000),
        chart_data,
        f"{latency_charts_dir}comparison-chart.png",
        figsize = (7, 8)
)

print("Generating LaTeX table...")

rows = []
rows.append("Test & Ilość opóźnień & Mediana & Średnia & Min & Max \\\\")
for key, data in chart_data.items():
    amt = len(data)
    mean = np.mean(data)
    median = np.median(data)
    std = np.std(data)
    min = np.min(data)
    max = np.max(data)

    to_mus = lambda x: x*1000000
    rows.append(f"{key} & {amt} & {to_mus(median):.2f} & {to_mus(mean):.2f} & {to_mus(min):.2f} & {to_mus(max):.2f} \\\\")

for row in rows:
    print(row)
