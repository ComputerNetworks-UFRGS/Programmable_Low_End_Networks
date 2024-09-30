#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

struct metadata {}

struct headers {
    ethernet_t ethernet;
}

parser ParserImpl(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition accept;
    }

}

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {}
}

control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action forward(bit<9> port) {
        standard_metadata.egress_spec = port;
    }

    action drop() {
        mark_to_drop( standard_metadata );
        exit;
    }

    action _nop() {}

    action forward_zero() {
	    forward(0);
    }

    table dmac {
        actions = {
            forward;
    	    forward_one;
            drop;
        }
        key = {
            hdr.ethernet.dstAddr: exact;
        }
	
        const entries = {
            0xd4d853f7dbfc: forward(1); // pc-vini
            0x047c16bfb9a1: forward(0); // pc-marcelo (enp4s0) - teste 1
            0xd4d853f632cc: forward(0); // pc-marcelo (wlo1) - teste 2
            0x1cccd67636c0: forward(1); // celular-marcelo (wlan0)
        }

        default_action = forward_zero();
        size = 512;
    }

    apply {
        dmac.apply();
    }

}

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
    }
}

control verifyChecksum(inout headers hdr, inout metadata meta) {
    apply {}
}

control computeChecksum(inout headers hdr, inout metadata meta) {
    apply {}
}

V1Switch(ParserImpl(), verifyChecksum(), ingress(), egress(), computeChecksum(), DeparserImpl()) main;
