# 02. Source preparation

This step clones the P4Pi project and runs `cpfiles.sh`, which downloads the expected BMv2 and P4C versions and applies the P4Pi changes.

## 1. Clone the P4Pi project

```bash
mkdir -p ~/p4c
cd ~/p4c

git clone https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks.git
cd Programmable_Low_End_Networks/p4pi

export P4PI_DIR="$PWD"
```

If the repository was already cloned, just enter the directory and set the variable:

```bash
cd ~/p4c/Programmable_Low_End_Networks/p4pi
export P4PI_DIR="$PWD"
```

## 2. Prepare `cpfiles.sh`

```bash
cd "$P4PI_DIR"
chmod +x ./compression-files/cpfiles.sh
```

Create the directory expected by the script:

```bash
sudo mkdir -p /usr/share/p4c/p4include
```

Make the script safer to re-run by replacing `mkdir build` with `mkdir -p build`:

```bash
sed -i 's/^mkdir build$/mkdir -p build/' ./compression-files/cpfiles.sh
```

## 3. Run the script

```bash
cd "$P4PI_DIR"
sudo ./compression-files/cpfiles.sh
```

Expected result:

- `behavioral-model/` is created under `$P4PI_DIR`
- `p4c/` is created under `$P4PI_DIR`
- BMv2 is checked out at `f745e1db5e281d1e30483496c3c0960a8d23c852`
- P4C is checked out at `1576090b74b610e979a3afeafec79d0a2f81a598`
- P4Pi custom files are copied into both repositories

## 4. Fix ownership after running with `sudo`

Because `cpfiles.sh` may be executed with `sudo`, the generated folders can be owned by `root`. Fix this before building:

```bash
cd "$P4PI_DIR"
sudo chown -R "$USER:$USER" behavioral-model p4c
```

## 5. Validate source directories

```bash
ls -la "$P4PI_DIR/behavioral-model"
ls -la "$P4PI_DIR/p4c"
```

Also confirm the commits:

```bash
cd "$P4PI_DIR/behavioral-model"
git show -s --oneline

cd "$P4PI_DIR/p4c"
git show -s --oneline
```
