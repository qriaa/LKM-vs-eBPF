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
        "Test kontrolny": results['control-syscalls-counter'][f"__x64_sys_{syscall}"],
        "LKM": results['lkm-syscalls-counter'][f"__x64_sys_{syscall}"],
        "eBPF bez JIT": results['ebpf-nojit-syscalls-counter'][f"__x64_sys_{syscall}"],
        "eBPF": results['ebpf-syscalls-counter'][f"__x64_sys_{syscall}"],
    }

execve_data = get_data_for_syscall("execve", results)
generate_comparison_hist_chart(
    (0, 0.000175),
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
    (0, 1000000),
    write_data,
    f"{latency_charts_dir}write-chart.png"
)
