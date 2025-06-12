#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np

from charts import generate_comparison_hist_chart

latency_data_path = "results/scenario-2/latency-data/"
perf_data_dir = "results/scenario-2/perf-data/"
latency_charts_dir = "results/scenario-2/latency-charts/"
#latency_chart_path = "results/scenario-2/latency-chart.png"

tests = [
    "control-syscalls-counter",
    "lkm-syscalls-counter",
    "ebpf-nojit-syscalls-counter",
    "ebpf-syscalls-counter"
]
tracked_functions = [ 
    "__x64_sys_execve",
    "__x64_sys_openat",
    "__x64_sys_read",
    "__x64_sys_write"
]

results = {}
for test in tests:
    filename = f"{latency_data_path}{test}.json"
    print(f"Loading {filename}...")
    with open(filename, "r") as f:
        results[test] = json.load(f)

print(f"Loaded JSON for the following tests: {list(results.keys())}")

print("Generating charts...")


def get_data_for_syscall(syscall, results):
    return {
        "Test kontrolny": results['control-syscalls-counter'][f"__x64_sys_{syscall}"]["latencies"],
        "LKM": results['lkm-syscalls-counter'][f"__x64_sys_{syscall}"]["latencies"],
        "eBPF": results['ebpf-syscalls-counter'][f"__x64_sys_{syscall}"]["latencies"],
        "eBPF bez JIT": results['ebpf-nojit-syscalls-counter'][f"__x64_sys_{syscall}"]["latencies"],
    }

def generate_latex_table(chart_data):
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

execve_data = get_data_for_syscall("execve", results)
generate_comparison_hist_chart(
    (0, 0.000225),
    (0, 800),
    execve_data,
    f"{latency_charts_dir}execve-chart.png"
)

openat_data = get_data_for_syscall("openat", results)
generate_comparison_hist_chart(
    (0, 0.000015),
    (0, 9000),
    openat_data,
    f"{latency_charts_dir}openat-chart.png"
)

read_data = get_data_for_syscall("read", results)
generate_comparison_hist_chart(
    (0, 0.000007),
    (0, 10000),
    read_data,
    f"{latency_charts_dir}read-chart.png"
)

write_data = get_data_for_syscall("write", results)
generate_comparison_hist_chart(
    (0, 0.000004),
    (0, 3000000),
    write_data,
    f"{latency_charts_dir}write-chart.png",
    y_in_thousands = True
)

print(f"LaTeX table for execve")
generate_latex_table(execve_data)
print(f"LaTeX table for openat")
generate_latex_table(openat_data)
print(f"LaTeX table for read")
generate_latex_table(read_data)
print(f"LaTeX table for write")
generate_latex_table(write_data)
