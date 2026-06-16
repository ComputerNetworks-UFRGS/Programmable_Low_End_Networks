# 02 - Basic Execution Tests

This document contains a filtered set of tests for a basic execution of the TCC environment.

The goal is to validate the main communication path without running every historical experiment.

## Assumptions

- VM1 IP: `192.168.200.1`
- VM2 IP: `192.168.200.2`
- TAP interface: `tap0`
- Both GNU Radio flowgraphs are already running.
- USRP devices are detected with `sudo uhd_find_devices`.

## Required Tools

```bash
sudo apt-get update
sudo apt-get install -y iperf3 curl wget siege
```

## Test 1 - Basic Connectivity

Run from VM1:

```bash
ping -I tap0 192.168.200.2
```

## Test 2 - TCP Throughput

Run on VM1:

```bash
iperf3 -s
```

Run on VM2:

```bash
iperf3 -c 192.168.200.1 -t 60
```

## Test 3 - UDP Low-Bandwidth Traffic

Run on VM1:

```bash
iperf3 -s
```

Run on VM2:

```bash
iperf3 -c 192.168.200.1 -u -b 10K -l 50 -t 60
```

## Test 4 - Basic HTTP Request

Run on VM1:

```bash
mkdir -p ~/data
echo "Hello, world - LoRa!" > ~/data/index.html
python3 -m http.server --directory ~/data 8080
```

Run on VM2:

```bash
curl http://192.168.200.1:8080/
```

Expected result:

```text
Hello, world - LoRa!
```

## Test 5 - 100 KB File Transfer

Run on VM1:

```bash
mkdir -p ~/data
dd if=/dev/zero of=~/data/100kb.bin bs=1K count=100
python3 -m http.server --directory ~/data 8080
```

Run on VM2:

```bash
time wget http://192.168.200.1:8080/100kb.bin
```

## Test 6 - Optional HTTP Load Test

Run on VM1:

```bash
mkdir -p ~/data
echo "Hello, world - LoRa!" > ~/data/index.html
python3 -m http.server --directory ~/data 8080
```

Run on VM2:

```bash
siege http://192.168.200.1:8080/ -t60s -c5
```

## Test 7 - Optional Simulated Audio File

Run on VM1:

```bash
mkdir -p ~/data
dd if=/dev/urandom of=~/data/simulated_audio_30kb.ogg bs=1K count=30
python3 -m http.server --directory ~/data 8080
```

Run on VM2:

```bash
time wget http://192.168.200.1:8080/simulated_audio_30kb.ogg -O received_audio_30kb.ogg
```

## Tests Not Included in the Basic Run

The following tests are useful for advanced evaluation, but are not part of the basic run:

- multiple UDP bitrates;
- reverse `iperf3` tests;
- 250 KB and 500 KB downloads;
- long `siege` runs;
- high-concurrency HTTP tests;
- realistic audio generation with `pico2wave`, `espeak`, or `ffmpeg`;
- repeated measurements for statistical analysis.
