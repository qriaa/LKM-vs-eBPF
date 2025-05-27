#!/usr/bin/env python3
import subprocess
import statistics

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

command = 'perf script --ns -F cpu,time,event | grep udp_logger'
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
        if event[0] == 'probe:udp_logger':
            opening_event = True
        elif event[0] == 'probe:udp_logger__return':
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

print(f"Scanned events: {scanned_events}")
print(f"Discarded events: {discarded_events}")
print(f"Mean: {statistics.mean(latencies)}")
print(f"Median: {statistics.median(latencies)}")
print(f"Stdev: {statistics.stdev(latencies)}")

