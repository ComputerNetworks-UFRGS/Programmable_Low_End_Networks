# Experiments

There are 3 rounds of experiments in this folder, however, we are taking in consideration only the measurements of the "take-3" folder.

That's because in the first round of experiments, we hadn't defined standards of measurements, for exemple, the right size of packets and the places where we would measure de latency (the specific interfaces). In the take 3 directory, there is a description of which interfaces we used to run the pings on. 

On the first round (take-1 folder) we hadn't recompiled the BMV2 without the debugging flags and we were logging every step of the BMV2 for debugging purposes.

On the second round (take-2 folder) we made measurements with different criteria, so they are not standarized.

### Why are we keepping all this records?

Every piece of data we generated is important for camparison reasons. All this information can be analysed and used on the future.


### How the compression works?

We are compressing ICMP packets that only have 0's as the payload, for example:

```
10.30.0.1 > p4pi-middle.inf.ufrgs.br: ICMP echo request, id 8823, seq 1, length 64
	0x0000:  ea89 b7c2 bb35 9a62 7874 fe65 0800 4500
	0x0010:  0054 b13b 4000 3e01 c207 0a1e 0001 8f36
	0x0020:  3011 0800 d587 2277 0001 0000 0000 0000
	0x0030:  0000 0000 0000 0000 0000 0000 0000 0000
	0x0040:  0000 0000 0000 0000 0000 0000 0000 0000
	0x0050:  0000 0000 0000 0000 0000 0000 0000 0000
	0x0060:  0000
```

(default fping packets).
<br/>

After the compression they look like this:

```
21:40:42.653157 00:00:3f:01:cf:b0 (oui Unknown) > 45:00:00:54:e2:92 (oui Unknown), ethertype Unknown (0x8f36), length 41: 
	0x0000:  4500 0054 e292 0000 3f01 cfb0 8f36 3011
	0x0010:  0a1e 0001 aaaa 78da 6360 b8db ae54 cec0
	0x0020:  c840 2600 0079 8f01 ff
```