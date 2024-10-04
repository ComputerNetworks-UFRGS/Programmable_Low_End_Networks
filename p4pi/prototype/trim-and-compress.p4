/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x0800;

const bit<16> PREAMBLE_COMPRESSED = 0xaaaa;

const bit<9> DROP_PORT = 511; /* Specific to V1 architecture */


/*************************************************************************
 *********************** H E A D E R S  ***********************************
 *************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header compressed_t {
    bit<16> isCompressed;
}

header payload_t {
    varbit<11664>  pktData;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
    bit<32>    bytes_extracted;
    bit<32>    payload_length_bits;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    compressed_t compressed;
    payload_t    payload_in;
    payload_t    payload_out;    
}

/*************************************************************************
 *********************** P A R S E R  ***********************************
 *************************************************************************/

parser MyParser(packet_in packet,
        out headers hdr,
        inout metadata meta,
        inout standard_metadata_t standard_metadata) {

    state start {
        // looks for ethernet header
        meta.bytes_extracted = 0;
        ethernet_t eth = packet.lookahead<ethernet_t>();

        transition select(eth.etherType) {
            TYPE_IPV4: parse_ethernet;
            default: parse_ipv4;
        }
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        meta.bytes_extracted = meta.bytes_extracted + 14;

        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: parse_payload;        
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        meta.bytes_extracted = meta.bytes_extracted + 20;
        transition parse_payload;
    }


    state parse_payload {
        // we must tell how many bits we are extracting
        transition select(packet.lookahead<bit<16>>()) {
            PREAMBLE_COMPRESSED: parse_payload_compressed;
            default: parse_payload_decompressed;
        }
    }

    state parse_payload_compressed {
	    meta.bytes_extracted = meta.bytes_extracted + 2;
        packet.extract(hdr.compressed); // simply to discard these two-bytes

        transition parse_payload_decompressed;
    }

    state parse_payload_decompressed {
        meta.payload_length_bits = (standard_metadata.packet_length - meta.bytes_extracted) * 8;
        packet.extract(hdr.payload_in, meta.payload_length_bits);
        transition accept;
    }

}

/*************************************************************************
 ************   C H E C K S U M    V E R I F I C A T I O N   *************
 *************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

control MyIngress(inout headers hdr,
        inout metadata meta,
        inout standard_metadata_t standard_metadata) {

    bit<16> payload_len_out_bytes = 0;  
    bit<16> payload_len_in_bytes = 0;
    bit<32> pkt_payload_len = 0;    

    action drop() {
        mark_to_drop(standard_metadata);
    }

    // ---------------------------------------------------
    // -------------- ETH REMOVE ACTIONS -----------------
    // ---------------------------------------------------

    action eth_build(macAddr_t dstAddr, macAddr_t srcAddr, egressSpec_t port){
        hdr.ethernet.setValid();
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = srcAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ethernet.etherType = TYPE_IPV4;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;

    }

    action eth_destroy(egressSpec_t port){
        hdr.ethernet.setInvalid();
        standard_metadata.egress_spec = port;
    }

    /* ---------------------------------------------------
       ------------------ GZIP ACTIONS -------------------
       --------------------------------------------------- */

    action gzip_deflate () {
	payload_len_out_bytes = 0;
        payload_len_in_bytes = (bit<16>)(meta.payload_length_bits / 8);
        pkt_payload_len = meta.payload_length_bits;

        hdr.payload_out.setValid();
        
        hdr.payload_out.pktData = hdr.payload_in.pktData; // why is it doing this attribution?
        deflate_payload(hdr.payload_in.pktData, payload_len_in_bytes, hdr.payload_out.pktData, payload_len_out_bytes);
	    // ???
        hdr.ipv4.totalLen = hdr.ipv4.totalLen - (bit<16>)pkt_payload_len + (bit<16>)meta.payload_length_bits;

        hdr.compressed.setValid();
        hdr.compressed.isCompressed = PREAMBLE_COMPRESSED;
        
    }
 
    action gzip_inflate () {
 	payload_len_out_bytes = 0;
        payload_len_in_bytes = (bit<16>)(meta.payload_length_bits / 8);
        pkt_payload_len = meta.payload_length_bits;

        hdr.payload_out.setValid();
        
        inflate_payload(hdr.payload_in.pktData, payload_len_in_bytes, hdr.payload_out.pktData, payload_len_out_bytes);
        
	    hdr.ipv4.totalLen = hdr.ipv4.totalLen - (bit<16>)pkt_payload_len + (bit<16>)meta.payload_length_bits;
        hdr.compressed.setInvalid();
	    hdr.payload_in.setInvalid();   	
    }

    table eth_forward {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            eth_build;
            eth_destroy;
            drop;
            NoAction;
        }
        // fix entries in each switch
        // s1: 
        //  dst: "9a:62:78:74:fe:65"
        //  src: "ea:89:b7:c2:bb:35"
	
	const entries = {
    		0: eth_destroy(1); // to lorasend
    	    	1: drop();
    	    	2: eth_build(0xea89b7c2bb35, 0x9a627874fe65, 0); // to lorarecv
    	}
 
        default_action = drop();

    }

    table gzip {
        key = {
            standard_metadata.egress_spec: exact;
        }
        actions = {
            gzip_deflate;
            gzip_inflate;
            drop;
            NoAction;
        }

        // constant entries for inflate and deflate functions
        const entries = {
            0: gzip_inflate();
            1: gzip_deflate();
        }

        default_action = NoAction();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            eth_forward.apply();

            // if egress == 2, then compress
            // if egress == 1 and is compressed, then decompress
            if (standard_metadata.egress_spec == 1 || (standard_metadata.egress_spec == 0 && hdr.compressed.isValid())) {
                gzip.apply();
            }
        
            // if the compression made the payload bigger, emit only payload_in
            if (hdr.compressed.isValid() && standard_metadata.egress_spec == 1) {
                if (payload_len_out_bytes > (bit<16>)(meta.payload_length_bits / 8)) {
                    hdr.compressed.setInvalid();
                    hdr.payload_out.setInvalid();
                } else {
                    hdr.payload_in.setInvalid();
                }
            }
        }
    }
}

/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

control MyEgress(inout headers hdr,
        inout metadata meta,
        inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
 *************   C H E C K S U M    C O M P U T A T I O N   **************
 *************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply {
        update_checksum(
                hdr.ipv4.isValid(),
                { hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.totalLen,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr },
                hdr.ipv4.hdrChecksum,
                HashAlgorithm.csum16);
    }
}

/*************************************************************************
 ***********************  D E P A R S E R  *******************************
 *************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.compressed);
        packet.emit(hdr.payload_in);
        packet.emit(hdr.payload_out);
    }
}

/*************************************************************************
 ***********************  S W I T C H  *******************************
 *************************************************************************/

    V1Switch(
            MyParser(),
            MyVerifyChecksum(),
            MyIngress(),
            MyEgress(),
            MyComputeChecksum(),
            MyDeparser()
            ) main;
