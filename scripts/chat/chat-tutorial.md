# Websockets chat 

This websockets chat is a simple application to demo the processing and communication of the Low End Networks prototype presented at NOMS 2025.

## Configuring devices

To make the chat work, first you need to enable compression on both the devices. For this, make an ssh connection and then run the following:

```shell
sudo -i
echo trim-and-compress > ~/t4p4s-switch
systemctl restart bmv2.service

# check if the bmv2 has started correctly
systemctl status bmv2.service
```

After this, you'll need to configure the end device firewall:

```shell
# flush the FORWARD chain
iptables -F FORWARD
iptables -P FORWARD ACCEPT

# configure the namespace firewall
# drops everything
ip netns exec ns iptables -P FORWARD DROP

# except for traffic in the port 8765 (defined for the chat)
ip netns exec ns iptables -A FORWARD -p tcp --dport 8765 -m conntrack --cstate ESTABLISHED,RELATED -j ACCEPT
ip netns exec ns iptables -A FORWARD -p tcp --dport 8765 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
ip netns exec ns iptables -A FORWARD -p tcp --sport 8765 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
ip netns exec ns iptables -A FORWARD -p tcp --dport 8765 -m conntrack --ctstate NEW -j ACCEPT
ip netns exec ns iptables -A FORWARD -p tcp --sport 8765 -m conntrack --ctstate NEW -j ACCEPT

# check if everything is working
ip netns exec ns iptables -nvL
```

## Final steps

After these initial configuration, you must run the server and the clients.

| Important: Install the `websockets` package with pip in the server device and in every client device.

```shell
pip install websockets
```

Finally, you may run the server with `python3 server.py` and the clients `python3 client.py`.

Check for the connection messages in the server and for the notification on the clients! There you go!

