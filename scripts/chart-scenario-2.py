#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np

from latency import get_latencies

latency_data_path = "results/scenario-2/latency-data/"
perf_data_dir = "results/scenario-2/perf-data/"
latency_charts_dir = "results/scenario-2/latency-charts/"
#latency_chart_path = "results/scenario-2/latency-chart.png"

tests = [
    "control-syscalls-counter",
    "lkm-syscalls-counter",
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

def generate_comparison_hist_chart(
        latency_range,
        count_range,
        data_dict,
        output_path
        ):
    fig, axs = plt.subplots(len(data_dict), 1, sharex=True)
    fig.subplots_adjust(hspace=0)

    axis_ranges = [
        latency_range[0], latency_range[1],
        count_range[0], count_range[1]
    ]

    hist_bins = np.linspace(latency_range[0], latency_range[1], num=200)

    for i, (key, result) in enumerate(data_dict.items()):
        median = np.median(result)
        max = np.max(result)
        axs[i].grid(alpha=0.3)
        axs[i].axis(axis_ranges)
        axs[i].axvline(x=median, color='r', linestyle='--')
        axs[i].hist(result, bins=hist_bins, label = key)
        axs[i].scatter(max, 0, marker='x') #label = "Najwyższe odnotowane opóźnienie"
        axs[i].legend()
        axs[i].yaxis.get_major_ticks()[0].set_visible(False) # Hide the 0 tick so it doesn't overlap

        latency_outliers = (
            len(np.where(np.asarray(result) < latency_range[0])[0]),
            len(np.where(np.asarray(result) > latency_range[1])[0])
        )
        print(f"Did not plot every entry for {key}:")
        print(f"Too-small outliers: {latency_outliers[0]} ({(latency_outliers[0] / len(result))*100}%)")
        print(f"Too-big outliers: {latency_outliers[1]} ({(latency_outliers[1] / len(result))*100}%)")
        print(f"Biggest outlier: {max*1000000} microseconds")
        print(f"Median: {median*1000000} microseconds")

    last_ax = axs[len(axs)-1]
    last_ax.xaxis.set_major_formatter(lambda x, pos: round(x*1000000, 2))
    last_ax.yaxis.get_major_ticks()[0].set_visible(True)

    fig.text(0.5, 0.03, r'Opóźnienia [${\mu}s$]', ha='center')
    fig.text(0.02, 0.5, 'Zaobserwowane wywołania funkcji', va='center', rotation='vertical')

    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")


def get_data_for_syscall(syscall, results):
    return {
        "Test kontrolny": results['control-syscalls-counter'][f"__x64_sys_{syscall}"],
        "LKM": results['lkm-syscalls-counter'][f"__x64_sys_{syscall}"],
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
