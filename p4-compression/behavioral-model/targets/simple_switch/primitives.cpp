/* Copyright 2013-present Barefoot Networks, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * Antonin Bas (antonin@barefootnetworks.com)
 *
 */

#include <bm/bm_sim/actions.h>
#include <bm/bm_sim/calculations.h>
#include <bm/bm_sim/core/primitives.h>
#include <bm/bm_sim/counters.h>
#include <bm/bm_sim/meters.h>
#include <bm/bm_sim/packet.h>
#include <bm/bm_sim/phv.h>
#include <bm/bm_sim/logger.h>

#include <random>
#include <thread>
#include <iostream>

#include "simple_switch.h"
#include "register_access.h"

// CHANGED
#include "zlib.h"
#define MAX_PAY 1458

template <typename... Args>
using ActionPrimitive = bm::ActionPrimitive<Args...>;

using bm::Data;
using bm::Field;
using bm::Header;
using bm::MeterArray;
using bm::CounterArray;
using bm::RegisterArray;
using bm::NamedCalculation;
using bm::HeaderStack;
using bm::Logger;

namespace {
SimpleSwitch *simple_switch;
}  // namespace

class modify_field : public ActionPrimitive<Data &, const Data &> {
  void operator ()(Data &dst, const Data &src) {
    bm::core::assign()(dst, src);
  }
};

REGISTER_PRIMITIVE(modify_field);

// CHANGED
class new_addr : public ActionPrimitive<Data &, const Data &> {
  void operator ()(Data &dest, const Data &anything) {
    printf("\n\n\n\n\nCHANGED\n\n\n\n\n");
  }
};
REGISTER_PRIMITIVE(new_addr);

class p4_logger : public ActionPrimitive<const Data &> {
  void operator ()(const Data &operand) {
    std::cout << "P4_LOGGER: " << operand.get_string() << std::endl;
  }
};
REGISTER_PRIMITIVE(p4_logger);

class deflate_payload : public ActionPrimitive<Field &, const Data &, Field &, Data &> {
  void operator ()(Field &payload_in, const Data &payload_in_len, Field &payload_out, Data &payload_out_len) {

    std::cout << "\n **** DEFLATE - 25-09 16:42 ****\n";
    std::cout << "Payload in len: " << payload_in_len.get_int() << "\n";
    std::string payload = payload_in.get_string();

    // in case the packet starts with 0's, fills the beginning of the packet to
    // fix the removal of them after the convertion to arith. IMPORTANT!!
    std::string preamble(payload_in_len.get_int() - payload.length(), (char) NULL);
    payload = preamble + payload;

    int payload_len = payload.length();

    std::cout << "Payload in str:" << std::endl;
    for (int i = 0; i < payload_len; i++) {
      printf ("%02x ", (unsigned char) payload[i]);
    }
    std::cout << std::endl;

    char payload_in_bytes[payload_len];
    for (int i = 0; i < payload_len; i++) {
      payload_in_bytes[i] = payload[i];
    }

    char payload_out_bytes[MAX_PAY];

    z_stream def_stream;
    def_stream.zalloc    = Z_NULL;
    def_stream.zfree     = Z_NULL;
    def_stream.opaque    = Z_NULL;
    def_stream.next_in   = (Bytef*) payload_in_bytes;
    def_stream.avail_in  = (uInt) payload_len;
    def_stream.next_out  = (Bytef*) payload_out_bytes;
    def_stream.avail_out = (uInt) MAX_PAY;

    deflateInit(&def_stream, Z_BEST_COMPRESSION);
    unsigned short def_code = deflate(&def_stream, Z_FINISH);
    deflateEnd(&def_stream);

    std::cout << "zlib: return_code: " << def_code << "\n";
    std::cout << "zlib: total_out: " << def_stream.total_out << "\n";

    std::cout << "\nCompressed payload\n";
    for (int i=0; i < (int) def_stream.total_out; i++){
      printf("%02x ", (unsigned char) payload_out_bytes[i]);
    }
    std::cout << "\n";

    payload_out.resize_field(def_stream.total_out);
    payload_out.set_bytes(payload_out_bytes, def_stream.total_out);
    payload_out_len.set(def_stream.total_out);

    std::cout << "\nPayload out len: " << payload_out.get_string().length() << "\n";

    payload = payload_out.get_string();
    payload_len = payload_out.get_string().length();

    std::cout << "Payload out str:" << std::endl;
    for (int i = 0; i < payload_len; i++) {
      printf ("%02x ", (unsigned char) payload[i]);
    }
    std::cout << std::endl;
  }
};
REGISTER_PRIMITIVE(deflate_payload);

class inflate_payload : public ActionPrimitive<const Field &, const Data &, Field &, Data &> {
  void operator ()(const Field &payload_in, const Data &payload_in_len, Field &payload_out, Data &payload_out_len) {
    
    std::cout << "\n **** INFLATE - 24-09 15:15 ****\n";

    std::cout << "Payload in len: " << payload_in_len.get_int() << "\n";

    std::string payload = payload_in.get_string();
    int payload_len = payload_in.get_string().length();
    std::cout << "Payload in str:" << std::endl;
    for (int i = 0; i < payload_len; i++) {
      printf ("%02x ", (unsigned char) payload[i]);
    }
    std::cout << std::endl;

    int paylen = payload_in.get_string().length();
    std::string payload_in_copy = payload_in.get_string();
    char payload_in_bytes[paylen];
    for (int i = 0; i < paylen; i++) {
      payload_in_bytes[i] = payload_in_copy[i];
    }

    char payload_out_bytes[MAX_PAY];

    z_stream inf_stream;
    inf_stream.zalloc    = Z_NULL;
    inf_stream.zfree     = Z_NULL;
    inf_stream.opaque    = Z_NULL;
    inf_stream.next_in   = (Bytef*) payload_in_bytes;
    inf_stream.avail_in  = (uInt) paylen;
    inf_stream.next_out  = (Bytef*) payload_out_bytes;
    inf_stream.avail_out = (uInt) MAX_PAY;

    inflateInit(&inf_stream);
    unsigned short inf_code = inflate(&inf_stream, Z_NO_FLUSH);
    inflateEnd(&inf_stream);

    std::cout << "zlib: return_code: " << inf_code << "\n";
    std::cout << "zlib: total_out: " << inf_stream.total_out << "\n";
     
    // resizes the field (changes the nbits and nbytes of the field and then updates the data);
    std::cout << "Resizing out field" << "\n";
    payload_out.resize_field(inf_stream.total_out); 
    payload_out.set_bytes(payload_out_bytes, inf_stream.total_out);
    payload_out_len.set(inf_stream.total_out);

    std::cout << "\nPayload out len: " << payload_out.get_string().length() << "\n";

    payload = payload_out.get_string();
    payload_len = payload_out.get_string().length();
    std::cout << "Payload out str:" << std::endl;
    for (int i = 0; i < payload_len; i++) {
      printf ("%02x ", (unsigned char) payload[i]);
    }
    std::cout << std::endl;
  }
};
REGISTER_PRIMITIVE(inflate_payload);

class modify_field_rng_uniform
  : public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &b, const Data &e) {
    // TODO(antonin): a little hacky, fix later if there is a need using GMP
    // random fns
    using engine = std::default_random_engine;
    using hash = std::hash<std::thread::id>;
    static thread_local engine generator(hash()(std::this_thread::get_id()));
    using distrib64 = std::uniform_int_distribution<uint64_t>;
    auto lo = b.get_uint64();
    auto hi = e.get_uint64();
    if (lo > hi) {
        Logger::get()->warn("random result is not specified when lo > hi");
        // Return without writing to the result field at all.  We
        // should avoid the distrib64 call below, since its behavior
        // is not defined in this case.
        return;
    }
    distrib64 distribution(lo, hi);
    auto rand_val = distribution(generator);
    BMLOG_TRACE_PKT(get_packet(),
                    "random(lo={}, hi={}) = {}",
                    lo, hi, rand_val);
    f.set(rand_val);
  }
};

REGISTER_PRIMITIVE(modify_field_rng_uniform);

class add_to_field : public ActionPrimitive<Field &, const Data &> {
  void operator ()(Field &f, const Data &d) {
    f.add(f, d);
  }
};

REGISTER_PRIMITIVE(add_to_field);

class subtract_from_field : public ActionPrimitive<Field &, const Data &> {
  void operator ()(Field &f, const Data &d) {
    f.sub(f, d);
  }
};

REGISTER_PRIMITIVE(subtract_from_field);

class add : public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.add(d1, d2);
  }
};

REGISTER_PRIMITIVE(add);

class subtract : public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.sub(d1, d2);
  }
};

REGISTER_PRIMITIVE(subtract);

class bit_xor : public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.bit_xor(d1, d2);
  }
};

REGISTER_PRIMITIVE(bit_xor);

class bit_or : public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.bit_or(d1, d2);
  }
};

REGISTER_PRIMITIVE(bit_or);

class bit_and : public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.bit_and(d1, d2);
  }
};

REGISTER_PRIMITIVE(bit_and);

class shift_left :
  public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.shift_left(d1, d2);
  }
};

REGISTER_PRIMITIVE(shift_left);

class shift_right :
  public ActionPrimitive<Data &, const Data &, const Data &> {
  void operator ()(Data &f, const Data &d1, const Data &d2) {
    f.shift_right(d1, d2);
  }
};

REGISTER_PRIMITIVE(shift_right);

class drop : public ActionPrimitive<> {
  void operator ()() {
    get_field("standard_metadata.egress_spec").set(
        simple_switch->get_drop_port());
    if (get_phv().has_field("intrinsic_metadata.mcast_grp")) {
      get_field("intrinsic_metadata.mcast_grp").set(0);
    }
  }
};

REGISTER_PRIMITIVE(drop);

class mark_to_drop : public ActionPrimitive<Header &> {
  void operator ()(Header &std_hdr) {
    if (egress_spec_offset == -1) {
      const auto &header_type = std_hdr.get_header_type();
      egress_spec_offset = header_type.get_field_offset("egress_spec");
      if (egress_spec_offset == -1) {
        Logger::get()->critical(
            "Header {} must be of type standard_metadata but it does not have "
            "an 'egress_spec' field",
            std_hdr.get_name());
        return;
      }

      mcast_grp_offset = header_type.get_field_offset("mcast_grp");
    }
    std_hdr.get_field(egress_spec_offset).set(
        simple_switch->get_drop_port());

    // This assumes that the P4 program is compiled with p4c and that the
    // "mcast_grp" field is defined in the same standard metadata header as
    // "egress_spec" in v1model.p4. That's a reasonnable assumption since
    // mark_to_drop is a recent primitive and was added specifically for
    // p4c. Even if the field is aliased as "intrinsic_metadata.mcast_grp" and
    // that alias is used in other parts of simple_switch, everything should
    // work fine. We could even consider erroring out if "mcast_grp" is not
    // found like we do for "egress_spec".
    if (mcast_grp_offset != -1) std_hdr.get_field(mcast_grp_offset).set(0);
  }

  // bmv2 creates a new instance of mark_to_drop every time the primitive is
  // called in the JSON, so it is safe to use data members for this. For a
  // given P4 program, the offsets should be the same for all instances of
  // mark_to_drop assuming p4c generates a correct JSON. When loading a new P4
  // program, the offsets *may* be different (but that's unlikely).
  int egress_spec_offset{-1};
  int mcast_grp_offset{-1};
};

REGISTER_PRIMITIVE(mark_to_drop);

class generate_digest : public ActionPrimitive<const Data &, const Data &> {
  void operator ()(const Data &receiver, const Data &learn_id) {
    // discared receiver for now
    (void) receiver;
    auto &packet = get_packet();
    RegisterAccess::set_lf_field_list(&packet, learn_id.get<uint16_t>());
  }
};

REGISTER_PRIMITIVE(generate_digest);

class add_header : public ActionPrimitive<Header &> {
  void operator ()(Header &hdr) {
    // TODO(antonin): reset header to 0?
    if (!hdr.is_valid()) {
      hdr.reset();
      hdr.mark_valid();
      // updated the length packet register (register 0)
      auto &packet = get_packet();
      packet.set_register(RegisterAccess::PACKET_LENGTH_REG_IDX,
          packet.get_register(RegisterAccess::PACKET_LENGTH_REG_IDX) +
          hdr.get_nbytes_packet());
    }
  }
};

REGISTER_PRIMITIVE(add_header);

class add_header_fast : public ActionPrimitive<Header &> {
  void operator ()(Header &hdr) {
    hdr.mark_valid();
  }
};

REGISTER_PRIMITIVE(add_header_fast);

class remove_header : public ActionPrimitive<Header &> {
  void operator ()(Header &hdr) {
    if (hdr.is_valid()) {
      // updated the length packet register (register 0)
      auto &packet = get_packet();
      packet.set_register(RegisterAccess::PACKET_LENGTH_REG_IDX,
          packet.get_register(RegisterAccess::PACKET_LENGTH_REG_IDX) -
          hdr.get_nbytes_packet());
      hdr.mark_invalid();
    }
  }
};

REGISTER_PRIMITIVE(remove_header);

class copy_header : public ActionPrimitive<Header &, const Header &> {
  void operator ()(Header &dst, const Header &src) {
    bm::core::assign_header()(dst, src);
  }
};

REGISTER_PRIMITIVE(copy_header);

class clone_ingress_pkt_to_egress
  : public ActionPrimitive<const Data &, const Data &> {
  void operator ()(const Data &mirror_session_id, const Data &field_list_id) {
    auto &packet = get_packet();
    // We limit mirror_session_id values to small enough values that
    // we can use one of the bit positions as a "clone was performed"
    // indicator, making mirror_seesion_id stored here always non-0 if
    // a clone was done.  This enables cleanly supporting
    // mirror_session_id == 0, in case that is ever helpful.
    RegisterAccess::set_clone_mirror_session_id(&packet,
        mirror_session_id.get<uint16_t>() |
        RegisterAccess::MIRROR_SESSION_ID_VALID_MASK);
    RegisterAccess::set_clone_field_list(&packet,
        field_list_id.get<uint16_t>());
  }
};

REGISTER_PRIMITIVE(clone_ingress_pkt_to_egress);

class clone_egress_pkt_to_egress
  : public ActionPrimitive<const Data &, const Data &> {
  void operator ()(const Data &mirror_session_id, const Data &field_list_id) {
    auto &packet = get_packet();
    // See clone_ingress_pkt_to_egress for why the arithmetic.
    RegisterAccess::set_clone_mirror_session_id(&packet,
        mirror_session_id.get<uint16_t>() |
        RegisterAccess::MIRROR_SESSION_ID_VALID_MASK);
    RegisterAccess::set_clone_field_list(&packet,
        field_list_id.get<uint16_t>());
  }
};

REGISTER_PRIMITIVE(clone_egress_pkt_to_egress);

class resubmit : public ActionPrimitive<const Data &> {
  void operator ()(const Data &field_list_id) {
    auto &packet = get_packet();
    RegisterAccess::set_resubmit_flag(&packet, field_list_id.get<uint16_t>());
  }
};

REGISTER_PRIMITIVE(resubmit);

class recirculate : public ActionPrimitive<const Data &> {
  void operator ()(const Data &field_list_id) {
    auto &packet = get_packet();
    RegisterAccess::set_recirculate_flag(&packet,
                                         field_list_id.get<uint16_t>());
  }
};

REGISTER_PRIMITIVE(recirculate);

class modify_field_with_hash_based_offset
  : public ActionPrimitive<Data &, const Data &,
                           const NamedCalculation &, const Data &> {
  void operator ()(Data &dst, const Data &base,
                   const NamedCalculation &hash, const Data &size) {
    auto b = base.get<uint64_t>();
    auto orig_sz = size.get<uint64_t>();
    auto sz = orig_sz;
    if (sz == 0) {
        sz = 1;
        Logger::get()->warn("hash max given as 0, but treating it as 1");
    }
    auto v = (hash.output(get_packet()) % sz) + b;
    BMLOG_TRACE_PKT(get_packet(),
                    "hash(base={}, max={}) = {}",
                    b, orig_sz, v);
    dst.set(v);
  }
};

REGISTER_PRIMITIVE(modify_field_with_hash_based_offset);

class no_op : public ActionPrimitive<> {
  void operator ()() {
    // nothing
  }
};

REGISTER_PRIMITIVE(no_op);

class execute_meter
  : public ActionPrimitive<MeterArray &, const Data &, Field &> {
  void operator ()(MeterArray &meter_array, const Data &idx, Field &dst) {
    auto i = idx.get_uint();
#ifndef NDEBUG
    if (i >= meter_array.size()) {
        BMLOG_ERROR_PKT(get_packet(),
                        "Attempted to update meter '{}' with size {}"
                        " at out-of-bounds index {}."
                        "  No meters were updated, and neither was"
                        " dest field.",
                        meter_array.get_name(), meter_array.size(), i);
        return;
    }
#endif  // NDEBUG
    auto color = meter_array.execute_meter(get_packet(), i);
    dst.set(color);
    BMLOG_TRACE_PKT(get_packet(),
                    "Updated meter '{}' at index {},"
                    " assigning dest field the color result {}",
                    meter_array.get_name(), i, color);
  }
};

REGISTER_PRIMITIVE(execute_meter);

class count : public ActionPrimitive<CounterArray &, const Data &> {
  void operator ()(CounterArray &counter_array, const Data &idx) {
    auto i = idx.get_uint();
#ifndef NDEBUG
    if (i >= counter_array.size()) {
        BMLOG_ERROR_PKT(get_packet(),
                        "Attempted to update counter '{}' with size {}"
                        " at out-of-bounds index {}."
                        "  No counters were updated.",
                        counter_array.get_name(), counter_array.size(), i);
        return;
    }
#endif  // NDEBUG
    counter_array.get_counter(i).increment_counter(get_packet());
    BMLOG_TRACE_PKT(get_packet(),
                    "Updated counter '{}' at index {}",
                    counter_array.get_name(), i);
  }
};

REGISTER_PRIMITIVE(count);

class register_read
  : public ActionPrimitive<Field &, const RegisterArray &, const Data &> {
  void operator ()(Field &dst, const RegisterArray &src, const Data &idx) {
    auto i = idx.get_uint();
#ifndef NDEBUG
    if (i >= src.size()) {
        BMLOG_ERROR_PKT(get_packet(),
                        "Attempted to read register '{}' with size {}"
                        " at out-of-bounds index {}."
                        "  Dest field was not updated.",
                        src.get_name(), src.size(), i);
        return;
    }
#endif  // NDEBUG
    dst.set(src[i]);
    BMLOG_TRACE_PKT(get_packet(),
                    "Read register '{}' at index {} read value {}",
                    src.get_name(), i, src[i]);
  }
};

REGISTER_PRIMITIVE(register_read);

class register_write
  : public ActionPrimitive<RegisterArray &, const Data &, const Data &> {
  void operator ()(RegisterArray &dst, const Data &idx, const Data &src) {
    auto i = idx.get_uint();
#ifndef NDEBUG
    if (i >= dst.size()) {
        BMLOG_ERROR_PKT(get_packet(),
                        "Attempted to write register '{}' with size {}"
                        " at out-of-bounds index {}."
                        "  No register array elements were updated.",
                        dst.get_name(), dst.size(), i);
        return;
    }
#endif  // NDEBUG
    dst[i].set(src);
    BMLOG_TRACE_PKT(get_packet(),
                    "Wrote register '{}' at index {} with value {}",
                    dst.get_name(), i, dst[i]);
  }
};

REGISTER_PRIMITIVE(register_write);

// I cannot name this "truncate" and register it with the usual
// REGISTER_PRIMITIVE macro, because of a name conflict:
//
// In file included from /usr/include/boost/config/stdlib/libstdcpp3.hpp:77:0,
//   from /usr/include/boost/config.hpp:44,
//   from /usr/include/boost/cstdint.hpp:36,
//   from /usr/include/boost/multiprecision/number.hpp:9,
//   from /usr/include/boost/multiprecision/gmp.hpp:9,
//   from ../../src/bm_sim/include/bm_sim/bignum.h:25,
//   from ../../src/bm_sim/include/bm_sim/data.h:32,
//   from ../../src/bm_sim/include/bm_sim/fields.h:28,
//   from ../../src/bm_sim/include/bm_sim/phv.h:34,
//   from ../../src/bm_sim/include/bm_sim/actions.h:34,
//   from primitives.cpp:21:
//     /usr/include/unistd.h:993:12: note: declared here
//     extern int truncate (const char *__file, __off_t __length)
class truncate_ : public ActionPrimitive<const Data &> {
  void operator ()(const Data &truncated_length) {
    get_packet().truncate(truncated_length.get<size_t>());
  }
};

REGISTER_PRIMITIVE_W_NAME("truncate", truncate_);

// In addition to setting the simple_switch global variable, this function also
// ensures that this unit is not discarded by the linker. It is being called by
// the constructor of SimpleSwitch.
int import_primitives(SimpleSwitch *sswitch) {
  simple_switch = sswitch;
  return 0;
}
