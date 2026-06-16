# 03 - Build BMv2 / behavioral-model

This BMv2 version uses Autotools, not CMake.

## Build

```bash
cd behavioral-model

./install_deps.sh
./autogen.sh
./configure
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## Validate Installation

```bash
which simple_switch
which simple_switch_CLI
simple_switch --help | head -n 5
```

Expected paths:

```text
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
```

## Common Issues

If the build fails with undefined references to `deflate`, `inflate`, or similar zlib symbols, install:

```bash
sudo apt-get install -y zlib1g-dev
```

If configure fails with `cannot find thrift`, install:

```bash
sudo apt-get install -y thrift-compiler libthrift-dev
```
