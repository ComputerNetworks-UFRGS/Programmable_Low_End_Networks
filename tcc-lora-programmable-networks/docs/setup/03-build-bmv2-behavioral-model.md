# 03. Build BMv2 / behavioral-model

This step builds and installs BMv2, including:

- `simple_switch`
- `simple_switch_CLI`
- BMv2 runtime libraries

Dependencies must already be installed through [`01-system-dependencies.md`](01-system-dependencies.md).

## 1. Enter the BMv2 directory

```bash
export P4PI_DIR="$HOME/p4c/Programmable_Low_End_Networks/p4pi"
cd "$P4PI_DIR/behavioral-model"
sudo chown -R "$USER:$USER" .
```

## 2. Fix zlib linking

The P4Pi custom primitives use `deflate` and `inflate`, which come from zlib.

If `simple_switch` is not linked with `-lz`, the build can fail with errors such as:

```text
undefined reference to `deflateInit_'
undefined reference to `deflate'
undefined reference to `deflateEnd'
undefined reference to `inflateInit_'
undefined reference to `inflate'
undefined reference to `inflateEnd'
```

Add `-lz` to `simple_switch_LDADD`:

```bash
cd "$P4PI_DIR/behavioral-model/targets/simple_switch"
sed -i '/^libsimpleswitch_thrift\.la$/i\  -lz \\' Makefile.am
```

Validate the result:

```bash
grep -n "simple_switch_LDADD" -A12 Makefile.am
```

The block should include `-lz` before `libsimpleswitch_thrift.la`.

## 3. Build and install

BMv2 at this version uses Autotools, not CMake.

```bash
cd "$P4PI_DIR/behavioral-model"

./autogen.sh
./configure
make -j"$(nproc)"
sudo make install
sudo ldconfig
```

## 4. Validate BMv2

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

If `simple_switch --help` prints usage information, BMv2 is installed correctly.
