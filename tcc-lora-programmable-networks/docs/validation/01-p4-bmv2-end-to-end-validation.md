# 01 - P4/BMv2 End-to-End Validation

This document validates whether p4c and BMv2 are installed and able to compile and run a simple P4 program.

## Validate Tools

```bash
which p4c
which p4c-bm2-ss
which simple_switch
which simple_switch_CLI
p4c --version
```

Expected examples:

```text
/usr/local/bin/p4c
/usr/local/bin/p4c-bm2-ss
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
p4c 1.2.3.0
```

## Compile a P4 Program

```bash
p4c-bm2-ss test.p4 -o test.json
```

## Run BMv2

```bash
simple_switch test.json
```

## Connect with CLI

In another terminal:

```bash
simple_switch_CLI
```

Expected behavior:

```text
Obtaining JSON from switch...
Done
RuntimeCmd:
```
