#!/usr/bin/env python3

import psutil
import time
import os

voltage = 5.0 #tension for Raspberry pi 4

def get_cpu_frequency():
    """Get the current CPU frequency in MHz"""
    with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", "r") as f:
        freq = int(f.read().strip())
    return freq / 1000  # convert to GHz

def estimate_current(cpu_usage, cpu_freq):
    """Estimate current based on CPU usage and frequency"""
    # Base current at idle (500 MHz)
    base_current = 0.5
    # Additional current draw per GHz of frequency increase
    freq_current = (cpu_freq - 0.5) * 0.5
    # Additional current draw based on CPU usage
    usage_current = (cpu_usage / 100) * 0.5

    return base_current + freq_current + usage_current

def calculate_power(current):
    return voltage * current

def main():
    while True:
        # Obtain the actual using on the CPU
        cpu_usage = psutil.cpu_percent(interval=1)

        # Obtain the actual frequemcy the CPU
        cpu_freq = get_cpu_frequency()

        # Estimate CPU usage and frequency function
        current = estimate_current(cpu_usage, cpu_freq)

        # Calculate the frequency
        power = calculate_power(current)

        print(f"Raspberry end : CPU -> Usage: {cpu_usage}% & Frequency: {cpu_freq} GHz -> Estimated Power: {power:.2f} Watts")
        time.sleep(1)

if __name__ == "__main__":
    main()