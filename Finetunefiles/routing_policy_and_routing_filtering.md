# Routing Policy and Routing Control

## Foreword

- On a complex data communication network, the routing policy can be configured to filter routes and set route attributes as needed. Route control affects data traffic forwarding.
- A routing policy is not a single technique or protocol, but a special technical topic or methodology that involves multiple tools and methods.
- This course describes route selection tools and principles, as well as how to configure route-policies.

## Objectives

- On completion of this course, you will be able to:
  - Use an ACL to filter routes.
  - Use an IP prefix to filter routes.
  - Use a filter-policy to filter routes.
  - Use a route-policy to filter routes and modify route attributes.

## Contents

1. Routing Control Overview
2. Route Control Tool
   - Route Matching Tool
   - Route-Policy
3. Route Control Cases

---

## 1. Routing Control Overview

### Technical Background

- R1 imports the network segment routes of services A and B to R1, but does not import the route destined for the service C network segment. When R3 imports OSPF routes to the IS-IS routing table, R3 needs to import only the route destined for the service B network segment.
- In this case, a tool is required to control routes to be imported.

Diagram description: A topology showing four routers in a line: R1 — R2 — R3 — R4. R1 connects to three services on its left side: Service A 172.16.1.0/24, Service B 172.16.2.0/24, and Service C 172.16.3.0/24. R1 and R2 are joined by interface GE0/0/2 (10.0.12.1/24) on R1 and GE0/0/3 (10.0.12.2/24) on R2, and this segment (R1–R2–R3) runs OSPF area 0. R2 and R3 are joined by GE0/0/2 (10.0.23.2/24) on R2 and GE0/0/3 (10.0.23.3/24) on R3. R3 and R4 are joined by GE0/0/2 (10.0.34.3/24) on R3 and GE0/0/3 (10.0.34.4/24) on R4, and this segment (R3–R4) runs IS-IS area 49.0001 Level-1. An annotation near R1 states "The route destined for the service C network segment is not imported." An annotation near R3/R4 states "The route destined for the service B network segment is imported."

### Routing Control Overview

- Route control can be implemented using a route-policy. The route-policy is flexibly used in the following scenarios:
  - Controlling route advertisement: A route-policy is used to filter the routes to be advertised so that a device advertises only the routes that match matching conditions.
  - Controlling route receipt: A route-policy is used to filter the routes to be accepted so that a device accepts only the routes that match matching conditions.
  - Controlling route import: A route-policy is used to filter the routes to be imported so that a device imports only the routes that match matching conditions.

Diagram description: A flow diagram showing a box labeled "Defining route characteristics" with text: "To match the routes against a route-policy, define a group of matching rules. The rules can base on various attributes, such as the destination address and tag value, in routing information." An arrow labeled "Apply" points from this box to three stacked boxes: "Route advertisement," "Route receipt," and "Route import."

---

## 2. Route Control Tool

### Route Matching Tool

#### Matching Tool 1: ACL

*(Breadcrumb on slide: ACL > IP Prefix List)*

- An access control list (ACL) is a matching tool that can match and distinguish packets and routes.
- An ACL consists of multiple permit, deny, or both clauses. Each statement is a rule of the ACL. The permit or deny action in each statement is an action bound to the rule.

Diagram description: A labeled diagram of an ACL numbered 2000, containing rules: "rule 5 permit source 1.1.1.0 0.0.0.255", "rule 10 deny source 2.2.2.0 0.0.0.255", "rule 15 permit source 3.3.3.0 0.0.0.255", followed by "..." and an implicit rule at the end of the ACL: "rule 4294967294 deny". Labels point out the ACL Number ("acl number 2000"), Rule number ("rule 5"), Action ("permit"), Matching condition (source IP address) ("source 1.1.1.0 0.0.0.255"), and note that the listed rules are "User-defined rules" while the final rule is the "Implicit rule at the end of an ACL".

- An ACL consists of the following elements:
  - ACL number: Each ACL configured on a device is assigned a number, which is called an ACL number and is used to identify the ACL. The ACL number range varies according to the ACL type.
  - Rule: As mentioned above, an ACL is usually consists of multiple permit, deny, or both clauses, and each clause is a rule of the ACL.
  - Rule number: Each rule has a rule number, which identifies an ACL rule. The value can be user-defined or automatically allocated by the system.
  - Action: "Permit" or "deny" in each rule is an action bound to a rule. ACLs are usually used together with other technologies. The meanings of actions vary according to the scenario.
    - For example, if an ACL is used together with a traffic filtering technology (the ACL is applied to the traffic filtering function), "permit" indicates that traffic is allowed to pass, and "deny" indicates that traffic is rejected.
  - Item to be matched against: The ACL defines abundant items to be matched against. In this example, the source IP address is used. The ACL also supports many other items. For instance, the items can be Layer 2 Ethernet frame header information (such as a source MAC address, destination MAC address, and Ethernet frame protocol type), Layer 3 packet information (such as a destination address and protocol type), or Layer 4 packet information (such as a TCP/UDP port number).

#### Wildcard

*(Breadcrumb on slide: ACL > IP Prefix List)*

Diagram description: A labeled example showing ACL 2000 with rules: "rule 5 deny source 10.1.1.1 0", "rule 10 deny source 10.1.1.2 0", "rule 15 permit source 10.1.1.0 0.0.0.255" — with the wildcard column highlighted (0, 0, 0.0.0.255 respectively). To the right, a "Wildcard" info box states: "A wildcard is a 32-bit string. It is used to indicate which bits must be exactly matched and which bits may not be matched in an IP address." and "The wildcard is usually expressed in dotted decimal notation similar to a network mask, and its meaning is opposite to that of the network mask." Below, a "Matching rule" note: "0: match; 1: no match". A worked question: "How do I match IP addresses within network segment 192.168.1.0/24?" shows 192.168.1.1 in binary (11000000 10101000 00000001 | 00000001) compared against wildcard 0.0.0.255 in binary (00000000 00000000 00000000 | 11111111), with the left 24 bits labeled "Exact match" and the rightmost 8 bits labeled "No match," annotated as the "Network segment 192.168.1.0/24".

- For an IP address to be matched against a matching rule, the address is followed by a 32-bit mask. The 32-bit mask is called a wildcard.
- The wildcard is in dotted decimal notation. After it is converted into the binary format, value 0 indicates a "match" and value 1 indicates "no match". 1s or 0s in the wildcard may be discontinuous.
- There are two examples:
  - rule 5: rejects packets with source IP address 10.1.1.1. The all-0 wildcard indicates that each bit must be exactly matched. Therefore, the host IP address 10.1.1.1 matches the rule.
  - rule 15: permits packets whose source IP addresses belong to network segment 10.1.1.0/24. The wildcard is 0.0.0.11111111, and the right-most 8 bits are 1, which indicates that these bits in packets can be ignored. As such, the right-most 8 bits in 10.1.1.xxxxxxxx can be any value, and the network segment 10.1.1.0/24 matches this rule.
- Example: To exactly match the network segment address of 192.168.1.1/24, which wildcard can be used?
  - It can be concluded that network bits must be exactly matched and host bits can be ignored. Therefore, the wildcard is 0.0.0.255.
- Two special wildcards:
  - The all-0 wildcard is used to exactly match a specific IP address.
  - When the all-1 wildcard is used to match 0.0.0.0, it indicates that all IP addresses are matched.

#### ACL Classification and Basic ACLs

*(Breadcrumb on slide: ACL > IP Prefix List)*

- Classification based on the ACL rule definition mode

| Category | Number Range | Rule Definition |
|---|---|---|
| Basic ACL | 2000–2999 | Defines rules based on source IP addresses, fragment information, and validity time ranges. |
| Advanced ACL | 3000–3999 | Defines rules based on source IP addresses, destination IP addresses, IP protocol types, ICMP types, TCP source/destination port numbers, UDP source/destination port numbers, and time ranges. |
| Layer 2 ACL | 4000–4999 | Defines rules based on the Ethernet frame header information, such as the source MAC address, destination MAC address, and Layer 2 protocol type. |
| User-defined ACL | 5000–5999 | Defines rules based on the packet header, offsets, string masks, and user-defined strings. |
| .... | .... | .... |

- Basic ACL

Diagram description: A table showing three column groupings — "IP Header" (containing "Source IP address"), "TCP/UDP Header", and "Data" — illustrating that a basic ACL only inspects the IP Header's source IP address field. Below it, the example ACL is shown: "acl number 2000", "rule 5 deny source 10.1.1.1 0", "rule 10 deny source 10.1.1.2 0", "rule 15 permit source 10.1.1.0 0.0.0.255".

- Only basic ACLs can be used to match routes.

#### ACL Fundamentals

*(Breadcrumb on slide: ACL > IP Prefix List)*

Diagram description: A flowchart titled "ACL Fundamentals" with a note: "Matching rule: The matching stops once the target is hit." The flow starts at "Start", then asks "Does an ACL to be applied exist?" — if No, goes directly to "Packets do not match the rule" → "End". If Yes, asks "Does the ACL contain rules?" — if No, goes to "Packets do not match the rule" → "End". If Yes, goes to "Analyze the first rule," then asks "Is the ACL action 'permit' or 'deny'?" — branching to "Result is permit" (permit) or "Result is deny" (deny), then to "End". Separately, after analyzing a rule, it asks "Does the target hit the rule?" — if No, asks "Do other rules exist?" — if Yes, goes to "Analyze the next rule" (looping back); if No, goes to "Packets do not match the rule" → "End". If Yes (target hits the rule), proceeds to the permit/deny action branch described above.

- The ACL matching mechanism is as follows:
  - After a device configured with an ACL receives a packet, the device matches the packet against ACL rules one by one. If the packet does not match an ACL rule, the device attempts to match the packet against a next rule.
  - Once the packet matches a rule, the device performs the action defined in the rule on the packet and no longer matches the packet against other rules.
- Matching process:
- The device checks whether an ACL is configured.
- If no ACL is configured, the device returns the result "negative match."
- If an ACL is configured, the device checks whether the ACL contains rules.
  - If the ACL does not contain rules, the device returns the result "negative match."
  - If the ACL contains rules, the device matches the packets against the rules in ascending order of rule IDs.
    - When the packets match a permit rule, the device stops matching and returns the result "positive match (permit)."
    - When the packets match a deny rule, the device stops matching and returns the result "positive match (deny)."
    - If the packets do not match any rule in the ACL, the device returns the result "negative match."

#### Matching Order and Result of ACL Rules

*(Breadcrumb on slide: ACL > IP Prefix List)*

- Configuration sequence (config mode)
  - The system matches packets against ACL rules in ascending order by rule ID. A rule with a smaller ID is earlier to be matched.

Diagram description: A flow diagram showing an "IP routing table" box containing entries 1.1.1.1/32, 1.1.1.0/24, 1.1.0.0/16, 1.0.0.0/8, labeled "Object to be matched." An arrow points to "acl 2000" containing "rule 5 permit source 1.1.0.0 0.0.255.255" with a note: "rule 5: matches route prefixes whose destination network addresses start at 1.1." Another arrow points to "Matching route entries" listing 1.1.1.1/32, 1.1.1.0/24, 1.1.0.0/16, labeled "Route entries to be matched."

- A question box: "What does 'permit' mean?"

- An ACL consists of multiple deny | permit clauses, each of which describes a rule. These rules may repeat or conflict. In this situation, the matching order decides the matching result.
- Huawei devices support two matching orders: automatic order (auto mode) and configured order (config mode). The configured mode is used by default.
  - Automatic order: The system arranges rules according to the precision degree of the rules (depth first principle), and matches packets against the rules in descending order of precision. A rule with the highest precision defines strictest conditions, and has the highest priority. This process is complex, so we will not go into details here. Anyone interested in this can read materials after class.
  - Configured order: The system matches packets against ACL rules in ascending order of rule IDs. That is, the rule with the smallest ID is processed first. This is the matching order we mentioned earlier.
    - If another rule is added, the rule is added to a corresponding position, and packets are still matched against the rules in ascending order by rule ID.
- Note: ACLs are always used together with other technologies. The actual functions of "permit" and "deny" vary with technologies. For example, when an ACL is used together with route filtering, "permit" means that a route is a match, and "deny" means that a route is not a match.

#### Common Matching Examples

*(Breadcrumb on slide: ACL > IP Prefix List)*

Diagram description: Three side-by-side examples.
- Example 1: Routes 1.1.1.0/24, 1.1.2.0/24, 1.1.3.0/24 matched against "acl 2000 rule 5 permit source 1.1.2.0 0.0.0.255" result in only 1.1.2.0/24 matching. Caption: "Matches routes with prefixes starting at 1.1.2."
- Example 2: Routes 1.1.1.0/24, 1.1.2.0/24, 0.0.0.0/0 matched against "acl 2000 rule 5 permit source 0.0.0.0 255.255.255.255" result in all three routes (1.1.1.0/24, 1.1.2.0/24, 0.0.0.0/0) matching. Caption: "Matches any route."
- Example 3: Routes 1.1.1.1/32, 1.1.1.2/32, 1.1.1.3/32 matched against "acl 2000 rule 5 permit source 1.1.1.1 0.0.0.254" result in 1.1.1.1/32 and 1.1.1.3/32 matching (not 1.1.1.2/32). Caption: "Matches routes carrying prefix 1.1.1 and ending with an odd number."

- A highlighted note box: "An ACL can match only route prefixes, but not network masks."

#### Basic Configuration Commands of Basic ACLs

*(Breadcrumb on slide: ACL > IP Prefix List)*

1. Create a basic ACL.

```
[Huawei] acl [ number ] acl-number [ match-order config ]
```
Create a numbered basic ACL (2000–2999) and enter the basic ACL view.

```
[Huawei] acl name acl-name { basic | acl-number } [ match-order config ]
```
Create a named basic ACL and enter the basic ACL view.

2. Configure an ACL rule.

```
[Huawei-acl-basic-2000] rule [ rule-id ] { deny | permit } [ source { source-address source-wildcard | any } | time-range time-name ]
```
You can run this command in the basic ACL view to configure rules for the basic ACL.

- Create a basic ACL.
- [Huawei] acl [ number ] acl-number [ match-order config ]
  - acl-number: specifies the number of an ACL.
  - match-order config: indicates the matching order of ACL rules. config indicates the configuration order.
- [Huawei] acl name acl-name { basic | acl-number } [ match-order config ]
  - acl-name: specifies the name of an ACL.
  - basic: indicates a basic ACL.
- Configure a basic ACL rule.
- [Huawei-acl-basic-2000] rule [ rule-id ] { deny | permit } [ source { source-address source-wildcard | any } | time-range time-name ]
  - rule-id: specifies the ID of an ACL rule.
  - deny: rejects packets that meet the matching conditions.
  - permit: permits the packets that meet the matching conditions.

#### Matching Tool 2: IP Prefix List

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

- An IP prefix list is a filter that uses the network address and mask length of routes as matching rules. An IP prefix list can be used when a routing protocol advertises or receives routes.
- Different from an ACL, an IP prefix list can match both the IP address prefix length and mask length, which enhances matching accuracy.

```
[Huawei] ip ip-prefix test index 10 permit 192.168.1.0 22 greater-equal 24 less-equal 26
```

Labels: ip-prefix-name, No. (Sequence number), Action, IP network segment and mask, Mask range.

1. ip-prefix-name: specifies the name of an IP prefix list.
2. Sequence number: indicates the sequence number of a matching entry in the IP prefix list. The IP prefixes are matched in ascending order by sequence number.
3. Action: permit or deny, indicating match or mismatch.
4. IP network segment and mask: match the network address of a route and exactly match the leftmost N bits of the network address.
5. Mask length range: mask-length <= greater-equal-value <= less-equal-value <= 32

#### IP-Prefix Fundamentals

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

Diagram description: A flowchart titled "IP-Prefix Fundamentals." Starts at "Start", then "Analyze the first Index entry" (labeled "Sequence matching"). Asks "Is the route to be matched within the defined range?" — if Yes, proceeds to ask "Is the action 'permit' or 'deny'?" (labeled "Unique match") — branching to "The matching result is permit" (permit) or "The matching result is deny" (deny) — then "End". If No (route not within the defined range), asks "Do other index entries exist?" — if Yes, goes to "Analyze the next index entry" (looping back to the range check); if No, the result is "The matching result is deny" (labeled "Denied by default") → "End".

#### Example of IP-Prefix Matching

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

Diagram description: A flow diagram. "IP routing table" box contains: 1.1.1.1/32, 1.1.1.0/27, 1.1.1.0/26, 1.1.1.0/25, 1.1.1.0/24, labeled "Object to be matched." An arrow points to "ip ip-prefix List1 index 10 permit 1.1.1.0 24 greater-equal 24 less-equal 27" with a note: "The preceding IP prefix list matches the routes whose left-most 24 bits in the network address are the same as those in 1.1.1.0 and whose network mask length is greater than or equal to 24 and less than or equal to 27. As such, 1.1.1.1/32 does not match the IP prefix list." Another arrow points to "Matching route entries" listing 1.1.1.0/27, 1.1.1.0/26, 1.1.1.0/25, 1.1.1.0/24, labeled "Matched route entries."

#### Basic Configuration Commands of an IP Prefix List

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

1. Create an IPv4 prefix list.

```
[Huawei] ip ip-prefix ip-prefix-name [ index index-number ] { permit | deny } ipv4-address mask-length [ match-network ] [ greater-equal greater-equal-value ] [ less-equal less-equal-value ]
```
Create an IPv4 prefix list or add an entry to the IPv4 prefix list.

- ip-prefix-name: specifies the name of an IP prefix list.
- index index-number: specifies the index of a matching entry in the IP prefix list.
- permit: indicates that the matching mode of the IP prefix list is permit.
- deny: indicates that the matching mode of the IP prefix list is deny.
- ipv4-address mask-length: specifies the IP address and mask length.
- greater-equal greater-equal-value: specifies the lower limit of the matching range of the mask length.
- less-equal less-equal-value: specifies the upper limit of the matching range of the mask length.

- ip-prefix-name: specifies the name of an IP prefix list. The value is a string of 1 to 169 case-sensitive characters, spaces not supported.
- index index-number: specifies the index of a matching entry in the IP prefix list. The value is an integer ranging from 0 to 4294967295. By default, the sequence number increases by 10 each time an entry is added and is automatically indexed. If the system automatically assigns an index, the index starts at 10.
- permit: indicates that the matching mode of the IP prefix list is permit. In this mode, if the IP address to be filtered is within the defined range, the IP address passes the filtering. If no match is found, the system moves to a next node.
- deny: indicates that the matching mode of the IP prefix list is deny. In this mode, if the IP address to be filtered is within the defined range, the IP address fails to pass the filtering and cannot be matched against a next node. If the IP address is out of the range, the system moves to a next node.
- ipv4-address mask-length: specifies the IP address and mask length. The mask-length value is an integer ranging from 0 to 32.

#### IP Prefix Configuration Example (1)

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

Diagram description: Topology showing a cloud containing routes 10.1.0.0/16, 10.1.1.0/24, 10.1.1.0/26, 10.1.1.1/32, 10.2.2.0/24, connected to R1, which connects to R2, which connects via OSPF to R3. A callout near R1 states "Use an IP prefix list to filter routes." Routes flow from the cloud through R1 toward R2/R3, labeled "Routes."

**Single-Statement Matching**

```
ip ip-prefix aa index 10 permit 10.1.1.0 24
```
- Case 1: The route 10.1.1.0/24 is permitted, and other routes are rejected.

```
ip ip-prefix bb index 10 deny 10.1.1.0 24
```
- Case 2: All routes are rejected.

- Case1: This is the single-node exact matching. Only the route of the specified destination address and mask can match the IP prefix. In addition, the matching mode of the node is permit. As such, the route 10.1.1.0/24 matches the node and is permitted, and the other routes are rejected because they fail to match the IP prefix.
- Case 2: This is the single-node exact matching, and the matching mode of the node is deny. As such, the route 10.1.1.0/24 matches the node and is rejected, and other routes are rejected by default because they do not match the IP prefix.

#### IP Prefix Configuration Example (2)

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

Diagram description: Same topology as the previous slide — cloud containing routes 10.1.0.0/16, 10.1.1.0/24, 10.1.1.0/26, 10.1.1.1/32, 10.2.2.0/24, connected to R1, which connects to R2, which connects via OSPF to R3. Callout: "Use an IP prefix list to filter routes."

**Multi-Statement Matching**

```
ip ip-prefix aa index 10 deny 10.1.1.0 24
ip ip-prefix aa index 20 permit 10.1.1.1 32
```
- Case 1: The route 10.1.1.0/24 is rejected, the route 10.1.1.1/32 is permitted, and other routes are rejected.

```
ip ip-prefix bb index 10 permit 10.1.1.0 24 greater-equal 26 less-equal 32
```
- Case 2: Routes 10.1.1.0/26 and 10.1.1.1/32 are permitted, and the other routes are rejected.

- Case 1: This is the multi-node exact matching.
  - When the route 10.1.1.0/24 is matched against index 10, the route meets the matching condition but is rejected because the matching mode is deny.
  - The route 10.1.1.1/32 does not match index 10 and continues to be matched against index 20. The matching is successful, and the matching mode of index 20 is permit, indicating that the route is permitted.
  - Other routes are rejected by default because they do not meet the conditions of indexes 10 and 20.
- Case 2: In this case, greater-equal-value is 26, and less-equal-value is 32. The setting must meet the following formula: mask-length <= greater-equal-value <= less-equal-value. Otherwise, the configuration fails.

#### IP Prefix Configuration Example (3)

*(Breadcrumb on slide: ACL > IP Prefix List, with IP Prefix List highlighted)*

Diagram description: Same topology as the previous two slides — cloud containing routes 10.1.0.0/16, 10.1.1.0/24, 10.1.1.0/26, 10.1.1.1/32, 10.2.2.0/24, connected to R1, which connects to R2, which connects via OSPF to R3. Callout: "Use an IP prefix list to filter routes."

**Wildcard address matching**

```
ip ip-prefix aa index 10 permit 0.0.0.0 8 less-equal 32
```
- Case 1: All routes with the mask length ranging from 8 to 32 bits are permitted.

```
ip ip-prefix bb index 10 deny 0.0.0.0 24 less-equal 32
ip ip-prefix bb index 20 permit 0.0.0.0 0 less-equal 32
```
- Case 2: The route 10.1.0.0/16 is permitted, and other routes are rejected.

- Case 1: In this case, greater-equal-value is 8, and less-equal-value is 32. Because the address 0.0.0.0 is a wildcard address, routes with the mask length ranging from 8 to 32 bits meet the matching conditions.
- Case 2:
  - For index 10, greater-equal-value is 24, and less-equal-value is 32. Because the address 0.0.0.0 is a wildcard address, routes with the mask length ranging from 24 to 32 bits are all denied.
  - For index 20, greater-equal-value is 0, and less-equal-value is 32. Because the address 0.0.0.0 is a wildcard address, all routes except the routes with the mask length ranging from 24 to 32 bits are permitted.

> Note: The body text for Case 2 above states the result is "10.1.0.0/16 is permitted, and other routes are rejected," which is copied verbatim from the slide; the explanatory notes below it describe the mechanics of indexes 10 and 20 as shown in the source without further reconciliation, since the instructions require preserving the material exactly as presented.

### Route-Policy

#### Policy Tool 1: Filter-Policy

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

- The filter-policy is a common tool for filtering routing information. It can filter routes to be accepted, advertised, and imported. The filter-policy applies to IS-IS, OSPF, and BGP.

Diagram description: Topology showing R1 — R2 — R3 running BGP between them. Above R1, a box lists routes 10.1.1.0, 10.1.2.0, 10.1.3.0. An arrow labeled "Filter-Policy" points from this box to a box above R2/R3 listing 10.1.1.0, 10.1.2.0, and 10.1.3.0 (struck through), indicating 10.1.3.0 is filtered out.

- As shown in the preceding figure, BGP runs between R1, R2, and R3. Routes are transmitted between devices. To filter certain routing information as needed, you can use the filter-policy.

#### Filter-Policy Application in Distance-Vector Routing Protocols

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

- In distance-vector routing protocols, routing information is transmitted between devices. To filter such information, you can use filter-policies. The following figure shows the locations where the filter-policies take effect in the inbound and outbound directions.

Diagram description: Two device boxes, R1 and R2. R1 contains "Database" and "IP routing table" boxes with an arrow from Database to IP routing table; "Routing information" flows into Database. Below R1, a "filter-policy export" label with an arrow pointing up into R1's IP routing table/Database flow. R2 similarly contains "Database" and "IP routing table" boxes. Above R2, a "filter-policy import" label with an arrow pointing down into R2's Database. Routing information flows out of R2's IP routing table labeled "Routing information," and also flows from R1 to R2.

- A distance-vector protocol generates routes based on the routing table. Consequently, the filter affects the routes to be accepted from neighbors and the routes to be advertised to neighbors.
- To filter out the routes from an upstream device to a downstream device, run the filter-policy export command on the upstream device or the filter-policy import command on the downstream device.

#### Filter-Policy Application in Link-State Routing Protocols

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

- In a link-state routing protocol, routing devices exchange LSAs, and then calculate entries in the routing table based on LSDB information summarized from the LSAs. A filter-policy, however, can filter routes but not LSAs.

Diagram description: Two device boxes, R1 and R2. LSAs flow left-to-right: into R1's LSDB, from R1's LSDB to R2's LSDB, and out of R2's LSDB, all labeled "LSA." R1 also has a "Locally originated Type 5 LSA" box feeding into a "filter-policy export" label, which feeds into R1's LSDB, with an annotation: "Export filtering: Filtering routes; Filtering routes to be imported from other protocols." R1's LSDB connects down to an "IP routing table" box; a "filter-policy import" label sits between them with an annotation: "Import filtering: Do not add routes to the routing table." R2's LSDB similarly connects down to its own "IP routing table" box.

- OSPF stores the flooded LSAs in its LSDB and runs the SPF algorithm to calculate a loop-free SPT with the local device as the root. The filter-policy module filters the routes calculated by OSPF (before the routes are installed into the routing table) but does not filter LSAs.
- The preceding example uses OSPF to show how a filter-policy is applied in a link-state routing protocol.

#### Basic Configuration Commands of a Filter-Policy (1)

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

1. Application in OSPF

```
[Huawei-ospf-100] filter-policy { acl-number | acl-name acl-name | ip-prefix ip-prefix-name | route-policy route-policy-name [ secondary ] } import
```
Configure a filter-policy to filter routes to be accepted by OSPF.

```
[Huawei-ospf-100] filter-policy { acl-number | acl-name acl-name | ip-prefix ip-prefix-name | route-policy route-policy-name } export [ protocol [ process-id ] ]
```
Filter the imported routes to be advertised based on the filter-policy.

- Command: [Huawei-ospf-100] filter-policy {acl-number | acl-name acl-name | ip-prefix ip-prefix-name | route-policy route-policy-name [secondary]} import
  - acl-number: specifies the number of a basic ACL. The value is an integer ranging from 2000 to 2999.
  - acl-name acl-name: specifies the name of an ACL. The value is a string of 1 to 32 case-sensitive characters, spaces not supported. The value must start with a letter (a to z or A to Z).
  - ip-prefix ip-prefix-name: specifies the name of an IP prefix list. The value is a string of 1 to 169 case-sensitive characters, spaces not supported. If spaces are used, the string must start and end with double quotation marks (").
  - route-policy route-policy-name: specifies the name of a route-policy. The value is a string of 1 to 40 case-sensitive characters, spaces not supported. If spaces are used, the string must start and end with double quotation marks (").
  - secondary: indicates that the sub-optimal route is selected.

#### Basic Configuration Commands of a Filter-Policy (2)

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

2. Application in IS-IS

```
[Huawei-isis-1] filter-policy { acl-number | acl-name acl-name | ip-prefix ip-prefix-name | route-policy route-policy-name } import
```
Configure a filter-policy to filter IS-IS routes to be added to the IP routing table.

```
[Huawei-isis-1] filter-policy { acl-number | acl-name acl-name | ip-prefix ip-prefix-name | route-policy route-policy-name } export [ protocol [ process-id ] ]
```
Configure a filter-policy for IS-IS to filter imported routes to be advertised.

#### Basic Configuration Commands of a Filter-Policy (3)

*(Breadcrumb on slide: Filter-Policy > Route-Policy, with Filter-Policy highlighted)*

3. Application in BGP

```
[Huawei-bgp-af-ipv4] filter-policy { acl-number | acl-name acl-name | ip-prefix ip-prefix-name } import
```
Configure a filter-policy to filter routes to be accepted by BGP.

```
[Huawei-bgp-af-ipv4] filter-policy { acl-number | acl-name acl-name | ip-prefix ip-prefix-name } export [ protocol [ process-id ] ]
```
Configure a filter-policy to filter routes to be advertised. Only the routes that pass the filtering can be advertised by BGP.

```
[Huawei-bgp-af-ipv4] peer { group-name | ipv4-address } filter-policy { acl-number | acl-name acl-name } { import | export }
```
Configure a filter-policy to filter routes to be advertised to or accepted from a specified peer or peer group.

#### Applying a Filter-Policy to OSPF

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

Diagram description: Two side-by-side diagrams under headers "filter-policy import" and "filter-policy export."
- Left ("filter-policy import"): R1 and R2 connected, exchanging LSA 1, LSA 2, LSA 3, LSA 4 (labeled "Link state information") in both directions. R1's routing table shows 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24, 10.1.4.0/24. R2's routing table shows only 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24 (10.1.4.0/24 filtered out). A config box below shows: "ospf 1 / filter-policy 2000 import". Caption: "The filter-policy import command configures a filter-policy to filter routes to be accepted. Only the routes that pass the filter-policy are added to the routing table. The routes that do not pass the filter-policy are not added to the routing table, but they can be advertised."
- Right ("filter-policy export"): R1 and R2 connected. R1 advertises routes 172.16.1.0/24, 172.16.2.0/24, 172.16.3.0/24 toward R2, but only 172.16.1.0/24 arrives (172.16.2.0/24 and 172.16.3.0/24 shown struck through). A config box shows: "ospf 1 / import-route static / filter-policy 2000 export". Caption: "After OSPF imports external routes using the import-route command, to prevent routing loops, you can run the filter-policy export command to filter the imported routes to be advertised. Only the external routes that meet the filtering conditions are translated into Type 5 LSAs (AS-external-LSAs) and then advertised."

- OSPF routing information is recorded in the LSDB. The filter-policy import command is used to filter the routes calculated by OSPF, but not to filter LSAs to be accepted or advertised.
- The filter-policy export command allows you to specify a protocol or process ID to filter the routes of a specified protocol or a specified process. If neither protocol nor process-id is specified, OSPF filters all imported routes.

#### Applying a Filter-Policy to IS-IS

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

Diagram description: Two side-by-side diagrams under headers "filter-policy import" and "filter-policy export."
- Left ("filter-policy import"): R1 and R2 connected, exchanging LSP 1, LSP 2, LSP 3, LSP 4 (labeled "Link state information") in both directions. R1's routing table shows 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24, 10.1.4.0/24. R2's routing table shows 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24 (10.1.4.0/24 filtered). A config box shows: "isis / filter-policy 2000 import". Caption: "Similar to usage in OSPF, the filter-policy import command affects only the local routing table. That is, the matching routes are not added to the routing table, and the LSP flooding and LSDB synchronization of the local device are not affected."
- Right ("filter-policy export"): A BGP cloud connects to R1, which connects to R2 via IS-IS. Two tables shown: "BGP routing table" and "IS-IS routing table," with an arrow from BGP routing table to IS-IS routing table. A config box shows: "isis 1 / import-route bgp / filter-policy 2000 export". Caption: "If IS-IS and other routing protocols are deployed on a network and a boundary device has imported routes from other routing protocols, the boundary device advertises all imported external routes to its IS-IS neighbors by default. To advertise only some imported external routes to neighbors, run the filter-policy export command."

- IS-IS routing entries can be used to guide IP packet forwarding only after they are successfully delivered to the IP routing table. If an IS-IS routing table has routes destined for a specific network segment but these routes do not need to be added to the IP routing table, run the filter-policy import command and use a basic ACL, an IP prefix list, or a route-policy to filter the IS-IS routes to be added to the IP routing table.

#### Applying a Filter-Policy to BGP

*(Breadcrumb on slide: Filter-Policy > Route-Policy)*

Diagram description: Two side-by-side diagrams under headers "filter-policy import" and "filter-policy export."
- Left ("filter-policy import"): R1 and R2 in AS 100, connected, exchanging "BGP Update" messages containing NLRI: Route-entry 1, NLRI: Route-entry 2 (from R1 side) and NLRI: Route-entry 1 (from R2 side). R1's routing table shows 10.1.1.0/24, 10.1.2.0/24. R2's routing table shows only 10.1.1.0/24. A config box shows: "bgp 100 / ipv4-family unicast / filter-policy 2000 import". Caption: "The filter-policy import command can be used to filter the routes to be accepted by BGP globally and determine whether to add the routes to the BGP routing table."
- Right ("filter-policy export"): R1 and R2 in AS 100, connected. R1's routing table shows 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24. A "BGP Update" message from R1 to R2 contains NLRI: Route-entry 1, NLRI: Route-entry 2. A config box shows: "bgp 100 / ipv4-family unicast / filter-policy 2000 export". Caption: "The filter-policy export command is used to filter the routes to be advertised. Only the routes that pass the filtering can be added to the local BGP routing table and advertised by BGP."

#### Policy Tool 2: Route-Policy

*(Breadcrumb on slide: Filter-Policy > Route-Policy, with Route-Policy highlighted)*

- A route-policy is a policy tool used to filter routes and set route attributes for the filtered routes.
- A route-policy consists of one or more nodes. Each node can be a set of conditional statements (matching conditions) and executive statements (actions). These statements are arranged in ascending order by sequence number.

Diagram description: "route-policy test" points via an arrow to a stack of nodes: "Node 1 (matching mode: permit)" containing "Conditional statement" and "Executive statement"; "Node 2 (matching mode: permit)" containing "Conditional statement" and "Executive statement"; "..."; "Node N (matching mode: permit)" containing "Conditional statement" and "Executive statement." A vertical bracket labeled "Top-Down" spans the nodes. To the right, notes state: "Each node contains one or more conditional statements. The relationship between multiple conditional statements on a node is AND. The action on the node is executed only when all conditional statements are met." and "The relationship between nodes is OR. The route-policy is executed in ascending order by node ID. A node in a route-policy will not be further matched."

- When a route-policy is used, the node with a smaller ID is matched first. After a route matches a node, the route is not matched against other nodes. If a route fails to match all nodes, the route is filtered out.

#### Components of a Route-Policy

*(Breadcrumb on slide: Filter-Policy > Route-Policy, with Route-Policy highlighted)*

- A route-policy consists of one or more nodes. Each node contains multiple if-match and apply clauses.

Diagram description: A box showing labeled components of the command "route-policy test permit node 10" with labels: "Route-policy name" (test), "Matching mode of a node" (permit), "Node ID" (10). Below, indented lines show "if-match x1" and "if-match x2" (labeled "Conditional statement") and "apply y1" (labeled "Executive statement"). This is followed by a second node block: "route-policy test permit node 20 / if-match x3 x4 / apply y2", and "...", and a final node block: "route-policy test permit node N / if-match xn / apply yn".

- permit or deny: The matching mode of a route-policy node is "permit" or "deny".
- node: specifies the node ID of a route-policy. The value is an integer ranging from 0 to 65535.
- if-match clause: defines the matching condition of a node.
- apply clause: defines an action to be performed on a matching route.

#### Matching Order for a Route-Policy

*(Breadcrumb on slide: Filter-Policy > Route-Policy, with Route-Policy highlighted)*

- Route-policies use different matching conditions and modes to select routes and change route attributes.

Diagram description: A flowchart starting at "route-policy," proceeding to "node 1," which contains "If-match / If-match / ..." (labeled "Sequence matching"). If the route meets all conditions ("Meet all conditions"), it proceeds to "Matching mode" — if "permit," goes to "apply / apply / ..." then "Match the route-policy" (labeled "Unique match"); if "deny," goes to "Deny." If the route meets only some conditions ("Meet only some conditions"), it goes to "Deny" as well, and continues down to "..." then "node N," which similarly contains "If-match / If-match / ..." and follows the same "Matching mode" logic (permit → apply → "Match the route-policy"; deny → "Deny"; meet only some conditions → "Deny").

- A route-policy contains N (N >= 1) nodes. After routes match the route-policy, the system checks whether the routes match the nodes in ascending order by node ID. The matching condition is defined in the if-match clause.
  - After a route matches all if-match clauses of a node, the system proceeds to select a matching mode and no longer matches the route against other nodes. The matching mode can be "permit" or "deny."
    - permit: The route is permitted, and the apply clause of the node is used to set some attributes of the route.
    - deny: The route is rejected.
  - If a route fails to match any if-match clause of the node, the route is further matched against the next node. If a route does not match any node, the route is rejected.

#### Basic Configuration Commands of a Route-Policy (1)

*(Breadcrumb on slide: Filter-Policy > Route-Policy, with Route-Policy highlighted)*

1. Create a route-policy.

```
[Huawei] route-policy route-policy-name { permit | deny } node node
```
Create a route-policy and enter the route-policy view.

2. (Optional) Configure if-match clauses.

```
[Huawei-route-policy] if-match ?
  acl: matches a basic ACL.
  cost: matches the cost of a route.
  interface: matches the outbound interface in a route.
  ip-prefix: matches a prefix list.
  ...
```

- Command: route-policy route-policy-name { permit | deny } node node
  - permit: sets the matching mode of a route-policy node to permit. If a route matches all if-match clauses of a node, the apply clause of the node is executed. Otherwise, the system goes to the next node.
  - deny: indicates that the matching mode of the route-policy node is deny. If a route matches all if-match clauses of a node, the route is rejected. Otherwise, the system goes to the next node.
  - node node: specifies the node ID of a route-policy. When a route-policy is used, the node with the smallest node ID is matched first. After a route matches a node, the route is not matched against other nodes. If a route fails to match any nodes, the route is filtered out. The value is an integer ranging from 0 to 65535.

#### Basic Configuration Commands of a Route-Policy (2)

*(Breadcrumb on slide: Filter-Policy > Route-Policy, with Route-Policy highlighted)*

3. (Optional) Configure an apply clause.

```
[Huawei-route-policy] apply ?
  cost: sets the cost of a route.
  cost-type {type-1 | type-2}: sets the OSPF cost type.
  ip-address next-hop: sets the next-hop address for an IPv4 route.
  preference: sets the preference of a routing protocol.
  tag: sets the tag field in routing information.
  ...
```

- The apply clause is used to specify an action for the route-policy and set the attributes of the routes that match the route-policy. If no apply clause is configured for a node, the node only filters routes. If one or more apply clauses are configured, all apply clauses are applied to the routes that match the node.

---

## 3. Route Control Cases

### Filtering Received Routes

Diagram description: Topology showing R1 connected to R2 connected to R3, running OSPF area 0. R1 advertises routes 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24, and 192.168.4.0/24 into OSPF.

- OSPF runs on R1, R2, and R3. R1 advertises the routes 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24, and 192.168.4.0/24 to OSPF.
- It is required that R3 cannot access network segment 192.168.1.0/24 on R1, but R2 can.
- To meet this requirement, you can use a filter-policy to filter the received routes on R3.

**The configuration of R3 is as follows:**

```
[R3] ip ip-prefix in index 10 permit 192.168.2.0 24
[R3] ip ip-prefix in index 10 permit 192.168.3.0 24
[R3] ip ip-prefix in index 10 permit 192.168.4.0 24

[R3] ospf
[R3-ospf-1] filter-policy ip-prefix in import
```

Note: Basic network configurations are not provided.

> Note: The three `ip ip-prefix in index 10 permit ...` lines all use the same index (10) in the source slide; this is reproduced exactly as shown without correction, per instructions to flag rather than fix apparent inconsistencies.

### Filtering Routes to Be Advertised

Diagram description: Topology showing R1 connected to R2 connected to R3, running OSPF area 0. An arrow labeled "Introduce direct routes" loops into R1, which has local networks 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24, 192.168.4.0/24.

- OSPF runs on R1, R2, and R3. R1 imports the direct routes 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24, and 192.168.4.0/24 to OSPF.
- It is required that R2 and R3 learn only the routes to 192.168.1.0/24 and not the routes to the other three network segments.
- To meet this requirement, configure a filter-policy on R1 to filter the imported routes to be advertised.

**The configuration of R1 is as follows:**

```
[R1] ip ip-prefix out index 10 permit 192.168.1.0 24

[R1] ospf
[R1-ospf-1] import-route direct
[R1-ospf-1] filter-policy ip-prefix out export
```

Note: Basic network configurations are not provided.

### Modifying Route Attributes

Diagram description: Topology showing R1 connected to R2 connected to R3, running OSPF area 0. An arrow labeled "Import direct routes" loops into R1, which has local network 192.168.1.0/24.

- OSPF runs on R1, R2, and R3. R1 imports the direct route 192.168.1.0/24 to OSPF.
- It is required that the OSPF route 192.168.1.0/24 learned by R2 and R3 be an external Type 1 route. By default, the route is an external Type 2 route.
- To meet this requirement, you can use a route-policy on R1 to change the type of external routes to external Type 1 when routes are imported.

**The configuration of R1 is as follows:**

```
[R1] ip ip-prefix external index 10 permit 192.168.1.0 24

[R1] route-policy RP permit node 10
[R1-route-policy] if-match ip-prefix external
[R1-route-policy] apply cost-type type-1
[R1-route-policy] quit

[R1] ospf
[R1-ospf-1] import-route direct route-policy RP
```

Note: Basic network configurations are not provided.

### Dual-Node Bidirectional Route Import

Diagram description: Topology showing a network segment 10.1.1.0/24 attached to R1, and a network segment 10.4.4.0/24 attached to R4. Inside a shaded region, R2 and R3 sit between R1 and R4. R1–R2, R1–R3, R2–R4, and R3–R4 are all connected. The left half (R1 side, containing R2 and R3) runs OSPF; the right half (R4 side, containing R2 and R3) runs IS-IS. Curved arrows above and below indicate route import: "Import OSPF routes to IS-IS" and "Import IS-IS routes to OSPF," both occurring at R2 and at R3.

- Bidirectional route import refers to the process in which boundary routers in two routing domains imports routes into each other.
- If two border routers are on the borders of two routing domains and bidirectional route import is performed on both border routers, this is called dual-node bidirectional route import.
- Dual-node bidirectional route import is a typical routing model. Single-node bidirectional route import lacks redundancy. Once a single border router is faulty, communication between two routing domains may fail. Therefore, dual-node bidirectional route import is generally used in large-scale network deployment.
- Although this function enhances network reliability, it may cause problems, such as sub-optimal paths and routing loops.

### Suboptimal Path Problem

*(Breadcrumb on slide: Suboptimal Path > Routing Loop)*

Diagram description: Topology showing 10.1.1.0/24 attached to R1. R1 connects to both R2 and R3 within an OSPF region (shaded box); R2 and R3 both connect to R4 within an IS-IS region (also inside the shaded box, to the right). Numbered steps annotate the diagram: (1) "Import direct routes" — a loop arrow at R1 importing 10.1.1.0/24; (2) arrows from R1 to R2 and R1 to R3 labeled with red solid lines (OSPF LSA); (3) arrows from R2 to R4 and R3 to R4 labeled with red dashed lines (IS-IS LSP). A green arrow shows "Access traffic" flowing from R4 through R3 through R2 back to R1 (labeled in the legend). The legend defines: red solid arrow = OSPF LSA, red dashed arrow = IS-IS LSP, green arrow = Access traffic. A table shows: Destination/Mask = 10.1.1.0/24, Proto = ISIS, Pre = 15, positioned near R3.

The following uses the direct route 10.1.1.0/24 as an example:

- R1 imports the direct route 10.1.1.0/24 to OSPF.
- R2 and R3 re-advertise bidirectional routes. R2 re-advertises the route 10.1.1.0/24 to IS-IS, and R3 learns the IS-IS route from R4.
- For R3, the IS-IS route with preference 15 is preferred over the OSPF external route with preference 150. Therefore, the IS-IS route from R4 is preferred. The path through which R3 accesses the network segment 10.1.1.0/24 is R3 -> R4 -> R2 -> R1, which is the second optimal path.

### Solving the Suboptimal Path Problem (1)

*(Breadcrumb on slide: Suboptimal Path > Routing Loop)*

Diagram description: Same topology as the previous slide (10.1.1.0/24 attached to R1; R1 connects to R2 and R3 in OSPF region; R2 and R3 connect to R4 in IS-IS region), but now the green "Access traffic" arrow flows directly from R1 to R3 (shorter path), rather than through R4/R2. The table now shows: Destination/Mask = 10.1.1.0/24, Proto = OSPF, Pre = 150, positioned near R3.

- Solution 1: In the IS-IS process of R3, configure a filter-policy to prevent the route 10.1.1.0/24 sent by R4 from being added to the local routing table.
- Perform the following operations on R3:

```
[R3] acl 2001
[R3-acl-basic-2001] rule 5 deny source 10.1.1.0 0
[R3-acl-basic-2001] rule 10 permit

[R3] isis
[R3-isis-1] filter-policy 2001 import
```

> Note: The ACL rule `rule 5 deny source 10.1.1.0 0` uses wildcard 0 (exact host match) against network address 10.1.1.0, which as written would only exactly match a route with host bits all zero represented as a /32-style exact match rather than the /24 network route; this is reproduced exactly as shown in the source slide without correction.

### Solving the Suboptimal Path Problem (2)

*(Breadcrumb on slide: Suboptimal Path > Routing Loop)*

Diagram description: Same topology as before (10.1.1.0/24 attached to R1; R1 connects to R2 and R3 in OSPF region; R2 and R3 connect to R4 in IS-IS region), with the green "Access traffic" arrow flowing directly from R1 to R3. The table shows: Destination/Mask = 10.1.1.0/24, Proto = OSPF, Pre = 14, positioned near R3.

- Solution 2: Configure an ACL on R3 to match the route 10.1.1.0/24, apply the ACL to the route-policy, and set the preference of the route that matches the ACL to 14 (higher than IS-IS). Run the preference ase command in the OSPF view to invoke the route-policy to change the preference of external routes.
- Perform the following operations on R3:

```
[R3]acl 2000
[R3-acl-basic-2000] rule permit source 10.1.1.0 0
[R3-acl-basic-2000] quit

[R3]route-policy hcip permit node 10
[R3-route-policy] if-match acl 2000
[R3-route-policy] apply preference 14
[R3-route-policy] quit

[R3]ospf 1
[R3-ospf-1] preference ase route-policy hcip
```

> Note: `[R3-acl-basic-2000] rule permit source 10.1.1.0 0` omits an explicit rule-id (no number given before "permit"), reproduced exactly as shown in the slide.

### Routing Loops

*(Breadcrumb on slide: Suboptimal Path > Routing Loop, with Routing Loop highlighted)*

Diagram description: Same topology as the suboptimal path slides (10.1.1.0/24 attached to R1; R1 connects to R2 and R3 in an OSPF region; R2 and R3 connect to R4 in an IS-IS region), with numbered arrows: (1) "Import direct routes" loop at R1; (2) R1 to R2 and R1 to R3 (OSPF LSA, red solid); (3) R2 to R4 and R3 to R4 (IS-IS LSP, red dashed); (4) an additional arrow from R3 back toward R1/R2 area, indicating re-advertisement forming a loop. Table shows: Destination/Mask = 10.1.1.0/24, Proto = ISIS, Pre = 15, positioned near R3.

**Scenario description:**
1. Import the direct route 10.1.1.0/24 to OSPF on R1.
2. Configure OSPF on R1, R2, and R3. The route to the network segment 10.1.1.0/24 is advertised in the entire OSPF area.
3. R2 re-advertises bidirectional routes.
4. Configure IS-IS on R2, R3, and R4. The route to the network segment 10.1.1.0/24 is advertised in the entire IS-IS domain.
5. R3 re-advertises bidirectional routes.
6. The route destined for the network segment 10.1.1.0/24 is advertised to the OSPF area again, forming a routing loop.

### Preventing Routing Loops (1)

*(Breadcrumb on slide: Suboptimal Path > Routing Loop, with Routing Loop highlighted)*

Diagram description: Same topology as the "Routing Loops" slide (10.1.1.0/24 attached to R1; OSPF region containing R1, R2, R3; IS-IS region containing R2, R3, R4), with the same numbered arrows (1) Import direct routes at R1, (2) R1→R2/R1→R3 OSPF LSA, (3) R2→R4/R3→R4 IS-IS LSP. Table shows: Destination/Mask = 10.1.1.0/24, Proto = OSPF, Pre = 150, positioned near R3.

- Solution 1: Configure a route-policy on R3 to filter out the route destined for 10.1.1.0/24 when OSPF imports IS-IS routes.
- Perform the following operations on R3:

```
[R3] acl 2001
[R3-acl-basic-2001] rule 5 deny source 10.1.1.0 0
[R3-acl-basic-2001] rule 10 permit

[R3] route-policy RP permit node 10
[R3-route-policy] if-match 2001
[R3-route-policy] quit

[R3] ospf
[R3-ospf-1] import-route isis 1 route-policy RP
```

> Note: `[R3-route-policy] if-match 2001` appears to be missing the `acl` keyword (compare to the `if-match acl 2000` syntax shown in the "Solving the Suboptimal Path Problem (2)" slide); reproduced exactly as shown in the source without correction.

### Preventing Routing Loops (2)

*(Breadcrumb on slide: Suboptimal Path > Routing Loop, with Routing Loop highlighted)*

Diagram description: Same topology as before (10.1.1.0/24 attached to R1; OSPF region containing R1, R2, R3; IS-IS region containing R2, R3, R4), with numbered arrows (1) Import direct routes at R1, (2) R1→R2/R1→R3 OSPF LSA, (3) R2→R4/R3→R4 IS-IS LSP. A callout above R2 reads "Configure a route-policy. Add tag 200 to the route 10.1.1.0/24." A callout below R3 reads "Using a route-policy to filter routes with tag 200."

- Solution 2: Use tags to implement selective route import. Add tag 200 to the route 10.1.1.0/24 imported from OSPF to IS-IS on R2, and filter the route with tag 200 when importing the route from IS-IS to OSPF on R3.
- Perform the following operations on R2:

```
[R2]acl 2000
[R2-acl-basic-2000]rule permit source 10.1.1.0 0
[R2-acl-basic-2000]quit

[R2]route-policy hcip permit node 10
[R2-route-policy]if-match acl 2000
[R2-route-policy]apply tag 200
[R2-route-policy]quit

[R2]isis 1
[R2-isis-1]import-route ospf route-policy hcip
```

### Preventing Routing Loops (3)

*(Breadcrumb on slide: Suboptimal Path > Routing Loop, with Routing Loop highlighted)*

Diagram description: Same topology as before (10.1.1.0/24 attached to R1; OSPF region containing R1, R2, R3; IS-IS region containing R2, R3, R4), with numbered arrows (1) Import direct routes at R1, (2) R1→R2/R1→R3 OSPF LSA, (3) R2→R4/R3→R4 IS-IS LSP. A callout above R2 reads "Configure a route-policy. Add tag 200 to the route 10.1.1.0/24." A callout below R3 reads "Using a route-policy to filter routes with tag 200."

- Perform the following operations on R3:

```
[R3]route-policy hcip deny node 10
[R3-route-policy]if-match tag 200
[R3-route-policy]quit
[R3]route-policy hcip permit node 20

[R3]ospf 1
[R3-ospf-1]import-route isis route-policy hcip
```

A highlighted note box: "Although IP prefix-based route filtering can be used for route re-advertisement, the involved configuration workload is heavy on a large network. Instead of using IP prefixes, setting tags greatly reduces the configuration workload."

> Note: In this code block, the line `[R3]route-policy hcip permit node 20` appears without a following `if-match`/`quit`, reproduced exactly as shown in the source slide.

### Thinking About the Following Scenario

*(Breadcrumb on slide: Suboptimal Path > Routing Loop, with Routing Loop highlighted)*

Diagram description: Topology showing network segment 10.1.1.0/24 attached to R1 and network segment 10.4.4.0/24 attached to R4. R1 and R4 sit on either side of a shaded region containing R2 (top) and R3 (bottom), both R2 and R3 connecting to both R1 and R4. The left portion (R1 side) is labeled OSPF; the right portion (R4 side) is labeled IS-IS. Curved arrows near R2 and R3 indicate bidirectional route import between OSPF and IS-IS at both nodes.

A highlighted note box: "On R1, import the network segment route 10.1.1.0/24 to OSPF; on R4, import the network segment route 10.4.4.0/24 to IS-IS; on R2 and R3, import routes bidirectionally. In this scenario, how can we prevent routing loops by setting tags?"

---

## Quiz

1. (Essay) What are the functions of export filter-policies in OSPF and BGP?
2. (Essay) What is the logical relationship between nodes in a route-policy? What is the logical relationship between multiple conditional statements on a node?

- In OSPF, the export filter-policy is used to filter the routes to be imported from other routing protocols to OSPF. In BGP, the export filter-policy is used to filter routes to be advertised.
- The logical relationship between nodes is OR, and the logical relationship between conditional statements is AND.

