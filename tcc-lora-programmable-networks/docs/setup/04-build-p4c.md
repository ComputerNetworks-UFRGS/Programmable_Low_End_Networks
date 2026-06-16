# 04 - Build p4c

## Build

```bash
cd p4c

mkdir -p build
cd build

cmake .. -DENABLE_P4C_GRAPHS=OFF
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## Validate Installation

```bash
which p4c
which p4c-bm2-ss
p4c --version
```

Expected version:

```text
p4c 1.2.3.0
```

## Note

The option below disables the optional graphs backend:

```bash
-DENABLE_P4C_GRAPHS=OFF
```

This avoids compatibility issues observed with some Boost versions.
