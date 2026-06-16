# 01. System dependencies

Install all operating system packages required to build both BMv2 and P4C.

This is the only dependency installation block used by the setup documentation. The following files should not repeat these commands:

- `03-build-bmv2-behavioral-model.md`
- `04-build-p4c.md`

## 1. Update APT

```bash
sudo apt-get clean
sudo apt-get update
```

If package installation fails with `404 Not Found`, refresh the package indexes again:

```bash
sudo apt-get clean
sudo apt-get update
sudo apt-get -o Acquire::Retries=3 -o Acquire::http::No-Cache=true update
```

## 2. Install dependencies

```bash
sudo apt-get install -y \
  git build-essential cmake pkg-config wget \
  autoconf automake autotools-dev libtool m4 \
  flex bison g++ gcc make \
  python3 python3-dev python3-pip python3-setuptools python3-wheel python3-venv python3-full \
  libgmp-dev libffi-dev libssl-dev \
  libboost-dev libboost-filesystem-dev libboost-program-options-dev \
  libboost-system-dev libboost-test-dev libboost-thread-dev \
  libboost-iostreams-dev libboost-graph-dev \
  libdbus-1-dev libevent-dev libfl-dev libltdl-dev \
  libnl-3-dev libnl-route-3-dev libpcap-dev \
  thrift-compiler libthrift-dev \
  protobuf-compiler libprotobuf-dev \
  libgc-dev \
  zlib1g-dev
```

## 3. Validate important tools

```bash
git --version
cmake --version | head -n 1
protoc --version
thrift --version
python3 --version
```

Expected examples:

```text
libprotoc 3.21.12
Thrift version 0.19.0
Python 3.12.x
```

Warnings such as `packages not upgraded` or `automatically installed and no longer required` are not blockers for this setup.
