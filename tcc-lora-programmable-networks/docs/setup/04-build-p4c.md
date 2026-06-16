# 04. Build P4C

This step builds and installs `p4c`, including the BMv2 backend:

- `p4c`
- `p4c-bm2-ss`
- `p4c-bm2-psa`

Dependencies must already be installed through [`01-system-dependencies.md`](01-system-dependencies.md).

## 1. Enter the P4C directory

```bash
export P4PI_DIR="$HOME/p4c/Programmable_Low_End_Networks/p4pi"
cd "$P4PI_DIR/p4c"
sudo chown -R "$USER:$USER" .
```

## 2. Validate Protobuf

```bash
protoc --version
```

Example:

```text
libprotoc 3.21.12
```

## 3. Configure the build

Disable the `graphs` backend because it can fail with newer Boost versions and is not required for BMv2 usage.

```bash
cd "$P4PI_DIR/p4c"
rm -rf build
mkdir -p build
cd build

cmake .. -DENABLE_P4C_GRAPHS=OFF
```

Successful configuration ends with:

```text
Configuring done
Generating done
Build files have been written to: .../p4c/build
```

## 4. If CMake cannot find LibGc

If this error appears:

```text
Could NOT find LibGc (missing: LIBGCCPP_LIBRARY LIBGC_LIBRARY LIBGC_INCLUDE_DIR)
```

Confirm the installed files:

```bash
dpkg -L libgc-dev | grep -E 'gc\.h|libgc\.so|libgccpp\.so|gc_cpp\.h'
find /usr -name 'libgc.so*' -o -name 'libgccpp.so*' -o -name 'gc_cpp.h'
```

If needed, configure with explicit paths:

```bash
cmake .. \
  -DENABLE_P4C_GRAPHS=OFF \
  -DLIBGC_INCLUDE_DIR=/usr/include \
  -DLIBGC_LIBRARY=/usr/lib/aarch64-linux-gnu/libgc.so \
  -DLIBGCCPP_LIBRARY=/usr/lib/aarch64-linux-gnu/libgccpp.so
```

## 5. Build and install

```bash
cd "$P4PI_DIR/p4c/build"
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## 6. Validate P4C

```bash
which p4c
which p4c-bm2-ss
p4c --version
```

Expected examples:

```text
/usr/local/bin/p4c
/usr/local/bin/p4c-bm2-ss
p4c 1.2.3.0 (SHA: 1576090b7 BUILD: RELEASE)
```
