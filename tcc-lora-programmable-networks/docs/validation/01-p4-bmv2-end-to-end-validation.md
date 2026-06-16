# 01. P4/BMv2 end-to-end validation

This validation checks whether the complete environment is functional:

1. `p4c-bm2-ss` compiles a P4 program.
2. `simple_switch` loads the generated JSON.
3. `simple_switch_CLI` connects to the running switch.
4. Runtime tables can be inspected and configured.

## 1. Validate installed binaries

```bash
which p4c
which p4c-bm2-ss
which simple_switch
which simple_switch_CLI

p4c --version
simple_switch --help | head -n 5
```

Expected paths:

```text
/usr/local/bin/p4c
/usr/local/bin/p4c-bm2-ss
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
```

## 2. Create a minimal P4 program

The following program parses Ethernet and IPv4, then applies an `ipv4_lpm` forwarding table.

```bash
cat > ~/forward.p4 << 'EOF'
#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
}

struct metadata { }

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action forward(bit<9> port) {
        standard_metadata.egress_spec = port;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            forward;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) { apply { } }

control MyVerifyChecksum(inout headers hdr, inout metadata meta) { apply { } }
control MyComputeChecksum(inout headers hdr, inout metadata meta) { apply { } }

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
EOF
```

## 3. Compile the program

```bash
p4c-bm2-ss ~/forward.p4 -o ~/forward.json
ls -l ~/forward.json
```

## 4. Run the switch

```bash
simple_switch ~/forward.json
```

Expected behavior:

```text
Calling target program-options parser
```

The process should keep running. This means the switch loaded the JSON and is waiting for traffic or runtime commands.

To confirm it is alive from another terminal:

```bash
ps aux | grep simple_switch
```

## 5. Connect with the runtime CLI

In another terminal:

```bash
simple_switch_CLI
```

Expected output:

```text
Obtaining JSON from switch...
Done
Control utility for runtime P4 table manipulation
RuntimeCmd:
```

## 6. Inspect and configure the table

Inside `RuntimeCmd:`:

```text
show_tables
table_info ipv4_lpm
table_add ipv4_lpm forward 10.0.0.1/32 => 1
table_dump ipv4_lpm
```

This validates:

- P4 parsing
- match-action pipeline
- runtime control plane through Thrift
- dynamic table entry insertion

## 7. Stop the switch

Return to the terminal running `simple_switch` and press:

```text
Ctrl+C
```
