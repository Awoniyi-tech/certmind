# IP Routing Basics

## Objectives

- On completion of this course, you will be able to:
  - Identify the IP routing table and FIB table.
  - Analyze the route-based forwarding process.
  - Describe the principles of route import.
  - Understand application scenarios of route import.

## Contents

1. IP Routing Basics
2. Advanced Applications of IP Routing

## 1. IP Routing Basics

### Overview of IP Routing

Diagram description: PC1 (192.168.11.1/24) is connected via interface GE0/0/0 to a router (highlighted blue). That router has additional interfaces GE0/0/1 and GE0/0/2 connecting into a mesh of routers. The topology shows several routers interconnected (a small mesh network), with a highlighted path (shown in orange/red) running from the router connected to PC1, across the mesh, to a router connected to PC2 (192.168.21.1/24). Arrows indicate the direction of IP packet flow from PC1 through the router mesh to PC2.

- When receiving an IP packet, a router matches the destination address of the IP packet with a routing entry.
  - If the IP packet matches a routing entry, the router forwards the packet according to the outbound interface or next hop in the routing entry.
  - If the IP packet does not match any routing entry, the router does not have routing information to guide packet forwarding. In this case, the router discards the packet.

### RIB and FIB

- A network device that provides the routing function maintains two important data tables: Routing Information Base (RIB) and Forwarding Information Base (FIB).

Diagram description: The diagram shows the control plane and data plane of a router. On the control plane, multiple sources feed into a "Route selection" process: Direct route → Direct routing table; Static route → Static routing table; OSPF process 1 → OSPF process 1 RIB table; "..." (other protocols); IS-IS process 1 → IS-IS process 1 RIB table. These routing tables feed into "Route selection," which populates the RIB (shown as a box on the control plane). The RIB is then "Downloaded" (arrow pointing down) to the FIB on the data plane. An IP packet arrives and is matched against the FIB to determine forwarding. Annotations note: "A router maintains a local core RIB table and RIB tables of routing protocols" (referring to the control-plane tables), and "The router downloads the optimal route from the local core routing table to the FIB table. The forwarding chip of the router forwards packets according to the FIB table."

- RIB table:
  - A RIB table can be considered to be located on the control plane of a router. Actually, a RIB table does not directly guide data forwarding. When a router queries routes, it does not query the destination address of a packet in the RIB table. Instead, it queries the FIB table to guide data forwarding. The router downloads the optimal route from the RIB table to the FIB table. If related entries in the RIB table change, the FIB table is synchronized immediately.
  - Because the two tables are consistent and the RIB table is easy to read, the RIB table (routing table) is used in most cases to describe the data forwarding process of a router. Actually, the router queries the FIB table, and the RIB table at the control layer provides only routing information.
- FIB table:
  - The FIB table is located on the data plane of a router and is also called the forwarding table. Each forwarding entry specifies the outbound interface and next-hop IP address for reaching a destination.
- Note:
  - Huawei routers and Layer 3 switches provide the routing function. This course uses routers as an example.
  - Both OSPF and Intermediate System to Intermediate System (IS-IS) use the Shortest Path First (SPF) algorithm to calculate routes based on link state information. For details about OSPF and IS-IS, see the following courses.
  - Routing process: A router supports multiple OSPF and IS-IS processes. Different processes can be assigned based on service types, and they are independent of each other. An OSPF process ID takes effect on the local device, and does not affect packet exchange between the local route and other routers. Packets can be exchanged between routers with different process IDs.

### RIB Table

- Each router has a RIB table. RIB tables fall into the local core routing table and protocol routing tables.

| Protocol Routing Table | Local Core Routing Table |
|---|---|
| A protocol routing table stores routing information discovered by the protocol. OSPF is used as an example. | Each router stores a local core routing table. A router preferentially selects the same entries in the routing table of each protocol to obtain the local core routing table, and then delivers the local core routes to the FIB table to guide packet forwarding. |

Diagram description: Two example tables are shown side by side.

Left (Protocol Routing Table — OSPF example):
```
Public routing table : OSPF
      Destinations : 1        Routes : 1

OSPF routing table status : <Active>
      Destinations : 1        Routes : 1
Destination/Mask    Proto   Pre    Cost   NextHop     Interface
10.3.3.3/32          OSPF    10     1      10.0.1.1    GigabitEthernet0/0/0

OSPF routing table status : <Inactive>
      Destinations : 0        Routes : 0
```

Right (Local Core Routing Table):
```
Routing Tables: Public
       Destinations : 10       Routes : 10
Destination/Mask    Proto  Pre  Cost  NextHop    Interface
0.0.0.0/0            Static 60   0    10.0.2.2   GigabitEthernet0/0/1
10.3.3.3/32           OSPF   10   1    10.0.1.1   GigabitEthernet0/0/0
10.4.4.4/32           EBGP  255   0    10.0.2.2   GigabitEthernet0/0/1
10.0.1.0/24           Direct  0   0    10.0.1.2   GigabitEthernet0/0/0
10.0.1.2/32           Direct  0   0    127.0.0.1  InLoopBack0
10.0.3.0/24           EBGP  255   0    10.0.2.2   GigabitEthernet0/0/1
127.0.0.0/8           Direct  0   0    127.0.0.1  InLoopBack0
127.0.0.1/32          Direct  0   0    127.0.0.1  InLoopBack0
```

- The optimal route in the local core routing table is selected based on the preference and metric of each routing protocol.

- Key fields in a routing table:
  - Destination: indicates the destination address of a route. It identifies the destination IP address or destination network segment of IP packets.
  - Mask: indicates the subnet mask of the destination IP address. It is used with the destination address to identify the address of the network segment where the destination host or router is located.
  - Proto (protocol): indicates the protocol through which routes are learned.
  - Pre (Preference): indicates the routing protocol preference of the route.
    - Routers define external and internal preferences. The external preference can be manually configured for each routing protocol, while the internal preference cannot be manually modified.
    - During route selection, a router first compares the external preferences of routes. When the same external preference is set for different routing protocols, the router selects the optimal route based on the internal preference.
  - Cost: indicates the cost of a route.
  - NextHop: indicates the next hop to the destination network. It specifies the next-hop device to which packets are forwarded.
  - Interface: indicates the outbound interface that forwards packets to the destination network. It specifies the local router interface from which packets are forwarded.
- The Preference value is used to compare the preferences of different routing protocols, while the Cost value is used to compare the preferences of different routes of the same routing protocol.
- Note: The routing table in the body is truncated.

### Longest Match Principle for IP Route Query

- When searching the FIB table, a router performs the "AND" operation on the destination address in a packet and the network mask of each entry in the FIB table. The router then compares the result of the "AND" operation with entries in the FIB table.
- According to the comparison, the router selects the optimal route to forward packets according to the longest match.

Diagram description: A callout box shows sample output of the FIB table (see code block below). Beside it, a question box asks: "If the destination IP address of a data packet is 10.3.3.3, which interface does the router forward the data packet?"

```
[Huawei] display fib 0
Route Flags: G - Gateway Route, H - Host Route, U - Up Route
             S - Static Route, D - Dynamic Route, B - Black Hole Route

FIB Table:
Total number of Routes : 8

Destination/Mask    Nexthop     Flag  TimeStamp  Interface   TunnelID
10.3.3.3/32         10.0.1.1    DGHU  t[15123]   GE0/0/0     0x0
10.4.4.4/32         10.0.2.2    DGHU  t[11177]   GE0/0/1     0x0
10.0.1.2/32         127.0.0.1   HU    t[9058]    InLoop0     0x0
127.0.0.1/32        127.0.0.1   HU    t[19]      InLoop0     0x0
127.0.0.0/8         127.0.0.1   U     t[19]      InLoop0     0x0
0.0.0.0/0           10.0.2.2    GSU   t[122]     GE0/0/1     0x0
10.0.1.0/24         10.0.2.2    U     t[9058]    GE0/0/0     0x0
10.0.3.0/24         10.0.2.2    DGU   t[11177]   GE0/0/1     0x0
```

- Each entry in the FIB table contains the physical or logical interface through which a packet is sent to a network segment or host to reach the next-hop router. An entry also indicates whether the packet can be sent to a destination host on a directly connected network.
- The **display fib** [ *slot-id* ] command is used to check information about the FIB table.
  - slot-id: displays information about the FIB table with a specified slot ID. The value is an integer, and the value range depends on the device configuration.
- Fields in the FIB table:
  - Total number of Routes: indicates the total number of routes in the routing table.
  - Destination/Mask: indicates the destination address or mask length.
  - Nexthop: indicates the next hop.
  - Flag: indicates the current flag, which is the combination of G, H, U, S, D, and B.
    - G (Gateway): indicates that the next hop is a gateway.
    - H (Host): indicates that the next hop is a host.
    - U (Up): indicates that the route status is Up.
    - S (Static): indicates the static route.
    - D (Dynamic): indicates the dynamic route.
    - B (Blackhole): indicates the blackhole route, with the next hop as a null interface.

### Route Types

Diagram description: Three side-by-side panels compare Direct Route, Static Route, and Dynamic Route.

- Direct Route panel: Shows a PC (192.168.11.0/24) connected via GE0/0/0 to a router, which connects via GE0/0/1 (10.0.12.0/24) to a second router. A table lists: Direct route → 192.168.11.0/24 → GE0/0/0; Direct route → 10.0.12.0/24 → GE0/0/1.
- Static Route panel: Shows a network 192.168.21.0/24 connected through a router mesh, with a static route configured. A table lists: Static route → 192.168.21.0/24 → GE0/0/1.
- Dynamic Route panel: Shows a router mesh with network 192.168.31.0/24, labeled "Dynamic routing protocol Example: OSPF." A table lists: OSPF → 192.168.31.0/24 → GE0/0/1.

- Direct routes are destined for the subnets to which directly connected interfaces belong. They are automatically generated by devices.
- Static routes are manually configured by network administrators.
- Dynamic routes are learned by dynamic routing protocols, such as OSPF, IS-IS, and Border Gateway Protocol (BGP).
  - The Border Gateway Protocol (BGP) is a distance vector routing protocol that allows devices in different ASs to communicate and select optimal routes.
  - An AS is a group of IP networks that are controlled by one entity, typically an Internet service provider (ISP), and have the same routing policy.

### Dynamic Routing Protocols

- Dynamic routing protocols are classified into the following types based on application scopes:
  - Interior Gateway Protocols (IGPs): run inside an autonomous system (AS), including the OSPF and IS-IS.
  - Exterior Gateway Protocols (EGPs): run between ASs, including the Border Gateway Protocol (BGP).

Diagram description: Company A's network (containing subnets 192.168.11.0/24, 192.168.12.0/24, 192.168.13.0/24, ...) runs OSPF internally and connects via two routers to ASBR1 and ASBR2. ASBR1/ASBR2 connect via BGP to ASBR3/ASBR4, which belong to Company B's network. Company B's network runs IS-IS internally and contains subnets 192.168.21.0/24, 192.168.22.0/24, 192.168.23.0/24, .... This illustrates OSPF (IGP) inside Company A, BGP (EGP) between the two companies' AS border routers, and IS-IS (IGP) inside Company B.

### Route Recursion

- Routes can be used to forward traffic only when they have directly connected next hops. However, a static or BGP route may contain an indirect next hop. Therefore, in a process referred to as route recursion, a device needs to search for a directly connected next hop for the route.

Diagram description: Three routers R1, R2, R3 are chained together. R1's interface GE0/0/0 (10.0.12.1/24) connects to R2's interface GE0/0/0 (10.0.12.2/24). R2's interface GE0/0/1 (10.0.23.2/24) connects to R3's interface GE0/0/1 (10.0.23.3/24), which is on network 192.168.21.0/24. A callout box shows: `ip route-static 192.168.21.0 24 10.0.23.3` recursing (arrow labeled "Recursion") to `ip route-static 10.0.23.0 24 10.0.12.2`. A table lists two destination entries for R1:

| Destination Network | Next Hop | Outbound Interface |
|---|---|---|
| 192.168.21.0/24 | 10.0.23.3 | GE0/0/0 |
| 10.0.23.0/24 | 10.0.12.2 | GE0/0/0 |

- Obtain the directly connected next hop through recursion. In this example, a route to 10.0.23.3 is added to R1 so that the route to 192.168.21.0/24 can be recursive.

### Data Forwarding Process

Diagram description: PC1 (192.168.11.1/24) sends a packet with destination IP address 192.168.21.1 to its gateway router (labeled "Gate," step 1) via GE0/0/1. The gateway router (R1, GE0/0/0, 10.0.12.1) forwards it (step 2) across network 10.0.12.0/24 to R2 (GE0/0/0, 10.0.12.2). R2 (step 3) uses its routing table to forward the packet via GE0/0/1 (10.0.23.2) across network 10.0.23.0/24 to R3 (GE0/0/0, 10.0.23.3). R3, acting as the gateway for PC2 (step 4), forwards the packet out GE0/0/1 (10.0.23... /192.168.21.2) to PC2 (192.168.21.2/24). Each router's routing table is shown beneath it:

R1's routing table:

| Destination/Mask | Next Hop | Outbound Interface |
|---|---|---|
| 10.0.12.0/24 | 10.0.12.1 | GE0/0/0 |
| 10.0.23.0/24 | 10.0.12.2 | GE0/0/0 |
| 192.168.11.0/24 | 192.168.11.2 | GE0/0/1 |
| 192.168.21.0/24 | 10.0.12.2 | GE0/0/0 |

R2's routing table:

| Destination/Mask | Next Hop | Outbound Interface |
|---|---|---|
| 10.0.12.0/24 | 10.0.12.2 | GE0/0/0 |
| 10.0.23.0/24 | 10.0.23.2 | GE0/0/1 |
| 192.168.11.0/24 | 10.0.12.1 | GE0/0/0 |
| 192.168.21.0/24 | 10.0.23.3 | GE0/0/1 |

R3's routing table:

| Destination/Mask | Next Hop | Outbound Interface |
|---|---|---|
| 10.0.12.0/24 | 10.0.23.2 | GE0/0/0 |
| 10.0.23.0/24 | 10.0.23.3 | GE0/0/0 |
| 192.168.11.0/24 | 10.0.23.2 | GE0/0/0 |
| 192.168.21.0/24 | 192.168.21.2 | GE0/0/1 |

- The process for PC1 to send a data packet to PC2 is as follows:
  1. PC1 sends the packet to the gateway R1.
  2. R1 searches the routing table for the next hop and outbound interface, and forwards the packet to R2.
  3. R2 forwards the packet to R3 based on the routing table.
  4. After receiving the packet, R3 looks up the routing table and finds that the destination IP address of the packet belongs to the network segment where the local interface resides. R3 then forwards the packet locally and finally sends the packet to the destination PC2.

## 2. Advanced Applications of IP Routing

### Scenario Analysis of Advanced Applications of IP Routing (1)

Diagram description: Company A's network (subnets 192.168.11.0/24, 192.168.12.0/24, 192.168.13.0/24, ...) runs OSPF and connects through routers R1 and R2 to a middle segment labeled "OSPF/IS-IS" (highlighted in red/orange), which connects to routers R3 and R4 running IS-IS, which in turn connect to Company B's network (subnets 192.168.21.0/24, 192.168.22.0/24, 192.168.23.0/24, ...).

- Scenario:
  - Assume that company A and company B have their own networks, which are managed and maintained independently. The networks of company A and company B run OSPF and IS-IS, respectively.
  - After the two companies are merged into one company, the original two networks must be integrated. To ensure that service traffic of the new company can be normally exchanged on the integrated network, the company requires interworking based on routing.

- OSPF and IS-IS are two different dynamic routing protocols, so they cannot directly exchange routing information.
- In the figure, OSPF is deployed on the network of company A, and R1 and R2 are edge devices. IS-IS is deployed on the network of company B, and R3 and R4 are edge devices. OSPF or IS-IS can be deployed on the connected network segments of borders. For example, OSPF can be deployed on network segments between R1 and R3 and between R2 and R4. In this case, only R3 and R4 are border devices.

### Scenario Analysis of Advanced Applications of IP Routing (2)

Diagram description: A three-tier hierarchical network is shown. Top tier: "HQ Backbone network" running BGP between two routers. Middle tier: "Branch Region core" running IS-IS, with routers cross-connected to the tier above and below. Bottom tier: "Municipal company LAN" running OSPF/Static routing, with multiple router/switch pairs (shown as repeating "...") cross-connected upward into the region core.

- Scenario:
  - On a large-scale enterprise network, a single routing protocol cannot meet network requirements. In most cases, multiple routing protocols coexist.
  - In addition, different routing protocols are designed and deployed in different network topologies considering the service logic or administrative management, making the routing hierarchy clear and controllable.
  - In such a network environment, interworking based on routing also needs to be implemented.

### Basic Concept of Route Import

Diagram description: An OSPF network (containing subnets 192.168.11.0/24, 192.168.12.0/24, 192.168.13.0/24, ...) connects via routers R1 and R2 to an IS-IS network (containing subnets 192.168.21.0/24, 192.168.22.0/24, 192.168.23.0/24, ...). A caption beneath states: "Routing information of two routing protocols is isolated from each other." A side panel states: "To implement interworking based on routing, perform the following operations: 1. Re-plan and modify network-wide routing protocols, which is complex. 2. Perform operations on the edge devices in OSPF and IS-IS routing domains so that routing information can be transmitted between OSPF and IS-IS. This solution does not change the original topology and is easy to deploy. However, loops may occur."

- Route import refers to the process of advertising routing information from one routing protocol to another.
  - Route import allows routing information to be transmitted between different routing protocols.
  - When importing routes, you can deploy route control to flexibly control service traffic.

- In the figure, OSPF and IS-IS networks have different network segments. Only R1 and R2 know all routing entries.
- Question: How do all devices obtain all routes?

### Direction of Route Import

- Route import is directional. If routing information is imported from routing protocol A to routing protocol B, routing protocol B can learn routing information about routing protocol A. However, routing protocol A does not know routing information about routing protocol B, unless route import from routing protocol B to routing protocol A is configured.
- When importing routes, pay attention to the following points:
  - Route preference
  - Route injection
  - Route metric

Diagram description: An OSPF network on the left connects through router R1 to an IS-IS network on the right. Curved arrows above and below R1 indicate two directions of import: "Import OSPF routes into IS-IS" and "Import IS-IS route into OSPF." The OSPF side lists subnets 192.168.11.0/24, 192.168.12.0/24, 192.168.13.0/24, ...; the IS-IS side lists subnets 192.168.21.0/24, 192.168.22.0/24, 192.168.23.0/24, .... A question beneath asks: "Can two networks communicate with each other if only OSPF routes are imported to IS-IS?"

- During route import, focus on the route convergence time. This course does not describe the route convergence time.
- The implementation and configuration of route import will be described in other HCIP-Datacom certification courses.

### Route Import: Route Preference

Diagram description: A diagram shows a direct route 10.1.1.0/24 (step 1, "Import direct route") entering router R1 on the boundary between an OSPF domain (left, containing routers R1, R2, R3) and an IS-IS domain (right, containing routers R2, R3, R4). Step 2 shows the OSPF route being learned via R1→R3 within OSPF. Step 3, labeled "Import OSPF routes into IS-IS," shows R2 importing OSPF routes into IS-IS. Step 4 shows the IS-IS route propagating from R2/R4 toward R3. Step 5 shows the "Access traffic" (a green line) flowing along path R3→R4→R2→R1, illustrated as the path actually chosen. A legend defines: blue solid arrow = OSPF route, red dashed arrow = IS-IS route, green solid arrow = Access traffic. A small table shows: Destination/Mask 10.1.1.0/24, Proto ISIS, Pre 15.

- Scenario:
  1. R1 imports the direct route 10.1.1.0/24 into OSPF.
  2. R3 learns the route (OSPF external route with the preference of 150) to the network segment 10.1.1.0/24 through OSPF.
  3. R2 imports OSPF routes to the IS-IS process.
  4. R3 also learns the route (the preference is 15) to the network segment 10.1.1.0/24 through IS-IS.
  5. For R3, the IS-IS route has a higher priority than the OSPF external route, so the IS-IS route from R4 is preferred.
- R3 accesses the network segment 10.1.1.0/24 through the path R3->R4->R2->R1, which is the second optimal path.

- Route preferences defined by Huawei:
  - Direct: 0
  - OSPF: 10
  - IS-IS: 5
  - Static: 60
  - OSPF ASE: 150
  - OSPF NSSA: 150
  - IBGP: 255
  - EBGP: 255
- Note: The route preferences may vary with vendors.

### Route Import: Route Injection

Diagram description: A direct route 10.1.1.0/24 (step 1, "Import direct route") enters R1 on the border between an OSPF domain (R1, R2, R3) and an IS-IS domain (R2, R3, R4). Step 2, labeled "Import OSPF route into IS-IS," shows R2 importing the OSPF route into IS-IS, which then propagates (also labeled step 2/4 arrows) within IS-IS toward R4. Step 5, labeled "Import IS-IS route into OSPF," shows R3 importing the IS-IS route back into OSPF, and step 6 shows this re-injected route being advertised again throughout the OSPF domain. A legend defines: blue solid arrow = OSPF route, red dashed arrow = IS-IS route.

- Scenario:
  1. R1 imports the direct route 10.1.1.0/24 to OSPF.
  2. The direct route 10.1.1.0/24 is advertised in the entire OSPF domain.
  3. R2 imports OSPF routes to the IS-IS process.
  4. The direct route 10.1.1.0/24 is advertised in the entire IS-IS domain.
  5. R3 imports IS-IS routes to the OSPF process.
  6. The direct route 10.1.1.0/24 is advertised in the entire OSPF domain again, resulting in route injection.

### Route Import: Route Metric

Diagram description: An OSPF domain (left, containing subnets 192.168.11.0/24 cost=100 and 192.168.12.0/24 cost=200) connects through router R1 to an IS-IS domain (right, containing subnets 192.168.21.0/24 cost=10 and 192.168.22.0/24 cost=10). Curved arrows above and below R1 indicate step 1 "Import OSPF route into IS-IS" and step 2 "Import IS-IS route into OSPF."

- Scenario:
  1. OSPF routes are imported into IS-IS.
  2. IS-IS routes are imported into OSPF.
- Different routing protocols define different route metrics. How are metrics of imported routes defined when routes are imported between routing protocols? What are the metrics?

### Route Import Scenario

- Route import involves the following scenarios:
  - Route import between dynamic routing protocols
  - Importing direct routes to a dynamic routing protocol
  - Importing static routes to a dynamic routing protocol

Diagram description: An OSPF domain (left) connects to an IS-IS domain (right) through shared routers. Three import operations are labeled: (1) "Import OSPF routes into IS-IS," shown with a curved arrow at the top boundary router; (2) "Import direct route," shown with a curved arrow on a router directly connected to subnet 192.168.11.0/24; (3) "Import static route," shown with a curved arrow on a router connected via a static route to subnet 192.168.21.0/24.

### Basic Configuration Commands for Route Import

1. Configure OSPF to import external routes.

```
[Huawei-ospf-100] import-route { bgp | direct | static | isis [ process-id-isis ] | ospf [ process-id-ospf ]}
```

In the OSPF view, import BGP routes, direct routes, static routes, IS-IS routes, and routes of other OSPF processes.

- If a device on an OSPF network needs to access a device on the network running a non-OSPF protocol, the OSPF device needs to import routes from the non-OSPF protocol into the OSPF network.

### Case 1: Importing Direct Routes to OSPF

Diagram description: Network segment 192.168.11.0/24 is directly connected to R1. R1 (10.0.12.1) connects to R2 (10.0.12.2/10.0.23.2), which connects to R3 (10.0.23.3), which is running OSPF. A curved arrow at R1 labeled "Import direct route / import-route direct" shows the direct route being imported into OSPF.

R1's routing table:

| Destination/Mask | Protocol | Next Hop |
|---|---|---|
| 192.168.11.0/24 | Direct | 192.168.11.1 |
| 10.0.12.0/24 | Direct | 10.0.12.1 |
| 10.0.23.0/24 | OSPF | 10.0.12.2 |

R3's routing table:

| Destination/Mask | Protocol | Next Hop |
|---|---|---|
| 192.168.11.0/24 | O_ASE | 10.0.23.2 |
| 10.0.12.0/24 | OSPF | 10.0.23.2 |
| 10.0.23.0/24 | Direct | 10.0.23.3 |

- You can run the **import-route direct** command to import all direct routes in the routing table to a dynamic routing protocol.
- The imported routes are advertised as OSPF external routes on the entire OSPF network.

- To enable a device configured with a dynamic routing protocol to advertise the routes of its directly connected interface to a dynamic routing protocol, enable the dynamic routing protocol on the interface. In addition, direct routes can be imported to dynamic routing protocols.
- In the figure:
  - OSPF is deployed on R1, R2, and R3. R1 has a direct network segment 192.168.11.0/24. To enable R2 and R3 to generate a route to 192.168.11.0/24, import the direct route to OSPF on R1.
- Note: On an OSPF network, if the protocol field in the routing table is displayed as O_ASE, the route is an OSPF external route.

### Case 2: Importing Static Routes to OSPF

Diagram description: Network segment 192.168.11.0/24 connects (OSPF not supported on this side) to R1 (10.0.12.1), which connects to R2 (10.0.12.2/10.0.23.2), which connects to R3 (10.0.23.3), running OSPF. A callout shows a static route command pointing left toward 192.168.11.0/24, and a curved arrow at R2 labeled "Import static route / import-route static."

```
ip route-static 192.168.11.0 24 10.0.12.1
```

R2's routing table:

| Destination/Mask | Protocol | Next Hop |
|---|---|---|
| 192.168.11.0/24 | Static | 10.0.12.1 |
| 10.0.12.0/24 | Direct | 10.0.12.2 |
| 10.0.23.0/24 | Direct | 10.0.23.2 |

R3's routing table:

| Destination/Mask | Protocol | Next Hop |
|---|---|---|
| 192.168.11.0/24 | O_ASE | 10.0.23.2 |
| 10.0.23.0/24 | Direct | 10.0.23.3 |

- You can run the **import-route static** command to import all static routes in the routing table to a dynamic routing protocol.
- The imported routes are advertised as OSPF external routes on the entire OSPF network.

- For dynamic routing protocols, static routes are considered as external routes and are not detected by dynamic routing protocols. To enable all devices in a dynamic routing protocol domain to learn a static route, import the static route to the dynamic routing protocol.
- In the figure:
  - R2 and R3 run OSPF, but R1 does not support OSPF. Add a static route pointing to network segment 192.168.11.0/24 and import the static route to OSPF on R2 so that both R2 and R3 can generate a route to 192.168.11.0/24.

### Case 3: Importing IS-IS Routes to OSPF

Diagram description: Network segment 192.168.11.0/24 connects to R1 (10.0.12.1), running IS-IS, which connects to R2 (10.0.12.2/10.0.23.2), which connects to R3 (10.0.23.3), running OSPF. A curved arrow at R2 labeled "Import IS-IS routes / import-route isis 1."

R2's routing table:

| Destination/Mask | Protocol | Next Hop |
|---|---|---|
| 192.168.11.0/24 | IS-IS | 10.0.12.1 |
| 10.0.12.0/24 | Direct | 10.0.12.2 |
| 10.0.23.0/24 | Direct | 10.0.23.2 |

R3's routing table:

| Destination/Mask | Protocol | Next Hop |
|---|---|---|
| 192.168.11.0/24 | O_ASE | 10.0.23.2 |
| 10.0.12.0/24 | O_ASE | 10.0.23.2 |
| 10.0.23.0/24 | Direct | 10.0.23.3 |

- You can run the **import-route isis 1** command to import all IS-IS routes in the routing table to a dynamic routing protocol.
- The imported routes are advertised as OSPF external routes on the entire OSPF network.

- The typical scenario is to import routes from one dynamic routing protocol to another.
- In the figure:
  - IS-IS runs on R1 and R2, and OSPF runs on R2 and R3. The routes maintained by the two protocols are isolated. Therefore, R1 has all routes on the IS-IS network but cannot access the OSPF network. R3 has all routes on the OSPF network but cannot access the IS-IS network. You can configure R2 to import IS-IS routes to OSPF.

### Quiz

1. (Single) If a router has the following four FIB entries, which route is used by the router to forward the IP packet with the destination IP address 10.0.1.1? ( )
   A. 0.0.0.0/0
   B. 10.0.0.0.0/16
   C. 10.0.1.0/24
   D. 10.0.2.0/24

   **Answer: C**

2. (Multiple) Which of the following statements about route import are false? ( )
   A. In the OSPF process of a router, you can run the import-route command to import routes from other OSPF processes.
   B. In the OSPF process of a router, you can run the import-route command to import static routes of the routing table.
   C. On a router, to import routes from routing protocol X to routing protocol Y, you need to run the import-route command in the view of routing protocol X.
   D. After the import-route command is run on a router and the direct route of GE0/0/1 is imported to OSPF, OSPF is activated on the interface and the interface periodically sends Hello packets.

   **Answer: CD**

### Summary

- Different routing protocols have different working mechanisms, so multiple routes may be generated to the same destination network segment. A router selects the optimal route based on the priority of the routing protocol and the route cost, and adds the optimal route to the FIB table. The router forwards data according to the FIB table.
- On a large-scale network running multiple routing protocols, routes are advertised between routing protocols by importing routes. A large number of routes may be imported, and some low-performance devices cannot support the imported routes. Therefore, route control is required to implement on-demand route distribution.
- OSPF, IS-IS, and route control listed in this course will be illustrated in subsequent courses.

---

**Notes on possible source anomalies (flagged, not corrected):**

- On slide "Quiz" question 1, option B is printed in the source as `10.0.0.0.0/16` (with an extra `.0`), which appears to be a typo in the original PDF for `10.0.0.0/16`. Preserved verbatim per instructions.

