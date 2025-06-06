#!/usr/bin/env python3
from argparse import ArgumentParser
import subprocess
import statistics
import matplotlib.pyplot as plt
import numpy as np

parser = ArgumentParser()
parser.add_argument("-f", "--file", default='perf.data', dest="filename", help="Grab data from FILE")
parser.add_argument("-p", "--probe", dest="probe", help="Name of tracked function")
#parser.add_argument("-r", "--return-probe", dest="return_probe", help="Name of function's return probe")
parser.add_argument("-c", "--chart-file", default='chart.png', dest="chart_file", help="Save chart to filename")
args = parser.parse_args()

probe = f"probe:{args.probe}"
return_probe = f"probe:{args.probe}__return"


def bash(command):
    try:
        result = subprocess.run(
            command,
            shell = True,
            capture_output = True,
            text = True,
            check = True
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.returncode}")
        print(f"stdout:\n{e.stdout}")
        print(f"stderr:\n{e.stderr}")
        return None, None
    except FileNotFoundError:
        print(f"'{command}' not found.")
        return None, None

command = f'perf script -i "{args.filename}" --ns -F cpu,time,event | grep -e "{probe}" -e "{return_probe}"'
print(f"Running {command}")
stdout, stderr = bash(command)

print("Calculating latencies...")
event_strings = stdout.split('\n')
event_strings.pop() # Last element is empty

cpus = {}
for event_string in event_strings:
    cpu, time, event = event_string.split()

    cpu = int(cpu[1:4]) # example: [007]
    time = float(time[:-1]) # Trailing ':'
    event = event[:-1] # Trailing ':'

    if cpu not in cpus:
        cpus[cpu] = []

    cpus[cpu].append((event, time))

latencies = []
scanned_events = 0
discarded_events = 0

for events in cpus.values():
    event_open = False
    open_time = 0

    for event in events:
        if event[0] == probe:
            opening_event = True
        elif event[0] == return_probe:
            opening_event = False
        else:
            print("Unrecognized event!")
            discarded_events += 1
            continue

        if (event_open == opening_event):
            print("Duplicate events")
            discarded_events += 1
            continue

        if opening_event:
            event_open = True
            open_time = event[1]
        else:
            event_open = False
            latencies.append(event[1] - open_time)

        scanned_events += 1

mean = statistics.mean(latencies)
median = statistics.median(latencies)
stdev = statistics.stdev(latencies)

print(f"Calculated latencies for '{args.filename}'")
print(f"Function probe: {probe}")
print(f"Function return probe: {return_probe}")
print(f"Scanned events: {scanned_events}")
print(f"Discarded events: {discarded_events}")
print(f"Mean: {mean}")
print(f"Median: {median}")
print(f"Stdev: {stdev}")

print("Generating chart...")

fig, ax = plt.subplots(figsize=(5, 3), layout='constrained')
ax.axis([0, 0.001, 0, 15000])
ax.set_xlabel(r'Opóźnienia [${\mu}s$]')
ax.xaxis.set_major_formatter(lambda x, pos: round(x*1000000))
ax.axvline(x=median, color='r', linestyle='--')
ax.set_ylabel('Zaobserwowane wywołania funkcji')
ax.hist(latencies, bins=np.linspace(0, 0.001, num=100))
plt.savefig(args.chart_file)
print(f"Chart generated into file '{args.chart_file}'")
