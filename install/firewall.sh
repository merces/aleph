#!/bin/bash

modprobe nf_conntrack_ftp

iptables -F
iptables -t nat -F
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

iptables -A INPUT -i lo -j ACCEPT

iptables -A INPUT -p icmp -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p udp --dport 20 -j ACCEPT
iptables -A INPUT -p tcp -m multiport --dport 21,22,443 -j ACCEPT
iptables -A INPUT -j LOG --log-prefix "INPUT: "

iptables -A FORWARD -j LOG --log-prefix "FORWARD: "

iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -p icmp -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -p tcp -m multiport --dport 25,53,80,443 -j ACCEPT
iptables -A OUTPUT -p udp -m multiport --dport 53,123 -j ACCEPT
iptables -A OUTPUT -j LOG --log-prefix "OUTPUT: "
