# IP Multicast Basics

## Foreword

- There are various services on the network. Generally, services can be classified into the following types based on the traffic model:
  - Point-to-point (P2P) services, such as File Transfer Protocol (FTP) and web services. The key characteristic of P2P services is that different users have different requirements for them. For example, user A needs to download document A, whereas user B needs to download document B. This type of service is usually carried in unicast mode, and the server sends different P2P data flows to different users.
  - Point-to-multipoint (P2MP) services, such as IPTV and video conferencing services. The key characteristic of P2MP services is that users have the same requirements for them. For example, users A, B, C, and D all need to watch video X. P2MP services can be carried in unicast, multicast, or broadcast mode. However, using unicast or broadcast to carry P2MP services encounters problems.
  - Multicast can prevent these problems.
- This course describes the advantages of using multicast to carry P2MP services, basic concepts of multicast, and the basic multicast forwarding process.

## Objectives

- On completion of this course, you will be able to:
  - Describe the definition and address structure of multicast.
  - Describe multicast data forwarding implementation.
  - Describe reverse path forwarding (RPF) implementation.

## Contents

1. Basic Concepts of Multicast
2. Multicast Data Forwarding Implementation

## 1. Basic Concepts of Multicast

### Problems of Using Unicast or Broadcast to Carry P2MP Services

- P2MP services can be carried in unicast, multicast, or broadcast mode. There are various implementation modes on the live network. However, some inherent problems occur if unicast or broadcast is used to carry P2MP services.

Diagram description: Two side-by-side topology diagrams. Left side, titled "P2MP services carried in unicast mode (IPTV scenario)": a video source server connects to a unicast network, which fans out to multiple clients — an IPTV client, an ordinary terminal, and another IPTV client. Callouts note that the video source server needs to maintain a large number of unicast flows (intensifying pressure on the server), that a large number of unicast flows consume a large amount of bandwidth, that when there are a large number of clients a large number of unicast flows are generated, and that one unicast flow is formed between each client and the video source. Right side, titled "P2MP services carried in broadcast mode (IPTV scenario)": a video source connects to a broadcast network which replicates and sends copies to all local interfaces except the inbound interface, reaching an IPTV client, an ordinary terminal, and another IPTV client. Callouts note that only one broadcast flow needs to be sent for one video, that the device replicates the broadcast flow and sends copies to all other local interfaces except the inbound interface, and that ordinary terminals may also receive broadcast data, causing security risks.

- Unicast transmission is implemented between a source IP host and a destination IP host. Most of data is transmitted in unicast mode on a network. For example, email and online banking applications are implemented in unicast mode.
  - In unicast communication, each data packet has a specific destination IP address. For the same data, if there are multiple receivers, the server needs to send the same number of unicast data packets. If a large number of receivers exist, replication of the same data and transmission of a large number of duplicate copies intensify the pressure on the server, affect device performance, and consume a lot of link bandwidth resources. Therefore, the unicast mode is applicable to networks with only a small number of users. When there are a large number of users, the unicast mode cannot ensure the network transmission quality.
- Broadcast transmission is implemented between a source IP host and all the other IP hosts on the local network. All hosts can receive data from the source host, regardless of whether they require the data.
  - Broadcast data packets are transmitted in a broadcast domain. Once a device sends a broadcast data packet, all other devices in the broadcast domain receive the packet and have to process it, which consumes resources. A large number of broadcast data packets will consume tremendous network bandwidth and device resources. The broadcast mode applies only to shared network segments, and cannot ensure information security and paid services.

### Using Multicast to Carry P2MP Services

- In multicast transmission mode, a data flow is transmitted to a group of users along a multicast distribution tree (MDT). Each link transmits only one copy of multicast data flows. Compared with unicast and broadcast, multicast has the following advantages:
  - Compared with unicast, multicast prevents the increase in the number of users from increasing the pressure on the video source or significantly increasing the consumption of network resources.
  - Compared with broadcast, multicast improves transmission security without wasting network resources. In addition, multicast transmission can be implemented across network segments.

Diagram description: A video source connects to a multicast network. The network device replicates multicast flows and sends copies to specific interfaces. Only one multicast flow needs to be sent for one video. Downstream, the tree fans out through devices to two IPTV clients and an ordinary terminal in between; a callout notes that ordinary terminals will not receive multicast flows.

- Multicast transmission is implemented between one source IP host and a group of IP hosts, with transit nodes selectively replicating and forwarding data based on demands of receivers.
- Multicast technologies efficiently implement P2MP service data transmission over an IP network, while conserving network bandwidth and reducing network loads.
- Multicast distribution tree (MDT): a forwarding path of multicast traffic.

### Multicast Data Packet Structure

- The structure of a multicast data packet is similar to that of a unicast packet, but the destination MAC address and destination IP address of a multicast data packet are different from those of a unicast packet.
  - The destination IP address of a multicast packet is a multicast IP address ranging from 224.0.0.0 to 239.255.255.255.
  - The destination MAC address of a multicast packet is a multicast MAC address, which is mapped from a multicast IP address.

Diagram description: A packet field diagram showing, left to right: Dest MAC, Scr MAC, Scr IP, Dest IP, Payload. Labels above indicate: multicast destination MAC address is the "multicast MAC address"; multicast source MAC address is "MAC 1"; multicast source IP address is "IP 1"; multicast destination IP address is "239.0.0.1 (multicast IP address)". Below, a topology shows a multicast source (IP 1, MAC 1) connected through a multicast network to a multicast group member that joins multicast group 239.0.0.1, with the "Multicast packet" labeled as it traverses the network.

### Multicast IP Addresses

- In the IPv4 address space, class D addresses (224.0.0.0/4) are used for multicast. A multicast address represents a P2MP data flow, for example, IPTV data flow or voice conference data flow.
- In most cases, different services (such as IPTV and voice conference services) on the same multicast network need to use different multicast IP addresses.
- IANA further defines class D addresses. The following table lists main multicast addresses.

| Address Range | Description |
|---|---|
| 224.0.0.0–224.0.0.255 | Permanent group addresses reserved for routing protocols |
| 224.0.1.0–231.255.255.255 233.0.0.0–238.255.255.255 | Temporary any-source multicast group addresses |
| 232.0.0.0–232.255.255.255 | Temporary source-specific multicast group addresses valid on the entire network |
| 239.0.0.0–239.255.255.255 | Temporary any-source multicast group addresses valid only in the local administration domain |

- IPv4 multicast addresses:
  - The IPv4 address space is divided into five classes, class A to class E. Class D addresses are IPv4 multicast addresses, ranging from 224.0.0.0 to 239.255.255.255. These addresses identify multicast groups and can only be used as destination addresses of multicast packets, not as source addresses.
  - Source addresses of IPv4 multicast packets are IPv4 unicast addresses, which can be class A, class B, or class C addresses and cannot be class D or class E addresses.
  - All receivers of a multicast group are identified by the same IPv4 multicast group address at the network layer. Once a user joins the multicast group, the user can receive IP multicast packets with the group address as the destination address.

### Multicast MAC Addresses

- When unicast IPv4 packets are transmitted on an Ethernet network, MAC addresses of receivers are used as destination MAC addresses. When a multicast packet is transmitted, its destination, however, is a group of unspecific members. Therefore, an IPv4 multicast MAC address is needed.
- As defined by IANA, the most significant 24 bits of an IPv4 multicast MAC address are 0x01005e, the 25th bit is 0, and the least significant 23 bits are the least significant 23 bits of an IPv4 multicast address. For example, multicast group IP address 224.0.1.1 corresponds to multicast MAC address 01-00-5e-00-01-01.

Diagram description: A bit-mapping diagram. The multicast IP address is shown as 32 bits split into: "1110 XXXX" (the fixed class D prefix, top 4 bits fixed as 1110), then "X XXX XXXX", "XXXX XXXX", "XXXX XXXX" — with a note that "5-bit information is lost" pointing at the boundary, and a bracket marking the 23 bits that get mapped. Below, the multicast MAC address is shown as 48 bits: "0000 0001", "0000 0000", "0101 1110", "0 XXX XXXX", "XXXX XXXX", "XXXX XXXX" — with a note that "25 bits are fixed" and an arrow labeled "Mapping between a multicast IP address and a multicast MAC address" pointing from the IP address's last 23 bits down to the MAC address's last 23 bits.

- The most significant 4 bits of an IPv4 multicast address are fixed as 1110, mapping the leftmost 25 bits of a multicast MAC address. Among the last 28 bits in the IPv4 address, only 23 bits are mapped to the rest bits in the MAC address, with 5 bits lost. For example, multicast IP addresses 224.0.1.1, 224.128.1.1, 225.0.1.1, and 239.128.1.1 are all mapped to multicast MAC address 01-00-5e-00-01-01. This must be taken into consideration during address assignment.
- IETF believes that this will not cause great impact because there is a very low probability that two or more group addresses in the same LAN will be mapped to the same MAC address.
- A multicast MAC address identifies a group of devices. The least significant bit of the first byte in a multicast MAC address is 1, for example, 0100-5e-00ab.
- The devices identified by the same multicast MAC address are in the same multicast group. These devices listen to the data frames whose destination MAC address is this multicast MAC address. A unicast MAC address can be assigned to an Ethernet interface, whereas a multicast or broadcast MAC address cannot be assigned to any Ethernet interface. In other words, a multicast or broadcast MAC address cannot be used as the source MAC address of a data frame, but can be used as the destination MAC address of a data frame.
- For example, the BPDU payload of the STP protocol is directly encapsulated in the Ethernet data frame, with the destination MAC address being 0180-c200-0000, which is a multicast MAC address. There are many similar examples, which are not listed here. These multicast MAC addresses are not associated with multicast IP addresses.
- In addition, we need to pay special attention to the multicast MAC addresses that map multicast IP addresses. The multicast MAC addresses described in this course are of such a type.

### Basic Architecture of a Multicast Network

- A multicast network can be divided into three parts:
  - Source end network: sends multicast data generated by the multicast source to the multicast forwarding network.
  - Multicast forwarding network: generates a loop-free multicast forwarding path, which is also referred to as an MDT.
  - Receiver end network: enables the multicast forwarding network to detect the locations of multicast group members and the multicast groups that the members join.

Diagram description: Three labeled zones left to right. "Source end network" contains a multicast source connected to a "Multicast router (FHR)"; a note says it "Sends multicast data to the multicast forwarding network." "Multicast forwarding network" shows multiple interconnected multicast routers with a "Multicast routing protocol" label on the internal links; a note says "Multicast forwarding paths are established based on multicast routing protocols." "Receiver end network" shows a "Multicast router (LHR)" connected to two multicast group members, one joining "multicast group 1" and the other joining "multicast group 2"; a note says "IGMP is used to obtain multicast group members' locations and the multicast groups that they join."

- Multicast source: a sender of multicast traffic, such as a multimedia server. A multicast source does not need to run any multicast protocol. It only needs to send multicast data.
- Multicast receiver: also called a multicast group member, is a device that expects to receive traffic of a specific multicast group, for example, a PC running multimedia live broadcast client software.
- Multicast group: a group of receivers identified by a multicast address. User hosts (or other receiver devices) that have joined a multicast group become members of the group and can identify and receive the IP packets destined for the multicast group address.
- Multicast router: a network device that supports multicast and runs multicast protocols. In addition to routers, switches and firewalls support multicast (depending on device models). Routers are used in this example.
- First-hop router (FHR): a router that directly connects to the multicast source on the multicast forwarding path and is responsible for forwarding multicast data from the multicast source.
- Last-hop router (LHR): a router that directly connects to multicast group members (receivers) on the multicast forwarding path and is responsible for forwarding multicast data to these members.
- The Internet Group Management Protocol (IGMP) is a protocol in the TCP/IP protocol suite and manages group memberships between receiver hosts and immediately neighboring multicast routers.

### Multicast Service Models

- When receiving multicast data, multicast group members can select multicast data sources. Therefore, two multicast service models are available: any-source multicast (ASM) and source-specific multicast (SSM).
  - ASM: After a member joins a multicast group, the member can receive data sent by any source to the group.
  - SSM: After a member joins a multicast group, the member can only receive data sent by the specific source to the group.

Diagram description: Two side-by-side diagrams. Left, "ASM model": Multicast source 1 and Multicast source 2 both connect into a multicast network, which reaches a multicast group member; a callout notes the member "Receives multicast packets from different sources." Right, "SSM model": Multicast source 1 and Multicast source 2 both connect into a multicast network, but the path from source 2 is blocked (marked with an X); a callout notes the member "Receives only the multicast packets from the specific source."

- ASM characteristics:
  - In ASM, to improve security, multicast source filter policies can be configured on routers to permit or deny packets from some multicast sources. This filters data sent to receiver hosts.
  - In the ASM model, each group address must be unique on the entire multicast network. That is, an ASM group address can only be used by only one multicast application at a time. If two applications use the same ASM group address to send data, their receiver hosts receive data from two sources, which may cause network traffic congestion and affect the receiver hosts.
- SSM characteristics:
  - The SSM model does not require globally unique group addresses, but the multicast source must be unique to multicast groups. That is, different applications on a source must use different SSM group addresses. Different applications on different sources can share one SSM group addresses because each source-group pair has an (S, G) entry. This model saves multicast group addresses without congesting the network.

## 2. Multicast Data Forwarding Implementation

### Problems That Accompany Multicast Data Forwarding (1)

- Multicast data forwarding depends on routing entries. However, such forwarding encounters the following problems:

**Forwarding loops occur, and duplicate packets are received.**

Diagram description: A topology with a multicast source connected to router RT1, which connects to RT2 and RT2 connects into a ring with RT3 and RT4, and RT4 connects down to a multicast group member that has joined multicast group G1. Each router shows a "Destination Group / Outbound Interface" table: RT1 shows G1 → IF1, IF2; RT2 shows G1 → IF1, IF2; RT3 shows G1 → IF1, IF2; RT4 shows G1 → IF1, IF2, IF3. Callout boxes labeled "Forwarding loop" and "Duplicate packet" point at the ring among RT1/RT2/RT3/RT4 and at RT4's extra incoming copy respectively — illustrating that without a mechanism to select a single correct upstream path, the multicast packet loops around the ring and the destination router receives duplicate copies.

### Problems That Accompany Multicast Data Forwarding (2)

- Multicast data forwarding depends on routing entries. However, such forwarding encounters the following problems:

**Sub-optimal paths exist, and duplicate packets are received.**

Diagram description: A topology with a multicast source at the top connected to RT1, which connects to RT2, and both RT1 and RT2 connect down to RT3, which connects to a multicast group member that joined multicast group G1. RT1 shows G1 → IF1, IF2; RT2 shows G1 → IF1, IF2; RT3 shows G1 → IF1, IF2, IF3. A callout labeled "Sub-optimal Path" points at the RT1–RT2 direct link, and a callout labeled "Duplicate packet" points at RT3 receiving the multicast packet twice (once via RT1 directly, once via RT2). A note states: "A loop may also occur in this topology. The figure on the left shows a loop situation, which is not described in this topology."

### Multicast Routing and RPF Check

- Loops, sub-optimal routes, and duplicate packets may occur during multicast forwarding. To prevent these problems, in addition to the destination network and outbound interface, multicast source and inbound interface information needs to be added to multicast routing entries. Then a device forwards only the multicast data received from the specified inbound interface, preventing problems such as loops, sub-optimal routes, and duplicate packets (partially solved) during multicast forwarding.
- For the same multicast source, the device can determine the unique inbound interface of multicast traffic through the reverse path forwarding (RPF) check.
- RPF check that is based on multicast routing entries:

Diagram description: A box labeled "Multicast routing entries" shows an example entry: "(192.168.0.2, 239.0.0.1) / Upstream Interface: GigabitEthernet1/0/0 //Unique inbound interface / Downstream interfaces: 1: GigabitEthernet2/0/0, 2: GigabitEthernet3/0/0", with an arrow labeled "Decided by the RPF check" pointing to the Upstream Interface line. To the right, a topology titled "RPF check prevents loops, sub-optimal paths, and duplicate packets": multicast source S1 connects to RT1, which connects to RT2, and both connect down to RT3; RT3 shows a "Multicast routing table" with columns Multicast Information (S1, G1), Inbound Interface (IF1), Outbound Interface (IF3). RT3 discards the duplicate copy of the multicast packet arriving on IF2 (marked with an X and the label "Discards data received from IF2"), while the copy on IF1 is accepted; the multicast group member joins multicast group G1.

- The outbound interface of a multicast routing entry is usually determined by the multicast routing protocol.
- Multicast routing protocols will be covered in the course of **PIM Implementation and Configuration**.
- A multicast routing entry contains a multicast source and a multicast group. Therefore, it is also called an (S, G) entry.

### Implementation of RPF Check

- Process of an RPF check:

Diagram description: A flowchart: "A multicast data packet reaches a device" → "Reads the source IP address" → "Searches for the outbound interface of the unicast route to the multicast source" → decision "Is the outbound interface the same as the inbound interface of the multicast packet?" → if No: "The multicast packet was received from an incorrect interface" → "Discards the multicast packet"; if Yes: "The multicast packet was received from the correct interface" → "Accepts the multicast packet." To the right, a topology: multicast source S1 connects to RT1, which connects to RT2, and both connect down to RT3. A packet header example shows "SIP:S1 DIP:G1 Payload". RT3 has an "RPF route" table: Destination Network Segment = S1, RPF Interface = IF1, with a note "Searches for the corresponding RPF route based on the multicast source IP address." RT3 performs the RPF check, discarding traffic on IF2 (marked with X) and accepting only traffic received through IF1, which reaches the multicast group member that joined multicast group G1. A note states: "All multicast routers need to perform the RPF check. This example uses RT3 as an example."

- Each multicast router searches its routing tables (unicast routing table and MBGP routing table or multicast static routing table) for the route to the packet source based on the source address of a received packet. Then, the multicast router checks whether the outbound interface of the route to the packet source is the same as the inbound interface of the received multicast packet. If they are the same, the router considers that the multicast packet was received through the correct interface and accepts it. This ensures the correct forwarding path and allows the router to accept the multicast packet only through one inbound interface. This process is called the RPF check.

### RPF Route Selection Rules

- RPF routes can be selected among unicast routes, MBGP routes, and multicast static routes. If a router has all these routes, it performs an RPF check on a multicast packet in the following way:

Diagram description: A flowchart showing "Multicast source IP" feeding into three parallel lookups — "Unicast routing table" (from the routing table), "MBGP routing table" (from the routing table), "Multicast static routing table" (from the routing table) — each producing a "Selects a candidate RPF route (including the outbound interface)". These three candidates feed into a box listing "RPF route selection rules: 1. Longest mask matching 2. Preference value 3. Multicast static route > MBGP route > Unicast route (preference order)", labeled "Rules-based selection", which outputs "Selects the RPF route (including the outbound interface)" → "Determines the RPF interface." To the right, a topology: multicast source S1 connects to RT1, connects to RT2, both connect down to RT3, which performs the RPF check (discarding data received from IF2, marked X) and accepts data on IF1, reaching the multicast group member that joined multicast group G1. Below, three example tables show: Unicast routing table (Destination Network Segment S1, Outbound Interface IF1); MBGP routing table (Destination Network Segment S1, Outbound Interface IF2); Multicast static routing table (Destination Network Segment S1, Outbound Interface IF1) — feeding into "RPF route selection" which determines the RPF route/interface.

- The router selects one of the three routes as the RPF route according to the following rules:
  - If route selection based on the longest match rule is configured, the router selects the route with the longest matching mask from the three routes.
  - If the masks of the three routes have the same length, the route with the highest preference is selected.
  - If the preferences of the three routes are also the same, the multicast static route, MBGP route, and unicast route are preferred in descending order.
- MBGP:
  - MBGP is used to transmit multicast source-related routing entries.
- Multicast static routing table:
  - It contains routes for which the mapping between the multicast source and the outbound interface is manually configured.

### Multicast Distribution Tree

- It is required that no loops, sub-optimal paths, or duplicate packets occur during multicast data forwarding.
- Through the RPF mechanism and multicast routing protocols, a loop-free multicast forwarding path (MDT) without sub-optimal paths or duplicate packets can be established on the multicast network.
- Each MDT takes the multicast source as the root and group members as leaves. Multicast data is forwarded based on the MDT.

Diagram description: A multicast source (root) connects to RT1, which connects into a "Multicast network" containing RT2 and RT3 arranged so that RT1 reaches both RT2 and RT3, and RT2 and RT3 both connect to RT4. RT4 connects to a multicast group member (leaf). RT3 also connects directly down to a second multicast group member (leaf). A legend distinguishes dashed blue arrows (multicast traffic) from solid red arrows (the MDT) — showing that the actual multicast traffic flow follows the tree defined by the red MDT path, from the source through RT1, RT2/RT3, to RT4 and the leaf members, without looping.

### Multicast Data Forwarding Process

- The multicast data forwarding process is as follows:

Diagram description: A topology showing a multicast source (192.168.10.1) sending a packet with header "192.168.10.1 → 239.0.0.1, Payload" into RT1. RT1 connects to RT2 and RT3; RT2 and RT3 both connect to RT4; RT4 connects to a multicast group member that joins multicast group 239.0.0.1. Each router box shows a "Multicast routing table" with Multicast information (S: 192.168.10.1, G: 239.0.0.1), Inbound Interface, and Outbound Interface, e.g., RT1: Inbound IF3, Outbound IF1; RT2: Inbound IF1, Outbound IF2; RT4 (right-hand box): Inbound IF1, Outbound IF3. An "RPF route" box at the top shows Destination Network Segment 192.168.10.1, RPF Interface IF1. Callout questions embedded in the diagram ask "How is an MDT generated?" (near RT1/RT3) and "How does a multicast network know the locations of multicast group members?" (near the receiver end), each router performing the RPF check as the packet is forwarded along dashed blue "Multicast traffic" arrows following the solid red "MDT" path down to the receiver.

- The outbound interface of a multicast routing entry and multicast forwarding path are determined by a multicast routing protocol.
  - Multicast routing protocols include PIM, MBGP, and Multicast Source Discovery Protocol (MSDP).
  - For details about multicast routing protocols, see the course of **PIM Implementation and Configuration**.
- The locations of multicast group members are advertised through IGMP.
  - For details about IGMP, see the course of **PIM Implementation and Configuration**.

### Multicast Protocol Introduction

- A multicast network needs to establish forwarding paths based on multiple multicast protocols.
  - IGMP runs on the receiver end network and is used to inform the multicast network of the locations of group members and the multicast groups that the members join.
  - Protocols working on the multicast forwarding network include PIM, MSDP, and MBGP.
    - PIM is mainly used to generate MDTs in an AS.
    - MSDP is mainly used to help generate inter-AS MDTs.
    - MBGP is used to help perform RPF check on inter-AS multicast traffic.

Diagram description: Two multicast network clouds representing autonomous systems, "Multicast network AS 100" and "Multicast network AS 200," each internally running PIM among their routers. A multicast source connects into AS 100 via a router; on the receiver side, a multicast group member connects to a router in AS 100 via IGMP, and another multicast group member connects to a router in AS 200 via IGMP. Between AS 100 and AS 200, the two boundary routers exchange MSDP and MBGP.

## Quiz

1. (Single) What is the range of IPv4 multicast addresses? ( )
   A. 192.168.0.0–192.168.255.255
   B. 172.21.0.0–172.21.255.255
   C. 224.0.0.0–239.255.255.255
   D. 240.0.0.0–255.255.255.255

2. (Multiple) Which of the following statements about the functions of RPF are true? ( )
   A. It prevents duplicate multicast packets.
   B. It accelerates multicast traffic forwarding.
   C. It prevents loops.

**Answers:**

1. C
   - The Internet Assigned Numbers Authority (IANA) allocates class D addresses for IPv4 multicast. An IPv4 address is 32 bits long, and the most significant 4 bits of a Class D IP address are 1110. Therefore, multicast IP addresses range from 224.0.0.0 to 239.255.255.255.
2. AC

## Summary

- Multicast is mainly used to solve the following problems when P2MP traffic is carried in unicast or broadcast mode:
  - When P2MP traffic is carried in unicast mode, with the increase of P2MP service terminals, the bandwidth consumption or the pressure on the source server may be too high.
  - When P2MP traffic is carried in broadcast mode, although the problems accompanying P2MP traffic transmission in unicast mode do not occur, the security is low.
- A multicast network consists of three parts: source end network, multicast forwarding network, and receiver end network.
  - The multicast forwarding network is responsible for forwarding multicast data between multicast routers, but problems such as loops, sub-optimal paths, and duplicate packets may occur. These problems can be partially or completely solved through the RPF check.

