# Traffic Filtering and Forwarding Path Control

## Foreword

- Traditionally, devices search their routing tables based on packets' destination addresses and then forward the packets. As services develop, in addition to using traditional modes, users want to forward packets and select routes through customized policies.
- To improve network security, users want to control the packets entering the network and isolate the unauthorized packets or the packets that have security risks at the network edge.
- This course discusses the traffic filtering technology, policy-based routing (PBR), as well as how to use the modular QoS command line interface (MQC) to control packet forwarding paths and filter traffic.

## Objectives

- On completion of this course, you will be able to:
  - Describe the application scenarios of PBR.
  - Describe the classification of PBR.
  - Describe how to configure PBR in MQC mode.
  - Describe how to filter packets in MQC mode.

## Contents

1. PBR
2. MQC
3. Traffic Filtering

## 1. PBR

### Technical Background

- In some scenarios, the traffic of specific users or services needs to be forwarded along a specified path, whereas the traffic of other users or services can still be forwarded based on the routing information base (RIB).

Diagram description: Enterprise X has two network segments (Network segment 1 and Network segment 2), each connected to its own switch (S). Both switches connect to an Egress router. The Egress router connects to two ISPs (ISP1 and ISP2) via the Internet cloud. A dashed blue arrow traces the path from Network segment 1 through its switch to the Egress router and out to ISP1. A solid red arrow traces the path from Network segment 2 through its switch to the Egress router and out to ISP2.

Example: An enterprise connected to two ISPs wants to access the Internet from network segment 1 through ISP1 and access the Internet from network segment 2 and through ISP2. This requirement cannot be met using traditional routing technologies.

### PBR Overview: Basic Concepts

Diagram description: A network cloud connects to router RTA. RTA has interfaces at 10.0.12.1/24 (toward RTB) and 10.0.13.1/24 (toward RTC). RTB has interface 10.0.12.2/24, and RTC has interface 10.0.13.2/24. Both RTB and RTC connect down to the same subnet 192.168.1.0/24. RTA is marked with a "P" (PBR execution point) label. RTA's routing table shows "192.168.1.0/24 via 10.0.12.2" (i.e., via RTB), but a red arrow labeled "PBR deployed to redirect traffic to RTC" shows traffic actually being redirected from RTA down to RTC instead. A callout note states: "In the routing table of RTA, the next-hop address of the route 192.168.1.0/24 is 10.0.12.2, and PBR is used to change the forwarding path."

- Policy-based routing (PBR) enables a network device to forward data based on not only the destination IP address of a packet, but also other elements such as the source IP address, source MAC address, destination MAC address, source port number, destination port number, and VLAN ID.
- You can also use an ACL to match specific packets and deploy PBR based on the ACL.
- If PBR is deployed on a device, the matched packets are preferentially forwarded based on a PBR policy. That is, a PBR policy has a higher priority than a traditional IP routing table in packet forwarding.

### PBR Overview: Structure

Diagram description: A box labeled "Policy-Based Routing" contains three stacked PBR nodes: "policy-based-route PBR node 1" (with a conditional statement and an executable statement), "policy-based-route PBR node 2" (with a conditional statement and an executable statement), and "policy-based-route PBR node 3" (with two conditional statements joined by AND, and an executable statement). Blue "OR" arrows connect node 1 to node 2 and node 2 to node 3, indicating the nodes are evaluated in an OR relationship. Within node 3, an "AND" arrow connects its two conditional statements.

- Similar to a route-policy, a PBR policy consists of multiple nodes, each of which consists of matching conditions (conditional statements) and actions (executable statements).
- Each node can contain multiple conditional statements.
- The relationship between multiple conditional statements in a node is AND, actions in the node can be executed only when all conditional statements are matched.
- The relationship between multiple nodes is OR, PBR is executed based on node IDs in ascending order. The matching is stopped if the conditional statements of a node are matched.

### PBR Overview: Command Syntax

Diagram description: The same "Policy-Based Routing" node structure (node 1, node 2, node 3 with OR relationships, node 3 having an AND between its two conditional statements) is shown on the left, with an arrow pointing to an expanded example command block on the right:

```
policy-based-route PBR permit node 10
if-match acl 2000
apply ip-address next-hop ip-address1
```

Callout labels point to parts of this command: "PBR name" points to the PBR policy name, "Node's matching mode" points to "permit", "Node index" points to "10", "Conditional statement" points to the `if-match acl 2000` line, and "Executable statement" points to the `apply ip-address next-hop ip-address1` line.

- PBR supports the following node matching modes:
  - permit: indicates that PBR is performed on the packets that meet the matching conditions.
  - deny: indicates that PBR is not performed on the packets that meet the matching conditions.

### Differences Between PBR and Route-Policy

| Item | Operation Object | Description |
|---|---|---|
| Route-policy | Routing information | A route-policy is a set of methods used to filter routing information and set route attributes. A route-policy sets or controls routes to affect the forwarding paths of data packets. |
| PBR | Data packet | PBR directly processes data packets, matches concerned packets using multiple methods, and then discards the unwanted packets or forcibly forwards packets along a specified path. |

### PBR Classification

**Interface PBR**

Diagram description: A vertical line represents an interface with a "P" (PBR execution point) marker on it. A dashed blue arrow (labeled "1", RIB-based forwarding) passes straight through vertically. A solid red arrow (labeled "2", PBR-based forwarding) diverts horizontally to the right at the PBR execution point.

- Interface PBR takes effect only for forwarded packets but not locally originated packets.
- Interface PBR is enabled in the interface view and takes effect for incoming packets on the interface. By default, a device forwards packets based on the next hop in the RIB. If interface PBR is configured, the device forwards packets based on the next hop specified by interface PBR.

**Local PBR**

Diagram description: A vertical line represents a device with a "P" (PBR execution point) marker on it. A dashed blue arrow (RIB-based forwarding) passes straight through vertically. A solid red arrow (PBR-based forwarding) diverts horizontally to the right at the PBR execution point.

- Local PBR takes effect for locally originated traffic, such as the traffic of locally originated ICMP packets.
- Local PBR is enabled globally in the system view.

### Typical Application Scenarios of PBR (1)

Diagram description: The Internet cloud connects to a Core switch (marked "P", PBR execution point). The Core switch also connects to a firewall (FW) in an off-path arrangement, and separately down to another switch (S) which connects to a group of users. Numbered blue arrows show the traffic flow: (1) traffic arrives at the Core switch from the Internet; (2) the Core switch diverts the traffic to the FW; (3) the FW returns the checked traffic to the Core switch; (4) the Core switch forwards the traffic down to the users via the downstream switch.

- The intranet firewall is connected to a core switch in off-path mode. To protect the intranet, PBR is deployed on Layer 3 interfaces of the core switch to divert the traffic from external networks to the firewall for security check. After the check is complete, the traffic is sent back to the core switch. The core switch then forwards the traffic to the intranet based on the routing table.
- Traffic diversion means the process of diverting traffic to other devices for security check. PBR is a common traffic diversion tool.

### Typical Application Scenarios of PBR (2)

Diagram description: Two ISP clouds (ISP1 and ISP2) connect to an Egress device (marked "P", PBR execution point). The Egress device connects down to a Core switch, which connects down to an Access switch, which connects down to two separate user groups. A solid red arrow traces a path from one user group up through the access switch, core switch, and egress device out to ISP1. A dashed blue arrow traces a path from the other user group similarly up to the egress device and out to ISP2.

- If an enterprise has multiple egress devices and you want to specify the egress devices for some network segments to access the Internet, configure PBR on intranet interfaces of the egress devices to match the traffic from the intranet and specify different next-hop public address for the egress devices.

### PBR Configuration (1)

1. Create PBR.

   ```
   [Huawei] policy-based-route policy-name { deny | permit } node node-id
   ```

   Create a PBR policy and a PBR node. If a PBR node already exists, enter the local PBR view.

2. Set the matching conditions of IP packets.

   ```
   [Huawei-policy-based-route-PBR-10] if-match acl acl-number
   [Huawei-policy-based-route-PBR-10] if-match packet-length min-length max-length
   ```

   By default, no matching condition is configured for a PBR policy. You can configure ACLs to match IP addresses or set the length of matching packets.

3. Specify the outbound interface of packets in the PBR policy.

   ```
   [Huawei-policy-based-route-PBR-10] apply output-interface interface-type interface-number
   ```

   By default, no outbound interface is configured for the PBR policy. After the configuration succeeds, the packets that match the PBR node can be sent from the specified outbound interface.
   The outbound interface of packets cannot be a broadcast interface, such as an Ethernet interface.

- If an ACL rule is set to permit, the device performs the following local PBR actions on the packets matching the ACL rule:
  - When the ACL rule of a PBR node is set to permit, PBR is performed on the packets that meet the matching conditions.
  - When the ACL rule of a PBR node is set to deny, PBR is not performed on the packets that meet the matching conditions, and packets are forwarded based on the destination address through RIB lookup.
- If an ACL is configured with rules, packets that do not match any ACL rule are forwarded according to the destination IP address through RIB lookup.
- If an ACL rule is set to deny or an ACL is not configured with any rule, local PBR that applies the ACL does not take effect, and packets are forwarded according to the destination IP address through RIB lookup.

### PBR Configuration (2)

4. Configure the next-hop IP address of packets in a PBR policy.

   ```
   [Huawei-policy-based-route-PBR-10] apply ip-address next-hop ip-address1 [ ip-address2 ]
   ```

   You can specify the next hop of packets. If no outbound interface is configured for a PBR node, packets matching PBR node are sent to the specified next hop.

5. Enable PBR globally.

   ```
   [Huawei] ip local policy-based-route Policy-name
   ```

6. Enable PBR on an interface.

   ```
   [Huawei-GigabitEthernet0/0/0] ip policy-based-route Policy-name
   ```

- In addition to the method described in this slide, interface PBR can also be configured in MQC mode.

### Configuration Examples (1)

Diagram description: Two ISP clouds are shown: ISP1 (public address 202.1.2.3) and ISP2 (public address 154.1.2.3), both connected to router RTA via its GE0/0/0 interface. RTA also connects to a server at 10.1.3.254. RTA connects down to a switch (S), which connects down to two more switches (S), each serving a user network segment: 10.1.1.0/24 (network segment 1) and 10.1.2.0/24 (network segment 2). A dashed blue arrow traces network segment 1's traffic path up through the switches to RTA and out to ISP1. A solid red arrow traces network segment 2's traffic path up to RTA and out to ISP2.

- Requirements:
  - The intranet has two network segments: network segment 1 (10.1.1.0/24) and network segment 2 (10.1.2.0/24). PBR is configured on GE0/0/0 of RTA so that users on network segment 1 can access the Internet through ISP1 and users on network segment 2 can access the Internet through ISP2.
  - RTA is connected to a server in off-path mode. It is required that the PBR deployed on RTA not affect intranet users' access to the server.

### Configuration Examples (2)

1. Configure ACL 3000. Configure ACL rule 1 to deny the traffic originated from network segment 1 to the server, and configure ACL rule 2 to permit the traffic originated from network segment 1 to the Internet.

   ```
   [RTA] acl number 3000
   [RTA-acl-adv-3000] rule 1 deny ip source 10.1.1.0 0.0.0.255 destination 10.1.3.254 0
   [RTA-acl-adv-3000] rule 2 permit ip source 10.1.1.0 0.0.0.255 destination 0.0.0.0 0
   ```

2. Configure ACL 3001. Configure ACL rule 1 to deny the traffic originated from network segment 2 to the server and ACL rule 2 to permit the traffic originated from network segment 2 to the Internet.

   ```
   [RTA] acl number 3001
   [RTA-acl-adv-3001] rule 1 deny ip source 10.1.2.0 0.0.0.255 destination 10.1.3.254 0
   [RTA-acl-adv-3001] rule 2 permit ip source 10.1.2.0 0.0.0.255 destination 0.0.0.0 0
   ```

### Configuration Examples (3)

3. Create a PBR policy named `hcip` and PBR node 10, invoke ACL 3000, and set the next-hop address to 202.1.2.3.

   ```
   [RTA] policy-based-route hcip permit node 10
   [RTA-policy-based-route-hcip-10] if-match acl 3000
   [RTA-policy-based-route-hcip-10] apply ip-address next-hop 202.1.2.3
   ```

4. Create PBR node 20 for the PBR policy `hcip`, invoke ACL 3001, and set the next-hop address to 154.1.2.3.

   ```
   [RTA] policy-based-route hcip permit node 20
   [RTA-policy-based-route-hcip-20] if-match acl 3001
   [RTA-policy-based-route-hcip-20] apply ip-address next-hop 154.1.2.3
   ```

5. Enable the PBR policy `hcip` on GE0/0/0.

   ```
   [RTA] interface GigabitEthernet 0/0/0
   [RTA-GigabitEthernet0/0/0] ip policy-based-route hcip
   ```

## 2. MQC

### MQC Overview (1)

Diagram description: Two boxes, "Traffic classifier" (configure a traffic classifier to match concerned data flows based on items such as VLAN tags, DSCP values, and ACL rules) and "Traffic behavior" (configure a traffic behavior to redirect concerned packets; you can set the next-hop IP address or outbound interface for redirection), both feed into a "Traffic policy" box (Traffic classifier -> Traffic behavior). Below that, a box titled "Applying a traffic policy" lists: apply the traffic policy to an interface in the inbound direction; use the traffic policy to control the incoming packets that belong to the VLAN and match the rules in the traffic classifier; apply the traffic policy globally or on a specific board.

- Modular QoS command line interface (MQC) groups the data flows that have the same characteristics and provides the same service for a group of data flows. MQC can also provide different services for the data flows of different classes.
- MQC involves three entities: traffic classifier, traffic behavior, and traffic policy.
- MQC traffic behaviors support packet redirection. Therefore, MQC can be used to implement IP unicast policy-based routing.

### MQC Overview (2)

Diagram description: A box labeled "Traffic policy" points to a stack of paired boxes: "Traffic classifier 1" / "Traffic behavior 1", "Traffic classifier 2" / "Traffic behavior 2", down through "Traffic classifier n" / "Traffic behavior n", illustrating that one traffic policy can bind multiple classifier-behavior pairs.

- A traffic policy is bound to a traffic classifier and a traffic behavior so that the device takes the action defined in the traffic behavior on the classified packets.
- A traffic policy can be bound to multiple traffic classifiers and traffic behaviors.

> **Note on source content:** Beneath this slide's normal bullet points, the original PDF page (p. 527) contains an out-of-place block of text that reads like a chatbot reply directed at someone named "Awoniyi," explaining an "MQC Workflow" in a different style (headers with emoji, a "Behavior Type / Description" table left empty, and an "Example Flow" about limiting YouTube traffic to 2 Mbps). This does not match the formatting or authorship of the rest of the deck and appears to be an artifact accidentally included in this export (e.g., pasted from an unrelated chat) rather than genuine Huawei course material. It is reproduced below verbatim per your preservation rule, but I'd recommend NOT using it as source material for quiz generation — it may not be accurate to the official curriculum and one of its tables is incomplete.
>
> ---
>
> Yes, Awoniyi, you've got the right idea! **MQC (Modular QoS CLI)** follows a structured flow where traffic is first **classified**, then a **behavior** is defined for that traffic, and finally a **policy** ties it all together and applies it to an interface. Let's break it down clearly:
>
> ---
>
> ### 🧭 MQC Workflow: Step-by-Step
>
> 1. **Traffic Classifier**
>    - Defines **what traffic to match**
>    - Based on criteria like:
>      - Source/destination IP
>      - Protocol (TCP, UDP)
>      - VLAN ID
>      - DSCP or IP precedence
>      - ACLs
>
> 2. **Traffic Behavior**
>    - Defines **what to do with matched traffic**
>    - This is where the magic happens—QoS actions are applied.
>
> 3. **Traffic Policy**
>    - Binds the classifier and behavior together
>    - Applied to an **interface** (inbound or outbound)
>
> ---
>
> ### 🔧 What Can "Traffic Behavior" Do?
>
> Here are common behaviors you can define:
>
> | Behavior Type | Description |
>
> ---
>
> ### 🧪 Example Flow
>
> Let's say you want to limit YouTube traffic to 2 Mbps:
>
> 1. **Classifier**: Match traffic to YouTube IPs or ports
> 2. **Behavior**: Apply traffic policing (CIR = 2000 kbps)
> 3. **Policy**: Bind classifier + behavior and apply to interface `GE0/0/1`
>
> ---
>
> So yes, MQC first **identifies** the traffic, then **acts** on it, and finally **enforces** that action through a policy. It's modular, flexible, and powerful—especially in Huawei and Cisco environments.
>
> *(End of out-of-place artifact text.)*

### MQC: Traffic Classifier

Diagram description: A box "Traffic classifier 1" / "Traffic behavior 1" points to a larger table of matching items grouped into three categories: "Layer 2 matching items" (Tag ID of a VLAN packet; Fields matching ACLs numbered 4000 through 4599; Destination or source MAC address; ...), "Layer 3 matching items" (Fields matching ACLs numbered 2000 through 3999; IPv4 packet length; IP precedence in IP packets; ...), and "Other matching items" (Inbound interface; Outbound interface; All packets; ...).

- A traffic classifier defines a group of traffic matching rules to classify packets. This figure illustrates the matching items supported by a traffic classifier.
- The relationship between rules in a traffic classifier can be AND or OR. The default relationship is AND.
  - AND: If a traffic classifier contains ACL rules, packets must match one ACL rule and all non-ACL rules. If a traffic classifier does not contain ACL rules, packets must match all non-ACL rules.
  - OR: If a packet matches a rule in a traffic classifier, the device considers that the packet matches the traffic classifier.

### MQC: Traffic Behavior

Diagram description: A box "Traffic classifier 1" / "Traffic behavior 1" points to a box titled "Executable actions" listing: Filtering packets; Traffic statistics collection; Adding VLAN tags to packets; Packet priority re-marking; Executing PBR on packets; ...

- A traffic behavior defines the actions to be performed, including packet filtering, priority re-marking, redirection, and traffic statistics collection.

### MQC: Traffic Policy

Diagram description: Two side-by-side scenarios are shown. Left, "Traffic policy invoked in the outbound direction": a device (SW1, marked "Q" for traffic policy execution point) receives packets with IP/MAC headers on the left and outputs packets with an added 802.1Q/IP/MAC header structure on the right, illustrating the device adding an 802.1Q tag to outgoing packets. Right, "Traffic policy invoked in the inbound direction": a router (SW1, marked "Q") has a solid blue arrow (RIB-based forwarding) passing straight through, and a dashed red arrow (Redirection using MQC) diverting upward/redirecting packets matching the traffic classifier.

- A traffic policy can be invoked on an interface.
- A traffic policy defines the inbound and outbound directions. A traffic behavior in the traffic policy matches incoming or outgoing packets, and is performed on the matched packets.
- Different from a PBR policy which can be invoked only on Layer 3 interfaces, a traffic policy can be invoked on both Layer 2 and Layer 3 interfaces.

### Configuration Procedure

1. Create a traffic classifier.

   ```
   [Huawei] traffic classifier classifier-name [ operator { and | or } ]
   ```

   By default, the relationship between rules in a traffic classifier is OR. For details about the matching rules in a traffic classifier, see the corresponding product manual.

2. Create a traffic behavior.

   ```
   [Huawei] traffic behavior behavior-name
   ```

   Define actions in the traffic behavior according to actual conditions. Different actions can be configured in the same traffic behavior so long as they do not conflict. For details about the executable actions in a traffic behavior, see the corresponding product manual.

3. Create a traffic policy. Bind a traffic classifier and a traffic behavior to the traffic policy.

   ```
   [Huawei] traffic policy policy-name
   [Huawei-trafficpolicy-policyname] classifier classifier-name behavior behavior-name
   ```

### PBR Using MQC (1)

Diagram description: Same topology as "Configuration Examples (1)": ISP1 (202.1.2.3) and ISP2 (154.1.2.3) connect to RTA via GE0/0/0. RTA connects down through a switch to two more switches serving network segment 1 (10.1.1.0/24) and network segment 2 (10.1.2.0/24). A dashed blue arrow traces segment 1's path to ISP1; a solid red arrow traces segment 2's path to ISP2.

- Requirements:
  - The intranet has two network segments: network segment 1 (10.1.1.0/24) and network segment 2 (10.1.2.0/24). Configure MQC on RTA to implement PBR, so that users on network segment 1 can access the Internet through ISP1 and users on network segment 2 can access the Internet through ISP2.
  - Enable MQC on GE0/0/0 of RTA.

### PBR Using MQC (2)

RTA configuration:

1. Configure ACL 3000 to match the traffic originated from network segment 1 to the Internet. Configure ACL 3001 to match the traffic originated from network segment 2 to the Internet.

   ```
   [RTA] acl number 3000
   [RTA-acl-adv-3000] rule 2 permit ip source 10.1.1.0 0.0.0.255 destination 0.0.0.0 0
   [RTA] acl number 3001
   [RTA-acl-adv-3001] rule 2 permit ip source 10.1.2.0 0.0.0.255 destination 0.0.0.0 0
   ```

2. Create traffic classifiers 1 and 2. Bind traffic classifier 1 to ACL 3000, and bind traffic classifier 2 to ACL 3001.

   ```
   [RTA] traffic classifier 1
   [RTA-classifier-1] if-match acl 3000
   [RTA] traffic classifier 2
   [RTA-classifier-2] if-match acl 3001
   ```

### PBR Using MQC (3)

3. Create traffic behaviors 1 and 2 to redirect packets to 202.1.2.3 and 154.1.2.3, respectively.

   ```
   [RTA] traffic behavior 1
   [RTA-behavior-1] redirect ip-nexthop 202.1.2.3
   [RTA] traffic behavior 2
   [RTA-behavior-2] redirect ip-nexthop 154.1.2.3
   ```

4. Create a traffic policy named `Redirect`. Bind traffic classifier 1 to traffic behavior 1, and bind classifier 2 to traffic behavior 2.

   ```
   [RTA] traffic policy Redirect
   [RTA-trafficpolicy-Redirect] classifier 1 behavior 1
   [RTA-trafficpolicy-Redirect] classifier 2 behavior 2
   ```

5. Apply the traffic policy `Redirect` in the inbound direction of GE0/0/0.

   ```
   [RTA] interface GigabitEthernet 0/0/0
   [RTA-GigabitEthernet0/0/0] traffic-policy Redirect inbound
   ```

## 3. Traffic Filtering

### Requirement Background

- To improve network security, an administrator needs to control the traffic entering the network and discard untrusted packets at the network edge. Untrusted packets are the packets that have security risks and the packets that users are not willing to accept. In addition, to ensure data access security, some departments are not allowed to communicate with each other on an enterprise network.

Diagram description: Left panel "Discarding Untrusted Packets" — an Internet cloud connects through devices toward a "Server area" containing servers. One callout notes "The access to the intranet server mapped to a public address is a normal behavior." Another callout, pointing to an attacker icon attempting to reach the server area, notes "The access to the intranet over the server without network access control is an attack behavior." A prohibition (no-entry) icon blocks a path, with the note "The server is prohibited from accessing the intranet in order to prevent redirection attacks."

Right panel "Restricting Mutual Access Between Departments" — a mesh of switches connects three department blocks (Department 1, Department 2, Department 3). No-entry icons block certain paths between switches leading to departments, with one path shown as a dashed green permitted path and others marked with prohibition icons in red. Caption: "Access between departments is restricted based on service requirements."

### Traffic Filtering Tools

Diagram description: Two comparison boxes are shown. Left, "Traffic-Filter": contains "Traffic matching tool" (IPv4 ACL, IPv6 ACL) and "Filter direction" (Inbound, Outbound). Right, "MQC": contains "Traffic matching tool" (IPv4 ACL, IPv6 ACL, MAC address, VLAN tag, IP precedence, ...) and "Filter direction" (Inbound, Outbound).

Traffic-filter can be enabled only in the interface view, whereas MQC can be enabled in multiple views.

### Traffic-Filter Deployment Position

- Traffic-filter can be flexibly deployed to filter the traffic entering a device or leaving a device. For bidirectional access, services can be blocked when traffic in either of the directions is prohibited.

Diagram description: Left panel "Blocking the traffic originated from department 1 to department 2" — two scenario rows. In the first row, RTA sits between Department 1 (10.1.2.0/24) and Department 2 (10.1.3.0/24); a "T" (traffic-filter execution point) marker sits on the near/left side of RTA, and outgoing traffic from Department 1 toward Department 2 is blocked (no-entry icon) right after leaving Department 1's side. In the second row, the "T" marker sits on the far/right side of RTA (closer to Department 2), and outgoing traffic is again blocked, this time just before reaching Department 2.

Right panel "Blocking the return traffic from department 1 to department 2" — similarly two scenario rows with RTA between Department 1 and Department 2. Solid red arrows show forward packets flowing from Department 1 to Department 2 (unblocked), while dashed red arrows show reverse packets flowing back from Department 2 to Department 1, which are blocked (no-entry icon) at the "T" marker position, which varies between the near side and far side of RTA in the two rows.

- The content of the invoked ACL varies according to the deployment position of traffic-filter.

### Using Traffic-Filter to Filter Traffic

Diagram description: Router RTA has three interfaces: GE0/0/0, GE0/0/1, and GE0/0/2, each connecting down to a separate switch, which in turn connects to Department 1 (10.1.1.0/24), Department 2 (10.1.2.0/24), and Department 3 (10.1.3.0/24) respectively. A red arrow traces a path from Department 2 toward Department 3, blocked by a no-entry icon just before reaching Department 3's switch.

The gateways of departments 1, 2, and 3 are all on RTA. It is required that traffic-filter be deployed on RTA to restrict the mutual access between departments 2 and 3.

RTA configuration:

1. Configure an ACL to deny the traffic originated from department 2 to department 3 and permit all the other traffic.

   ```
   [RTA] acl number 3000
   [RTA-acl-adv-3000] rule 1 deny ip source 10.1.2.0 0.0.0.255 destination 10.1.3.0 0.0.0.255
   [RTA-acl-adv-3000] rule 2 permit ip
   ```

2. Apply the traffic-filter to GE0/0/2.

   ```
   [RTA] interface GigabitEthernet 0/0/2
   [RTA-GigabitEthernet0/0/2] traffic-filter outbound acl 3000
   ```

Question: Are there any other options to configure ACL rule and traffic-filter on interfaces?

### Using MQC to Filter Traffic (1)

Diagram description: Same topology as above — RTA with GE0/0/0, GE0/0/1, GE0/0/2 connecting to Department 1 (10.1.1.0/24), Department 2 (10.1.2.0/24), and Department 3 (10.1.3.0/24), with traffic from Department 2 toward Department 3 blocked.

The gateways of departments 1, 2, and 3 are all on RTA. It is required that MQC be deployed on RTA to restrict the mutual access between departments 2 and 3.

RTA configuration:

1. Configure an ACL to match the traffic originated from department 2 to department 3.

   ```
   [RTA] acl number 3000
   [RTA-acl-adv-3000] rule 1 permit ip source 10.1.2.0 0.0.0.255 destination 10.1.3.0 0.0.0.255
   ```

2. Create a traffic classifier named `2_3` and a traffic behavior named `2_3`.

   ```
   [RTA] traffic classifier 2_3
   [RTA-classifier-2_3] if-match acl 3000
   [RTA] traffic behavior 2_3
   [RTA-behavior-2_3] deny
   ```

When you filter packets matching an ACL rule, if the ACL rule is set to permit, the device processes the packets according to the action (deny or permit) configured in the traffic behavior. If the ACL rule is set to deny, the device discards the packets regardless of whether deny or permit is configured in the traffic behavior.

### Using MQC to Filter Traffic (2)

3. Create a traffic policy named `2_3`. Bind traffic classifier `2_3` and traffic behavior `2_3` to the traffic policy `2_3`.

   ```
   [RTA] traffic policy 2_3
   [RTA-trafficpolicy-2_3] classifier 2_3 behavior 2_3
   ```

4. Apply the traffic policy `2_3` in the inbound direction of GE0/0/1.

   ```
   [RTA] interface GigabitEthernet 0/0/1
   [RTA-GigabitEthernet0/0/1] traffic-policy 2_3 inbound
   ```

