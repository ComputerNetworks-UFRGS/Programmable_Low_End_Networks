# 02 - Source Preparation

This document describes the source preparation for the BMv2 and p4c environment.

## BMv2 Repository

```bash
git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model
git checkout f745e1db5e281d1e30483496c3c0960a8d23c852
```

Expected commit:

```text
f745e1d changed VERSION number to 1.15.0 for release (#1092)
```

## p4c Repository

```bash
git clone https://github.com/p4lang/p4c.git
cd p4c
git checkout 1576090b74b610e979a3afeafec79d0a2f81a598
git submodule update --init --recursive
```

Expected version:

```text
p4c 1.2.3.0
```

## Ownership Fix

If the repositories were created by a script executed with `sudo`, fix ownership before building:

```bash
sudo chown -R "$USER:$USER" behavioral-model
sudo chown -R "$USER:$USER" p4c
```
