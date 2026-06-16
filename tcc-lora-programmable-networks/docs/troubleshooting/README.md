# Troubleshooting

This file documents the main errors found during the BMv2/P4C setup and how each one was fixed.

## APT `404 Not Found`

Example:

```text
E: Failed to fetch ... 404 Not Found
```

Fix:

```bash
sudo apt-get clean
sudo apt-get update
sudo apt-get -o Acquire::Retries=3 -o Acquire::http::No-Cache=true update
```

## `destination path already exists`

Example:

```text
fatal: destination path 'p4c' already exists and is not an empty directory.
fatal: destination path 'behavioral-model' already exists and is not an empty directory.
```

Cause: the repository was already cloned.

This is usually safe if the script continues and performs the checkout.

## `mkdir: cannot create directory 'build': File exists`

Cause: the script uses `mkdir build`.

Fix:

```bash
sed -i 's/^mkdir build$/mkdir -p build/' ./compression-files/cpfiles.sh
```

Or remove old build directories:

```bash
rm -rf behavioral-model/build p4c/build build
```

## `Permission denied` when creating `build`

Cause: files were created as `root` after running scripts with `sudo`.

Fix:

```bash
cd "$P4PI_DIR"
sudo chown -R "$USER:$USER" behavioral-model p4c
```

## `CMakeLists.txt` not found in BMv2

Cause: this BMv2 version uses Autotools, not CMake.

Correct build flow:

```bash
./autogen.sh
./configure
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## `cannot find thrift`

Cause: `thrift-compiler` is missing or not in `PATH`.

Fix:

```bash
sudo apt-get install -y thrift-compiler libthrift-dev
thrift --version
```

## Python `externally-managed-environment`

Cause: Ubuntu blocks system-wide `pip` installation through PEP 668.

For this setup, the warning can usually be ignored if BMv2 builds and installs successfully.

If a Python package is strictly required, use a virtual environment or pass `--break-system-packages` only if acceptable for the machine.

## zlib linking failure in BMv2

Example:

```text
undefined reference to `deflateInit_'
undefined reference to `inflateInit_'
```

Fix:

```bash
sudo apt-get install -y zlib1g-dev
cd "$P4PI_DIR/behavioral-model/targets/simple_switch"
sed -i '/^libsimpleswitch_thrift\.la$/i\  -lz \\' Makefile.am
```

Then rebuild BMv2.

## Protobuf not found by P4C

Example:

```text
Could NOT find Protobuf
```

Fix:

```bash
sudo apt-get install -y protobuf-compiler libprotobuf-dev
protoc --version
```

## Boost iostreams not found by P4C

Example:

```text
Could not find a package configuration file provided by "boost_iostreams"
```

Fix:

```bash
sudo apt-get install -y libboost-iostreams-dev libboost-graph-dev
```

## LibGc not found by P4C

Example:

```text
Could NOT find LibGc (missing: LIBGCCPP_LIBRARY LIBGC_LIBRARY LIBGC_INCLUDE_DIR)
```

Fix:

```bash
sudo apt-get install -y libgc-dev
```

If CMake still cannot find it:

```bash
cmake .. \
  -DENABLE_P4C_GRAPHS=OFF \
  -DLIBGC_INCLUDE_DIR=/usr/include \
  -DLIBGC_LIBRARY=/usr/lib/aarch64-linux-gnu/libgc.so \
  -DLIBGCCPP_LIBRARY=/usr/lib/aarch64-linux-gnu/libgccpp.so
```

## Graphs backend failure with Boost 1.83

Example:

```text
error: there are no arguments to ‘bad_archive_exception’
```

Fix: disable the graphs backend.

```bash
cmake .. -DENABLE_P4C_GRAPHS=OFF
```

This backend is not required for BMv2 usage.
