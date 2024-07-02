# Stop-and-wait ARQ

The transmitter sends one data frame at a time. After transmitting a frame, the transmitter does not send any further data until it has received an ACK from the receiver. The receiver sends an ACK only after a correct receiving a correct frame. If the sender does not receive an ACK before the expiry of a predefined timeout period, it re transmits the frame previously sent.

ARQ is simple, but not very effective. Assuming that the data exchange goes perfectly (no lost packets or ACKs), the delay between each packet is twice the transmission delay.

In this case, the sender does not receive the acknowledgement, the maximum timeout is exceeded and the frame is re transmitted. The recipient therefore receives two copies of the same frame, and if the frames are not numbered, he has no way of knowing whether the second frame received is a copy of the first or the next frame (which may contain the same data).

![image_1.png](https://github.com/ComputerNetworks-UFRGS/Programmable_Low_End_Networks/blob/main/Documentation/assets/image_1.png)

---

# Using Selective Repeat ARQ

Selective Repeat ARQ is based on Stoped-and-wait ARQ

We have a sender side and a receiver side, a sequence of numbers and a window size.

Here, for example, we have a sequence of numbers, here 8, with a window size of 4.

![Untitled](Stop-and-wait%20ARQ%20a6eb25b76ced4ebbab0e33c4cd906c5b/Untitled%201.png)

![Untitled](Stop-and-wait%20ARQ%20a6eb25b76ced4ebbab0e33c4cd906c5b/Untitled%202.png)

This means that the sender can send 4 packets without waiting for a response from the receiver; once the receiver sends an ACK, the window shifts and the sender can send an additional packet. 

![Untitled](Stop-and-wait%20ARQ%20a6eb25b76ced4ebbab0e33c4cd906c5b/Untitled%203.png)

For example, if packet 2's ACK can't be forwarded, usually not all subsequent packets are re transmitted, and subsequent ACKs are cancelled until the packet is re transmitted. In this case, following the ACK of packet 3, all subsequent packets are re transmitted, and the packet of packet 2 can be retransmitted.

![Untitled](Stop-and-wait%20ARQ%20a6eb25b76ced4ebbab0e33c4cd906c5b/Untitled%204.png)

---

# Use of tokens for alternating emission

Each Raspberry Pi must manage a token that indicates when it can send packets. For example, one Raspberry Pi starts with the token and, after sending a certain number of packets, transfers the token to the other Raspberry Pi. This can be managed by a simple counter or a flag.

We have to define in the code the length of the sequence of number we want and the length of the window size.

![Untitled](Stop-and-wait%20ARQ%20a6eb25b76ced4ebbab0e33c4cd906c5b/Untitled%205.png)

---

# Conclusion

The aim would be to associate the Selective Repeat ARQ with the using of tokens for alternating emission between both raspberry pi to have a increase of the efficiency because we need less retransmission and we don´t need to re transmit all the frames after a lost frame.