    #include <core.p4>
    #include <v1model.p4>

    const bit<9> DROP_PORT = 511; /* Specific to V1 architecture */

    const bit<16> TYPE_IPV4 = 0x800;
    const bit<8> PREAMBLE_TAG = 0xfe;
    const bit<8> PREAMBLE_CPU = 0xfd;

    const bit<48> MAC_BCAST_ADDR = 0xffffffffffff;

    const bit<8> TAG_STATUS_PNDG = 0x00;
    const bit<8> TAG_STATUS_SENT = 0x01;
    const bit<8> TAG_STATUS_RECV = 0x02;
    const bit<8> TAG_STATUS_ACKD = 0x04;
    const bit<8> TAG_STATUS_DROP = 0x05;

    #define PKT_DIR_NULL   0x0
    #define PKT_DIR_TUNN   0x1
    #define PKT_DIR_HOST   0x2


    /*************************************************************************
    *********************** H E A D E R S  ***********************************
    *************************************************************************/

    typedef bit<9>  egressSpec_t;
    typedef bit<48> macAddr_t;
    typedef bit<32> ip4Addr_t;
    typedef bit<8>  tagAddr_t;
    typedef bit<8>  deviceAddr_t;

    typedef bit<8>  devId_t;
    typedef bit<8>  tagId_t;

    //incluso packet_in e packet_out
    #define CPU_PORT 255

    // packet in: 2 bytes
    @controller_header("packet_in")
    header packet_in_header_t {
        bit<16>  ingress_port;
    }

    // packet out: 2 bytes
    @controller_header("packet_out")
    header packet_out_header_t {
        bit<16> egress_port;
    }

    //fim incluso packet_in e packet_out

    // 14 bytes
    header ethernet_t {
        macAddr_t ethdstAddr;
        macAddr_t ethsrcAddr;
        bit<16>   etherType;
    }

    // 4 bytes
    header tag_t {
        bit<8> preamble;
        devId_t dev_id;
        tagId_t tag_id;
        bit<8> proto;
    }

    // 20 bytes
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

    header payload_t {
        varbit<11664>  pktData;
    }

    struct metadata {
        bit<32>    bytes_extracted;
        bit<32>    payload_length;
        bit<2>     packet_direction;
    }

    struct headers {
        packet_out_header_t     packet_out;
        packet_in_header_t      packet_in;
        ethernet_t   ethernet;
        tag_t        tag;
        ipv4_t       ipv4;
        payload_t    payload_in;
        payload_t    payload_out;
    }

    register<tagId_t>(65536) tag_status;

    /*************************************************************************
    *********************** P A R S E R  ***********************************
    *************************************************************************/

    parser MyParser(packet_in packet,
                    out headers hdr,
                    inout metadata meta,
                    inout standard_metadata_t standard_metadata) {

        state start {
            meta.bytes_extracted = 0;
            transition select(standard_metadata.ingress_port){
                CPU_PORT: parse_packet_out;
                default: parse_ethernet_tag;
            }
        }

        state parse_packet_out {
            packet.extract(hdr.packet_out);
            meta.bytes_extracted = meta.bytes_extracted + 2;
            transition parse_ethernet_tag;
        }

        state parse_ethernet_tag {
            transition select(packet.lookahead<bit<8>>()) {
                PREAMBLE_TAG: parse_tag;
                PREAMBLE_CPU: parse_cpu;
                default: parse_ethernet;
            }
        }

        state parse_tag {
            packet.extract(hdr.tag);
            meta.bytes_extracted = meta.bytes_extracted + 4;
            transition parse_payload;
        }

        state parse_cpu {
            packet.extract(hdr.tag);
            meta.bytes_extracted = meta.bytes_extracted + 4;
            transition parse_ethernet;
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
            meta.payload_length = (standard_metadata.packet_length - meta.bytes_extracted) * 8;
            packet.extract(hdr.payload_in, meta.payload_length);
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
        action drop() {
            mark_to_drop(standard_metadata);
        }

        action tag_build(deviceAddr_t dev_id, tagAddr_t tag_id, egressSpec_t port) {
            standard_metadata.egress_spec = port;
            hdr.tag.setValid();
            hdr.tag.preamble = PREAMBLE_TAG;
            hdr.tag.dev_id = dev_id;
            hdr.tag.tag_id = tag_id;
            hdr.tag.proto = hdr.ipv4.protocol;

            // hdr.ethernet.setInvalid();
            // hdr.ipv4.setInvalid();
        }

        action send_to_cpu() {
            standard_metadata.egress_spec = CPU_PORT;
            hdr.packet_in.setValid();
            hdr.packet_in.ingress_port = (bit<16>)standard_metadata.ingress_port;
        }

        action ipv4_build(ip4Addr_t ip_src, ip4Addr_t ip_dst) {
            hdr.ethernet.setValid();
            hdr.ethernet.etherType = TYPE_IPV4;

            hdr.ipv4.setValid();
            hdr.ipv4.version = 4;
            hdr.ipv4.ihl = 5;
            hdr.ipv4.diffserv = 0;
            hdr.ipv4.totalLen = (bit<16>)standard_metadata.packet_length;

            if (hdr.tag.preamble == PREAMBLE_TAG)
                // the packet did not have an eth + ipv4 header. add 20 bytes, and decrement
                // 4 bytes from the tag header
                hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16;
            else
                // the packet already had an eth + ipv4 header along with tag_cpu, so we must
                // decrement those bytes
                hdr.ipv4.totalLen = hdr.ipv4.totalLen - 18;

            hdr.ipv4.identification = 0; // sequential identification numbers
            hdr.ipv4.flags = 0x2; // do not fragment
            hdr.ipv4.fragOffset = 0;
            hdr.ipv4.ttl = 128; // expect worst case for ttl
            hdr.ipv4.protocol = hdr.tag.proto;
            hdr.ipv4.hdrChecksum = 0;
            hdr.ipv4.srcAddr = ip_src;
            hdr.ipv4.dstAddr = ip_dst;
            new_addr(hdr.ipv4.dstAddr, ip_dst);

            // hdr.tag.setInvalid();
        }

        action set_dmac(macAddr_t dst_mac_addr, egressSpec_t sw_port, macAddr_t sw_port_mac) {
            standard_metadata.egress_spec = sw_port;

            hdr.ethernet.ethdstAddr = dst_mac_addr;
            hdr.ethernet.ethsrcAddr = sw_port_mac;
        }

        action set_dmac_bcast() {
            standard_metadata.mcast_grp = 1;

            hdr.ethernet.ethdstAddr = MAC_BCAST_ADDR;
            hdr.ethernet.ethsrcAddr = MAC_BCAST_ADDR;
        }

        table ipv4_lpm {
            key = {
                hdr.ethernet.ethsrcAddr: exact;
                hdr.ipv4.srcAddr: exact;
                hdr.ipv4.dstAddr: exact;
            }
            actions = {
                tag_build;
                send_to_cpu;
                drop;
                NoAction;
            }
            size = 1024;
            default_action = send_to_cpu();
        }

        table dmac {
            key = {
                hdr.ipv4.dstAddr: exact;
            }
            actions = {
                set_dmac;
                set_dmac_bcast;
                drop;
                NoAction;
            }
            size = 1024;
            default_action = set_dmac_bcast();
        }

        table tag_exact {
            key = {
                hdr.tag.dev_id: exact;
                hdr.tag.tag_id: exact;
            }
            actions = {
                ipv4_build;
                drop;
                NoAction;
            }
            size = 1024;
            default_action = drop();
        }

        apply {
            bit<32>    tag_reg;
            bit<8>     status;
            bit<16>    payload_length_bytes = (bit<16>)(meta.payload_length / 8);

            meta.packet_direction = PKT_DIR_NULL;

            if (!hdr.tag.isValid() && hdr.ipv4.isValid()) {
                // we received a packet that only has an eth + ipv4 header
                ipv4_lpm.apply();

                tag_reg = ((bit<32>)hdr.tag.dev_id) << 8 | (bit<32>)hdr.tag.tag_id;

                // the packet may or may not have matched an entry in the ipv4_lpm table.
                // in case it did not match an entry, we need to send it to the controller
                if (standard_metadata.egress_spec == CPU_PORT) {
                    // do nothing. send_to_cpu() already triggered by table miss event

                } else {
                    // it did match a rule in the switch table. now, we need to check
                    // if we are going to send the packet with a tag_def or tag_cpu

                    tag_status.read(status, (bit<32>)tag_reg);
                    if (status == TAG_STATUS_PNDG) {
                        // we did not receive a tag packet before. first packet of the tunnel
                        hdr.tag.preamble = PREAMBLE_CPU;
                        // register that we have sent the first packet of the tunnel

                        status = TAG_STATUS_SENT;
                        tag_status.write(tag_reg, status);
                        
                    } else if (status == TAG_STATUS_SENT) {
                        // we did not receive a tag_def packet yet, so (re)send it. there is
                        // the chance the other end might have missed it
                        hdr.tag.preamble = PREAMBLE_CPU;

                    } else if (status == TAG_STATUS_RECV) {
                        // Recieved at the destination switch, need change do ACK
                        status = TAG_STATUS_ACKD;
                        tag_status.write(tag_reg, status);

                    } else if (status == TAG_STATUS_ACKD) {
                        // we already received a tag_def from the other end. tunnel online
                        hdr.ethernet.setInvalid();
                        hdr.ipv4.setInvalid();
                    }
                    
                    // we are sending the packet to the tunnel
                    meta.packet_direction = PKT_DIR_TUNN;

                }

            } else if (hdr.tag.isValid()) {
                // we received a tag packet, that may or may not have eth + ipv4 headers
                tag_exact.apply();

                tag_reg = ((bit<32>)hdr.tag.dev_id) << 8 | (bit<32>)hdr.tag.tag_id;
                tag_status.read(status, tag_reg);

                // the packet may or may not have matched an entry in the tag_build table.
                // if it did not match an entry, we need either send it to the cpu or discard
                if (standard_metadata.egress_spec == DROP_PORT) {
                    // we had a table miss. send it to the controller, if a tag_cpu not sent yet
                    if (standard_metadata.ingress_port == CPU_PORT) {
                        // this case is particularly strange: we received the packet from the
                        // controller, but it did not match any table. do nothing here.

                    } else if (hdr.tag.preamble == PREAMBLE_CPU) {
                        // this is a tag_cpu packet not yet sent to the controller (hence the
                        // table miss event we had. send it now
                        send_to_cpu();

                    } else {
                        // this is a tag_def packet we don't know about. discard it

                    }

                } else {
                    // we had a table match. now, we need to check if we are receiving the
                    // first packet of the tunnel, or we are receiving a tag_default
                    if (hdr.tag.preamble == PREAMBLE_CPU) {
                        // first packet of the tunnel, mark status "received"
                        status = TAG_STATUS_RECV;
                        tag_status.write(tag_reg, status);

                    } else { // if (hdr.tag.preamble == PREAMBLE_DEF)
                        // not first packet of the tunnel, mark status "received"
                        // if tag_status is TAG_STATUS_RECV, the tag is PREAMBLE_DEF and is not comming from CPU, it is not to this switch, then drop it.

                        if (standard_metadata.ingress_port != CPU_PORT && status == TAG_STATUS_RECV) {
                            // mark the packet to drop
                            status = TAG_STATUS_DROP;
                            tag_status.write(tag_reg, status);

                        } else if (status != TAG_STATUS_DROP) {
                            status = TAG_STATUS_ACKD;
                            tag_status.write(tag_reg, status);

                        }
                    }

                    if (status == TAG_STATUS_DROP) {
                        drop();

                    } else {
                        // set the source and destination mac addresses of the packet
                        dmac.apply();

                        // disable the tag header, so that we can send it to the host
                        hdr.tag.setInvalid();

                        if (standard_metadata.ingress_port == CPU_PORT) {
                            // decrement 2 bytes from pkt_out header
                            hdr.ipv4.totalLen = hdr.ipv4.totalLen - 2;
                        }
                        
                        // we are receiving the packet from the tunnel
                        meta.packet_direction = PKT_DIR_HOST;
                        
                    }
                }
            }
            
            if (meta.packet_direction == PKT_DIR_TUNN) {
                
                // in pktData, in pktDataLen, out defPktData, out defPktDataLen
                hdr.payload_out.pktData = hdr.payload_in.pktData;
                if (payload_length_bytes != 0) {
                    deflate_payload(hdr.payload_in.pktData, payload_length_bytes, hdr.payload_out.pktData, payload_length_bytes);
                    inflate_payload(hdr.payload_out.pktData, payload_length_bytes, hdr.payload_in.pktData, payload_length_bytes);
                }

            } else if (meta.packet_direction == PKT_DIR_HOST) {

                // in defpktData, in defPktDataLen, out pktData, out pktDataLen
                hdr.payload_out.pktData = hdr.payload_in.pktData;
                if (payload_length_bytes != 0) {
                    bit<32>    pkt_payload_len = meta.payload_length;
                    hdr.payload_out.pktData = hdr.payload_in.pktData;
                    inflate_payload(hdr.payload_in.pktData, payload_length_bytes, hdr.payload_out.pktData, payload_length_bytes);
                    hdr.ipv4.totalLen = hdr.ipv4.totalLen - (bit<16>)pkt_payload_len + (bit<16>)meta.payload_length;
                }

            } else {
                
                // we are very likely going to discard the packet

            }
            
            hdr.payload_out.setValid();
        }
    }



    /*************************************************************************
    ****************  E G R E S S   P R O C E S S I N G   *******************
    *************************************************************************/

    control MyEgress(inout headers hdr,
                        inout metadata meta,
                        inout standard_metadata_t standard_metadata) {
        apply {
        }
    }

    /*************************************************************************
    *************   C H E C K S U M    C O M P U T A T I O N   **************
    *************************************************************************/

    control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
        apply {
                update_checksum(
                hdr.ipv4.isValid(),
                {hdr.ipv4.version,
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
            packet.emit(hdr.packet_in);
            packet.emit(hdr.tag);
            packet.emit(hdr.ethernet);
            packet.emit(hdr.ipv4);
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
