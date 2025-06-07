#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np

from latency import get_latencies

tracked_function = "net_rx_action"
tests = [
    "lkm-firewall",
    "ebpf-nf-firewall",
    "ebpf-xdp-firewall"
]
perf_data_dir = "results/scenario-1/perf-data/"
#latency_charts_dir = "results/scenario-1/latency-charts/"
latency_chart_path = "results/scenario-1/latency-chart.png"

results = {}

for test in tests:
    print(f"Calculating latencies for {test}")
    results[test], scanned_events, discarded_events = get_latencies(f"{perf_data_dir}{test}.data", tracked_function)
    print(f"Probed function: {tracked_function}")
    print(f"Scanned events: {scanned_events}")
    print(f"Discarded events: {discarded_events}")

print("Generating chart...")

min_latency=0
max_latency=0.00075
min_counts=0
max_counts=25000

fig, axs = plt.subplots(3, 1, sharex=True)
fig.subplots_adjust(hspace=0)

test_id_to_legend = {
    "lkm-firewall": "LKM z Netfilter",
    "ebpf-nf-firewall": "eBPF z Netfilter",
    "ebpf-xdp-firewall": "eBPF z XDP"
}

for i, (key, result) in enumerate(results.items()):
    median = np.median(result)
    max = np.max(result)
    axs[i].grid(alpha=0.3)
    axs[i].axis([min_latency, max_latency, min_counts, max_counts])
    axs[i].axvline(x=median, color='r', linestyle='--')
    axs[i].hist(result, bins=np.linspace(min_latency, max_latency, num=200), label = test_id_to_legend[key])
    axs[i].scatter(max, 0, marker='x') #label = "Najwyższe odnotowane opóźnienie"
    axs[i].legend()

last_ax = axs[len(axs)-1]
last_ax.xaxis.set_major_formatter(lambda x, pos: round(x*1000000))

fig.text(0.5, 0.03, r'Opóźnienia [${\mu}s$]', ha='center')
fig.text(0.02, 0.5, 'Zaobserwowane wywołania funkcji', va='center', rotation='vertical')

plt.savefig(latency_chart_path)
print(f"Chart generated into file '{latency_chart_path}'")

