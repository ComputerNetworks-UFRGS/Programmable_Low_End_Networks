# Print script commands and exit on errors.
set -xe

PY3LOCALPATH=`${HOME}/py3localpath.py`

move_usr_local_lib_python3_from_site_packages_to_dist_packages() {
    local SRC_DIR
    local DST_DIR
    local j
    local k

    SRC_DIR="${PY3LOCALPATH}/site-packages"
    DST_DIR="${PY3LOCALPATH}/dist-packages"

    # When I tested this script on Ubunt 16.04, there was no
    # site-packages directory.  Return without doing anything else if
    # this is the case.
    if [ ! -d ${SRC_DIR} ]
    then
	return 0
    fi

    # Do not move any __pycache__ directory that might be present.
    sudo rm -fr ${SRC_DIR}/__pycache__

    echo "Source dir contents before moving: ${SRC_DIR}"
    ls -lrt ${SRC_DIR}
    echo "Dest dir contents before moving: ${DST_DIR}"
    ls -lrt ${DST_DIR}
    for j in ${SRC_DIR}/*
    do
	echo $j
	k=`basename $j`
	# At least sometimes (perhaps always?) there is a directory
	# 'p4' or 'google' in both the surce and dest directory.  I
	# think I want to merge their contents.  List them both so I
	# can see in the log what was in both at the time:
        if [ -d ${SRC_DIR}/$k -a -d ${DST_DIR}/$k ]
   	then
	    echo "Both source and dest dir contain a directory: $k"
	    echo "Source dir $k directory contents:"
	    ls -l ${SRC_DIR}/$k
	    echo "Dest dir $k directory contents:"
	    ls -l ${DST_DIR}/$k
            sudo mv ${SRC_DIR}/$k/* ${DST_DIR}/$k/
	    sudo rmdir ${SRC_DIR}/$k
	else
	    echo "Not a conflicting directory: $k"
            sudo mv ${SRC_DIR}/$k ${DST_DIR}/$k
	fi
    done

    echo "Source dir contents after moving: ${SRC_DIR}"
    ls -lrt ${SRC_DIR}
    echo "Dest dir contents after moving: ${DST_DIR}"
    ls -lrt ${DST_DIR}
}

# ---------------------------> Changed for PLEN P4 compression

# SRC - Programmable Low End Networks
BMV2_COMMIT="b447ac4c0cfd83e5e72a3cc6120251c1e91128ab"  # August 10, 2019
PI_COMMIT="41358da0ff32c94fa13179b9cee0ab597c9ccbcc"    # August 10, 2019
P4C_COMMIT="69e132d0d663e3408d740aaf8ed534ecefc88810"   # August 10, 2019
PROTOBUF_COMMIT="v3.2.0"
GRPC_COMMIT="v1.3.2"

# <---------------------------

#Src
# BMV2_COMMIT="f16d0de3486aa7fb2e1fe554aac7d237cc1adc33"      # 2022-May-01
# PI_COMMIT="f547455a260b710706bef82afab4cb9937bac416"        # 2022-May-01
# P4C_COMMIT="1471fdd22b683e1946b7730d83c877d94daba683"       # 2022-May-01
PTF_COMMIT="405513bcad2eae3092b0ac4ceb31e8dec5e32311"       # 2022-May-01
MININET_COMMIT="aa0176fce6fb718a03474f8719261b07b670d30d"  # 2022-Apr-02
# PROTOBUF_COMMIT="v3.6.1"
# GRPC_COMMIT="tags/v1.17.2"


#Get the number of cores to speed up the compilation process
NUM_CORES=`grep -c ^processor /proc/cpuinfo`

sudo apt-get update

KERNEL=$(uname -r)
DEBIAN_FRONTEND=noninteractive sudo apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
sudo apt-get install -y --no-install-recommends --fix-missing\
  autoconf \
  automake \
  bison \
  build-essential \
  ca-certificates \
  clang \
  cmake \
  cpp \
  curl \
  flex \
  g++ \
  git \
  iperf3 \
  iproute2 \
  libboost-dev \
  libboost-filesystem-dev \
  libboost-graph-dev \
  libboost-iostreams-dev \
  libboost-program-options-dev \
  libboost-system-dev \
  libboost-test-dev \
  libboost-thread-dev \
  libelf-dev \
  libevent-dev \
  libffi-dev \
  libfl-dev \
  libgc-dev \
  libgflags-dev \
  libgmp-dev \
  libjudy-dev \
  libpcap-dev \
  libpython3-dev \
  libreadline-dev \
  libssl-dev \
  libtool \
  libtool-bin \
  linux-headers-$KERNEL\
  llvm \
  make \
  net-tools \
  pkg-config \
  python3 \
  python3-dev \
  python3-pip \
  python3-setuptools \
  tcpdump \
  unzip \
  valgrind \
  vim \
  wget \
  xcscope-el \
  xterm

sudo apt-get purge -y python3-protobuf || echo "Failed to remove python3-protobuf, probably because there was no such package installed"
sudo pip3 install protobuf==3.6.1
sudo pip3 install scapy
sudo pip3 install ipaddr
sudo pip3 install pypcap
sudo pip3 install psutil crcmod

# --- Mininet --- #
git clone https://github.com/mininet/mininet mininet
cd mininet
git checkout ${MININET_COMMIT}
patch -p1 < "${HOME}/mininet-dont-install-python2-2022-apr.patch"
cd ..
# TBD: Try without installing openvswitch, i.e. no '-v' option, to see
# if everything still works well without it.
sudo ./mininet/util/install.sh -nw

# --- Protobuf --- #
git clone https://github.com/google/protobuf.git
cd protobuf
git checkout ${PROTOBUF_COMMIT}
./autogen.sh
# install-p4dev-v4.sh script doesn't have --prefix=/usr option here.
./configure --prefix=/usr
make -j${NUM_CORES}
sudo make install
sudo ldconfig
# Force install python module
#cd python
#sudo python3 setup.py install
#cd ../..
cd ..

# --- gRPC --- #
git clone https://github.com/grpc/grpc.git
cd grpc
git checkout ${GRPC_COMMIT}
git submodule update --init --recursive
patch -p1 < "${HOME}/disable-Wno-error-and-other-small-changes.diff" || echo "Errors while attempting to patch grpc, but continuing anyway ..."
make -j${NUM_CORES}
sudo make install
sudo pip3 install coverage>=4.0
sudo pip3 install cython==0.29.34
sudo pip3 install enum34>=1.0.4
sudo pip3 install protobuf>=3.5.0.post1
sudo pip3 install six>=1.10
sudo pip3 install wheel>=0.29
GRPC_PYTHON_BUILD_WITH_CYTHON=1 sudo pip3 install .
sudo ldconfig
cd ..

# --- PI/P4Runtime --- #
git clone https://github.com/p4lang/PI.git
cd PI
git checkout ${PI_COMMIT}
git submodule update --init --recursive
./autogen.sh
# install-p4dev-v4.sh adds more --without-* options to the configure
# script here.  I suppose without those, this script will cause
# building PI code to include more features?
./configure --with-proto
make -j${NUM_CORES}
sudo make install
# install-p4dev-v4.sh at this point does these things, which might be
# useful in this script, too:
# Save about 0.25G of storage by cleaning up PI build
make clean
move_usr_local_lib_python3_from_site_packages_to_dist_packages
sudo ldconfig
cd ..

# --- Bmv2 --- # CHANGED
git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model
git checkout ${BMV2_COMMIT}

# ---------------------> Copy changed file
cp ../p4compression/behavioral-model/targets/simple_switch/primitives.cpp targets/simple_switch/primitives.cpp
# <---------------------

sed -i 's/make\ -j2/make\ -j4/' ci/install-thrift.sh
./install_deps.sh
./autogen.sh
./configure --enable-debugger --with-pi --with-thrift
make -j${NUM_CORES}
sudo make install-strip
sudo ldconfig
cd ..

# --- P4C --- # CHANGED
git clone https://github.com/p4lang/p4c
cd p4c
git checkout ${P4C_COMMIT}

# ---------------------> Copy changed files
cp ../p4compression/frontends/p4/fromv1.0/programStructure.cpp frontends/p4/fromv1.0/programStructure.cpp
cp ../p4compression/frontends/p4/fromv1.0/v1model.h frontends/p4/fromv1.0/v1model.h

cp ../p4compression/p4include/v1model.p4 p4include/v1model.p4

cp ../p4compression/backends/bmv2/simple_switch/simpleSwitch.cpp backends/bmv2/simple_switch/simpleSwitch.cpp
cp ../p4compression/backends/bmv2/simple_switch/simpleSwitch.h backends/bmv2/simple_switch/simpleSwitch.h
# <---------------------

git submodule update --init --recursive
mkdir -p build
cd build
cmake ..
make -j3
sudo make install
sudo ldconfig
move_usr_local_lib_python3_from_site_packages_to_dist_packages
cd ../..

# --- PTF --- #
git clone https://github.com/p4lang/ptf
cd ptf
git checkout ${PTF_COMMIT}
sudo python3 setup.py install
cd ..