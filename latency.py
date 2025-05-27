#!/usr/bin/env python3
from argparse import ArgumentParser
import subprocess
import statistics

parser = ArgumentParser()
parser.add_argument("-f", "--file", default='perf.data', dest="filename", help="Grab data from FILE")
parser.add_argument("-p", "--probe", dest="probe", help="Name of function's probe")
parser.add_argument("-r", "--return-probe", dest="return_probe", help="Name of function's return probe")
args = parser.parse_args()

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

command = f'perf script -i "{args.filename}" --ns -F cpu,time,event | grep -e "{args.probe}" -e "{args.return_probe}"'
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
        if event[0] == args.probe:
            opening_event = True
        elif event[0] == args.return_probe:
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

print(f"Calculated latency for '{args.filename}'")
print(f"Function probe: {args.probe}")
print(f"Function return probe: {args.return_probe}")
print(f"Scanned events: {scanned_events}")
print(f"Discarded events: {discarded_events}")
print(f"Mean: {statistics.mean(latencies)}")
print(f"Median: {statistics.median(latencies)}")
print(f"Stdev: {statistics.stdev(latencies)}")

