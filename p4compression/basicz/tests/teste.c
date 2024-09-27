#include <stdio.h>
#include <string.h>

#include "zlib.h"

#define MAX_PAY 2000

int main () {
  char packet_in [] = {};
  int paylen = sizeof (packet_in);

  char packet_out [MAX_PAY], packet_res [MAX_PAY];

  memset (packet_out, 0, sizeof (packet_out));
  memset (packet_res, 0, sizeof (packet_res));

   for (int i = 0; i < sizeof (packet_in); i++) {
      printf ("%02x ", (unsigned char) packet_in[i]);
     }
    printf ("\n");


    z_stream def_stream;
    def_stream.zalloc    = Z_NULL;
    def_stream.zfree     = Z_NULL;
    def_stream.opaque    = Z_NULL;
    def_stream.next_in   = (Bytef*) packet_in;
    def_stream.avail_in  = (uInt) paylen;
    def_stream.next_out  = (Bytef*) packet_out;
    def_stream.avail_out = (uInt) MAX_PAY;

    deflateInit(&def_stream, Z_BEST_COMPRESSION);
    unsigned short def_code = deflate(&def_stream, Z_FINISH);
    deflateEnd(&def_stream);

    printf ("ret: %d, out: %lu\n", def_code, def_stream.total_out);

    for (int i = 0; i < def_stream.total_out; i++) {
      printf ("%02x ", (unsigned char) packet_out[i]);
     }
    printf ("\n");

    z_stream inf_stream;
    inf_stream.zalloc    = Z_NULL;
    inf_stream.zfree     = Z_NULL;
    inf_stream.opaque    = Z_NULL;
    inf_stream.next_in   = (Bytef*) (packet_out);
    inf_stream.avail_in  = (uInt) def_stream.total_out;
    inf_stream.next_out  = (Bytef*) packet_res;
    inf_stream.avail_out = (uInt) MAX_PAY;

    inflateInit(&inf_stream);
    unsigned short inf_code = inflate(&inf_stream, Z_NO_FLUSH);
    inflateEnd(&inf_stream);
 
    printf ("ret: %d, out: %lu\n", inf_code, inf_stream.total_out);

 
   for (int i = 0; i < inf_stream.total_out; i++) {
      printf ("%02x ", (unsigned char) packet_res[i]);
     }
    printf ("\n");

  return 0;
}
