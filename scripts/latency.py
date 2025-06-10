#!/usr/bin/env python3
import json
import subprocess
from argparse import ArgumentParser
import statistics
import matplotlib.pyplot as plt
import numpy as np

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

def parse_perf_output(perf_output):
    print("Parsing perf output...")
    table = []
    event_strings = perf_output.split('\n')
    event_strings.pop() # Last element is empty

    for event_string in event_strings:
        cpu, time, event = event_string.split()

        cpu = int(cpu[1:4]) # example: [007]
        time = float(time[:-1]) # Trailing ':'
        event = event[:-1] # Trailing ':'

        table.append((cpu, time, event))
    return table

def calc_latencies_for_probe_pair(data, probe, return_probe):
    cpus = {}
    for event in data:
        cpu, time, event = event
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
                #print("Unrecognized event!")
                discarded_events += 1
                continue

            if (event_open == opening_event):
                #print("Duplicate events")
                discarded_events += 1
                continue

            if opening_event:
                event_open = True
                open_time = event[1]
            else:
                event_open = False
                latencies.append(event[1] - open_time)

            scanned_events += 1
    return (latencies, scanned_events, discarded_events)


def get_latencies(file, tracked_function):
    probe = f"probe:{tracked_function}"
    return_probe = f"probe:{tracked_function}__return"

    command = f'perf script -i "{file}" --ns -F cpu,time,event | grep -e "{probe}" -e "{return_probe}"'
    print(f"Running {command}")
    stdout, stderr = bash(command)

    print("Calculating latencies...")
    all_events = parse_perf_output(stdout)

    latencies, scanned_events, discarded_events = calc_latencies_for_probe_pair(all_events, probe, return_probe)
    print(f"Scanned events: {scanned_events}")
    print(f"Discarded events: {discarded_events}")
    return {tracked_function: latencies}


def get_latencies_multiple(file, tracked_functions):
    command = f'perf script -i "{file}" --ns -F cpu,time,event'
    print(f"Running {command}")
    stdout, stderr = bash(command)

    print("Calculating latencies...")
    all_events = parse_perf_output(stdout)

    print("Separating events...")
    by_function = {}
    for event in all_events:
        for function in tracked_functions:
            probe = f"probe:{function}"
            return_probe = f"probe:{function}__return"

            if event[2] in [probe, return_probe]:
                if function not in by_function:
                    by_function[function] = []
                by_function[function].append(event)

    for function, data in by_function.items():
        probe = f"probe:{function}"
        return_probe = f"probe:{function}__return"

        latencies, scanned_events, discarded_events = calc_latencies_for_probe_pair(data, probe, return_probe)
        print(f"Function {function}:")
        print(f"Scanned events: {scanned_events}")
        print(f"Discarded events: {discarded_events}")
        by_function[function] = latencies
    return by_function


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", default='perf.data', dest="input", help="Grab data from FILE")
    parser.add_argument("-o", "--output", default='latencies.json', dest="output", help="Save latencies to FILE")
    parser.add_argument("-p", "--probes", nargs='+', dest="probes", help="Probes to calc latency for")
    args = parser.parse_args()

    output = get_latencies_multiple(args.input, args.probes)

    print(f"Saving output to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(output, f)

