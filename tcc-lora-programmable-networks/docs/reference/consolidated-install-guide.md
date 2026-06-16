# Consolidated installation guide: BMv2 and P4C for P4Pi

This file is a compact reference of the full setup flow.

For day-to-day execution, prefer the staged files in `docs/setup/`.

## 1. Install dependencies

```bash
sudo apt-get clean
sudo apt-get update

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

## 2. Clone and prepare sources

```bash
mkdir -p ~/p4c
cd ~/p4c

git clone https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks.git
cd Programmable_Low_End_Networks/p4pi
export P4PI_DIR="$PWD"

chmod +x ./compression-files/cpfiles.sh
sudo mkdir -p /usr/share/p4c/p4include
sed -i 's/^mkdir build$/mkdir -p build/' ./compression-files/cpfiles.sh
sudo ./compression-files/cpfiles.sh
sudo chown -R "$USER:$USER" behavioral-model p4c
```

## 3. Build BMv2

```bash
cd "$P4PI_DIR/behavioral-model/targets/simple_switch"
sed -i '/^libsimpleswitch_thrift\.la$/i\  -lz \\' Makefile.am

cd "$P4PI_DIR/behavioral-model"
./autogen.sh
./configure
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## 4. Build P4C

```bash
cd "$P4PI_DIR/p4c"
rm -rf build
mkdir -p build
cd build

cmake .. -DENABLE_P4C_GRAPHS=OFF
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## 5. Validate

```bash
which p4c
which p4c-bm2-ss
which simple_switch
which simple_switch_CLI

p4c --version
simple_switch --help | head -n 5
```

Expected examples:

```text
/usr/local/bin/p4c
/usr/local/bin/p4c-bm2-ss
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
p4c 1.2.3.0 (SHA: 1576090b7 BUILD: RELEASE)
```
