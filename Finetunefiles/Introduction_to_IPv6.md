# Introduction to IPv6

*(Source pages 887–936 of the original export. This is the second of two distinct topics found in the uploaded PDF; the first, "PIM Implementation and Configurations," is provided as a separate file. This document begins at the title slide, page 887.)*

Diagram description (title slide): Standard Huawei course title slide with the title "Introduction to IPv6" over a background photo of a modern office campus, and the HUAWEI logo in the bottom right corner.

## Foreword

- IPv4 is a widely used Internet protocol. In the early stage of the Internet, IPv4 developed rapidly due to its simple design, easy implementation, and good interoperability. However, with the rapid development of the Internet, IPv4's design defects become increasingly obvious. Internet Protocol version 6 (IPv6) was developed to address the defects.
- IPv6 is also called IP next generation (IPng). Designed by the Internet Engineering Task Force (IETF), IPv6 is an upgraded version of IPv4.
- This course describes the basic concepts, address classification, and packet format of IPv6.

## Objectives

- On completion of this course, you will be able to:
  - Describe the development status of IPv6.
  - Explicate the advantages of IPv6 over IPv4.
  - Describe the basic concepts of IPv6.
  - Describe the format of an IPv6 packet header.
  - Describe the IPv6 address format and types.
  - Configure IPv6 addresses and routes.

## Contents

1. IPv6 Overview
2. IPv6 Address Introduction
3. IPv6 Packet Structure
4. Basic IPv6 Configuration

## 1. IPv6 Overview

*(Running header across this section's slides: IPv6 Status | IPv6 Advantages | IPv6 Transition Technologies | IPv6 Routing.)*

### IPv4 Status

- On February 3, 2011, the Internet Assigned Numbers Authority (IANA) announced even allocation of its last 4.68 million IPv4 addresses to five Regional Internet Registries (RIRs) around the world. The IANA thereafter had no available IPv4 address.

Diagram description: A horizontal timeline showing successive IPv4 address exhaustion milestones at five dates — 2011.4, 2012.9, 2014.6, 2015.9, and 2019.11.25 — each marked "IPv4 address exhaustion," with brief annotations noting that specific RIRs (including RIPE and ARIN, as legible in the source) announced exhaustion of their allocations at these points. (Note: the source scan partially obscures which RIR is paired with each of the five dates; RIPE and ARIN are the two legible RIR names in this transcription pass — recommend a visual check of the original slide if the full source-to-date mapping is needed.)

- The IANA is responsible for assigning global Internet IP addresses. The IANA assigns some IPv4 addresses to continent-level RIRs, and then each RIR assigns addresses in its regions. The five RIRs are as follows:
  - RIPE: Réseaux IP Européens, which is a European IP address registration center and serves Europe, Middle East, and Central Asia.
  - LACNIC: Latin American and Caribbean Internet Address Registry, which is an Internet address registration center for Latin America and the Caribbean and serves the Central America, South America, and the Caribbean.
  - ARIN: American Registry for Internet Numbers, which is an Internet number registration center in the United States and serves North America and some Caribbean regions.
  - AFRINIC: Africa Network Information Centre, which serves Africa.
  - APNIC: Asia Pacific Network Information Centre, which serves Asia and the Pacific.
- IPv4 has proven to be a very successful protocol. It has survived the development of the Internet from a small number of computers to hundreds of millions of computers. However, this protocol was designed based on the network scale several decades ago. With the expansion of the Internet and the launch of new applications, IPv4 has shown more and more limitations.
- The rapid expansion of the Internet scale was unforeseen at that time. Especially over the past decade, the Internet has experienced explosive growth and has been accessed by numerous households. It has become a necessity in people's daily life. In this case, IPv4 address exhaustion is becoming an urgent issue.
- In the 1990s, the IETF launched technologies such as network address translation (NAT) and classless inter-domain routing (CIDR) to delay IPv4 address exhaustion. However, these transition solutions can only slow down the speed of address exhaustion, but cannot fundamentally solve the issue.

### Development Status of IPv6

- Significant increase in the Global IPv6 Deployment Ratio: By October 2019, countries or regions with a comprehensive IPv6 deployment rate of over 30% included Belgium, India, Malaysia, and the United States (as legible in the source).
- Sharp Increase in the Number of Global IPv6 Users: According to Google website monitoring, by September 2019, users who use IPv6 to access Google websites accounted for over 30%.
- Improved IPv6 Support for Mainstream Software and Hardware:
  - By October 10, 2019, 14.6% of global websites, 19.2% of the top 1 million websites, and nearly 30% of the top 1000 websites support IPv6 access.
  - Major cloud service providers and CDN carriers, such as Cloudflare, Akamai, Microsoft Azure, and Amazon, all support IPv6.
  - Windows and macOS operating systems for mass users support IPv6.
- Global Networks and Carriers Increasingly Support IPv6: By October 2019, 1505 of the 1527 top domains worldwide support IPv6, accounting for 98.6% of the total.

*(Note: the source slide's list of specific countries/regions with a >30% IPv6 deployment ratio was only partially legible in this transcription pass; the figures and percentages above are transcribed as they appear. Recommend a visual check of the original if the exact country list matters.)*

### Why IPv6?

| IPv4 | IPv6 |
|---|---|
| Public address exhaustion | Nearly infinite address space |
| Improper packet header design | Hierarchical address allocation |
| Oversized routing table and low table lookup efficiency | Plug-and-play |
| Broadcast flooding caused by dependency on ARP | Simplified packet header |
| | IPv6 security features |
| | Integrity of E2E communication |
| | Mobility |
| | Enhanced QoS features |

### IPv6 Advantages

- **Nearly infinite address space:** This is the most obvious advantage over IPv4. An IPv6 address consists of 128 bits. The address space of IPv6 is about 8 x 10^28 times that of IPv4. It is claimed that IPv6 can allocate a network address to each grain of sand in the world. This makes it possible for a large number of terminals to be online at the same time and unified addressing management, providing strong support for the Internet of Things (IoT).
- **Hierarchical address structure:** IPv6 addresses are divided into different address segments based on application scenarios thanks to the nearly infinite address space. In addition, the continuity of unicast IPv6 address segments is strictly required, facilitating IPv6 route aggregation and reducing the size of IPv6 address tables.
- **Plug-and-play:** Any host or terminal must have a specific IP address to obtain network resources and transmit data. Traditionally, IP addresses are assigned manually or automatically using DHCP. In addition to the preceding two methods, IPv6 supports SLAAC.
- **E2E network integrity:** NAT used widely on IPv4 networks damages the integrity of E2E connections. After IPv6 is used, NAT devices are no longer required, and online behavior management and network monitoring become simple. In addition, applications do not need complex NAT adaptation code.
- **Enhanced security:** IPsec was initially designed for IPv6. Therefore, IPv6-based protocol packets (such as routing protocol and neighbor discovery packets) can be encrypted in E2E mode, despite the fact that this function is not widely used currently. The security capability of IPv6 data plane packets is similar to that of IPv4+IPsec.
- **High scalability:** IPv6 extension headers are not a part of the main data packet. However, if necessary, the extension headers can be inserted between the IPv6 header and payload to assist IPv6 in encryption, mobility, optimal path selection, and QoS, improving packet forwarding efficiency.
- **Improved mobility:** When a user moves from one network segment to another on a traditional network, a typical triangle route is generated. On an IPv6 network, the communication traffic of such mobile devices can be directly routed without the need of the original triangle route. This feature reduces traffic forwarding costs and improves network performance and reliability.
- **Enhanced QoS:** IPv6 reserves all QoS attributes of IPv4 and additionally defines a 20-bit Flow Label field for applications or terminals. This field can be used to allocate specific resources to special services and data flows. Currently, this mechanism has not been fully developed or applied yet.

*(Note: the source slide states the Flow Label field length as "20-byte" in one place in the deck's advantages summary table, but as "20 bits" both later in this same slide's notes and again on the IPv6 Header slide later in this document. 20 bits is the value defined by the IPv6 specification (RFC 8200) and is used consistently elsewhere in this deck, so "20-byte" in the summary table appears to be a source-side inconsistency/typo; it is flagged here rather than silently corrected in the summary table above, and the body text is transcribed as "20 bits" to match the rest of the deck.)*

### Introduction to IPv6 Transition Technologies (1)

- NAT alleviates IPv4 address insufficiency, and IPv6 is the final solution to this issue. Currently, different regions in the world have different requirements for IPv6 deployment, and IPv4 networks are still dominant. Therefore, IPv6 and IPv4 will coexist in a short period of time.
- The evolution from an IPv4 network to an IPv6 network involves the following technologies:
  - Dual-stack technology: enables both IPv4 and IPv6 stacks on a device.
  - Tunneling technology: encapsulates a type of protocol data into another type of one.
  - Translation technology: translates between IPv6 and IPv4 addresses.
- There is no optimal transition technology solution, and no technical solution can resolve all issues. Generally, multiple technologies are combined into different transition solutions to address different network access scenarios.

### Introduction to IPv6 Transition Technologies (2)

**Dual-stack technology:**
- Devices support IPv4/IPv6. IPv4 and IPv6 are independently deployed on a network and coexist within a period of time. This technology has little impact on existing IPv4 services.
- The evolution solution is simple and easy to understand. The workload of network planning and design is relatively low.
- Much hardware and software (such as network devices, terminals, and operating systems) on live networks support dual stack. Even IPv6 is enabled by default and can be directly used.
- The hardware and software of devices must support dual stack.

**Tunneling technology:**
- IPv4 traffic is encapsulated in an IPv6 tunnel, or IPv6 traffic is encapsulated in an IPv4 tunnel.
- This technology implements interconnection between isolated IPv6 islands on an IPv4 network or interconnection between isolated IPv4 islands on an IPv6 network.
- Devices (usually tunnel endpoints) must support dual stack and tunneling technology.
- This technology is applicable to a temporary isolated island interconnection but not long-term and stable services.

**Translation technology:**
- IPv4 traffic is translated into IPv6 traffic (mainly IP header modification), or IPv6 traffic is translated into IPv4 traffic.
- This technology implements communication between native IPv4 and IPv6 networks.
- This implementation damages the integrity of E2E connections. The ALG function must be provided for special applications.
- Network management and audit become complex.
- NAT and DNS devices must be deployed on a network.

Diagram description: Three side-by-side deployment scenarios. (1) Dual-stack: an IPv6 host and an IPv4 host both connect through a "Dual-stack device," with separate IPv4 data and IPv6 data paths shown running in parallel end to end. (2) Tunnel: two dual-stack devices at the edges of an IPv4 (or IPv6) network encapsulate the other protocol's traffic into a tunnel that crosses the native network, decapsulating it at the far end. (3) Translation: an IPv6 host connects through a DNS64/NAT64 device to reach an IPv4 host, with the NAT64 device translating IPv6 data to IPv4 data (and vice versa) and DNS64 assisting with address translation for DNS lookups.

### Introduction to IPv6 Routing Protocols

| OSPFv3 | IS-IS for IPv6 | BGP4+ | PIM |
|---|---|---|---|
| 1. This protocol runs based on links. A single link supports multiple instances. | 1. This protocol is a simple extension of the original protocol but not a new protocol or version. IS-IS routers can communicate with each other. | 1. BGP4+ is not a new protocol or version, and the IPv6 address family only needs to be supported on the Multiprotocol Extensions for BGP (MP-BGP) architecture. BGP4+ routers can communicate with BGP4 routers. | 1. The actual version of Protocol Independent Multicast (PIM) is still PIMv2. |
| 2. The IP address information in the LSA header is deleted to implement decoupling from a network layer protocol. | 2. A network layer protocol identifier (NLPID) is added to declare support for IPv6. | 2. Two types of network layer reachability information (NLRI) are added to support the advertisement of IPv6 reachable routes and next hop information and the withdrawal of unreachable routes. | 2. The only difference is that both protocol packets and multicast data packets use IPv6 addresses. |
| 3. A flooding scope field is defined in LSAs to support the processing of unknown LSAs. | 3. Two types of TLVs are added to support the advertisement of IPv6 network reachability and interface IPv6 addresses. | | |
| 4. LSAs are added to support advertisement of IPv6 routes. | | | |

These protocols are simple extensions of the original ones, and their versions remain unchanged.

- Similar to IPv4 networks, IPv6 networks also support static routes.

## 2. IPv6 Address Introduction

### Contents (section marker)

1. IPv6 Overview
2. IPv6 Address Introduction
   - IPv6 Address Overview
   - IPv6 Address Types
   - IPv6 Address Planning Example
3. IPv6 Packet Structure
4. Basic IPv6 Configuration

### IPv6 Address

- The length of an IPv6 address is 128 bits. Generally, an IPv6 address is divided into eight segments using colons, and each segment contains 16 bits and is expressed in hexadecimal notation.

```
2001 : 0DB8 : 0000 : 0000 : 0008 : 0800 : 200C : 417A
16 bits  16 bits  16 bits  16 bits  16 bits  16 bits  16 bits  16 bits
```

- The letters in an IPv6 address are case insensitive. For example, A is equivalent to a.
- Similar to an IPv4 address, an IPv6 address is expressed in the format of IPv6 address/mask length.
  - IPv6 address: `2001:0DB8:2345:CD30:1230:4567:89AB:CDEF/64`

### IPv6 Address Format

**Compressed format:**
- Leading 0s in each segment can be suppressed. However, if all bits of a segment are 0s, at least one 0 must be reserved. The trailing 0s cannot be suppressed.
- If one or more consecutive segments contain only 0s, they can be replaced using two consecutive colons (::). However, this substitution can only be applied once in the IPv6 address.
- For example, `2001:DB8:0:1::45ff/64` is an IPv6 address in compressed format.
- An IPv4 address consists of four decimal numbers separated by dots and a mask, for example, 192.168.1.1/24. The length of an IPv6 address is 128 bits, and it is suitable for an IPv6 address to inherit the decimal format of an IPv4 address. The IPv6 address format different from the IPv4 address format is defined in RFC 2373.

### IPv6 Address Structure

- An IPv6 address is composed of two parts:
  - Network prefix: consists of n bits and has the same function as the network ID of an IPv4 address.
  - Interface ID: consists of (128 - n) bits and is parallel to the host ID of an IPv4 address.
- Example of an IPv6 unicast address: `2001:0DB8:6101:0001:5ED9:98FF:FECA:A298/64`

Diagram description: The example address `2001:0db8:6101:0001:5ed9:98ff:feca:a298` is split visually into two labeled halves: the first 64 bits (`2001:0db8:6101:0001`) labeled "Network prefix," and the last 64 bits (`5ed9:98ff:feca:a298`) labeled "Interface ID."

### IPv6 Address Prefix

- Due to the limitations of IPv4 address planning and allocation, the IETF classifies IPv6 addresses into different types. Different types of IPv6 addresses are assigned different prefixes and are strictly managed by address allocation organizations.
- Currently, common IPv6 addresses or prefixes are as follows:

| IPv6 Address or Prefix | Description |
|---|---|
| 2001::/16 | Used for the IPv6 Internet, similar to a public IPv4 address. |
| 2002::/16 | Used for 6to4 tunnels. |
| FE80::/10 | Link-local address prefix, which is used for communication within the local link range. |
| FF00::/8 | Multicast address prefix, which is used for IPv6 multicast. |
| ::/128 | Unspecified address, which is similar to 0.0.0.0 in IPv4. |
| ::1/128 | Loopback address, which is similar to 127.0.0.1 in IPv4. |

- Latest definition of the IANA for IPv6 prefixes.

### IPv6 Address's Interface ID

- An interface ID can be manually configured, automatically generated by the system, or generated based on the IEEE EUI-64 specification.
- The method of generating an interface ID based on the IEEE EUI-64 specification is most commonly used. In this method, the MAC address of an interface is converted into an IPv6 address' interface ID.

Diagram description: Step-by-step conversion of MAC address `08-70-5A-90-18-01` into a 64-bit interface ID:
1. The MAC address `08-70-5A-90-18-01` is written out in binary as `00001000 01110000 01011010 10010000 00011000 00000001`, with the seventh bit (the "universal/local" bit, u/l bit) noted as indicating whether the MAC address is a global management address.
2. The seventh bit is reversed (flipped from 0 to 1).
3. `FFFE` is inserted at the midpoint (between the 3rd and 4th bytes) of the MAC address.
4. The result is the binary string `00001010 01110000 01011010 11111111 11111110 10010000 00011010 00000001`, which converts back to hexadecimal as `0A-70-5A-FF-FE-90-1A-01` — this becomes the 64-bit interface ID.

- Currently, the interface ID of an IPv6 address can be generated in the following ways:
  - Generated based on the IEEE EUI-64 specification:
    - The typical length of an interface ID is 64 bits. The IEEE EUI-64 specification defines a method of generating an interface ID, that is, transforming a 48-bit MAC address to a 64-bit interface ID.
    - A 48-bit MAC address can be transformed to a 64-bit interface ID by changing the seventh bit from 0 to 1 and inserting FFFE in the middle of a MAC address.
    - This method reduces the configuration workload. Only one IPv6 prefix needs to be obtained to form an IPv6 address with the interface ID.
    - The defect of this method is that attackers can deduce IPv6 addresses based on MAC addresses.
  - Randomly generated by a device:
    - The device generates an interface ID randomly. Currently, the Windows operating system uses this method.
  - Manually configured:
    - An interface ID can be manually specified.

## IPv6 Address Types

### Contents (section marker)

1. IPv6 Overview
2. IPv6 Address Introduction
   - IPv6 Address Overview
   - **IPv6 Address Types**
   - IPv6 Address Planning Example
3. IPv6 Packet Structure
4. Basic IPv6 Configuration

### IPv6 Address Types

- **Unicast address:** identifies an interface. A packet destined for a unicast address is sent to the interface having that unicast address. In IPv6, an interface may have multiple IPv6 addresses.
- **Multicast address:** identifies multiple interfaces. A packet destined for a multicast address is sent to all the interfaces having that multicast address. Only the interfaces that join a multicast group listen to the packets destined for the corresponding multicast address.
- **Anycast address:** identifies a group of network interfaces (usually on different nodes). A packet sent to an anycast address is routed to the nearest interface having that address, according to the router's routing table.
- IPv6 does not define any broadcast address.

### Common IPv6 Unicast Address — GUA

- A global unicast address (GUA) is also called an aggregatable GUA. This type of address is globally unique and is used by hosts that need to access the Internet. It is equivalent to a public IPv4 address.

Diagram description: A GUA is shown split into three fields: a 3-bit fixed prefix (value `001`), a 45-bit Global routing prefix, a 16-bit Subnet ID, and a 64-bit Interface ID. The Global routing prefix + Subnet ID together form the "Network address" portion, and the Interface ID forms the "Host address" portion. Two example client devices are shown connected to the IPv6 Internet, each with an address in this format: `2001:1::1/64` and `2001:2::1/64`.

- Global routing prefix: is assigned by a provider to an organization. Generally, the prefix is at least 48 bits.
- Subnet ID: is defined by an organization based on network requirements.
- Interface ID: identifies a device's interface.
- You can apply for a GUA from a carrier or the local IPv6 address management organization.

### Common IPv6 Unicast Address — ULA

- A unique local address (ULA) is a private IPv6 address that can be used only on an intranet. This type of address cannot be routed on an IPv6 public network and therefore cannot be used to directly access a public network.

Diagram description: A ULA is shown split into fields: an 8-bit fixed prefix (`1111 1101`), a 40-bit randomly generated Global ID, a 16-bit Subnet ID, and a 64-bit Interface ID. Three example client devices are shown on an intranet (not connected to the IPv6 Internet), with addresses `FD00:1AC0:872E::1/64`, `FD00:1AC0:872E::2/64`, and `FD00:2BE1:2320::1/64`.

- A ULA uses the FC00::/7 address block, in which only FD00::/8 is currently used. FC00::/8 is reserved for future expansion.
- Although a ULA is valid only in a limited scope, it also has a globally unique prefix (generated randomly, and therefore the conflict probability is very low).

### Common IPv6 Unicast Address — LLA

- A link-local address (LLA) is another type of IPv6 address with a limited application scope. The valid scope of an LLA is the local link, with the prefix of FE80::/10.

Diagram description: An LLA is shown split into fields: a 10-bit fixed prefix (`1111 1110 10`), a 54-bit field fixed at all 0s, and a 64-bit Interface ID. Four example devices are shown on the same local link (not connected to the IPv6 Internet), with addresses `FE80::1`, `FE80::2`, `FE80::3`, and `FE80::4`.

- An LLA is used for communication on a single link, such as during IPv6 SLAAC and IPv6 neighbor discovery.
- Data packets with the source or destination IPv6 address being an LLA are not forwarded out of the originating link. In other words, the valid scope of an LLA is the local link.
- Each IPv6 interface must have an LLA. Huawei devices support automatic generation and manual configuration of LLAs.

### IPv6 Multicast Address

- An IPv6 multicast address identifies a multicast group. Packets destined for a multicast address are sent to members in the multicast group. A multicast address is composed of the prefix (FF::/8) as well as the Flags, Scope, and Group ID fields.

Diagram description: An IPv6 multicast address is shown split into fields: an 8-bit fixed prefix (`11111111`), a 4-bit Flags field, a 4-bit Scope field, an 80-bit Reserved field (must be 0), and a 32-bit Group ID field.

- Flags: Indicates a permanent or temporary multicast address.
  - The value 0000 indicates a permanent multicast address.
  - The value 0001 indicates a temporary multicast address.
- Scope: Indicates the multicast group scope.
  - 0: reserved
  - 1: interface-local scope, which spans only a single interface on a node and is useful only for loopback transmission of multicast
  - 2: link-local scope (for example, FF02::1)
  - 5: site-local scope
  - 8: organization-local scope
  - E: global scope
  - F: reserved
- Group ID: Indicates a multicast group ID.

### IPv6 Multicast MAC Address

- The destination IP address of multicast IPv6 packets is a multicast IPv6 address, and the destination MAC address is a multicast MAC address.
- The first 16 bits of a multicast MAC address are 33:33, which is a MAC address prefix reserved for IPv6 multicast, and the last 32 bits are directly mapped from the last 32 bits of a multicast IPv6 address.

Diagram description: The 128-bit multicast IPv6 address `FF02:0000:0000:0000:0000:0000:0000:0001` has its last 32 bits (`0000:0001`) mapped directly into the last 32 bits of a 48-bit multicast MAC address, which is prefixed with the fixed `33:33` multicast MAC address prefix, producing the multicast MAC address `33:33:00:00:00:01`.

- When unicast IP packets are transmitted on an Ethernet, they use the MAC addresses of next hops as destination MAC addresses. However, when multicast packets are transmitted, their destination is a group of unspecific members but not a specific receiver. Therefore, they use a multicast MAC address as the destination MAC address.
- IPv4 multicast MAC address:
  - As defined by the IANA, the 24 most significant bits of an IPv4 multicast MAC address are 0x01005E, the 25th bit is 0, and the 23 least significant bits are mapped from those of an IPv4 multicast address.
  - The most significant four bits of an IPv4 multicast address are 1110, indicating the multicast identifier. However, only 23 bits of the least significant 28 bits are mapped to the IPv4 multicast MAC address. As a result, 5 bits of the IPv4 multicast address are lost. Therefore, 32 IPv4 multicast addresses are mapped to the same IPv4 multicast MAC address. During Layer 2 processing, a device may need to receive multicast data from multicast groups other than the local IPv4 multicast group. In this case, the redundant multicast data needs to be filtered by the upper layer.
- IPv6 multicast MAC address:
  - When an IPv6 multicast packet is sent on an Ethernet link, the corresponding MAC address is 0x3333-A-A-A-A, where A-A-A-A is directly mapped from the last 32 bits of a multicast IPv6 address.

### Solicited-Node Multicast Address

- If a node has an IPv6 unicast or anycast address, a solicited-node multicast address is generated for the node, and the node joins the corresponding multicast group. This address is used for neighbor discovery and duplicate address detection. A solicited-node multicast address is valid only on the local link.

Diagram description: A unicast IPv6 address (64-bit prefix + 64-bit Interface ID) has the last 24 bits of its Interface ID copied out. The corresponding solicited-node multicast address is constructed as the fixed 104-bit prefix `FF02:0000:0000:0000:0000:0001:FF` followed by those same copied 24 bits.

- An application scenario example of a solicited-node multicast address is as follows: In IPv6, ARP and broadcast addresses are canceled. When a device needs to request the MAC address corresponding to an IPv6 address, the device still needs to send a request packet, which is a multicast packet. The destination IPv6 address of the packet is the solicited-node multicast address corresponding to the target IPv6 unicast address. Because only the target node listens to the solicited-node multicast address, the multicast packet is received only by the target node, without affecting the network performance of other non-target nodes.

### Solicited-Node Multicast Address Example

- Before sending data to PC2, PC1 needs to obtain the MAC address of PC2. PC1 initiates a process similar to ARP resolution in IPv4. IPv6 uses ICMPv6 NS and NA messages to implement address resolution. The destination IPv6 address of NS messages is the solicited-node multicast address corresponding to the target IPv6 unicast address.

Diagram description: PC1 (MAC `000D-88F8-03B0`, IPv6 address `4000::D4B5:2A08:3AB8:F820`) sends an ICMPv6 Neighbor Solicitation (NS, Type 135) to PC2 (MAC `0013-7284-EFDC`, IPv6 address `4000::213:72FF:FE84:EFDC`). The NS message's fields:
```
ICMPv6 Type: 135 (NS)
Source Address: 4000::D4B5:2A08:3AB8:F820
Destination Address: FF02::1:FF84:EFDC
Target Address: 4000::213:72FF:FE84:EFDC
Source Link-layer (Option): 000D-88F8-03B0
```
PC2 replies with an ICMPv6 Neighbor Advertisement (NA, Type 136):
```
ICMPv6 Type: 136 (NA)
Source Address: 4000::213:72FF:FE84:EFDC
Destination Address: 4000::D4B5:2A08:3AB8:F820
Target Address: 4000::213:72FF:FE84:EFDC
Target Link-layer (Option): 0013-7284-EFDC
```

### IPv6 Anycast Address

- An anycast address identifies a group of network interfaces, which usually belong to different nodes. An anycast address can be used as the source or destination address of IPv6 packets.

Diagram description: Two web servers in different regions of the Internet both advertise the same anycast IPv6 address, `2001:0DB8:84C2::1`. PC1 accesses the web service and is routed along the shortest path to the nearer of the two servers; PC2, located elsewhere, accesses the same anycast address and is instead routed along the shortest path to the other, nearer server — illustrating that each client reaches the topologically closest instance of the service while using the identical destination address.

- The anycast process involves an anycast packet initiator and one or more responders.
  - An initiator of an anycast packet is usually a host requesting a service (for example, a web service).
  - The format of an anycast address is the same as that of a unicast address. A device, however, can send packets to multiple devices with the same anycast address.
- Anycast addresses have the following advantages:
  - Provide service redundancy. For example, a user can obtain the same service (for example, a web service) from multiple servers that use the same anycast address. These servers are all responders of anycast packets. If no anycast address is used and a server fails, the user needs to obtain the address of another server to establish communication again. If an anycast address is used and a server fails, the user can automatically communicate with another server that uses the same address, implementing service redundancy.
  - Provide better services. For example, a company deploys two servers — one in province A and the other in province B — to provide the same web service. Based on the optimal route selection rule, users in province A preferentially access the server deployed in province A when accessing the web service provided by the company. This increases the access speed, reduces the access delay, and greatly improves user experience.

### Comparison Between IPv6 and IPv4 Addresses

| | IPv4 | IPv6 |
|---|---|---|
| Address space | 2^32 | 2^128 |
| Representation | Dotted decimal notation | Colon hexadecimal notation |
| Address type | Unicast, multicast, and broadcast | Unicast, multicast, and anycast |
| | Class A, B, C, D, and E addresses | N/A |
| | Multicast address 224.0.0.0/4 | IPv6 multicast address FF00::/8 |
| | Broadcast address | N/A |
| | Unspecified address 0.0.0.0/32 | Unspecified address ::/128 |
| Others | Loopback address 127.0.0.0/8 | Loopback address ::1/128 |
| | Public IP address | Global unicast address |
| | Private IP addresses 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16 | Unique local address FD00::/8 |
| | APIPA address 169.254.0.0/16 | Link-local address FE80::/10 |

## IPv6 Address Planning Example

### Contents (section marker)

1. IPv6 Overview
2. IPv6 Address Introduction
   - IPv6 Address Overview
   - IPv6 Address Types
   - **IPv6 Address Planning Example**
3. IPv6 Packet Structure
4. Basic IPv6 Configuration

### IPv6 Address Planning Example

Diagram description: An IPv6 address is planned across labeled bit-field blocks: a fixed M-bit Network prefix, then a 3-bit "Attribute block" field, a 3-bit "Network" field, a 6-bit "Region" field, an N-bit "Allocable address" field, and finally a 64-bit Interface ID. The Attribute-block field's 3 bits are further broken down into 8 possible values (000 through 111), mapped as: 000/001 = Network address, 01x = Network address, 0 = Reserved, 011 = Reserved, and 100/101/110/111 = User address (four separate user-address ranges) — illustrating how a small number of leading bits in the subnet portion of the address can be used to distinguish network-infrastructure addresses from reserved space and from multiple pools of user addresses.

- N (Attribute block): identifies allocable addresses.
- Network: identifies a regional network, for example, a branch or functional network.
- Region: identifies a backbone network that is independently managed.
- Allocable address: identifies a network, service platform, user address, and other information.
- Fixed network prefix obtained from an address allocation organization.
  - Network addresses: including loopback, interconnection, and management addresses of network devices.
  - Service platform address: address allocated to a platform server.
  - User addresses: addresses allocated by services to users.
  - Reserved: reserved for future extension.
- Address planning and design suggestions:
  - Based on the obtained address prefix, determine the number of functional blocks (for example, 3+3+6+N in the figure) into which the subnet address is divided, and determine the meaning of each functional block and the number of bits occupied by it to avoid address waste.

### Suggestions on IPv6 Address Use

**Key Points of Address Planning:**
- Generally, the IPv6 addresses obtained by an ISP from an address allocation organization have a prefix length of at least /32. The prefix length of the IPv6 addresses obtained by an enterprise user is usually /48.
- Although IPv6 addresses have a large space, they must still be properly planned during network planning.
- Ensure that each IPv6 address is unique on the entire network (except for some special applications, such as anycast).
- Ensure the continuity, aggregability, and scalability of IPv6 addresses.
- Service address: Plan appropriate bits in an IPv6 address to carry service, VLAN, or location information, facilitating route planning and QoS deployment.
- User address: Reserve consecutive address segments for users with different service types. Determine user types and distribution areas based on specific bits.
- It is recommended that a prefix length of /64 be allocated to a terminal network segment (such as user hosts and servers).
- It is recommended that a prefix length of /127 be allocated to P2P links.
- It is recommended that a prefix length of /128 be allocated to loopback interfaces.

**Address Planning Practice** (illustrated examples):
- A /128 IPv6 address is allocated to a loopback interface: `2031:0:A0::1/128`
- A prefix length of /127 is allocated to P2P links, with uplink and downlink interconnection addresses kept consecutive to facilitate aggregation: `2031:0:1::/127`
- A VLANIF interface uses a /64 IPv6 address: `2031:0:130F::FFFF/64`
- A /64 IPv6 address is allocated to a terminal network segment (such as hosts and servers): `2031:0:130F::/64`

## 3. IPv6 Packet Structure

### Contents (section marker)

1. IPv6 Overview
2. IPv6 Address Introduction
3. IPv6 Packet Structure
4. Basic IPv6 Configuration

### IPv6 Packet Composition

Diagram description: An IPv6 packet is shown composed of three sequential blocks: "IPv6 header," "Extension header(s)," and "Upper-layer protocol data unit," with the extension header(s) and upper-layer protocol data unit together forming the "Payload" of the IPv6 packet.

- An IPv6 packet is generally composed of the following parts:
  - IPv6 header: provides basic packet forwarding information. Routers use the information to forward most packets.
  - Extension headers: provide extended packet forwarding information, such as segmentation and encryption. This part is optional and does not need to be processed by each router. A sender adds one or more extension headers only when a router or destination node needs to perform special processing.
  - Upper-layer protocol data unit: is generally composed of an upper-layer protocol header and its payload. This part is similar to the upper-layer protocol data unit in an IPv4 packet.
- As shown in the figure, an IPv6 packet is composed of the following parts:
  - **IPv6 header:** Each IPv6 packet must contain a header with a fixed length of 40 bytes. The IPv6 header provides basic packet forwarding information, which is parsed by all routers on a forwarding path.
  - **Extension headers:** An IPv6 extension header is an optional header that may follow an IPv6 header. An IPv6 packet can contain no extension header, or it can contain one or more extension headers with different lengths. The IPv6 header and extension headers replace the IPv4 header and its options. The extension headers enhance IPv6 significantly. Unlike the options in an IPv4 header, the maximum length of an extension header is not limited. Therefore, an extension header can contain all the extension data required for IPv6 communication. The extended packet forwarding information provided by an extension header is generally parsed by the destination router but not all routers on a path.
  - **Upper-layer protocol data unit:** is composed of the upper-layer protocol header and its payload, which can be an ICMPv6 packet, a TCP packet, or a UDP packet.

### IPv6 Header

Diagram description: A side-by-side comparison of the IPv4 header (20 to 60 bytes, variable length) and the IPv6 header (fixed 40 bytes). The IPv4 header's fields are shown as: Version, IHL, ToS, Total Length, Identification, Flags, Fragment Offset, TTL, Protocol, Header Checksum, Source Address, Destination Address, and Options+Padding. The IPv6 header's fields are shown as: Version, Traffic Class, Flow Label, Payload Length, Next Header, Hop Limit, Source Address, and Destination Address. Fields present in IPv4 but removed in IPv6 (Header Checksum, the fragmentation-related fields for intermediate nodes, Options/Padding) are marked "Removed"; fields that map to a differently-named IPv6 equivalent (e.g., Total Length → Payload Length, TTL → Hop Limit, Protocol → Next Header) are marked "Name/Location changed"; and the new Flow Label field is marked "New."

**Improvements of an IPv6 Header over an IPv4 Header:**
- The checksum at Layer 3 is removed. The checksums at Layer 2 and Layer 4 have been provided in the protocol stack. Therefore, the checksum at Layer 3 is removed to save router processing resources.
- The fragmentation function on the intermediate node is removed. Fragments are processed only on the source node that generates data but not on the intermediate node, preventing the intermediate node from consuming a large amount of CPU resources to process fragments.
- The fixed-length IPv6 header is defined. This facilitates fast hardware processing and improves the forwarding efficiency of routers.
- Security options are supported. IPv6 provides optimal support for IPsec, allowing the upper-layer protocols to omit many security options.
- The Flow Label field is added. This improves QoS efficiency.

- The IPv6 header is also called a fixed header, which contains eight fields. The total length of the fixed header is 40 bytes. The eight fields are Version, Traffic Class, Flow Label, Payload Length, Next Header, Hop Limit, Source Address, and Destination Address.
  - **Version:** This field indicates the version of IP and its value is 6. The length is 4 bits.
  - **Traffic Class:** This field indicates the class or priority of an IPv6 packet and its function is similar to that of the ToS field in an IPv4 header. The length is 8 bits.
  - **Flow Label:** This field is used by a source to label sequences of packets for which it requests special handling by IPv6 routers. The length is 20 bits. Generally, a flow can be determined based on the source IPv6 address, destination IPv6 address, and flow label.
  - **Payload Length:** This field indicates the length of the IPv6 payload. The payload refers to the extension header and upper-layer protocol data unit that follow the IPv6 header. The length is 16 bits. If the payload length exceeds its maximum value of 65535 bytes, the field is set to 0, and the Jumbo Payload option in the Hop-by-Hop Options header is used to express the actual payload length.
  - **Next Header:** This field indicates the type of the first extension header (if any) that follows the IPv6 header or the protocol type in the upper-layer protocol data unit. The length is 8 bits.
  - **Hop Limit:** This field defines the maximum number of hops that an IP packet can pass through, and its function is similar to that of the TTL field in an IPv4 packet. The value is decreased by 1 each time an IP packet passes through a router. The packet is discarded if Hop Limit is decreased to zero. The length is 8 bits.
  - **Source Address:** This field indicates the address of a sender and its length is 128 bits.
  - **Destination Address:** This field indicates the address of a receiver and its length is 128 bits.

### IPv6 Extension Headers (1)

Diagram description: A packet layout showing the fixed IPv6 header (Version, Traffic Class, Flow Label, Payload Length, Next Header, Hop Limit, Source Address, Destination Address) followed by two chained extension headers, each with its own Next Header field, Extension Header Length field, and extension header data, followed finally by the Payload (such as TCP/UDP packets). Each extension header's Next Header field points to the type of the following header, chaining them together.

- Next Header: 8 bits long. This field is similar to the Next Header field in the IPv6 header, indicating the next extension header (if any) or upper-layer protocol type.
- Extension Header Length: 8 bits long. This field indicates the extension header length excluding the Next Header field.
- Extension Header Data: variable length. This field includes a series of options and the padding field.
- The Options field in an IPv4 header is placed in extension headers of an IPv6 packet. An IPv6 extension header is an optional header that may follow an IPv6 header. Why is an extension header designed in IPv6? Each intermediate router must check whether the options contained in the IPv4 header exist. If the options exist, the intermediate router must process them. This reduces the efficiency for routers to forward IPv4 packets. Therefore, the Options field is placed in extension headers in IPv6 to resolve this issue. In this case, the intermediate router does not need to process each possible option, accelerating packet processing and improving forwarding performance.
- A typical IPv6 packet does not contain any extension header. A sender adds one or more extension headers only when a router or destination node needs to perform special processing. Unlike IPv4, IPv6 has variable-length extension headers, which are not limited to 40 bytes, to facilitate further extension. To improve extension header processing efficiency and transport protocol performance, IPv6 requires that the extension header length be an integral multiple of 8 bytes.

### IPv6 Extension Headers (2)

- Conventions for extension headers:
  - Extension headers must appear in the order shown below.
  - Each extension header can appear only once, except for the Destination Options header that can appear at most twice (once before the Routing header and once before the upper-layer header). If there is no Routing header, the Destination Options header can appear only once.

Diagram description: A vertically stacked list showing the required order of IPv6 extension headers when multiple are present: Hop-by-Hop Options header, Destination Options header, Routing header, Fragment header, Authentication header, Encapsulating Security Payload header, Destination Options header (second occurrence), Upper-layer header. Below this, three example packet layouts illustrate the Next Header chaining: (1) IPv6 Header [Next Header = 6] → TCP Segment (TCP), directly, with no extension headers; (2) IPv6 Header [Next Header = 43] → Routing Header [Next Header = 6] → TCP Segment (TCP); (3) IPv6 Header [Next Header = 43] → Routing Header [Next Header = 44] → Fragment Header [Next Header = 6] → TCP Segment (TCP).

- Currently, RFC 2460 defines the following six IPv6 extension headers:
  - Hop-by-Hop Options header: is used to carry multiple options such as the router alarm option that must be examined by every node along a packet's delivery path.
  - Destination Options header: is used to carry multiple options such as the home address option of mobile IPv6 that need to be examined only by a packet's destination node.
  - Routing header: is used by an IPv6 source to list all intermediate nodes to be "visited" on the way to a packet's destination. This function is very similar to IPv4's Loose Source and Record Route option. The destination address in the IPv6 header is not the final destination address of a packet but the first address listed in the Routing header.
  - Fragment header: is used by an IPv6 source to send a packet that is too large to fit in the MTU of the path to its destination. The Fragment header is processed only by the destination node.
  - Authentication header: is used by IPsec and processed only by the destination node.
  - Encapsulating Security Payload header: is used by IPsec and processed only by the destination node.
- The Hop-by-Hop Options and Destination Options headers provide option functions and support extensibility (such as mobility). Options use the TLV mode.
- If there is no extension header in a packet (that is, the packet contains only the IPv6 header and upper-layer protocol data unit), the value of the Next Header field in the IPv6 header specifies the upper-layer protocol type. If the value of the Next Header field in the IPv6 header is 6, the upper-layer protocol is TCP. If there is one extension header in a packet, the value of the Next Header field in the IPv6 header specifies the extension header type. For example, if the value of the Next Header field is 43, the extension header is a Routing header. The value of the Next Header field in the extension header specifies the upper-layer protocol type. If there are multiple extension headers in a packet, the value of the Next Header field in each extension header specifies the type of the next extension header, and the value of the Next Header field in the last extension header specifies the upper-layer protocol type.

## 4. Basic IPv6 Configuration

### Contents (section marker)

1. IPv6 Overview
2. IPv6 Address Introduction
3. IPv6 Packet Structure
4. Basic IPv6 Configuration

### Configuration (1)

1. Enable IPv6 packet forwarding on a device.
```
<Huawei> system-view
[Huawei] ipv6
```
2. Enable IPv6 on an interface.
```
[Huawei] interface interface-type interface-number
[Huawei-GigabitEthernet1/0/0] ipv6 enable
```
3. Configure global unicast IPv6 addresses.
```
[Huawei-GigabitEthernet1/0/0] ipv6 address { ipv6-address prefix-length | ipv6-address/prefix-length }
```

A maximum of 10 global unicast addresses can be configured on each interface.

### Configuration (2)

1. Enable OSPFv3 on a device.
```
<Huawei> system-view
[Huawei] ospfv3 [ process-id ]
```

OSPFv3 supports multi-process. Multiple OSPFv3 processes running on a router are differentiated by process IDs. You can set an OSPFv3 process ID when enabling OSPFv3. The process ID is only locally valid and does not affect packet exchange with other routers.

2. Configure a router ID for an OSPFv3 process.
```
[Huawei-ospfv3-1] router-id router-id
```

A router ID must be manually configured, and OSPFv3 cannot run properly without a router ID.

3. Enable an OSPFv3 process on an interface and specify an area to which the process belongs.
```
[Huawei] interface interface-type interface-number
[Huawei-GigabitEthernet1/0/0] ospfv3 process-id area area-id
```

### Case: Configuring a Dual-Stack Network (1)

Diagram description: A topology with PC1 — R1 — R2 — PC2. R1's interface GE1/0/0 (toward R2) is addressed 10.0.12.1/24 and 2001:DB8:1::1/64; R2's corresponding GE1/0/0 is 10.0.12.2/24 and 2001:DB8:1::2/64. R1's GE2/0/0 (toward PC1) is 192.168.1.254/24 and 2001:DB8:2::1/64; PC1 is 192.168.1.1/24 and 2001:DB8:2::2/64. R2's GE2/0/0 (toward PC2) is 192.168.3.254/24 and 2001:DB8:3::1/64; PC2 is 192.168.3.1/24 and 2001:DB8:3::2/64.

Configuration requirements:
- Configure interface IP addresses on R1 and R2.

1. Enable IPv6 globally and on related interfaces on R1 and R2. The following uses R1 as an example.
```
[R1] ipv6
[R1] interface GigabitEthernet 1/0/0
[R1-GigabitEthernet1/0/0] ipv6 enable
[R1] interface GigabitEthernet 2/0/0
[R1-GigabitEthernet2/0/0] ipv6 enable
```
2. Configure global unicast IPv4 and IPv6 addresses on the interfaces of the PCs, R1, and R2. The following uses R1 as an example.
```
[R1] interface GigabitEthernet 1/0/0
[R1-GigabitEthernet1/0/0] ip address 10.0.12.1 24
[R1-GigabitEthernet1/0/0] ipv6 address 2001:DB8:1::1 64
[R1] interface GigabitEthernet 2/0/0
[R1-GigabitEthernet2/0/0] ip address 192.168.1.254 24
[R1-GigabitEthernet2/0/0] ipv6 address 2001:DB8:2::1 64
```

### Case: Configuring a Dual-Stack Network (2)

Configuration requirements:
- Configure interface IP addresses on R1 and R2.
- Configure OSPFv2 and OSPFv3 on R1 and R2 respectively to implement dual-stack communication between PC1 and PC2.

Configure OSPFv2 on R1 and R2 so that PC1 and PC2 can communicate through the IPv4 network.
```
[R1] ospf 1 router-id 10.0.1.1
[R1-ospf-1] area 0
[R1-ospf-1-area-0.0.0.0] network 10.0.12.0 0.0.0.255
[R1-ospf-1-area-0.0.0.0] network 192.168.1.0 0.0.0.255
[R1-ospf-1-area-0.0.0.0] quit
[R1-ospf-1]

[R2] ospf 1 router-id 10.0.2.2
[R2-ospf-1] area 0
[R2-ospf-1-area-0.0.0.0] network 10.0.12.0 0.0.0.255
[R2-ospf-1-area-0.0.0.0] network 192.168.3.0 0.0.0.255
[R2-ospf-1-area-0.0.0.0] quit
[R2-ospf-1]
```

### Case: Configuring a Dual-Stack Network (3)

Configuration requirements:
- Configure interface IP addresses on R1 and R2.
- Configure OSPFv2 and OSPFv3 on R1 and R2 respectively to implement dual-stack communication between PC1 and PC2.

Configure OSPFv3 on R1 and R2 so that PC1 and PC2 can communicate through the IPv6 network.
```
[R1] ospfv3
[R1-ospfv3-1] router-id 10.0.1.1
[R1-ospfv3-1] quit
[R1] interface gigabitethernet1/0/0
[R1-gigabitethernet1/0/0] ospfv3 1 area 0
[R1] interface gigabitethernet2/0/0
[R1-gigabitethernet2/0/0] ospfv3 1 area 0

[R2] ospfv3
[R2-ospfv3-1] router-id 10.0.2.2
[R2-ospfv3-1] quit
[R2] interface gigabitethernet1/0/0
[R2-gigabitethernet1/0/0] ospfv3 1 area 0
[R2] interface gigabitethernet2/0/0
[R2-gigabitethernet2/0/0] ospfv3 1 area 0
```

### Verifying the Configuration

Ping the IPv6 address of PC2 (2001:DB8:2::2, the address on R1's PC1-facing side per the topology) from R1 (pinging the IPv4 address is omitted):
```
<R1> ping ipv6 2001:db8:2::2
  PING 2001:db8:2::2 : 56 data bytes, press CTRL_C to break
  Reply from 2001:DB8:2::2
  bytes=56 Sequence=1 hop limit=255 time = 40 ms
  Reply from 2001:DB8:2::2
  bytes=56 Sequence=2 hop limit=255 time = 10 ms
```

Ping the IPv6 address of PC2 from PC1 (pinging the IPv4 address is omitted):
```
PC1>ping 2001:db8:3::2
  Ping 2001:db8:3::2: 32 data bytes, Press Ctrl_C to break
  From 2001:db8:3::2: bytes=32 seq=1 hop limit=64 time<1 ms
  From 2001:db8:3::2: bytes=32 seq=2 hop limit=64 time=16 ms
  From 2001:db8:3::2: bytes=32 seq=3 hop limit=64 time=16 ms
  From 2001:db8:3::2: bytes=32 seq=4 hop limit=64 time<1 ms
```

*(Note: the source slide's OCR rendered these addresses as "2001:db88:2::2" and "2001:db88:3::2" — with a doubled "8". Every other occurrence of this prefix throughout the deck, including in the topology diagram on this same slide, consistently uses "2001:DB8" with a single "8". The doubled "88" is therefore treated here as a scanning/OCR artifact rather than a genuine source typo, and has been corrected to "db8" for consistency. Recommend a visual double-check of the original slide image if exact confirmation is needed.)*

## Quiz

1. (Essay) What are the advantages of IPv6 over IPv4?
2. (Essay) What are the differences of an IPv6 header from an IPv4 header?

**Answers:**

1. Unlimited address space, hierarchical address structure, plug-and-play, simplified packet header, security features, mobility, and enhanced QoS features.
2. Differences between IPv6 header and IPv4 header:
   - The packet format of IPv6 header + extension headers is used.
   - The checksum at Layer 3 is removed. The checksums at Layer 2 and Layer 4 are sufficiently robust, and therefore the checksum at Layer 3 is removed to save router processing resources.
   - The fragmentation function on the intermediate node is removed. Fragments are processed only on the source node that generates data but not on the intermediate router, preventing the intermediate router from consuming a large amount of CPU resources to process fragments.
   - The fixed-length IPv6 header is defined to facilitate fast hardware processing and improve the forwarding efficiency of routers.
   - Security options are supported. IPv6 provides optimal support for IPsec, allowing the upper-layer protocols to omit many security options.
   - The Flow Label field is added to improve QoS efficiency.

## Summary

- As a next-generation Internet protocol, IPv6 has more advantages than IPv4 and can meet service development requirements.
- IPv6 has a large address space. It also simplifies packet headers, improving the packet forwarding efficiency of routers. IPv6 addresses are easy to divide and plan, facilitating route aggregation. In addition, IPv6 supports plug-and-play and enhances QoS.
- The dynamic routing protocols commonly used on IPv4 networks can still be used on IPv6 networks through version upgrade (OSPFv3) or protocol extension (IS-IS for IPv6 or BGP4+).

---

*(This file ends here, at document page 935 — the "Thank you" slide on document page 936 is a standard closing slide with no course-specific content, and is omitted per the H2/H3 structural rule of this transcription; let me know if you'd like it included as a final line.)*

