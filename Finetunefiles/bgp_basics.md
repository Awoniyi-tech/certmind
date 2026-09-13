# BGP Basics

## Foreword

- A network is divided into different autonomous systems (ASs) to facilitate network management. An Exterior Gateway Protocol (EGP) was used to dynamically exchange routing information between ASs. However, the EGP advertises only reachable routes and does not select optimal routes or prevent routing loops. Therefore, the EGP cannot meet network management requirements.
- BGP was designed to replace the EGP and has the following capabilities: BGP selects optimal routes, prevents routing loops, transmits routing information efficiently, and maintains a lot of routes.
- This course describes BGP basics.

## Objectives

- On completion of this course, you will be able to:
  - Describe basic concepts of BGP.
  - Describes BGP peer types.
  - Learn how to set up a BGP peer relationship.
  - Learn BGP state machine.
  - Perform basic BGP configurations.

## Contents

1. Introduction to BGP
2. Basic Concepts of BGP
3. Basic BGP Configurations

## 1. Introduction to BGP

### AS

Diagram description: Two dashed boxes represent AS 100 (top) and AS 200 (bottom). AS 100 contains four routers running OSPF (labeled "OSPF" in the middle). AS 200 contains two sub-groups: a left group of routers running OSPF and a right group (shaded gray) of routers running IS-IS. A dashed line with a question mark connects AS 100 to AS 200, indicating an unresolved question of how the two ASs should communicate.

- IGPs, such as OSPF and IS-IS, are widely used on organizational networks. As the network scale expands and the number of routes on the network increases, IGPs cannot manage large-scale networks. As a result, the concept of Autonomous Systems (ASs) emerges.
- An AS is a collection of devices that are managed by the same organization and use the same route selection policy.
- ASs are distinguished by AS numbers. An AS number can be expressed in 16-bit or 32-bit format. The Internet Assigned Numbers Authority (IANA) assigns AS numbers.
- When different ASs need to communicate with each other, which routing protocol should be used to transmit routes between the ASs?

- IANA: an organization under the Internet Architecture Board (IAB). The IANA authorizes the Network Information Center (NIC) and other organizations to assign IP addresses and domain names. In addition, the IANA maintains the protocol identifier database used by the TCP/IP protocol suite, including AS numbers.
- In 16-bit format, AS numbers 64512-65534 are private ones. In 32-bit format, AS numbers 4200000000-4294967294 are private ones.

### Using an IGP to Transmit Routes

Diagram description: The same AS 100 / AS 200 topology as the previous slide. A red dashed arrow labeled "OSPF" points from AS 200 up to AS 100, annotated "OSPF LSA," indicating an attempt to use OSPF itself to carry routing information between the two ASs.

- A direct or logical link (for example, a GRE tunnel) must be established between ASs for peer relationship setup.
- ASs may belong to different organizations or companies and cannot be trusted mutually. Using an IGP may expose network information inside an AS.
- As the network scale expands, the number of routes increases, the routing table size increases, route convergence becomes slow, and device performance consumption increases.

- Virtual private network (VPN): is used to build a logically and directly connected network.

### Using BGP to Transmit Routes

Diagram description: The same AS 100 / AS 200 topology. A red dashed arrow labeled "BGP" points from AS 200 up to AS 100, annotated "BGP route update," indicating that BGP (rather than the IGP) is used to carry routing information between the two ASs.

The Border Gateway Protocol (BGP) is specially used between ASs for route transmission. Compared with a conventional IGP, BGP has the following characteristics:

- BGP is based on TCP. A BGP connection can be established as long as a TCP connection can be established.
- BGP transmits only routing information, but does not expose topology information in an AS.
- BGP routes are updated only upon network changes. They are not updated periodically.

### BGP Development History

Diagram description: A horizontal timeline with three snapshots. Left snapshot (about 1980): two dashed boxes, AS 100 and AS 200, connected by a dashed "EGP" arrow, labeled "About 1980, the concept of AS was proposed." Middle snapshot (1989): AS 100 and AS 200 connected by a dashed "BGP-1" arrow, labeled "In 1989, the first RFC of BGP was released." Right snapshot (current): AS 100 and AS 200 connected by a dashed "BGP4+" arrow, labeled "Currently, BGP4+ is proposed."

- Below the left snapshot: In about 1980, the network scale expands and the number of routes increases. To solve this problem, the concept of AS is introduced. An External Gateway Protocol (EGP) is used between ASs.
- Below the middle snapshot: An EGP advertises only routes and does not control route selection or prevent routing loops. In 1989, BGP RFC 1105 (BGP-1) was released. RFC 1163 released in 1990 proposed the concept of path attributes. BGP can select routes and control paths based on path attributes.
- Below the right snapshot: After years of development, many RFCs about BGP have been released. Starting from BGP-4 (RFC 1771), BGP has become a classless routing protocol, and BGP4+ supports multiple address families.

- The latest RFC for BGP-4 is RFC 4271. Compared with RFC 1771, RFC 4271 further describes some details, such as events, state machine, and BGP route decision-making process.

### BGP Application in Enterprises

Diagram description: Two panels side by side.

Left panel, "Communication within an Enterprise": A cloud labeled "HQ, AS 100" containing two routers connects via dashed red "BGP" arrows down to "Branch 1" (AS 200) and "Branch 8" (AS 800), each represented by a small building icon and a router, with "..." indicating additional branches in between.

Right panel, "Communication Between Enterprises and a Carrier": Enterprise A (a building icon with a router) connects via a dashed red "BGP" arrow to a router inside a green cloud labeled "Carrier X, AS 1000." The carrier cloud has two routers, one connecting via BGP to Enterprise A and another connecting via BGP down to Enterprise B (AS 200) and, further along with "...", to Enterprise N (AS 800).

- Under the left panel: Branches of a large enterprise use BGP to exchange routes. Different branches belong to different BGP ASs.
- Under the right panel: The enterprise and carrier can use BGP to exchange routes so that the enterprise network can obtain specific routes to the carrier network and the carrier can obtain routes to the enterprise network.

## Contents

1. Introduction to BGP
2. Basic Concepts of BGP
3. Basic BGP Configurations

## 2. Basic Concepts of BGP

*Note: Slides in this section display a navigation breadcrumb at the top with the stages: Overview, Peer Relationship, Message and State Machine, Protocol Entry, Route Generation, Advertisement Rule. The currently highlighted stage is noted per slide below where relevant.*

### Overview of BGP

Navigation breadcrumb: **Overview** highlighted (Peer Relationship, Message and State Machine, Protocol Entry, Route Generation, Advertisement Rule not yet highlighted).

- BGP is a path vector protocol that allows devices between ASs to communicate and selects optimal routes. BGP-1 (defined in RFC 1105), BGP-2 (defined in RFC 1163), and BGP-3 (defined in RFC 1267) are three earlier versions of BGP. BGP-4 (defined in RFC 1771) has been used since 1994. Since 2006, unicast IPv4 networks have been using BGP-4 defined in RFC 4271, and other networks (such as IPv6 networks) have been using Multiprotocol BGP (MP-BGP) defined in RFC 4760.
- BGP has the following characteristics:
  - BGP uses TCP (port 179) as the transport layer protocol and triggers route updates instead of periodic route updates.
  - BGP can carry a large amount of routing information and support large-scale networks.
  - BGP provides various routing policies to flexibly select routes and instruct peers to advertise routes based on routing policies.
  - BGP supports MPLS/VPN applications and transmits VPN routes.
  - BGP offers route summarization and route dampening functions to prevent route flapping, enhancing network stability.

### BGP Characteristics (1)

Navigation breadcrumb: **Overview** highlighted.

Diagram description: Two BGP speaker routers, one in AS 200 and one in AS 300, connect via a dashed red line. A protocol stack box above shows "BGP" over "TCP" over "IP," indicating BGP runs over TCP over IP between the speakers. Below, a box labeled "IP routing Table, Route number: 70W+" (i.e., over 700,000 routes) is shown associated with the connection, indicating the scale of routes a BGP speaker can carry.

- BGP uses TCP as the transport layer protocol and TCP port number is 179. BGP sessions between routers are established based on TCP connections.
- A router that runs BGP is called a BGP speaker or a BGP router.
- Two routers that establish a BGP session are peers of each other, and BGP peers exchange BGP routing tables.
- A BGP router sends only incremental BGP route updates.
- BGP can carry a large number of route prefixes and can be applied to large-scale networks.

### BGP Characteristics (2)

Navigation breadcrumb: **Overview** highlighted.

Diagram description: Four ASs (AS 100, AS 200, AS 300, AS 400) each containing a router pair connected by "...". Dashed red "BGP" arrows interconnect the routers of AS 100–AS 400, AS 200–AS 100, AS 200–AS 300, and AS 300–AS 400, showing a partial mesh of BGP sessions. A yellow arrow labeled "BGP route update" points along one of the connections toward network 10.1.2.0/8. A callout box shows a sample BGP route update:
```
BGP route update
10.1.2.0/8
Path Attribute – Origin: IGP
Path Attribute – AS_PATH: 200
Path Attribute – Nexthop: 10.0.12.1
...
```

- BGP is also called a path vector routing protocol.
- Each BGP route carries multiple path attributes. Different from IS-IS and OSPF that use costs to select paths, BGP selects paths based on path attributes. Therefore, BGP is easy to operate and allows you to select the most appropriate path control mode in different scenarios.

### BGP Peer Relationship

Navigation breadcrumb: **Peer Relationship** highlighted.

Diagram description: AS 100 is shown as a large oval containing an OSPF network with two routers labeled as an "IBGP Peer" pair, connected to each other by a dashed line. From each of these two routers, a red dashed "EBGP Peer" line extends outward through a cloud labeled "WAN" down to two separate routers: one in AS 200 and one in AS 300.

- Different from OSPF and IS-IS, BGP sessions are established based on TCP. The two routers that establish a BGP peer relationship do not need to be directly connected.
- BGP has two types of peer relationships:
  - External BGP (EBGP): BGP peer relationship between BGP routers in different ASs. To establish an EBGP peer relationship between two routers, ensure that the following conditions are met:
    - The two routers belong to different ASs (AS numbers).
    - When configuring EBGP, ensure that the IP address of the peer specified in the **peer** command is reachable and the TCP connection can be set up.
  - Internal BGP (IBGP): BGP peer relationship between BGP routers in the same AS.

### Establishing a BGP Peer Relationship (1)

Navigation breadcrumb: **Peer Relationship** highlighted.

Diagram description: Router R1 in AS 200 and router R2 in AS 300, connected across a "WAN" cloud. Below them, three sequential message-exchange boxes are shown, numbered 1, 2, 3:
1. TCP SYN → / ← TCP SYN+ACK / TCP ACK → (a TCP three-way handshake between R1 and R2)
2. Open → / ← Open (both routers exchange Open messages)
3. Keepalive → / ← Keepalive (both routers exchange Keepalive messages)

- The router that first starts BGP initiates a TCP connection. As shown in the figure on the left, R1 first starts BGP and uses a random port number to initiate a TCP connection to port 179 of R2.
- After the three-way handshake is complete, R1 and R2 send Open messages carrying parameters to each other to establish a peer relationship. After the parameters are negotiated, R1 and R2 send Keepalive messages to each other. After receiving the Keepalive messages from each other, the two routers establish a peer relationship. In addition, R1 and R2 periodically send Keepalive messages to maintain the connection.
- The Open message carries the following information:
  - My Autonomous System: indicates the AS number.
  - Hold Time: is used to negotiate the time for sending Keepalive messages.
  - BGP Identifier: indicates the router ID of the local router.

- Each BGP peer initiates a TCP three-way handshake, so two TCP connections are established. Actually, BGP retains only one TCP connection. After obtaining the BGP identifier of the peer from an Open message, the BGP peer compares the local router ID with the peer router ID. If the local router ID is smaller than the remote router ID, the local router terminates the TCP connection and uses the TCP connection initiated by the remote router to exchange BGP messages.

### Establishing a BGP Peer Relationship (2)

Navigation breadcrumb: **Peer Relationship** highlighted.

Diagram description: Router R1 (AS 200) and router R2 (AS 300), connected across a "WAN" cloud, with a message box below showing "Update →" and "← Update," indicating that after the peer relationship is established, both routers exchange Update messages.

- After a BGP peer relationship is established, a BGP router sends a BGP Update message to advertise routes to the peer.

### Source Address of a TCP Connection

Navigation breadcrumb: **Peer Relationship** highlighted.

Diagram description: A network within AS 200 contains four routers: R1, R2, R3, and R4, arranged so that R1 connects to R4, R4 connects to R3, and R1 and R3 both connect to R2 (R2 is marked with a red "X," indicating a failure/down state on the direct R1–R2–R3 path segment being discussed). R1's interface toward R2 is GE0/0/0 (10.0.12.1); R3's interface toward R2 is GE0/0/0 (10.0.13.3). A dashed red line labeled "IBGP peer" connects R1 and R3 directly (logically, not physically). A callout box beneath states: "Typically, a network in an AS provides certain redundancy. If R1 and R3 use directly connected interfaces to establish an IBGP peer relationship, the BGP session will be interrupted once the directly connected interface or link fails. However, due to redundant links, the IP connectivity between R1 and R3 is not Down. (R1 and R3 can still communicate with each other through R4.)"

- By default, BGP uses the interface that sends BGP messages as the local interface of a TCP connection.
- When deploying IBGP peer relationships, you are advised to use loopback addresses as source addresses of TCP connections. The loopback interface is stable. The reliability can be ensured by using the IGP and redundancy topology in the AS.
- During EBGP peer relationship setup, the IP address of the directly connected interface is often used as the source address. If you use a loopback interface to establish an EBGP peer relationship, pay attention to the EBGP multi-hop problem.

### BGP Message Types (1)

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A layered packet-encapsulation diagram. At the top, a horizontal row shows: L2 Header | IP Header | TCP Header | BGP Packet | CRC. Below, the "BGP Packet" segment expands into "BGP Header" and "BGP Packet" (payload). Below that, the BGP Header expands into a box labeled "Marker (16 bytes)" with two sub-fields "Length (2 bytes)" and "Type (1 byte)." To the right, a list box shows the five possible message types corresponding to the Type field: Open, Update, Notification, Keepalive, Route-refresh.

There are five types of BGP messages. Different types of messages have the same header.

- Different from common IGP protocols, BGP uses TCP as the transport layer protocol and port 179. This enables BGP to establish peer relationships between indirectly connected routers.

Open: carrying parameters (like router ID) to establish a peer relations[hip].
Update: advertising routes to the peer.
Notification:
Keepalive: sent periodically to check the connection between two dev[ices].
Route-refresh:

*Note: In the source slide, the descriptions for "Notification" and "Route-refresh" are left blank/incomplete in the speaker notes (they are elaborated on later slides "BGP Message Format: Notification" and "BGP Message Format: Route-refresh").*

### BGP Message Types (2)

Navigation breadcrumb: **Message and State Machine** highlighted.

| Name | Function | Usage Scenario |
|---|---|---|
| Open | Negotiate BGP peer parameters and establish peer relationships. | After a BGP TCP connection is established, Open messages are sent. |
| Update | Send BGP route update. | After a BGP peer relationship is established and routes need to be sent or routes change, Update messages are sent. |
| Notification | Report error information and terminate the peer relationship. | When detecting an error during BGP running, the local BGP router sends a Notification message to notify the peer of the error. |
| Keepalive | Indicate that the peer relationship is established and the BGP peer relationship is maintained. | After receiving a Keepalive message from the peer, the BGP router sets the peer relationship status to Established and periodically sends Keepalive messages to maintain the connection. |
| Route-refresh | Request the peer to retransmit routes if routing policies are changed. Only the BGP devices supporting route-refresh can send and respond to Route-refresh messages. | When the routing policy changes, Route-refresh messages are sent to trigger the peer to re-advertise routes. |

### BGP Message Format: Header Format

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A box labeled "Marker (16 bytes)" sits above two smaller boxes labeled "Length (2 bytes)" and "Type (1 byte)." Next to the Type field, a small legend lists the five type values: 1: Open, 2: Update, 3: Notification, 4: Keepalive, 5: Route-refresh.

The five types of BGP messages have the same header, as shown in the left part of the figure. The main fields are described as follows:

- Marker: is used to check whether synchronization information of BGP peers is complete and for BGP authentication. It has 16 bytes. If authentication is not used, all bits are set to 1 (all FFs in hexadecimal notation).
- Length: indicates the total length of a BGP message (including the packet header), in bytes. It has 2 bytes.
- Type: indicates the type of BGP messages. It has 1 byte. The value ranges from 1 to 5, indicating Open, Update, Notification, Keepalive, and Route-refresh messages.

### BGP Message Format: Open

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A stacked field diagram for the Open message body: Version (8 bits) / My AS (16 bits) / Hold Time (16 bits) / BGP Identifier (32 bits) / Opt Parm Len (8 bits) / Optional parameters (variable length).

The Open message is the first message sent after a TCP connection is established. It is used to establish a connection between BGP peers. The figure on the left shows the Open message format. The main fields in the Open message are described as follows:

- Version: indicates the BGP version number. For BGPv4, the value is 4.
- My AS: indicates the local AS number. By comparing AS numbers of the two ends, you can determine whether the peer end and the local end are in the same AS.
- Hold Time: indicates the holding time. BGP peers need to negotiate the holding time and keep it consistent when establishing a peer relationship. If a router does not receive any Keepalive or Update message from its peer within the holding time, the BGP connection is considered as disconnected.
- BGP Identifier: indicates the router ID of a BGP router. The field is in IP address format and identifies a BGP router.

- Opt Parm Len: indicates the length of Optional parameters.
- Optional parameters: declares optional capabilities of a BGP router, such as authentication and multi-protocol support.
- In addition to IPv4 unicast routing information, BGP4+ supports multiple network layer protocols, such as IPv6 and multicast. During negotiation, BGP peers negotiate the support for network layer protocols through the Optional parameters field.

### BGP Message Format: Update

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A stacked field diagram for the Update message body: Withdrawn Routes length (2 bytes) / Withdrawn Routes (N bytes) / Total path attribute length (2 bytes) / Path Attributes (N bytes) / NLRI (N bytes).

- Update messages are used to transmit routing information between peers. Update messages can be used to advertise and withdraw routes.
- An Update message can advertise a type of routes with the same path attributes, which are placed in Network Layer Reachability Information (NLRI) fields. In addition, the Update message can carry multiple unreachable routes, which are stored in the Withdrawn Routes field.
- The figure on the left shows the message format. The main fields in the message are described as follows:
  - Withdrawn routes: indicates the list of unreachable routes.
  - Path attributes: indicates the list of all path attributes related to NLRI. Each path attribute consists of a Type-Length-Value (TLV).
  - NLRI: indicates the prefix and prefix length of a reachable route.

- Withdrawn Routes Length: indicates the length of the Withdrawn Routes field, in bytes. If the value is 0, the Withdrawn Routes field is omitted.
- Total path attribute length: indicates the length of the Path Attributes field, in bytes. If the value is 0, the Path Attributes field does not exist.

### BGP Message Format: Notification

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A stacked field diagram for the Notification message body: Error Code (8 bits) / Error Subcode (8 bits), followed by Data (variable length).

When BGP detects an error (may occur during or after the establishment of a peer relationship), BGP sends a Notification message to the peer to notify the peer of the error cause. Then the BGP connection is interrupted immediately.

- Error Code and Error Subcode: are used to notify the peer of the specific error type.
- Data: is used to describe the detailed error content. The length is variable.

### BGP Message Format: Keepalive

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A field diagram showing the Keepalive message consists only of the header: Marker (16 bytes) above Length (2 bytes) and Type (1 byte), with no additional payload fields.

- After receiving a Keepalive message from the peer, the BGP router sets the peer relationship status to Established and periodically sends Keepalive messages to maintain the connection.
- The Keepalive message only contains the packet header without any other fields.

### BGP Message Format: Route-refresh

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A stacked field diagram for the Route-refresh message body: AFI (16 bits) / Res (8 bits) / SAFI (8 bits).

- Route-refresh messages are used to request the peer to resend routing information of a specified address family. In most cases, after the local end modifies a routing policy, the peer sends Update messages again. Then the local end recalculates BGP routes according to the new routing policy.
- The main fields are described as follows:
  - Address Family Identifier (AFI): identifies an address family, for example, IPv4.
  - Res.: is reserved. The 8 bits must be set to 0.
  - Subsequent Address Family Identifier (SAFI): indicates the sub-address family identifier.

- During Open message negotiation, the two BGP routers negotiate whether they support route-refresh. If they support route-refresh, you can run the refresh bgp command to softly reset the BGP connection to refresh a BGP routing table without tearing down any BGP connection.
- If a device's peer does not support route-refresh, you can run the peer keep-all-routes command to configure the device to retain all routing updates received from the peer so that the device can refresh its routing table without tearing down the BGP connection with the peer.
- By default, the device is not configured to retain all routing updates received from the peer.

### BGP State Machine (1)

Navigation breadcrumb: **Message and State Machine** highlighted.

| Peer Status | Usage |
|---|---|
| Idle | Prepare TCP connections and monitor remote peers. When enabling BGP, prepare sufficient resources. |
| Connect | A TCP connection is being set up. Authentication is completed during the TCP connection setup. If the TCP connection fails to be established, the local end enters the Active state and attempts to establish a TCP connection repeatedly. |
| Active | The TCP connection fails to be set up and the local end attempts to establish a TCP connection repeatedly. |
| OpenSent | After the TCP connection is established, the local end sends an Open packet carrying parameters to negotiate the establishment of the peer. |
| OpenConfirm | After the parameter and capability negotiation succeeds, the local end sends a Keepalive message and waits for the Keepalive message from the peer end. |
| Established | The local end has received the Keepalive message from the peer. The capabilities of the two ends are the same after negotiation. The local end starts to use the Update message to advertise routing information. |

**Learner note (annotation found beneath this slide in the source, not official Huawei text):**

Note that it's after the TCP connection has been established that the Peer relationship will be up.

let kuku say the process is
1: Idle
2: Connect: This is where the TCP connection is established, and authentication is also set up. If it fails, it goes back to Active (Active is like the initial repeated state for failed connections).
3: OpenSent: After the TCP connection is done, the Open packet (to share routing) is sent next.
4: OpenConfirm: At this stage, once both peer parameters match (i.e., their configurations align), the peer sends a keepalive message and waits for a reply.
5: Established: The keepalive message is received and acknowledged, and the capabilities of both ends are confirmed to be the same.

### BGP State Machine (2)

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: A state machine flow diagram with states arranged left to right: Idle → Connect → OpenSent → OpenConfirm → Established. From Idle, an arrow labeled "Start" leads to Connect. From Connect, an arrow labeled "TCP Established" leads to OpenSent; an arrow labeled "TCP Failed" leads down to a state "Active." From Active, an arrow labeled "TCP Established" leads to OpenSent, and an arrow labeled "Connect Retry Timeout" loops back up to Connect. From OpenSent, an arrow labeled "Receive Correct Open" leads to OpenConfirm. From OpenConfirm, an arrow labeled "Receive Correct Keepalive" leads to Established. Each of Connect, OpenSent, OpenConfirm, and Established has an "Error" arrow looping back up to Idle.

- Initially, BGP is in Idle state. In Idle state, a BGP device refuses BGP connection requests from the peer. The BGP device initiates a TCP connection with its BGP peer and changes its state to Connect only after receiving a Start event from the system.
  - The Start event occurs when an operator configures a BGP process or resets an existing BGP process or when the router software resets a BGP process.
  - If an error occurs in any state, for example, BGP receives a Notification message or a TCP disconnection notification, BGP returns to the Idle state.
- In the Connect state, BGP starts the Connect Retry timer and waits for a TCP connection to be established:
  - If the TCP connection is established, BGP sends an Open message to the peer and transitions to the OpenSent state.
  - If the TCP connection fails to be established, BGP transitions to the Active state.
  - If the BGP device does not receive a response from the peer before the Connect Retry timer expires, the BGP device attempts to establish a TCP connection with another peer and stays in Connect state.

- In Active state, the BGP device keeps trying to establish a TCP connection with the peer.
  - If the TCP connection is established, BGP sends an Open message to the peer, terminates the Connect Retry timer, and transitions to the OpenSent state.
  - If the TCP connection fails to be established, BGP stays in Active state.
  - If the BGP device does not receive a response from the peer before the Connect Retry timer expires, the BGP device returns to the Connect state.
- In OpenSent state, the BGP device waits for an Open message from the peer and then checks the validity of the received Open message, including the AS number, version, and authentication password.
  - If the received Open message is valid, BGP sends a Keepalive message and transitions to the OpenConfirm state.
  - If the received Open message is invalid, the BGP device sends a Notification message to the peer and returns to the Idle state.
- In OpenConfirm state, the BGP device waits for a Keepalive or Notification message from the peer. If the BGP device receives a Keepalive message, it changes to the Established state. If it receives a Notification message, it returns to the Idle state.
- In Established state, the BGP device exchanges Update, Keepalive, Route-refresh, and Notification messages with the peer.
  - If the BGP device receives a valid Update or Keepalive message, it considers that the peer is working properly and maintains the BGP connection with the peer.
  - If the BGP device receives an invalid Update or Keepalive message, it sends a Notification message to the peer and returns to the Idle state.
  - If the BGP device receives a Route-refresh message, it does not change its status.
  - If the BGP device receives a Notification message, it returns to the Idle state.
  - If BGP receives a TCP disconnect notification, it terminates the TCP connection with the peer and returns to the Idle state.

### Illustration of BGP State Machine (1)

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: Two panels side by side.

Left panel, "Idle state": Router R1 (AS 200) and router R2 (AS 300) connected across a WAN. A callout states: "After a BGP peer is configured, the device attempts to establish a TCP connection. If the TCP connection cannot be established, the device remains in Idle state." Caption beneath: "There is no route to the BGP peer (common cause), so the local end remains in Idle state."

Right panel, "Connect, Active": Router R1 (AS 200) and router R2 (AS 300) connected across a WAN, with a message sequence showing repeated "TCP SYN" attempts ("Retransmit TCP SYN" shown multiple times with "..." between), transitioning from a "Connect" state to an "Active" state. Caption beneath: "After a BGP peer is configured and the route to the peer address is found, a TCP three-way handshake is initiated. During the three-way handshake, the BGP device is in Connect state. If the TCP connection cannot be established for a long time, the BGP device enters the Active state."

### Illustration of BGP State Machine (2)

Navigation breadcrumb: **Message and State Machine** highlighted.

Diagram description: Two panels side by side.

Left panel, "OpenSent, OpenConfirm": Router R1 (AS 200) and router R2 (AS 300) connected across a WAN. A message sequence shows "TCP Connection Established," then R1 transitions to "OpenSent" and exchanges "Open →" / "← Open" messages with R2, then R1 sends a "Keepalive →" message and transitions to "OpenConfirm." Caption beneath: "After the TCP three-way handshake is complete, the local end sends an Open message to establish a peer relationship and enters the OpenSent state. After receiving an Open message from the peer end and verifying that the parameters are correct, the local end sends a Keepalive message. Then the local end enters the OpenConfirm state."

Right panel, "Established": Router R1 (AS 200) and router R2 (AS 300) connected across a WAN. A message sequence shows R1 exchanging "Open" and "Keepalive" messages with R2, with R1 transitioning from "OpenConfirm" to "Established." Caption beneath: "After entering the OpenConfirm state and receiving a Keepalive message from its peer, the BGP router enters the Established state. The peer relationship is then established."

### BGP Peer Table

Navigation breadcrumb: **Protocol Entry** highlighted.

```
<R1>display bgp peer
 BGP local router ID : 10.0.1.1
 Local AS number : 100
 Total number of peers : 1        Peers in established state : 1

 Peer          V    AS  MsgRcvd  MsgSent  OutQ  Up/Down    State        PrefRcv
 10.0.12.2     4    100   25719    25714     0  0428h32m   Established        1
```

You can run the **display bgp peer** command to check the BGP peer table. The parameters in the command output are described as follows:

- Peer: indicates the IP address of the peer.
- V: indicates the BGP version used on the peer.
- AS: indicates the AS number.
- Up/Down: indicates the period of time during which a BGP session keeps the current state.
- State: indicates the status of the peer.
- PrefRcv: indicates the number of route prefixes sent from the peer.

- The BGP peer table lists the BGP peer of the local device and the status of the peer.
- MsgRcvd: indicates the number of received messages.
- MsgSent: indicates the number of sent messages.
- OutQ: indicates the message to be sent to the specified peer. The value is always 0.

### BGP Routing Table (1)

Navigation breadcrumb: **Protocol Entry** highlighted.

```
<R1>display bgp routing-table
 BGP Local router ID is 10.0.1.1
 Status codes: * - valid, > - best, d - damped,
               h - history,  i - internal, s - suppressed, S - Stale
               Origin : i - IGP, e - EGP, ? - incomplete
 Total Number of Routes: 2
      Network            NextHop        MED     LocPrf    PrefVal Path/Ogn
 *>i  10.0.45.0/24        10.0.4.4       0       100       0       ?
 *  i                     10.0.4.4       0       100       0       ?
```

- Run the **display bgp routing-table** command on the device to check the BGP routing table.
  - Network: indicates the destination network address and subnet mask of the route.
  - NextHop: indicates the IP address of the next hop.
- To check detailed information about a route, run the **display bgp routing-table** *ipv4-address* { *mask* | *mask-length*} command. This command displays detailed information about matched BGP routes.

- The BGP routing table lists all the BGP routes discovered by the local device. If multiple routes to the same destination exist, all the routes are listed, but only one route is preferred for each destination.

### BGP Routing Table (2)

Navigation breadcrumb: **Protocol Entry** highlighted.

Diagram description: Two callout boxes side by side, both showing detailed output for the same route (10.0.45.0/24) from two different perspectives/annotators.

Left box:
```
<R1>display bgp routing-table 10.0.45.0 24
 BGP local router ID : 10.0.1.1
 Local AS number : 100
 Paths:   2 available, 1 best, 1 select
 BGP routing table entry information of 10.0.45.0/24:
 From: 10.0.2.2 (10.0.2.2)          #Specify the route source.
 Route Duration: 06h19m44s
 Relay IP Nexthop: 10.0.12.2
 Relay IP Out-Interface: GigabitEthernet0/0/0
 Original nexthop: 10.0.4.4          #Specify the next-hop IP address of the route.
 Qos information : 0x0
 AS-path Nil, origin incomplete, MED 0, localpref 100, pref-val 0, valid,
 internal, best, select, active, pre 255, IGP cost 2  # Indicate the path
 attribute and whether the path is preferred.
 Originator:  10.0.4.4
 Cluster list: 10.0.2.2
 Not advertised to any peer yet
```

Right box (BGP routing table entry information of 10.0.45.0/24, from a different peer):
```
 From: 10.0.3.3 (10.0.3.3)
 Route Duration: 05h17m56s
 Relay IP Nexthop: 10.0.12.2
 Relay IP Out-Interface: GigabitEthernet0/0/0
 Original nexthop: 10.0.4.4
 Qos information : 0x0
 AS-path Nil, origin incomplete, MED 0, localpref 100, pref-val 0, valid,
 internal, pre 255, IGP cost 2, not preferred for peer address
 Originator:  10.0.4.4
 Cluster list: 10.0.3.3
 Not advertised to any peer yet
```

- The **display bgp routing-table** *ipv4-address* { *mask* | *mask-length* } command displays information about a BGP route with a specified IP address/mask length. The information includes the route originator, next-hop address, and route path attributes.

### BGP Route Generation

Navigation breadcrumb: **Route Generation** highlighted.

Diagram description: Two boxes at the top, "IGP routing table" (containing "Route") and "BGP routing table" (containing "Route"), connected by a curved arrow labeled "① Import," representing R1 importing a route from its IGP routing table into its BGP routing table. Below, AS 200 contains four routers running OSPF; two of them are R1 and R2. R1 connects via a red dashed "EBGP" line to router R3 in AS 300. A yellow arrow labeled "② BGP route update" points from R1 toward R3.

- Different from an IGP, BGP does not discover or calculate routes. Instead, BGP injects routes from the IGP routing table to the BGP routing table and sends Update messages carrying the routes to BGP peers.
- BGP can import routes in either of the following modes:
  - network
  - import-route
- Similar to an IGP, BGP can summarize routes based on existing routes to generate a summarized route.

### Importing Routes Using the network Command (1)

Navigation breadcrumb: **Route Generation** highlighted.

Diagram description: Two boxes at the top, "IGP routing table" (containing "10.1.0.0/24 OSPF" and "10.2.0.0/24 OSPF") and "BGP routing table" (containing "*>i 10.1.0.0/24" and "*>i 10.2.0.0/24"), connected by a curved arrow labeled "① Import routes using the network command." A callout shows the configuration:
```
bgp 200
 network 10.1.0.0 24
 network 10.2.0.0 24
```
Below, AS 200 contains four routers running OSPF, including R1 and R2. R1 connects via a red dashed "EBGP" line to router R3 in AS 300.

Routes are imported by using the **network** command:

1. The BGP router in AS 200 has learned two routes to 10.1.0.0/24 and 10.2.0.0/24 through OSPF. The two routes are imported to the BGP process through the **network** command and added to the local BGP routing table.
2. The BGP router in AS 200 sends Update messages to advertise routes to the BGP router in AS 300.
3. After receiving the routes, the BGP router in AS 300 adds the two routes to the local BGP routing table.

- The routes imported using the network command must exist in the IP routing table. Otherwise, the routes cannot be imported to the BGP routing table.

**Learner note (annotation found beneath this slide in the source, not official Huawei text):**

### What Does the `network` Command Do in BGP?

The `network` command in BGP is **not used to learn routes**—it's used to **advertise routes** that already exist in the router's routing table (RIB).

So in the example:

- The router in **AS 200** learns `10.1.0.0/24` and `10.2.0.0/24` via **OSPF**.
- These routes are now present in the **IP routing table**.
- To **advertise** these routes to BGP peers, the router must run:

```
network 10.1.0.0 255.255.255.0
network 10.2.0.0 255.255.255.0
```

This tells BGP: "Hey, if these routes exist in my routing table, go ahead and advertise them to my BGP neighbors."

### Important Clarification

- The `network` command **does not create** or **import** routes into BGP.
- It **references existing routes** and makes them **eligible for advertisement**.
- If the route is **not present** in the IP routing table, the `network` command **won't work**—BGP will ignore it.

### So What's Happening in This Scenario?

1. R1 or R2 (in AS 200) learns routes via OSPF.
2. These routes are installed in the IP routing table.
3. They use the `network` command to **advertise** those routes via BGP.
4. The routes appear in the **local BGP table** and are marked with `*>i` (iBGP learned, best route).

### Importing Routes Using the network Command (2)

Navigation breadcrumb: **Route Generation** highlighted.

Diagram description: AS 200 contains four routers running OSPF, including R1 and R2. R1 connects via a red dashed "EBGP" line to router R3 in AS 300. A yellow arrow labeled "② BGP route update" points from R1 toward R3, next to a callout box:
```
BGP Update
10.1.0.0/24
10.2.0.0/24
```
Below R3, a box labeled "③ R3's BGP routing table" shows:
```
BGP routing table
*>i  10.1.0.0/24
*>i  10.2.0.0/24
```

Routes are imported by using the **network** command:

1. The BGP router in AS 200 has learned two routes to 10.1.0.0/24 and 10.2.0.0/24 through OSPF. The two routes are imported to the BGP process through the **network** command and added to the local BGP routing table.
2. The BGP router in AS 200 sends Update messages to advertise routes to the BGP router in AS 300.
3. After receiving the routes, the BGP router in AS 300 adds the two routes to the local BGP routing table.

### Importing Routes Using the import-route Command

Navigation breadcrumb: **Route Generation** highlighted.

Diagram description: Two boxes at the top, "IGP routing table" (containing "10.1.0.0/24 OSPF" and "10.3.0.0/24 Static") and "BGP routing table" (containing "*>i 10.1.0.0/24" and "*>i 10.3.0.0/24"), connected by a curved arrow labeled "① Import routes using the import-route command." A callout shows the configuration:
```
bgp 200
 import-route ospf
 import-route static
```
Below, AS 200 contains four routers running OSPF, including R1 and R2. R1 connects via a red dashed "EBGP" line to router R3 in AS 300. A yellow arrow labeled "② BGP route update" points from R1 toward R3.

- Although the routes imported by using the **network** command are accurate, only one route can be imported into the IP routing table one by one. If a large number of routes are imported, the configuration commands are complex. In this case, you can use the **import-route** command to import the following routes to the BGP routing table:
  1. Direct routes
  2. Static routes
  3. OSPF routes
  4. IS-IS routes

### BGP Route Summarization

Navigation breadcrumb: **Route Generation** highlighted.

Diagram description: On the left, "Routes before summarization on R1" shows a "BGP routing table" box listing 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24. An arrow points to "Route after summarization on R1," showing an updated "BGP routing table" box listing the same three routes plus a fourth summarized entry, 10.1.0.0/22. A callout shows the configuration used:
```
bgp 200
 aggregate 10.1.0.0 22 detail-suppressed
```
Below, AS 200 contains four routers running OSPF, including R1 and R2. R1 connects via a red dashed "EBGP" line to router R3 in AS 300. A yellow arrow labeled "② BGP route update" points from R1 toward R3 carrying a callout "BGP Update: 10.1.0.0/22." Below R3, a box labeled "③ R3's BGP routing table" shows "BGP routing table: 10.1.0.0/22" only.

Similar to an IGP, BGP also supports manual route summarization. You can run the **aggregate** command in the BGP view to manually summarize BGP routes. After BGP has learned specific routes, the device will import the specified summarized routes to BGP.

- After route summarization is performed, the local BGP routing table contains an additional summarized route in addition to the original specific routes.
- If detail-suppressed is specified during route summarization, BGP advertises only the summarized route to the peer, but not the specific routes before route summarization.
- If detail-suppressed is configured during route summarization, only BGP route to 10.1.0.0/22 is displayed in R3's routing table, and the specific routes before summarization are not displayed.

**Learner note (annotation found beneath this slide in the source, not official Huawei text):**

This means the detail-suppressed command is working by allowing only the summarized route to be advertised to the other AS. At the other AS the update reaches, and only this summarized route will be displayed in its routing table too.

### Advertisement Rule

Navigation breadcrumb: **Route Generation** highlighted (transitioning toward Advertisement Rule).

- After BGP generates BGP routes using the network, import-route, or aggregate command, BGP sends Update messages carrying the BGP routes to the peer.
- BGP routes are advertised according to the following rules:
  - Only the optimal and valid routes are advertised.
  - The routes obtained from EBGP peers are advertised to all BGP peers.
  - IBGP split horizon: The routes obtained from IBGP peers are not advertised to IBGP peers.
  - When a router learns a BGP route (IBGP route) from its IBGP peer, the router cannot use this route or advertise this route to its EBGP peer unless the router learns this route from an IGP. In this situation, IBGP routes and IGP routes need to be synchronized. Route synchronization is used to prevent BGP routing blackholes.

**Learner note (annotation found beneath this slide in the source, not official Huawei text; the following has been reconstructed from a heavily OCR-garbled handwritten-style note for readability, preserving the original meaning):**

### BGP Route Advertisement Rules (Simplified)

EBGP routes can be shared freely
- If a router learns a route from an EBGP peer (outside its AS), it can advertise it to any other BGP peer—no restriction.

IBGP routes are restricted (Split Horizon rule)
- If a router learns a route from an IBGP peer (inside its AS), it cannot advertise that route to another IBGP peer.
- This prevents routing loops inside the AS.

IBGP routes need IGP support to be usable
- If a router learns a route from an IBGP peer, it won't use that route to forward traffic unless it also knows how to reach the next-hop IP via an IGP (like OSPF or IS-IS).
- This is where route synchronization comes in.

Route synchronization prevents blackholes
- A routing blackhole happens when a router advertises a route it can't actually reach.
- Synchronization makes sure that IGP and BGP agree on how to reach the destination—so traffic doesn't get dropped.

### BGP Route Advertisement Rule 1

Navigation breadcrumb: **Advertisement Rule** highlighted.

Diagram description: A box labeled "R1's BGP routing table" shows two entries: "*>i 10.1.0.0/24, Nexthop 11.1.0.1" and "*i (blank), Nexthop 11.1.0.2." Below, AS 200 contains four routers running OSPF, including R1 and R2. R1 connects via a red dashed "EBGP" line to router R3 in AS 300. A yellow arrow labeled "① BGP route update" points from R1 toward R3, carrying a callout "BGP Update: 10.1.0.0/24."

- Rule 1: Only the optimal and valid routes (that is, the next-hop address is reachable) are advertised.
- Run the display bgp routing-table command to check the BGP routing table.

```
Total Number of Routes: 2
      Network         NextHop      MED   LocPrf   PrefVal  Path/Ogn
*>i   10.1.0.0/24      11.1.0.1     0     100      0        ?
*  i                   11.1.0.2     0     100      0        ?
```

- The BGP routing table contains the optimal and valid routes with the following flags:
  - *: indicates the valid route.
  - >: indicates the optimal route.

### BGP Route Advertisement Rule 2

Navigation breadcrumb: **Advertisement Rule** highlighted.

Diagram description: Router R1 (AS 300) sends a route via a yellow "BGP Update message" arrow to router R2 in AS 200 over an "EBGP" connection (R1's BGP routing table shows "*>i 10.1.0.0/24"). Within AS 200, R2 and R3 are connected via "IBGP" (shown with double-headed dashed arrows). R2 also connects via a red dashed "EBGP" line to router R4 in AS 300. Two boxes labeled "BGP router in AS 300, Check the BGP routing table" appear beneath R3 and R4 respectively, each showing "BGP routing table: *>i 10.1.0.0/24," indicating that the route originally advertised by R1 eventually reaches both R3 (via IBGP from R2) and R4 (via EBGP from R2).

- Rule 2: The routes obtained from EBGP peers are advertised to all peers.
- The routes that R2 obtains from EBGP peers are advertised to all EBGP and IBGP peers.

### BGP Route Advertisement Rule 3 (1)

Navigation breadcrumb: **Advertisement Rule** highlighted.

Diagram description: Within AS 200, three routers R1, R2, and R3 are fully interconnected via "IBGP" sessions (dashed lines). A yellow "BGP Update message" arrow flows from R2 to R3 (step ①). Dashed red arrows show a would-be further propagation from R3 to R1 (step ②) and from R1 back to R2 (step ③), illustrating a potential routing loop if IBGP-learned routes were re-advertised to other IBGP peers.

- Rule 3: The BGP routes obtained from an IBGP peer are not advertised to other IBGP peers.
- This is also called IBGP split horizon.
- As shown in the figure, if the routes learned by an IBGP peer are advertised to other IBGP peers, a routing loop occurs:
  - R2 advertises a route to its IBGP peer R3.
  - R3 advertises the received route to its IBGP peer R1.
  - R1 continues to advertise the route to its IBGP peer R2.

### BGP Route Advertisement Rule 3 (2)

Navigation breadcrumb: **Advertisement Rule** highlighted.

Diagram description: Titled "Full-mesh IBGP connections." Within AS 200, three routers R1, R2, and R3 are shown with IBGP sessions between R1–R2, R1–R3, and R2–R3. A yellow "BGP Update message" arrow flows from R2 to R1, but a red "X" is drawn on the dashed IBGP arrow from R1 to R3, indicating R1 is blocked (by split horizon) from forwarding the route it learned from R2 onward to R3.

- Rule 3 may bring new problems. As shown in the figure on the left, when R2 sends a route to R1, R1 cannot send the route to R3 because of the limitation of rule 3. As a result, R3 cannot learn the route.
- To solve this problem, you can establish full-mesh IBGP peer relationships in an AS. Here, R2 and R3 establish an IBGP peer relationship so that R2 can advertise routes to R3.

### BGP Route Advertisement Rule 4 (1)

Navigation breadcrumb: **Advertisement Rule** highlighted.

Diagram description: Within AS 200, router R1 runs OSPF and connects to routers R2 and R3, which have an "IBGP" session between them (a yellow "BGP Update message" arrow flows from R3 to R2). R2 connects via a red dashed "EBGP" line to router R4 in AS 100. R3 connects via a red dashed "EBGP" line to router R5 in AS 300. A box labeled "BGP routing table" beneath R4 shows "*>i 10.0.4.0/24."

- Rule 4: When a router learns a BGP route (IBGP route) from its IBGP peer, the router cannot use this route or advertise this route to its EBGP peer unless the router learns this route from an IGP. In this situation, IBGP routes and IGP routes need to be synchronized. This rule is also called BGP synchronization rule.
- In the figure:
  - R4 has a route to 10.0.4.0/24, which is advertised to R2.
  - R2 advertises the route to its indirectly connected IBGP peer R3.
  - R3 advertises the route to R5.
  - R5 initiates an access request to 10.0.4.4.

### BGP Route Advertisement Rule 4 (2)

Navigation breadcrumb: **Advertisement Rule** highlighted.

Diagram description: Same topology as the previous slide (R1 running OSPF, R2 and R3 connected via IBGP, R2–R4 EBGP, R3–R5 EBGP). A green dashed line labeled "R5 accesses a data packet at 10.0.4.4" traces the path of a packet: R5 sends the packet to R3 (step ①); R3, finding a BGP route with next hop R2 (an indirect next hop), recurses the route through IGP and forwards the packet toward R1 (step ②); R1, having no route to 10.0.4.4 (since R1 does not run BGP and has no IBGP peer relationship with R2), discards the packet (step ③).

- R5 accesses 10.0.4.4.
  - R5 searches the routing table and sends the packet to R3.
  - After receiving the packet, R3 searches the routing table and finds a BGP route with the next hop being R2. R2 is an indirect next hop and needs to recurse routes. The route learned through IGP is recursed to R1. R3 sends the packet to R1.
  - After receiving the packet, R1 searches the routing table. Because R1 is not a BGP router and does not establish an IBGP peer relationship with R2, R1 does not have the BGP route to 10.0.4.0/24. As a result, R1 does not find the matching route and discards the packet.

- The root cause of this problem is that the BGP-incapable router in AS 200 does not have the route learned from BGP. As a result, R1 fails to find the route and discards the packet. BGP synchronization is defined as follows: BGP routes are advertised only when they exist in the IGP routing table. For example, in the figure, when R3 finds that the OSPF routing table does not contain the route to 10.0.4.0/24, R3 does not advertise the route to R5. This prevents subsequent access failures.
- The solutions are as follows:
  - BGP routes are redistributed to an IGP. This mode is seldom used.
  - Fully-mesh IBGP peer relationships are established so that all routers on the network have BGP routes.

## Contents

1. Introduction to BGP
2. Basic Concepts of BGP
3. Basic BGP Configurations

## 3. Basic BGP Configurations

### BGP Configuration

1. Start a BGP process, specify the local AS number, and enter the BGP view.

```
[Huawei] bgp { as-number-plain | as-number-dot }
[Huawei-bgp] router-id ipv4-address
```

When running the **router-id** command to configure the BGP router ID, you are advised to set the BGP router ID to the IP address of the loopback interface on the device.

2. Create a BGP peer and specify the peer address and AS number.

```
[Huawei-bgp] peer { ipv4-address | ipv6-address } as-number { as-number-plain | as-number-dot }
```

3. Configure the source address used to establish the peer relationship and the maximum number of hops of an EBGP peer.

```
[Huawei-bgp] peer ipv4-address connect-interface interface-type interface-number [ ipv4-source-address ]
[Huawei-bgp] peer ipv4-address ebgp-max-hop [ hop-count ]
```

In this case, you can also specify the source address used for establishing a connection. By default, the maximum number of hops allowed for an EBGP connection is 1. That is, an EBGP connection must be established on a directly connected physical link.

- If the router ID is not set, BGP selects the router ID in the system view as the router ID. For router ID selection rules in the system view, see the description about the router-id command.

### Configuration Example (1)

Diagram description: Within AS 100, routers R1 and R2 run OSPF; R1 and R3 (R3 sitting on the boundary of AS 100) have a dashed red "IBGP peer" line drawn diagonally between them. R3 connects via a red dashed "EBGP peer" line to router R4 in AS 200, over interconnection addresses 10.0.34.3/24 (R3 side) and 10.0.34.4/24 (R4 side).

- The figure shows BGP peer relationships, AS numbers, and device interconnection addresses.
- The IP address of Loopback1 on each device is 10.0.x.x/32, where x is the device ID. All devices use the IP address of Loopback1 as the router ID.
- R1 and R3 establish an IBGP peer relationship using the IP address of Loopback1 as the source address of a TCP connection; R3 and R4 establish an EBGP peer relationship using the IP address of the interconnected interface as the source address.

R1 configuration:
```
[R1] bgp 100
[R1-bgp] router-id 10.0.1.1
[R1-bgp] peer 10.0.3.3 as-number 100
[R1-bgp] peer 10.0.3.3 connect-interface LoopBack1
```

R3 configuration:
```
[R3] bgp 100
[R3-bgp] router-id 10.0.3.3
[R3-bgp] peer 10.0.1.1 as-number 100
[R3-bgp] peer 10.0.1.1 connect-interface LoopBack1
[R3-bgp] peer 10.0.34.4 as-number 200
```

### Configuration Example (2)

Diagram description: Same topology as the previous slide (R1 and R2 in AS 100 running OSPF; R1–R3 IBGP peer; R3–R4 EBGP peer over 10.0.34.3/24–10.0.34.4/24).

- The figure shows BGP peer relationships, AS numbers, and device interconnection addresses.
- The IP address of Loopback1 on each device is 10.0.x.x/32, where x is the device ID. All devices use the IP address of Loopback1 as the router ID.
- R1 and R3 establish an IBGP peer relationship using the IP address of Loopback1 as the source address of a TCP connection; R3 and R4 establish an EBGP peer relationship using the IP address of the interconnected interface as the source address.

R4 configuration:
```
[R4] bgp 200
[R4-bgp] router-id 10.0.4.4
[R4-bgp] peer 10.0.34.3 as-number 100
```

### Configuration Example (3)

Check the BGP peer relationship on R3.

```
<R3> display bgp peer
 BGP Local router ID : 10.0.3.3
 local AS number : 100
 Total number of peers : 2         Peers in established state : 2

 Peer         V   AS   MsgRcvd  MsgSent  OutQ  Up/Down    State         PrefRcv
 10.0.1.1     4   100        0        0     0  00:00:07   Established        0
 10.0.34.4    4   200       32       35     0  00:17:49   Established        0
```

### Quiz

1. (Essay) What is the TCP destination port number used by BGP?

   **Answer: 179**

2. (Essay) What types of BGP peer relationships? What is the basis for classification?

   **Answer: BGP peer relationships fall into IBGP and EBGP peer relationships, which are classified based on whether the two devices belong to the same AS.**

3. (Multiple) Which of the following messages are used to establish a BGP peer relationship and update routes? ( )
   A. Route-refresh
   B. Open
   C. Notification
   D. Update

   **Answer: BD**

---

**Notes on possible source anomalies / annotations (flagged, not corrected):**

- The slide "BGP Message Types (1)" contains speaker notes that are incomplete in the source PDF — the descriptions for "Notification" and "Route-refresh" message types are left blank in that note block (they are fully described later on the dedicated "BGP Message Format: Notification" and "BGP Message Format: Route-refresh" slides, which are included above in full).
- Several slides in this deck contain additional handwritten-style learner annotations (found underneath the official Huawei speaker notes in the source PDF) that are not part of Huawei's original course material. These have been preserved above, each clearly labeled "**Learner note**," so they are not mistaken for official Huawei content. One such note (under "Advertisement Rule") was significantly garbled by OCR in the source (missing letters, e.g., "t" instead of "it," "restr ct" instead of "restrict") and has been reconstructed for readability while preserving its original meaning; this is flagged here rather than silently presented as a clean transcription.

