# BGP EVPN Basics

## Foreword

- Standard BGP-4 supports only IPv4 unicast addresses. To support more network layer protocols, Multiprotocol Extensions for BGP-4 (MP-BGP) (RFC 4760) was proposed as an extension to BGP-4 to allow different types of address families to be distributed in BGP at the same time. The address families include IPv4 multicast, IPv6, L3VPN, and Ethernet Virtual Private Network (EVPN) address families.
- With the development and commercial use of software-defined networking (SDN), EVPN plays an important role in various solutions, covering all scenarios, including campus networks, data centers, IP WAN transport networks, and software-defined networking in a wide area network (SD-WAN).
- This course describes the concept of MP-BGP, development history of EVPN, common EVPN route types, and EVPN usage scenarios.

## Objectives

On completion of this course, you will be able to:
- Understand basic MP-BGP concepts.
- Understand the origin of EVPN.
- Understand common EVPN route types.
- Understand typical EVPN usage scenarios.

## Contents

1. MP-BGP
2. EVPN

## 1. MP-BGP

### MP-BGP

- As defined in RFC 4760, MP-BGP is used to extend BGP-4 to allow BGP to carry multiple network layer protocols, such as IPv6, L3VPN, and EVPN. This extension has good backward compatibility. That is, an MP-BGP-capable router can interact with a router that supports only BGP-4.

Diagram description: A chain of three BGP speakers — R1, R2, R3 — connected in sequence. R1 and R2 exchange only IPv4 (labeled "BGP-4" beneath their link). R2 and R3 exchange a stack of address families — EVPN, L3VPN, IPv6, and IPv4 — labeled "MP-BGP" beneath their link. This illustrates that R2, being MP-BGP-capable, can speak plain BGP-4 to R1 while also speaking full MP-BGP (carrying EVPN, L3VPN, IPv6, IPv4) to R3.

Note: https://datatracker.ietf.org/doc/rfc4760/

### BGP-4 Extensions

- BGP-4 has three IPv4-specific pieces of information: NEXT_HOP, AGGREGATOR, and IPv4 network layer reachable information (NLRI). To support multiple network layer protocols, BGP-4 has to provide the following abilities:
  - Ability of associating network layer protocols with next-hop information
  - Ability of associating network layer protocols with NLRIs
- The two abilities are collectively referred to as the address family (AF) defined by the Internet digital distribution agency (IANA).
- To implement forward compatibility, MP-BGP adds two new attributes: MP_REACH_NLRI and MP_UNREACH_NLRI, which are used to indicate reachable and unreachable destinations, respectively. The two attributes are optional non-transitive.

Diagram description: Two side-by-side boxes compare the structure of a BGP-4 Update message versus an MP-BGP Update message. The BGP-4 Update message box shows: Path attributes (containing NEXT_HOP, AGGREGATOR...), followed by NLRI (IPv4) containing X.X.X.X/X. The MP-BGP Update message box shows: Path attributes (containing the new MP_REACH_NLRI field, which itself contains NEXT_HOP and NLRI).

- According to BGP-4, NEXT_HOP and AGGREGATOR fields are contained in Path attributes of IPv4, and the IPv4 NLRI carries IPv4 routing entries.
- The Path attributes field is added in MP-BGP. MP_REACH_NLRI is a new field of path attributes. The NEXT_HOP and NLRI fields of the corresponding network layer protocol and the NLRI belong to MP_REACH_NLRI.

### MP_REACH_NLRI

- MP_REACH_NLRI is carried in a BGP Update message and provides the following functions:
  - Advertises reachable routes to BGP peers.
  - Advertises the next-hop address of a reachable route to a BGP peer.
- It contains the following fields:

| MP_REACH_NLRI Format | Field Description |
|------------------------|--------------------|
| Address Family Identifier (2 octets) | Network layer protocol. Value 2 indicates IPv6. |
| Subsequent Address Family Identifier (1 octet) | This field is used together with address family identifier (AFI). Value 1 indicates unicast. Therefore, when the values of AFI and SAFI are 2 and 1, it indicates IPv6 unicast. |
| Length of Next Hop Network Address (1 octet) | Length of a next-hop IP address. |
| Network Address of Next Hop (variable) | Next-hop address. The format is determined by the AFI and SAFI. |
| Reserved (1 octet) | All 0s. |
| Network Layer Reachability Information (variable) | The length of this field is variable. This field can contain reachable routes. |

- In the SAFI field, value 1 indicates unicast, and value 2 indicates multicast. The value is allocated by the IANA. The allocation rules are defined in RFC 2434 (titled "Guidelines for Writing an IANA Considerations Section in RFCs").
- In this section, the AFI of EVPN is 25 (L2VPN) and the SAFI is 70 (EVPN).

### MP_UNREACH_NLRI

- MP_UNREACH_NLRI is carried in BGP Update messages to withdraw unreachable routes.
- It contains the following fields:

| MP_UNREACH_NLRI Format | Field Description |
|--------------------------|--------------------|
| Address Family Identifier (2 octets) | Network layer protocol. Value 2 indicates IPv6. |
| Subsequent Address Family Identifier (1 octet) | This field is used together with the AFI. Value 1 indicates unicast, and value 2 indicates IPv6 unicast. |
| Withdrawn Routes (variable) | The length of this field is variable. This field lists the routes that need to be withdrawn. The format of this field is determined by the AF and SAFI. |

- The AFI of EVPN is 25 (L2VPN) and the subsequent address family identifier (SAFI) is 70 (EVPN).

## Contents

1. MP-BGP
2. EVPN
   - EVPN Overview
   - Common EVPN Routes
   - Typical EVPN Usage Scenarios

## 2. EVPN

### EVPN Overview

#### MPLS Overview

- Multiprotocol Label Switching (MPLS) is located between the data link layer and the network layer in the TCP/IP protocol stack. An MPLS header is added between the two layers. Packets are forwarded based on the MPLS header. The MPLS header is also called the MPLS label.
- MPLS replaces IP forwarding with label switching to implement label-based rapid forwarding.

Diagram description: An IP network cloud sends traffic destined for 3.3.3.3, forwarded initially via IP address-based forwarding. It enters an "MPLS domain" containing a chain of three routers. Between the first and second router, traffic is forwarded using MPLS label-based forwarding (with one MPLS label). Between the second and third router, traffic is again forwarded using MPLS label-based forwarding (with a different MPLS label, shown in a different color). After exiting the MPLS domain, traffic reverts to IP address-based forwarding into an IP network 3.3.3.0/24. A packet structure legend at the bottom right shows a packet composed of an Ethernet Header, an MPLS Header, and an IP Packet.

- MPLS originates from IPv4 and its core technologies can be extended to multiple network protocols, including IPv6, Internet Packet Exchange (IPX), Appletalk, DECnet and Connectionless Network Protocol (CLNP). "Multiprotocol" in MPLS indicates that multiple network protocols are supported.
- MPLS replaces IP forwarding with label switching. A label is a short and fixed-length connection identifier that has only local significance. It is similar to the virtual path identifier (VPI)/virtual channel identifier (VCI) of Asynchronous Transfer Mode (ATM) and the data link connection identifier (DLCI) of Frame Relay.
- MPLS domain: An MPLS domain consists of a series of consecutive network devices that run MPLS.

#### VPLS Overview

- Virtual private LAN service (VPLS) is an Ethernet-based L2VPN technology. VPLS provides services similar to LAN services on an MPLS network and allows users to access the network from different locations.

Diagram description: Two enterprises are shown spanning a shared MPLS network via two PE routers, PE1 and PE2. Enterprise A has CE1 (address 11.1.1.1) connected to PE1, and CE2 (address 11.1.1.2) connected to PE2; a label states "CE1 and CE2 of enterprise A belong to the same Layer 2 network." Enterprise B has CE3 (address 12.1.1.3) connected to PE1, and CE4 (address 12.1.1.4) connected to PE2; a label states "CE3 and CE4 of enterprise B belong to the same Layer 2 network."

#### Traditional L2VPN

- Traditional L2VPN services, such as VPLS, provide Layer 2 connections between remote sites. An L2VPN network is built and functions like a Layer 2 switch to transparently transmit Ethernet packets. In this example, PE1 and PE2 form a VPLS network to transparently transmit VLAN traffic between CE1 and CE2.
- In a traditional L2VPN, remote MAC addresses are learned through ARP broadcast flooding, and therefore, PEs need to carry broadcast traffic. Broadcast consumes a large amount of interface bandwidth, which is a typical issue of traditional L2VPN.

Diagram description: CE1 (with MAC1) sends VLAN 20 and VLAN 10 traffic into PE1. PE1 and PE2 form a VPLS network, labeled as functioning like a "Layer 2 switch." PE2 forwards VLAN 20 and VLAN 10 traffic out to CE2 (with MAC2).

- VPLS does not support all-active access or load balancing and implements slow fault convergence. For details, see materials of the HCIE-HCIE-Datacom Ethernet VPN and RFC 7209 titled "Requirements for Ethernet VPN (EVPN)."

#### Emergence of EVPN

- With new technologies and scenarios emerging, VPLS cannot meet the requirements of L2VPN. The industry has reviewed the requirements for Ethernet VPN (RFC 7209) and proposed a new solution, that is, EVPN.
- EVPN was first defined in RFC 7432. EVPN introduces the control plane to better control MAC address learning.
- EVPN uses MP-BGP on the control plane and supports MPLS label switched paths (LSPs) or IP/Generic Routing Encapsulation (GRE) tunneling on the data plane.

Diagram description: A two-row table shows the EVPN architecture split into Control plane (EVPN using MP-BGP) and Data plane (Label switching (MPLS) or IP/GRE tunnel). Alongside, two routers R1 (with MAC1) and R2 (with MAC2) are connected; step 1 shows "EVPN on the control plane learns the peer MAC address," and step 2 shows "The data plane forwards data."

Note: 
- https://datatracker.ietf.org/doc/rfc7209/
- https://datatracker.ietf.org/doc/rfc7432/

#### Advantages of EVPN

- EVPN introduces the control plane to learn MAC and IP addresses to guide data forwarding, implementing forwarding-control separation.
- EVPN resolves typical problems in traditional L2VPNs and offers more benefits, such as active-active, rapid convergence, and simplified O&M.

Diagram description: Two CEs (CE1 and CE2) connect into a mesh of four PE routers (PE1, PE2, PE3, PE4) over an "IP or MPLS" core. CE1 connects to both PE1 and PE2; CE2 connects to both PE3 and PE4. All four PEs are interconnected. A callout above states: "Control plane: PEs exchange BGP EVPN packets to transmit MAC and IP addresses." A callout below states: "Data plane: Data forwarding paths are formed by IP tunnels or MPLS label forwarding paths. The data plane forwards data and does not need to broadcast packets to learn MAC addresses." A list on the right enumerates "Other advantages of EVPN": CEs can access PEs in all-active mode; Automatic discovery of PE members; Loop prevention; Broadcast traffic optimization; Support for Equal-Cost Multi-Path (ECMP).

- For more details, see the *HCIE-Datacom Ethernet VPN*.

## Contents

1. MP-BGP
2. EVPN
   - EVPN Overview
   - Common EVPN Routes
   - Typical EVPN Usage Scenarios

### Common EVPN Routes

#### EVPN NLRI

- EVPN defines a new type of BGP NLRI, known as EVPN NLRI, to carry all EVPN routes.
- EVPN NLRI is a new extension to MP-BGP. It is included in MP_REACH_NLRI. For the EVPN NLRI, the AFI is 25 and the SAFI is 70.

Diagram description: Two side-by-side field tables. The left table shows the general MP_REACH_NLRI format: Address Family Identifier (2 octets), Subsequent Address Family Identifier (1 octet), Length of Next Hop Network Address (1 octet), Network Address of Next Hop (variable), Reserved (1 octet), Network Layer Reachability Information (variable) — with the last field highlighted. The right table shows the MP_REACH_NLRI of BGP EVPN specifically: AFI: 25, SAFI: 70, Length of a next-hop IP address, Next-hop IP address in an EVPN route, All 0s, EVPN NLRI (highlighted, corresponding to the highlighted NLRI field on the left).

#### EVPN Route

- The EVPN NLRI format uses the Type-Length-Value (TLV) structure, making packets highly flexible and scalable.
  - Route Type field: defines different EVPN routes. RFC 7432 defines four types of routes.
  - Length field: defines the length of a field.
  - Route Type Specific field: contains fields of a particular route type.

Diagram description: The EVPN NLRI format is shown as three stacked fields: Route Type (1 byte), Length (1 byte), Route Type Specific (variable). To the right, a bracketed list shows the four common EVPN routes defined in the Route Type field: 1 Ethernet A-D Route, 2 MAC Advertisement Route, 3 Inclusive Multicast Route, 4 Ethernet Segment Route.

- The NLRI field in the MP_REACH_NLRI/MP_UNREACH_NLRI attribute contains the EVPN NLRI (encoded as specified above).
- The EVPN NLRI is carried in BGP [RFC4271] using BGP Multiprotocol Extensions [RFC4760] with an Address Family Identifier (AFI) of 25 (L2VPN) and a Subsequent Address Family Identifier (SAFI) of 70 (EVPN). The NLRI field in the MP_REACH_NLRI/MP_UNREACH_NLRI attribute contains the EVPN NLRI (encoded as specified above).
- In order for two BGP speakers to exchange labeled EVPN NLRI, they must use BGP Capabilities Advertisements to ensure that they both are capable of properly processing such NLRI. This is done as specified in [RFC4760], by using capability code 1 (multiprotocol BGP) with an AFI of 25 (L2VPN) and a SAFI of 70 (EVPN).

#### More Types of EVPN Routes and Their Functions

- EVPN is not limited to L2VPN applications. With the increase of EVPN route types, more applications, such as L3VPN, are supported.

| Type of Route | Function | RFC |
|----------------|----------|-----|
| (Type 1) Ethernet A-D Route | • Aliasing<br>• MAC address batch withdraw<br>• All-active flag<br>• ESI label advertisement | RFC 7432 |
| (Type 2) MAC/IP Advertisement Route | • MAC address learning notification<br>• MAC/IP binding<br>• MAC mobility | RFC 7432 |
| (Type 3) Inclusive Multicast Route | Automatic discovery of multicast tunnel endpoints and multicast types | RFC 7432 |
| (Type 4) Ethernet Segment Route | Automatic discovery of ES members<br>DF election | RFC 7432 |
| (Type 5) IP Prefix Route | IP prefix advertisement (support for L3VPN) | draft-ietf-bess-evpn-prefix-advertisement |

- The Type 5 route (IP prefix route) related standard is in the draft phase, in draft-ietf-bess-evpn-prefix-advertisement.

#### EVPN Protocol Standards

Diagram description: A two-row grid separates EVPN protocol standards into Control plane and Data plane, further grouped by underlying technology/scenario columns (MPLS, SR-MPLS, VXLAN, GRE/IPsec), and mapped to network scenario labels beneath (IP WAN transport network; Data center and campus networks; SD-WAN).

**Control plane row:**
- RFC 7432 — "BGP MPLS-Based Ethernet VPN" (the basic standard, spanning the general control-plane box)
- RFC 8365 — "A Network Virtualization Overlay Solution using EVPN"
- draft-ietf-bess-evpn-inter-subnet-forwarding — "Integrated Routing and Bridging in EVPN"
- IP Prefix Advertisement in EVPN — draft-ietf-bess-evpn-prefix-advertisement
- BGP SD-WAN — draft-dunbar-idr-sdwan-port-safi

**Data plane row (aligned under corresponding technology columns):**
- MPLS column: RFC 7432 (BGP MPLS-Based Ethernet VPN)
- SR-MPLS column: RFC 7623 (Provider Backbone Bridging Combined with Ethernet VPN); RFC 8663 (MPLS Segment Routing over IP)
- VXLAN column: RFC 7348 (Virtual eXtensible Local Area Network)
- GRE/IPsec column: ExtGRE (Huawei proprietary)

**Scenario labels beneath data plane columns:** MPLS and SR-MPLS columns map to "IP WAN transport network"; VXLAN column maps to "Data center and campus networks"; GRE/IPsec column maps to "SD-WAN".

## Contents

1. MP-BGP
2. EVPN
   - EVPN Overview
   - Common EVPN Routes
   - Typical EVPN Usage Scenarios

### Typical EVPN Usage Scenarios

#### EVPN on an IP WAN Transport Network

Diagram description: A table maps "WAN Scenarios" columns (E-LAN, E-Line, E-Tree, L3VPN) against two rows: "Without EVPN" and "With EVPN." Without EVPN: E-LAN uses VPLS, E-Line uses VPWS, E-Tree uses VPLS E-Tree, L3VPN uses L3VPN. With EVPN: E-LAN uses EVPN (RFC 7432 Basic Standard) and also PBB-EVPN (RFC 7623); E-Line uses EVPN VPWS (RFC 8214); E-Tree uses EVPN E-Tree (draft-ietf-bess-evpn-etree); L3VPN uses EVPN L3VPN (draft-ietf-bess-evpn-prefix-advertisement-05). All of these "With EVPN" solutions are shown converging into and unified by a single central "EVPN" node, with a note stating: "The EVPN control plane unifies all services, and the EVPN standards are gradually mature and complete."

- E-Line, E-Tree, and E-LAN are three types of Ethernet virtual circuits (EVCs). For details, see metro Ethernet standards at https://wiki.mef.net/display/CESG/E-Line.
- The Metropolitan Ethernet Forum (MEF) defines three types of EVCs: point-to-point EVC, multipoint-to-multipoint EVC, and root-multipoint EVC.
  - E-Line: A point-to-point EVC strictly associates two User-to-Network Interfaces (UNIs).
  - E-LAN: A multipoint-to-multipoint EVC can associate two or more UNIs. Users or carriers can add any UNIs to the EVC or delete some UNIs from the EVC without affecting other UNIs.
  - E-Tree: This EVC is similar to the hub-spoke model in L3VPN. It consists of one or more root UNIs and several leaf UNIs. The root UNI can directly communicate with all UNIs in the EVC, whereas a leaf UNI can only communicate directly with the root UNI in the EVC, and two leaf UNIs cannot communicate with each other directly.

#### EVPN on a Data Center Network

- The network virtualization overlay (NVO) solution (RFC 8365) of EVPN is used in cloud data centers.
- It is recommended that the data plane use Virtual Extensible LAN (VXLAN) encapsulation and the control plane use EVPN to construct a flexible data center overlay network.

Diagram description: A two-tier data center fabric. The Spine tier (top) contains two spine devices interconnected in a "VXLAN/EVPN" cloud. The Leaf tier (below) contains three leaf devices, each connecting down to endpoint devices: a Server cluster, a Value-added service (VAS) resource pool, and an Egress router, respectively. A callout box notes: "All services in the data center are carried by the VXLAN overlay network." and "The underlay network consisting of spine and leaf nodes performs high-speed forwarding."

#### EVPN Application on a Campus Network

- The campus network virtualization solution is similar to that in the cloud data center. The EVPN NVO solution (RFC 8365) is used.
- VXLAN encapsulation and EVPN are used on different underlying networks to build a flexible overlay network.

Diagram description: A two-layer diagram. The top "Overlay (virtual network layer)" shows three separate virtual networks (Virtual network 1, Virtual network 2, Virtual network 3), each represented by a small set of interconnected switch icons. The bottom "underlay" layer shows the physical campus network: an AP connects to an LSW, which connects to another LSW, which connects to an LSW labeled "Native AC," which connects up to a core switch/router icon, which connects to an NGFW and out to the Internet/WAN cloud. Additional LSW-to-LSW links are shown forming the physical underlay topology beneath the virtual overlays above.

#### EVPN Application in SD-WAN

- SD-WAN is a next-generation enterprise branch interconnection solution that supports intelligent dynamic traffic steering, Zero Touch Provisioning (ZTP), and visualization.
- In the SD-WAN solution, EVPN is deployed between route reflectors (RRs) and customer-premises equipment (CPE) devices to advertise SD-WAN overlay VPN routes on the control plane. IPsec VPN is used on the data plane to build secure forwarding channels.

Diagram description: A central RR at the top connects via BGP EVPN routes (dashed blue lines) down to two CPE devices — Site 1 (CPE) and Site 2 (CPE). Site 1 holds site information (addresses 1.1.1.1 and 2.2.2.1); Site 2 holds site information (addresses 1.1.1.2 and 2.2.2.2). Between Site 1 and Site 2, two parallel underlying transport paths are shown — Transport network-1 and Transport network-2 — each carrying an IPsec VPN tunnel (solid lines) directly between the two CPEs, alongside the BGP EVPN control-plane routes from the RR.

- Overlay VPN routes include site VPN route prefixes, next-hop route information, and IPsec key pairs required for data encryption of data channels between CPEs. For details, see materials of the SD-WAN course.

## Quiz

1. (Essay) Please describe the principles and common route types of EVPN.
2. (Essay) Please describe usage scenarios of EVPN.

Note (answers provided in PDF speaker notes):
1. EVPN is an extension to MP-BGP. EVPN provides five major types of routes and is used as the control plane of Layer 2 or Layer 3 tunnels.
2. EVPN can be widely used in all enterprise scenarios, such as SD-WAN, campus networks, data centers, and WANs. In data centers and campus networks, EVPN and VXLAN are used together to construct a service overlay network. In SD-WAN scenarios, EVPN and IPsec are used together to build enterprise branch interconnection networks. On a WAN, EVPN can be used with various underlying tunneling and label technologies, such as MPLS, Segment Routing (SR), VPLS, and virtual private wire service (VPWS).

## Summary

- MP-BGP's extension to BGP-4 allows different types of address families, such as IPv4 multicast, IPv6, L3VPN, and EVPN, to be distributed in BGP.
- This course describes EVPN that is used to solve the Ethernet L2VPN problems. With the increase of usage scenarios and protocol extensions, EVPN can be used in various scenarios, including WANs, data centers, campus networks, and SD-WANs.

