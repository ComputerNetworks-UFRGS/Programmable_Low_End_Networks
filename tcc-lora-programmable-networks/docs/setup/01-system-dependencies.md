# 01 - System Dependencies

Install the common system dependencies required by BMv2, p4c, GNU Radio validation commands, and basic test tools.

## Install Packages

```bash
sudo apt-get update
sudo apt-get install -y \
  autoconf automake libtool m4 \
  cmake g++ gcc make pkg-config \
  flex bison \
  thrift-compiler libthrift-dev \
  protobuf-compiler libprotobuf-dev \
  libpcap-dev libgmp-dev \
  libboost-dev \
  libboost-iostreams-dev \
  libboost-graph-dev \
  libboost-system-dev \
  libboost-filesystem-dev \
  libboost-program-options-dev \
  libboost-thread-dev \
  libevent-dev libssl-dev \
  libgc-dev \
  zlib1g-dev \
  iperf3 curl wget siege
```

## Notes

Keep package installation centralized in this file. Avoid repeating the same `apt-get install` block in the BMv2, p4c, GNU Radio, or validation documents.
