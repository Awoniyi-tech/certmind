# BGP Path Attributes and RRs

## Foreword

- Each BGP route has multiple path attributes. When a router advertises a BGP route to its peer, the route carries multiple path attributes. These attributes describe route characteristics that affect BGP route selection in some scenarios.
- IBGP split horizon prevents routing loops in an AS, but also brings the following problem: A BGP route can be only transmitted to one next hop in an AS. If IBGP peers establish full-mesh connections, the load on devices increases.
- This course describes BGP path attributes and route reflectors (RRs).

## Objectives

On completion of this course, you will be able to:
- Describe common BGP path attributes and their functions.
- Describe the concept and application scenarios of BGP RRs.
- Describe the rules and working mechanism of BGP RRs.

## Contents

1. BGP Path Attributes
2. BGP RRs

## 1. BGP Path Attributes

### Path Attributes

Diagram description: Two BGP speakers are shown connected — one in AS 200 and one in AS 300 — exchanging a BGP Update message. The BGP Update message box lists Path Attribute: Origin, Path Attribute: AS_PATH, and Path Attribute: Local_Pref.

- Each BGP route has multiple path attributes.
- When a router advertises a BGP route to its peer, it also advertises the path attributes carried in the route.
- BGP path attributes affect route selection.

### Path Attribute Classification

Diagram description: A classification chart divides BGP path attributes into two main branches — "Well-known" and "Optional" — each split into two sub-types. Well-known splits into "Well-known mandatory" (containing Origin, AS_Path, Next_hop) and "Well-known discretionary" (containing Local_Preference, Atomic_aggregate). Optional splits into "Optional transitive" (containing Aggregator, Community) and "Optional non-transitive" (containing MED, Cluster-List, Originator-ID).

- Well-known attributes can be identified by all BGP routers.
- Well-known attributes are classified into the following types:
  - Well-known mandatory: It must be included in each Update message.
  - Well-known discretionary: It may be included in some Update messages.
- Not all optional attributes need to be identified by BGP routers.
- Optional attributes are classified into the following types:
  - Optional transitive: A BGP device may not identify this type of attribute but still accepts and advertises them to peers.
  - Optional non-transitive: A BGP device may not identify this type of attribute, in which case it ignores them without advertising them to peers.

Note: There are many BGP attributes. This section lists only common BGP attributes.

### Example of BGP Update Messages

```
Border Gateway Protocol - UPDATE Message
    Marker: ffffffffffffffffffffffffffffffff
    Length: 53
    Type: UPDATE Message (2)
    Withdrawn Routes Length: 0
    Total Path Attribute Length: 28
    Path attributes
        Path Attribute - ORIGIN: IGP
        Path Attribute - AS_PATH: 65536 1 2 3
        Path Attribute - NEXT_HOP: 172.16.1.1
    Network Layer Reachability Information (NLRI)
        30.0.0.0/8
            NLRI prefix length: 8
            NLRI prefix: 30.0.0.0
```

(Path attribute in a BGP Update message: the Path Attribute lines above.)

### AS_Path

**Attribute classification: Well-known Mandatory** (compared against Well-known Discretionary, Optional Transitive, Optional Non-transitive)

Diagram description: A chain of three routers — R1 (AS 100, connected to network 10.0.1.0/24), R2 (AS 200), R3 (AS 300) — connected in sequence. R1 sends a BGP Update to R2 with AS_Path: 100 and NLRI: 10.0.1.0/24. R2 forwards a BGP Update to R3 with AS_Path: 200 100 and NLRI: 10.0.1.0/24.

- This attribute is a well-known mandatory attribute. It is a list of AS numbers that the route to the destination network passes through.
- Function: Ensures that routes are transmitted between EBGP peers without loops. In addition, it is one of the attributes used for route selection.
- When a route is advertised to an EBGP peer, the router adds the local AS number to the AS_Path of the route. When a route is advertised to an IBGP peer, the AS_Path remains unchanged.

### AS_Path Prevents Loops

**Attribute classification: Well-known Mandatory**

Diagram description: Four routers form a ring — R1 (AS 100, connected to network 10.0.1.0/24), R2 (AS 200), R3 (AS 300), R4 (AS 400) — connected R1–R2–R3–R4–R1. A BGP Update flows in sequence: step 1 R1→R2, step 2 R2→R3, step 3 R3→R4, step 4 R4→R1. By the time the update reaches R4 to send back to R1, the AS_Path attribute is "400 300 200 100" with NLRI: 10.0.1.0/24.

The AS_Path attribute in the BGP Update message sent by R1 to R4 is 400 300 200 100. R1 does not accept the route because it has its own AS number. This prevents routing loops.

Note (speaker note from PDF): What we mean by it having its own AS number is that it has its own unique number, like the 100 within the AS numbers it receives. Once you find your own AS number inside the received AS_path, you must not accept it. This is to prevent loops.

### AS_Path Affects Route Selection

**Attribute classification: Well-known Mandatory**

Diagram description: R1 (AS 100, connected to network 10.0.1.0/24) has two paths toward R5 (AS 500): one path via R2 (AS 200) directly to R5, and another path via R3 (AS 300) then R4 (AS 400) then to R5. The BGP Update arriving at R5 via R2 shows AS_Path: 200 100 and NLRI: 10.0.1.0/24. The BGP Update arriving at R5 via R4 shows AS_Path: 400 300 100 and NLRI: 10.0.1.0/24.

The AS_Path attribute affects BGP route selection. As shown in the figure, R5 learns BGP routes to the 10.0.1.0/24 network segment from both R2 and R4. If other conditions are the same, R5 preferentially selects the routes advertised by R2. This is because the AS_Path attribute of the route is short, that is, the number of AS numbers is small.

### AS_Path Types

**Attribute classification: Well-known Mandatory**

Diagram description (AS_SEQUENCE, left side): Three routers in sequence — R1 (AS 100), R2 (AS 200), R3 (AS 300) — with a BGP Update flowing from R1 to R3. The resulting AS_PATH attribute box shows: type=AS_SEQENCE, value=200 100.

Diagram description (AS_SET, right side): R1 (AS 100) connects to two networks 10.0.1.0/24 and 10.0.2.0/24, and connects to R3 (AS 300). R2 (AS 200) connects to two networks 10.0.3.0/24 and 10.0.4.0/24, and also connects to R3 (AS 300). R3 summarizes the route 10.0.0.0/16 and adds the AS_SET keyword. The resulting AS_PATH attribute value is: AS_PATH=300 {100, 200} (including AS_SEQENCE and AS_SET). R4 is shown downstream of R3.

AS numbers in the AS_Path are in an ordered list. By default, the AS_Path is of this type (i.e., AS_SEQUENCE).

- Route summarization reduces the device burden and shields specific routes to reduce the impact of route flapping. After routes are summarized, the AS_Path attribute is lost, which may cause routing loops. Therefore, the AS_Path of the AS_SET type can be used to carry AS numbers before route summarization.
- If the summarized route needs to carry the numbers of ASs through which all specific routes pass so as to prevent routing loops, you can specify the as-set parameter in the aggregate command.
- In the example of AS_SET, if routes are summarized in AS 300 and the as-set parameter is configured, the AS_Paths of specific routes are represented by an AS-Set set. The AS numbers in the brackets ({}) are not listed in sequence. The summarized route carries AS numbers to prevent loops.
- In addition to AS_SET and AS_AS_SEQENCE, AS_Path also has two types: AS_Confed_Sequence and AS_Confed_Set, which are used in BGP confederation and are not involved in this course.

### Changing the AS_Path

**Attribute classification: Well-known Mandatory**

You can use a route-policy to modify the AS_Path attribute of a BGP route in one of the following modes:

Diagram description: Three side-by-side transformation boxes labeled "additive," "overwrite," and "none overwrite," each showing an input AS_Path, an applied route-policy command, and the resulting AS_Path.

| Mode | Input AS_Path | Command Applied | Resulting AS_Path | Description |
|------|--------------|------------------|--------------------|-------------|
| additive | AS_Path: 100 | apply as-path 300 additive | AS_Path: 300 100 | Add a new AS_Path value, which is placed preceding original AS_Path value. |
| overwrite | AS_Path: 100 200 300 | apply as-path 400 overwrite | AS_Path: 400 | Replace the existing AS_Path value with a new value. |
| none overwrite | AS_Path: 100 200 300 | apply as-path none overwrite | AS_Path: (empty) | Delete the existing AS_Path value. |

### Origin

**Attribute classification: Well-known Mandatory**

- This attribute is a well-known mandatory attribute and identifies the origin of a BGP route. As described in the table, the Origin attribute is classified into three types based on the mode in which routes are imported to BGP.
- If multiple routes with different Origin attributes are destined for the same destination and other conditions are the same, routes with Origin attributes of IGP, EGP, and Incomplete are in descending order of priority.

| Type | Flag | Description |
|------|------|-------------|
| IGP | i | If the route is imported to BGP by the originating BGP router through the **network** command, the Origin attribute of the BGP route is IGP. |
| EGP | e | If the route is learned through an EGP, the Origin attribute of the BGP route is EGP. |
| Incomplete | ? | If the route is learned in other modes but not the preceding two modes, the Origin attribute is Incomplete. For example, routes are imported to BGP using the **import-route** command. |

### Origin Attribute in the BGP Routing Table

**Attribute classification: Well-known Mandatory**

```
[R2] display bgp routing-table
BGP Local router ID is 10.0.2.2
Status codes: * - valid, > - best, d - damped,
              h - history,  i - internal, s - suppressed, S - Stale
              Origin : i - IGP, e - EGP, ? - incomplete

Total Number of Routes: 4
   Network            NextHop         MED     LocPrf    PrefVal    Path/Ogn

*>i  10.0.1.0/24        10.0.12.1       0       200        0          i
*  i                     10.0.23.3       0       100        0          i
```
(Origin column indicated by arrow beneath Path/Ogn column, showing "i" values.)

### Next_Hop

**Attribute classification: Well-known Mandatory**

- This attribute is a well-known mandatory attribute and is used to specify the next-hop address to the destination network.
- After a router learns a BGP route, it checks the Next_Hop attribute of the BGP route. The Next_Hop attribute (IP address) must be reachable on the local router. If the Next_Hop attribute is unreachable, the BGP route is unavailable.
- The rules for setting the default Next_Hop attribute of BGP routes in different scenarios are as follows:
  - When advertising a BGP route to its EBGP peer, a router sets the Next_Hop attribute of the route to the source IP address of a TCP connection.
  - When receiving a BGP route advertised by an EBGP peer, the router does not change the Next_Hop attribute of the route that is advertised to its IBGP peer.
  - If a router receives a BGP route whose Next_Hop value is on the same network segment as the EBGP peer, the router retains the Next_Hop value of the route and advertises the route to its BGP peer.

### Default Operation for Next_Hop (1)

**Attribute classification: Well-known Mandatory**

Diagram description: AS 100 contains R1 (connected to network 10.0.1.0/24, and to R2 via link 10.0.12.1) and AS 200 contains R2 (address 10.0.12.2, and connected via 10.0.23.2 to R3 at 10.0.23.3). A BGP Update flows from R1 down to R2 with Next_Hop: 10.0.12.1 and NLRI: 10.0.1.0/24.

When advertising a BGP route to its EBGP peer, a router sets the Next_Hop attribute of the route to the source IP address of a TCP connection.

### Default Operation for Next_Hop (2)

**Attribute classification: Well-known Mandatory**

Diagram description: Same topology as previous slide (R1 in AS 100, R2 and R3 in AS 200). The BGP Update from R1 to R2 carries Next_Hop: 10.0.12.1, NLRI: 10.0.1.0/24. R2 then forwards this same update to R3, still showing Next_Hop: 10.0.12.1, NLRI: 10.0.1.0/24 (unchanged).

When receiving a BGP route advertised by an EBGP peer, the router does not change the Next_Hop attribute of the route that is advertised to its IBGP peer.

### Default Operation for Next_Hop (3)

**Attribute classification: Well-known Mandatory**

Diagram description: AS 100 contains R1 and R2 connected via IBGP (address 10.0.123.1 on R1, 10.0.123.2 on R2, with R2 also connected to network 10.0.2.0/24). AS 200 contains R3 (address 10.0.123.3), connected to both R1 and R2 via EBGP on the same shared network segment 10.0.123.0. Arrows show EBGP from R3 to R1, and R1 relaying to R2 via IBGP.

The Next_hop attribute of the route 10.0.2.0/24 received by R3 is 10.0.123.2.

If a router receives a BGP route whose Next_Hop value is on the same network segment as the EBGP peer, the router retains the Next_Hop value of the route and advertises the route to its BGP peer.

### Changing the Next_Hop Attribute

**Attribute classification: Well-known Mandatory**

Diagram description: AS 100 contains R1 (network 10.0.1.0/24, link 10.0.12.1) and AS 200 contains R2 (10.0.12.2, connected via 10.0.23.2 to R3 at 10.0.23.3). A BGP Update flows R1→R2 with Next_Hop: 10.0.12.1, NLRI: 10.0.1.0/24. A configuration box shows the **peer next-hop-local** command being applied on R2. R2 then forwards to R3 a BGP Update with Next_Hop: 10.0.23.2 (changed to R2's own address), NLRI: 10.0.1.0/24.

The **peer next-hop-local** command can be used to configure a BGP device to set the value of the Next_Hop attribute to the source address of a TCP connection for peer relationship setup when the BGP device advertises routes to an IBGP peer or a peer group.

Note (speaker note from PDF): By default, the Next_Hop attribute of the BGP route 10.0.1.0/24 advertised by R2 to R3 is 10.0.12.1. If R2 does not advertise the route 10.0.12.0/24 to the IGP of AS 200, R3 cannot learn the route to 10.0.12.1. In this case, the next hop of the BGP route 10.0.1.0/24 is unreachable, so the route is considered invalid.

```
bgp 200
peer 10.0.23.3 as-number 200
peer 10.0.23.3 next-hop-local
```

### Local_Preference

**Attribute classification: Well-known Discretionary**

Diagram description: R4 (connected to network 10.0.45.0/24) and R5 (also connected to network 10.0.45.0/24) both connect via EBGP to R1 and R3 respectively, which are both inside AS 200 and connect via IBGP to R2. R1 sends a BGP Update to R2 with Local_Preference: 200, NLRI: 10.0.45.0/24. R3 sends a BGP Update to R2 with Local_Preference: 100, NLRI: 10.0.45.0/24.

Note (callout box in PDF): On R1 and R3, configure a routing policy for R2 so that the value of the Local_Preference attribute in the route 10.0.45.0/24 sent by R1 to R2 is 200 and R3 retains the default value of Local_Preference. In this case, the route 10.0.45.0/24 advertised by R1 is preferred.

- The Local_Preference attribute is a well-known discretionary attribute. It can be used to inform routers in an AS of the preferred path to leave the AS.
- A larger value of the Local_Preference attribute indicates a better BGP route. The default value is 100.
- This attribute can be advertised only to IBGP peers but not EBGP peers.

### Checking the Local_Preference Attribute in the BGP Routing Table

**Attribute classification: Well-known Discretionary**

```
[R2] display bgp routing-table
BGP Local router ID is 10.0.2.2
Status codes: * - valid, > - best, d - damped,
              h - history,  i - internal, s - suppressed, S - Stale
              Origin : i - IGP, e - EGP, ? - incomplete

Total Number of Routes: 4
   Network            NextHop         MED     LocPrf    PrefVal    Path/Ogn

*>i  10.0.45.0/24       10.0.12.1       0        200        0          i
*  i                     10.0.23.3       0        100        0          i
```
(LocPrf column indicated as the Local_Preference column.)

The BGP route with the Local_Preference value of 200 takes precedence over the BGP route with the Local_Preference value of 100. In the BGP routing table, the BGP route from 10.0.12.1 is the optimal route.

### Precautions for Local_Preference

**Attribute classification: Well-known Discretionary**

- The Local_Preference attribute can be transmitted only between IBGP peers (the Local_Preference value is not lost during transmission between IBGP peers unless a policy is configured), but cannot be transmitted between EBGP peers. If the AS_Path attribute of a route received between EBGP peers carries Local_Preference, errors may occur in the BGP process.
- However, you can use the inbound policy on the AS border router to change the Local_Preference value. That is, after a route is received, the local device assigns the Local_Preference value to the route.
- You can run the bgp default local-preference command to change the default Local_Preference value. The default value is 100.
- When a router sends a route update to its EBGP peer, the route update cannot carry the Local_Preference attribute. After the peer receives the route, the peer assigns the default Local_Preference value (100) to the route and then advertises the route to its IBGP peer.
- For the routes imported by using the network or import-route commands, the Local_Preference value is 100 by default and can be transmitted to other IBGP peers in the AS. During the transmission, the Local_Preference value remains unchanged unless it is affected by a routing policy.

### Background of the Community Attribute (1)

**Attribute classification: Optional Transitive**

Diagram description: AS 100 contains R1, which connects to two internal groups of routes — "Route to the production network" (10.1.0.0/24, 10.1.1.0/24, 10.1.2.0/24) and "Route to the office network" (10.2.0.0/24, 10.2.1.0/24, 10.2.2.0/24). R1 connects across to AS 200, which contains R2 and R3. BGP routes (both groups) flow from R1 to R2.

Note (callout box in PDF): In AS 100, a large number of routes are imported to BGP. These routes are used on the production and office networks. Currently, BGP routers in AS 200 need to apply different policies to these routes. If filters such as the ACL and IP prefix list are used, the matching efficiency is low.

### Background of the Community Attribute (2)

**Attribute classification: Optional Transitive**

Diagram description: Same topology as previous slide, but now R1 tags outgoing BGP routes with Community values: routes to the "production area" (10.1.0.0/24, 10.1.1.0/24, 10.1.2.0/24) carry Community 100:10, and routes to the "office area" (10.2.0.0/24, 10.2.1.0/24, 10.2.2.0/24) carry Community 100:20, both flowing from R1 to R2/R3 in AS 200.

Note (callout box in PDF): With the Community attribute, different Community attribute values can be added to different types of routes. These attribute values are updated to AS 200 with BGP routes. Therefore, BGP routers in AS 200 only need to implement differentiated policies based on Community attribute values, without considering the specific route prefix.

### Community

**Attribute classification: Optional Transitive**

Diagram description: R1 (connected to network 10.0.1.0/24) in AS 200 (with R2) connects to AS 100. A BGP Update flows from R1 to R2, and then onward, carrying route 10.0.1.0/24 with Community = 12:10000 at each hop.

- The Community attribute is an optional transitive attribute. It is a route tag used to simplify the execution of routing policies.
- You can assign a specific Community attribute value to certain routes. Then the routes can be filtered based on the Community attribute value but not the network prefix or mask and the corresponding policy can be executed.

### Community Attribute Format

**Attribute classification: Optional Transitive**

Diagram description: A conversion diagram shows the Community attribute's 4-byte structure. RFC format splits it into two 2-byte fields labeled AA and NN. Example values: Community AA=12, NN=10000. In hexadecimal notation, AA=0x000C, NN=0x2710, combined as 0x000C2710. This converts to decimal notation: 796432.

The Community attribute has 32 bits, that is, 4 bytes. The value can be in either of the following formats:
- The value is an integer in decimal notation.
- The value is in AA:NN format, in which AA indicates the AS number and NN indicates a user-defined number.

Note: The Community attribute includes self-defined and well-known community attributes.

### Well-known Community Attribute

**Attribute classification: Optional Transitive**

| Community Attribute | Value | Description |
|---------------------|-------|--------------|
| Internet | 0 (0x00000000) | A BGP device can advertise the received route with the Internet attribute to all peers. By default, all routes belong to the Internet community. |
| No_Advertise | 4294967042 (0xFFFFFF02) | A BGP device does not advertise the received route with the No_Advertise attribute to any peer. |
| No_Export | 4294967041 (0xFFFFFF01) | A BGP device does not advertise the received route with the No_Export attribute to devices outside the local AS. |
| No_Export_Subconfed | 4294967043 (0xFFFFFF03) | A BGP device does not advertise the received route with the No_Export_Subconfed attribute to devices outside the local AS or to devices outside the local sub-AS. |

RFC 1997 defines several well-known community attributes, as described in the table.

Note: The No_Export_Subconfed community attribute involves the concept of BGP confederation and is not involved in this course.

### MED

**Attribute classification: Optional Non-transitive**

Diagram description: AS 200 contains R2 and R3, both connected to network 10.0.23.0/24. R2 advertises the BGP route 10.0.23.0/24 with MED = 10 to R4 (in AS 100). R3 advertises the same BGP route 10.0.23.0/24 with MED = 20, also toward R4. R4 in turn advertises the BGP route 10.0.23.0/24 onward to R5 (in AS 300) without carrying the MED.

Note (callout box in PDF): Configure a routing policy on R2 and R3 so that the MED value of the BGP route advertised by R2 to R4 is 10 and the MED value of the BGP route advertised by R3 is 20. If other conditions are the same, R4 preferentially selects the BGP routes advertised by R2.

- The multi-exit discriminator (MED) is an optional non-transitive attribute. It helps determine the optimal route when traffic enters an AS. That is, when there are multiple ingresses to the local AS, the AS can use the MED attribute to dynamically affect the path that other ASs select.
- A smaller MED value indicates a better BGP route.
- The MED is used for BGP route selection between ASs. After an MED is advertised to an EBGP peer, the route advertised by the peer in the AS carries the MED. When the route is advertised to the EBGP peer again, the route does not carry MED by default.

### Precautions for the MED

**Attribute classification: Optional Non-transitive**

- By default, a router compares the MED values of only the BGP routes from the same neighboring AS. That is, if two routes to the same destination are from different neighboring ASs, the router does not compare the MED values of the two routes.
- A BGP router determines whether to carry the MED attribute in a route advertised to its EBGP peers as follows (assume that no policy is configured on the EBGP peers):
  - If the BGP route is locally originated (imported using the network or import-route command), the BGP route carries the MED attribute by default and is sent to the EBGP peer.
  - If a BGP route is learned from a BGP peer, the route advertised to an EBGP peer does not carry the MED attribute by default.
  - When a route is transmitted between IBGP peers, the MED value is retained and transmitted with the route. The MED value will not be changed or lost during the transmission unless a policy is deployed.

### Default Operation for the MED Attribute (1)

**Attribute classification: Optional Non-transitive**

Diagram description: AS 200 contains R1 (connected to network 10.0.1.0/24) and R2, running OSPF between them. AS 100 contains R3, connected to R2 via BGP. The BGP route 10.0.1.0/24 is advertised from R2 to R3 with MED = 100.

- If a router learns a route through an IGP and imports the route to its BGP routing table using the network or import-route command, the MED value of the generated BGP route inherits the IGP metric value of the route. For example, in the preceding figure, R2 learns the route 10.0.1.0/24 through OSPF and the OSPF cost of the route is 100 in the global routing table of R2. When R2 imports the route into its BGP table using the network command, the MED value of the generated BGP route is 100.
- If a router imports a locally direct or static route to BGP using the network or import-route command, the MED of the BGP route is 0 because the cost of the direct or static route is 0.

### Default Operation for the MED Attribute (2)

**Attribute classification: Optional Non-transitive**

Diagram description: AS 200 contains R1 (connected to network 10.0.1.0/24) and R2, running OSPF between them. AS 100 contains R3, and AS 300 contains R4. R2 advertises the BGP route 10.0.1.0/24 to R3 with MED = 999. R3 then advertises the BGP route 10.0.1.0/24 onward to R4 without the MED attribute.

- If a router learns a route from a peer through BGP, the router does not transmit the MED value by default when updating the route to its EBGP peer. That is, the MED attribute is not transmitted across ASs. As shown in the figure, if R3 learns a BGP route with the MED attribute from R2, it advertises the route without the MED attribute to R4 by default.
- You can run the **default med** command to change the default MED value. The default med command takes effect only for the local routes imported using the import-route command and BGP summarized routes. For example, if **default med 999** is configured on R2, R2 advertises the MED value 999 to R3 with the route imported using the import-route command or generated using the aggregate command.

### Atomic_Aggregate and Aggregator

**Attribute classification: Well-known Discretionary and Optional Transitive**

Diagram description: R1 (AS 100, routes 10.0.1.0/24, 10.0.2.0/24) and R2 (AS 200, routes 10.0.3.0/24, 10.0.4.0/24) both connect to R3 (AS 300). R3 summarizes the specific routes into 10.0.0.0/16 and advertises this summarized route onward to R4 (AS 400).

Note (callout box in PDF): On R3, specific routes are summarized to 10.0.0.0/16. Atomic_Aggregate: The summarized route loses path attributes of specific routes, so an alarm needs to be reported to the downstream peer. The alarm contains the summarization device and the AS number of the summarization device.

Atomic_Aggregate is a well-known discretionary attribute, while Aggregator is an optional transitive attribute.

```
bgp 300
aggregate 10.0.0.0 16 detail-suppressed
```

- The aggregate command on R3 summarizes BGP routes 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24, and 10.0.4.0/24 into 10.0.0.0/16, and detail-suppressed is specified to prevent specific routes from being advertised. That is, R3 advertises only the summarized BGP route to R4.
- Atomic_Aggregate is a well-known discretionary attribute. It is a warning flag and does not carry any information. When a router receives a BGP route update and finds that the route carries the Atomic_Aggregate attribute, the router knows that the path attribute of the route may be lost. In this case, the router advertises the route with the Atomic_Aggregate attribute to other peers. In addition, the router that receives the route update cannot further redefine the route.
- The Aggregator attribute is an optional transitive attribute. When route summarization is performed, the router that summarizes routes can add the Aggregator attribute to the summarized route and record the local AS number and its router ID in the attribute. The Aggregator attribute is used to identify the AS and BGP router where routes are summarized.

### Checking the Summarized Route

**Attribute classification: Well-known Discretionary and Optional Transitive**

```
[R4]display bgp routing-table 10.0.0.0 16
BGP local router ID : 10.0.4.4
Local AS number : 400
Paths:   1 available, 1 best, 1 select
BGP routing table entry information of 10.0.0.0/16:
From: 10.0.34.3 (10.0.3.3)
Route Duration: 00h00m21s
Direct Out-interface: GigabitEthernet0/0/0
Original nexthop: 10.0.34.3
Qos information : 0x0
AS-path 300, origin igp, pref-val 0, valid, external, best, select, active, pre 255
Aggregator: AS 300, Aggregator ID 10.0.3.3, Atomic-aggregate
Not advertised to any peer yet
```

In detailed information about BGP routes, the Aggregator attribute records the AS number and router ID of the summarization device. In addition, the Atomic-Aggregate attribute indicates that the route is a summarized route.

### Preferred-Value

Diagram description: R1 and R3 both belong to AS 100, and both connect to network 10.0.13.0/24. R2, in AS 200, has EBGP connections to both R1 and R3, and accesses 10.0.13.0/24 through either path.

Note (callout box in PDF): Configure a routing policy (import policy) on R2 to set the Preferred-Value value of the route 10.0.13.0/24 advertised by R1 to 300 and the Preferred-Value value of the route 10.0.13.0/24 advertised by R3 to 200. In this way, R2 preferentially selects the route sent from R1 to reach 10.0.13.0/24.

- Preferred-Value is a Huawei-specific attribute and is valid only on the local device. If multiple routes are available to the same destination, the route with the largest PrefVal value is selected as the optimal route.
- The value ranges from 0 to 65535. A larger value indicates a higher route priority.
- The Preferred-Value attribute can be configured only on the local router and affects only route selection of the local router. This attribute is not advertised to any BGP peer.

### Checking the Preferred-Value in the BGP Routing Table

```
[R2] display bgp routing-table
BGP Local router ID is 10.0.2.2
Status codes: * - valid, > - best, d - damped,
              h - history,  i - internal, s - suppressed, S - Stale
              Origin : i - IGP, e - EGP, ? - incomplete

Total Number of Routes: 4
   Network            NextHop         MED     LocPrf    PrefVal    Path/Ogn

*>   10.0.13.0/24       10.0.12.1       0                  300        100 i
*                        10.0.23.3       0                  200        100 i
```
(Preferred-Value column indicated as the PrefVal column.)

The BGP route with the Preferred-Value of 300 takes precedence over the BGP route with the Preferred-Value of 200. The BGP route from 10.0.12.1 in the BGP routing table is the optimal route.

Note: The Preferred-Value attribute is abbreviated as PrefVal in the routing table.

## 2. BGP RRs

### IBGP Issues in the Transit AS

Diagram description: AS 100 contains one router connected via BGP peer relationship (dashed red arrows) to a router in AS 200. AS 200 itself contains four routers arranged with full-mesh OSPF connections among them (labeled generically, forming a square with diagonal connections), and one of these routers also has a BGP peer relationship (dashed red arrow) to a router in AS 300.

- To ensure that all BGP routers in AS 200 can learn complete BGP routes, IBGP peers in an AS must establish full-mesh connections. However, there are the following disadvantages:
  - Routers need to maintain a large number of TCP and BGP connections, especially when there are a large number of routers.
  - The BGP network in an AS has poor scalability.
- Therefore, route reflector (RR) technology can be used.

### RR

Diagram description: AS 200 (running OSPF) contains three routers: R1 (the RR, at the top), R2 (Client), and R3, all interconnected via IBGP. R1 reflects a BGP Update (yellow arrows) down to R2 and R3. AS 100 contains R4, connected via BGP to R2, advertising route 10.0.4.0/24 (shown as *>i 10.0.4.0/24 in R2's table). AS 300 contains R5, connected to R3.

- After the RR is imported, there are two roles:
  - RR
  - Client
- An RR reflects learned routes so that IBGP routes are advertised within an AS without establishing full-mesh IBGP connections.
- When specifying a BGP router as an RR, you need to specify its client. The client does not need to be configured and does not know that an RR exists on the network.

### Route Reflection Rules

- When an RR receives BGP routes:
  - If the RR learns an IBGP route from a non-client peer, the RR reflects the route to all clients.
  - If the RR learns an IBGP route from its client, the RR reflects the route to all non-clients and all clients except the client that sends the IBGP route.
  - If a route is learned from an EBGP peer, the route is advertised to all clients and non-client IBGP peers.

Note: An RR reflects only the optimal BGP routes that it uses.

### Reflection Rule Example (1)

**Rule 1:** Diagram description: AS 100 contains R1, connected to AS 200 which contains R2 (the RR), R3 (Client, connected to network 10.0.3.0/24), and R5. R2 reflects (blue dashed arrow) the route learned from non-client peer R3 out to client R4 (shown at the bottom).

If the RR learns an IBGP route from a non-client peer, the RR reflects the route to all clients.

**Rule 2:** Diagram description: AS 100 contains R1, connected to AS 200 which contains R2 (the RR), R3 (Client, connected to network 10.0.3.0/24), R4 (Client), and R5. R3 sends the route to R2; R2 then reflects (blue dashed arrow) the route out to client R4, but not back to R3 (the client that sent it).

If the RR learns an IBGP route from its client, the RR reflects the route to all non-clients and all clients except the client that sends the IBGP route.

### Reflection Rule Example (2)

**Rule 3:** Diagram description: AS 100 contains R1, connected to network 10.0.1.0/24, connected to AS 200 which contains R2 (the RR), R3 (Client), and R5. R1 sends the route via EBGP into R2, and R2 reflects/advertises it to both R3 and R5.

If a route is learned from an EBGP peer, the route is advertised to all clients and non-client IBGP peers.

- Pay attention to the difference between "reflection" and "sending".
- "Sending" refers to traditional BGP route transmission (scenario where the RR does not exist).
- "Reflection" refers to route transmission performed by an RR in compliance with route reflection rules. The RR inserts special path attributes into the reflected routes.

Note: When reflecting routes, the RR does not modify the following BGP path attributes: Next_Hop, AS_Path, Local_Preference, and MED. If the RR modifies these attributes, routing loops may occur.

### Routing Loop Prevention in RR Scenarios

Diagram description: AS 200 contains an RR at the top, with R2 (Client) and R3 (RR) below it, connected via IBGP in a triangle. Step 1: a route update is sent up to the RR. Step 2: the RR reflects the route back down. Step 3: R2 and R3 exchange/reflect further along the dashed blue path.

BGP route reflection may cause routing loops.

- RR deployment breaks the split horizon rule, which may cause routing loops. To prevent routing loops, the RR adds two special path attributes to BGP routes:
  - Originator_ID
  - Cluster_List
- Originator_ID and Cluster_List are optional non-transitive attributes.

### Originator ID

Diagram description: R1 is the RR at the top. R2 (connected to network 10.0.2.0/24, Router ID 10.0.2.2) and R3 (RR) are below, connected via IBGP peer relationships to each other and to R1. Step 1: R2 sends the BGP route 10.0.2.0/24 to R3. Step 2: R3 (acting as RR) reflects the route to R1, adding Originator_ID 10.0.2.2. Step 3: R1 reflects the route back down to R2, still carrying BGP route 10.0.2.0/24 with Originator_ID 10.0.2.2.

Note (callout box in PDF): After R3 receives the BGP route 10.0.2.0/24 from R2, it adds the Originator_ID 10.0.2.2 to the route before reflecting the route to R1. After receiving the route, R1 reflects the Originator_ID to R2. After R2 receives the route, it finds that the Originator_ID contains its own router ID and ignores the route update.

- When reflecting a BGP route, an RR adds the Originator_ID attribute to the reflected route. The Originator_ID attribute value is the router ID of the BGP router that advertises the route in the local AS.
- If multiple RRs exist in an AS, the Originator_ID attribute is created by the first RR and is not changed by subsequent RRs (if any).
- When a BGP router receives an IBGP route with the Originator_ID attribute and the Originator_ID attribute value is the same as its router ID, the BGP router ignores the route update.

### RR Cluster

Diagram description: Two overlapping oval "RR cluster" groupings are shown. RR cluster 1 contains Client R1 and RR R2. RR cluster 2 contains Client R2 (same router, acting as client in this second cluster) and RR R3. R1 and R2 are connected via IBGP; R2 and R3 are connected via IBGP.

- Each RR cluster consists of an RR and clients. An AS can have multiple RR clusters, as shown in the following figure.
- Each cluster has a unique cluster ID (Cluster_ID, which is the BGP router ID of an RR by default).
- Before an RR reflects a route, the RR places the local Cluster_ID on top of the Cluster_List.
- When an RR receives a BGP route carrying the Cluster_list attribute and the Cluster_ID of the RR is contained in the Cluster_List attribute, the RR considers that a loop occurs for the route and ignores the route update.

### Cluster_List

Diagram description: AS 200 contains R4 (the top-level RR), with R1 (RR) and R3 (RR) below it, and R2 at the bottom-left. Router IDs are all in the form 10.0.x.x, where x indicates the device ID. Step 1: R2 sends a route update to R1. Step 2: R1 (RR) reflects the route to R3, adding Originator_ID 10.0.2.2 and Cluster_List 10.0.1.1. Step 3: R3 (RR) reflects the route to R4, updating Cluster_List to 10.0.3.3 10.0.1.1 (keeping Originator_ID 10.0.2.2). Step 4: R4 (RR) reflects the route back toward R1, updating Cluster_List to 10.0.4.4 10.0.3.3 10.0.1.1 (keeping Originator_ID 10.0.2.2).

- A route is sent from R2 to R1. When reflecting the route to R3, R1 adds the Originator_ID and Cluster_List (10.0.1.1) to the route. When R3 reflects the route to R4, the Cluster_List value is 10.0.3.3 10.0.1.1. When R4 reflects the route to R1, the Cluster_List value is 10.0.4.4 10.0.3.3 10.0.1.1.
- When R4 reflects the route to R1, R1 finds that the Cluster_List contains its own Cluster_ID and determines that a loop exists. Therefore, R1 ignores the route update.

### Example of RR Application

Diagram description: AS 100 contains R1, connected to network 10.0.1.0/24, connected via EBGP to R2. AS 200 contains R2, R3 (the RR), R4, and R5, all interconnected via IBGP (R2–R3, R3–R4, R3–R5).

R1 advertises the route 10.0.1.0/24 to BGP. R2 learns the route from R1 and advertises the route to R3. However, the IBGP route learned by R3 from R2 cannot be advertised to R4 or R5 because of the split horizon rule. Therefore, you can configure R3 as an RR and configure R4 and R5 as clients so that R4 and R5 can learn the BGP route 10.0.1.0/24.

### BGP Configuration

1. Specify an RR and its client.
```
[Huawei-bgp] peer {group-name | ipv4-address} reflect-client
```
By default, the RR and its client are not configured.

2. Configure the cluster ID of the RR.
```
[Huawei-bgp] reflector cluster-id cluster-id
```
By default, each RR uses its router ID as the cluster ID.

### Configuration Example (1)

Diagram description: AS 100 contains R1, R2 (RR), and R3 (Client), interconnected via IBGP peer relationships (R1–R2, R2–R3), and running OSPF among all three. R3 connects via EBGP to R4 in AS 200, at link addresses 10.0.34.3 (R3 side) and 10.0.34.4 (R4 side). R4 is connected to network 10.4.4.0/24.

- The IP address of Loopback0 on a device is 10.0.x.x/32, where x is the device ID. All devices use the address of Loopback0 as the BGP router ID.
- R1, R2, and R3 belong to AS 100. OSPF runs in AS 100, and IP addresses of all directly connected interfaces are advertised to OSPF.
- In AS 100, the IP address of the loopback interface is used as the source address for IBGP update. R2 functions as the RR, and R3 functions as the client.
- R4 belongs to AS 200 and uses the IP address of the interconnected interface to establish an EBGP peer relationship with R3. R4 advertises 10.4.4.0/24 to BGP.

**R1 configuration:**
```
[R1] bgp 100
[R1-bgp] router-id 10.0.1.1
[R1-bgp] peer 10.0.2.2  as-number 100
[R1-bgp] peer 10.0.2.2 connect-interface LoopBack0
```

**R2 configuration:**
```
[R2] bgp 100
[R2-bgp] router-id 10.0.2.2
[R2-bgp] peer 10.0.1.1 as-number 100
[R2-bgp] peer 10.0.1.1 connect-interface LoopBack0
[R2-bgp] peer 10.0.3.3 as-number 100
[R2-bgp] peer 10.0.3.3 connect-interface LoopBack0
[R2-bgp] peer 10.0.3.3 reflect-client
```

### Configuration Example (2)

Diagram description: Same topology as Configuration Example (1) — AS 100 contains R1, R2 (RR), R3 (Client) via IBGP/OSPF; R3 connects via EBGP (10.0.34.3/10.0.34.4) to R4 in AS 200, which connects to network 10.4.4.0/24.

- The IP address of Loopback0 on a device is 10.0.x.x/32, where x is the device ID. All devices use the address of Loopback0 as the BGP router ID.
- R1, R2, and R3 belong to AS 100. OSPF runs in AS 100, and IP addresses of all directly connected interfaces are advertised to OSPF.
- In AS 100, the IP address of the loopback interface is used as the source address for IBGP update. R2 functions as the RR, and R3 functions as the client.
- R4 belongs to AS 200 and uses the IP address of the interconnected interface to establish an EBGP peer relationship with R3. R4 advertises 10.4.4.0/24 to BGP.

**R3 configuration:**
```
[R3] bgp 100
[R3-bgp] router-id 10.0.3.3
[R3-bgp] peer 10.0.2.2  as-number 100
[R3-bgp] peer 10.0.2.2 connect-interface LoopBack0
[R3-bgp] peer 10.0.34.4 as-number 200
```

**R4 configuration:**
```
[R4] bgp 200
[R4-bgp] router-id 10.0.4.4
[R4-bgp] peer 10.0.34.3 as-number 100
[R4-bgp] network 10.4.4.0 24
```

Note: The R4 configuration line `[R4-bgp] network 10.4.4.0 24` appears in the source PDF without a subnet mask in dotted-decimal or prefix-length slash notation (i.e., written as "10.4.4.0 24" rather than "10.4.4.0 255.255.255.0" or "10.4.4.0/24"). This is reproduced exactly as shown in the source slide; it may be shorthand notation used by the course rather than a literal CLI typo — worth double-checking against the actual Huawei CLI syntax used elsewhere in this course.

### Configuration Example (3)

Check the BGP route 10.4.4.0/24 on R3 and R1.

```
[R3-bgp]display bgp routing-table 10.4.4.0 24
BGP local router ID : 10.0.3.3
Local AS number : 100
Paths:   1 available, 1 best, 1 select
BGP routing table entry information of 10.4.4.0/24:
From: 10.0.34.4 (10.0.4.4)
Route Duration: 00h04m36s
Direct Out-interface: GigabitEthernet0/0/1
Original nexthop: 10.0.34.4
Qos information : 0x0
AS-path 200, origin igp, MED 0, pref-val 0, valid, external, best, select,
active, pre 255
Advertised to such 1 peers:
   10.0.2.2
```

```
[R1]display bgp routing-table 10.4.4.0 24
   ........
BGP routing table entry information of 10.4.4.0/24:
From: 10.0.2.2 (10.0.2.2)        #The route is originated from R2.
Route Duration: 00h00m19s
Relay IP Nexthop: 10.0.12.2
Relay IP Out-Interface: GigabitEthernet0/0/0
Original nexthop: 10.0.34.4    # The next-hop address remains unchanged.
Qos information : 0x0
AS-path 200, origin igp, MED 0, localpref 100, pref-val 0, valid, internal,
best, select, active, pre 255, IGP cost 3
Originator:  10.0.3.3            #The route is originated from 10.0.3.3.
Cluster list: 10.0.2.2            #Cluster_ID is the router ID of R2.
Not advertised to any peer yet
```

In detailed information about BGP routes, the Aggregator/Originator and Cluster list fields on R1 show that the route originated from R3 (10.0.3.3) and was reflected by R2 (Cluster_ID 10.0.2.2), while the next-hop address (10.0.34.4) remains unchanged throughout reflection, consistent with the rule that RRs do not modify Next_Hop, AS_Path, Local_Preference, or MED when reflecting routes.

