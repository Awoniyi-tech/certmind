# IGMP Implementation and Configurations

## Foreword

- In multicast communication, a multicast network needs to send multicast data to specific multicast group members. Therefore, the multicast network needs to know the locations of the group members and the multicast groups that the group members join.
- Through Internet Group Management Protocol (IGMP), group members send group joining messages to the multicast network, so that the multicast network obtains the locations of the group members and the multicast groups that the group members join.
- This course describes the functions and implementation of IGMP, including the implementation and differences of IGMPv1, IGMPv2, and IGMPv3, and the implementation of IGMP snooping, IGMP SSM mapping, as well as IGMP proxy.

## Objectives

- On completion of this course, you will be able to:
  - Understand IGMP implementation and configurations.
  - Understand the differences between different IGMP versions.
  - Understand the implementation of IGMP snooping.
  - Understand the implementation of IGMP SSM mapping.
  - Understand the implementation of IGMP proxy.

## Contents

1. IGMP Introduction
   - Overview
   - Implementation of IGMP
2. IGMP Feature Introduction
   - IGMP Snooping Introduction
   - IGMP SSM Mapping Introduction
   - IGMP Proxy Introduction
3. IGMP Configurations

## 1. IGMP Introduction

### Overview

#### Demands of Forwarding on a Multicast Network

- IP multicast transmits packets from a source to a group of receivers. In the multicast communication model, the multicast source does not need to know the locations of receivers, and multicast data can be sent to multicast group members only through the multicast network.
- The multicast network needs to know the locations of multicast group members and the multicast groups that the members join so that the multicast network can forward multicast data to the members.
- How does the multicast network discover multicast group members?

Diagram description: A multicast source sends a multicast packet into a multicast network containing several routers, which fan out to three multicast group members. Question-mark callouts are attached to each branch: near the top receiver, "Do group members need to receive multicast data?"; near the middle receiver, "Which multicast group do group members need to receive packets of?"; near the bottom receiver, "Are group members still in the group?" — illustrating the three fundamental questions the multicast network must answer (presence, group membership, and continued membership) to correctly forward data.

#### Multicast Group Member Discovery

- A multicast network can discover multicast group members in either of the following modes:
  - Manual static configuration: An interface connected to multicast group members is manually specified on a multicast router, and information about the multicast group members is statically configured.
    - The manual static mode is not flexible and requires heavy configuration workload. However, it features high stability and can quickly establish a multicast forwarding path for new group members.
  - Dynamic discovery: The multicast network obtains the interface connected to multicast group members and their group joining information through IGMP messages.
    - Being flexible and easy to configure, the dynamic discovery mode is widely used on the live network.
- After the multicast network obtains the locations of group members and the multicast groups that the group members join, multicast packets can be forwarded accordingly.

Diagram description: A multicast source sends packets of multicast group G1 into a router connected to a multicast network, which reaches two multicast group members, each shown joining multicast group G1. A callout labeled "Multicast data forwarding according to group joining information" points at the network, showing that once group-joining information is known, the network forwards data only to the interested members.

- Multicast packet forwarding on a multicast network depends on an MDT. For details about the MDT, see **PIM Implementation and Configurations**.

#### IGMP Overview

- In the TCP/IP protocol suite, IGMP is responsible for managing IP multicast members. It establishes and maintains multicast group memberships between IP hosts and the multicast routers that are directly adjacent to the IP hosts.
- IGMP manages multicast members through IGMP messages exchanged between multicast group members and multicast routers. IGMP messages are encapsulated in IP packets.
- There are three versions of IGMP:
  - IGMPv1
  - IGMPv2
  - IGMPv3
- After exchanging IGMP messages with group members, multicast routers generate IGMP routing entries and IGMP group entries.
- IGMP routing entries and IGMP group entries help the multicast routers generate multicast routing entries.

Diagram description: A router with an IGMP-capable interface (IF1) connects upward to a multicast network and downward, via a switch, to two multicast group members — member 1 joining multicast group G1, member 2 joining multicast group G2. The router maintains an "IGMP Group" table (Multicast Group: G1, G2) and an "IGMP Routing Table" (Multicast Group / Outbound Interface: G1 → IF1, G2 → IF1), populated by IGMP messages exchanged with each member.

#### IGMP Group Entries and Routing Entries

- IGMP generates IGMP routing entries and IGMP group entries, based on which multicast routing entries are generated.
  - An IGMP group entry is created when an IGMP Report message is received from a host. This entry is used to maintain group joining information and instruct multicast routing protocols (such as PIM) to create a corresponding (*, G) entry.
  - An IGMP group entry is as follows:

```
GigabitEthernet1/0/0(192.168.1.254):
  Total 1 IGMP Group reported
  Group Address    Last Reporter    Uptime      Expires
  239.0.0.1        192.168.1.1      00:02:04    00:01:17
  (Multicast group) (IP address of a group member)
```

  - IGMP routing entries are used to extend the outbound interfaces of multicast routing entries.
  - An IGMP routing entry is as follows:

```
00001. (*, 239.0.0.1)    //Receives multicast data from any multicast source.
     List of 1 downstream interface
       GigabitEthernet1/0/0 (192.168.1.254)   //Outbound interface
       Protocol: IGMP
```

#### IGMP Entries and Multicast Routing Entries

- On the last-hop multicast router (multicast leaf router), a multicast routing table is formed by summarizing IGMP routing entries, IGMP group entries, and the multicast protocol routing table (PIM routing table).
- IGMP routing entries and IGMP group entries provide multicast group addresses and outbound interfaces for the multicast routing table.

Diagram description: An "IGMP group entry" box shows the same example table as above (GigabitEthernet1/0/0(192.168.1.254), Group Address 239.0.0.1, Last Reporter 192.168.1.1, Uptime 00:02:04, Expires 00:01:17). An arrow labeled "Instructs the multicast router to create a PIM routing entry" points from the IGMP group entry to a "PIM routing table" box. Below, an "IGMP routing entry" box shows: 00001. (1.1.1.1, 239.0.0.1) //Receives multicast data from multicast source, List of 1 downstream interface, GigabitEthernet1/0/0 (192.168.1.254) //Outbound interface, Protocol: IGMP. Both the IGMP routing entry and the PIM routing table feed into a "Summarizes multicast routing information" box, which produces a final "Multicast routing entry" box: (1.1.1.1, 239.0.0.1), Upstream Interface: GigabitEthernet1/0/1, Downstream interfaces: 1: GigabitEthernet1/0/0.

- For details about the PIM protocol, see **PIM Implementation and Configurations**.

### Implementation of IGMP

#### Basic Concepts of IGMPv1

*(IGMPv1 → IGMPv2 → IGMPv3)*

- IGMPv1 uses a query-report mechanism to manage multicast groups.
- The query-report mechanism is implemented through two types of messages:
  - General Query message: a message sent by a querier to all hosts and routers on the local shared network to discover the multicast groups that have members.
  - Report message: Hosts send Report messages to the querier to request to join a multicast group or respond to Query messages.
- IGMP messages are multicast. Therefore, a multi-access network requires only one multicast router to send Query messages. This multicast router is called an IGMP querier.

Diagram description: A multicast network containing two multicast routers, both with IGMP-capable interfaces, connects down through a switch to two multicast group members. The router acting as IGMP querier sends a "General Query" message. Member 1 joins multicast group G1 and member 2 joins multicast group G2; each responds with a "Report" message back up through the switch to the routers. A legend distinguishes solid red arrows (General Query message), dashed blue arrows (Report message), and yellow dots (IGMP-capable interface).

#### IGMPv1 Message Format

- Both IGMPv1 General Query messages and Report messages are multicast messages with the destination address 224.0.0.1.
- IGMPv1 General Query messages are similar to Report messages in format, including three major fields: Version, Type, and Group Address.

Diagram description: A bit-field diagram, 0–31 bits wide, two rows. Row 1: Version (bits 0–3), Type (bits 4–7), Unused (bits 8–15), Checksum (bits 16–31). Row 2: Group Address (full 32 bits).

| Field | Description |
|---|---|
| Version | IGMP version. In IGMPv1 messages, this field is 1. |
| Type | Message type. The following two message types are available: 0x11: General Query message; 0x12: Report message |
| Group Address | Multicast group address. In a General Query message, this field is 0s. In a Report message, this field is set to the address of the multicast group that the member requests to join. |

#### IGMPv1 Group Joining Mechanism

- Through General Query messages and Report messages, the IGMP querier can know which multicast groups have members on the network segment.
- The basic process of IGMPv1 group joining is as follows:

Diagram description: A multicast network reaches an IGMP querier (IF1, IF2), which connects through a switch down to two multicast group members, member 1 and member 2, both joining multicast group G1. Numbered steps: ① The IGMP querier sends a General Query message. ② Member 1 responds with a Report message; member 2 does not respond with a Report message due to Report message suppression (shown crossed out). ③ After receiving the Report message, the IGMP querier generates an IGMP routing entry (Multicast Information *, G1 → Outbound Interface IF1) and an IGMP group entry (Multicast Group G1). A legend distinguishes solid red (General Query message), dashed blue (Report message from member 1), dotted (Report message from member 2), and yellow dots (IGMP-capable interface).

- The General Query and Report process is as follows:
  - The IGMP querier sends a General Query message, with destination address 224.0.0.1 (indicating all hosts and routers on the network segment). All group members start a timer when they receive the General Query message. The IGMP querier sends General Query messages at intervals. The interval is configurable, and the default interval is 60 seconds. Group members 1 and 2 are members of G1, and start Timer-G1 upon reception of the General Query message. By default, the value of the timer is a random value ranging from 0 to 10, in seconds.
  - The group member whose timer expires first sends a Report message for the group.
  - After receiving the Report message from group member 1, the IGMP querier knows that members of G1 exist on the local network segment. Then, the IGMP querier generates an IGMP group entry and (*, G1) IGMP routing entry. The asterisk (*) indicates any multicast source. Once the IGMP querier receives data of G1, it forwards the data to this network segment.
- Report message suppression mechanism:
  - The IGMP querier sends General Query messages at intervals. The interval is configurable, and the default interval is 60 seconds. Group members 1 and 2 are members of G1, and start Timer-G1 upon reception of the General Query message. By default, the value of the timer is a random value ranging from 0 to 10, in seconds.
  - Assuming that Timer-G1 on group member 1 expires first, group member 1 sends a Report message with G1 address as the destination address to the network segment. When group member 2 receives the Report message from group member 1, it stops Timer-G1 and does not send a Report message for G1. This mechanism reduces the number of Report messages transmitted on the network segment.

#### IGMPv1 Querier Election Mechanism

- General Query messages are multicast. Therefore, a network segment requires only one querier to query information about all group members.
- IGMPv1 does not have its own querier election mechanism. Instead, it relies on the multicast routing protocol (PIM) to elect an IGMP querier.
- IGMPv1 uses the unique assert winner or DR elected by PIM as the querier. The querier is the only device that sends Query messages on the local network segment.
- Both the querier and non-querier can receive Report messages with destination address 224.0.0.1. Therefore, they can generate both IGMP routing entries and IGMP group entries.

Diagram description: A multicast network reaches two multicast routers via a switch down to a multicast group member. The router elected as PIM DR is labeled "IGMPv1 querier" and sends "General Query" messages, while the non-querier router (marked with an X on its Query attempt) does not send General Query messages, per the note "A non-IGMPv1 querier does not send General Query messages." Both routers maintain an "IGMP Group" box and "IGMP Routing Table" box, with a note above both: "Both the IGMPv1 querier and non-querier can receive Report messages and generate IGMP entries." The group member responds with a "Report" message. A legend distinguishes General Query message (solid) and Report message (dashed).

- The assert winner or DR is used to forward multicast traffic.
- Detailed functions of the assert winner or DR will be covered in the course of **PIM Implementation and Configurations.**

#### IGMPv1 Group Leaving Mechanism

- IGMPv1 does not have Leave messages. After a group member leaves the multicast group, the member no longer responds to General Query messages.
- If no group members exist in a multicast group on a network segment, the IGMP querier will not receive any Report messages from any group member on the network segment. In this case, the IGMP querier deletes the multicast forwarding entries of this group after a certain period (130s by default).

Diagram description: A multicast network reaches an IGMP querier (IF1, IF2), connected via a switch down to two multicast group members. Member 1 joins multicast group G1; member 2 leaves multicast group G2. Numbered steps: ① The querier periodically sends General Query messages. ② G1 still has a group member, and the member responds with a Report message; all members in G2 have left, and the Query message is not responded to. ③ The multicast router can still receive Report messages of G1 and therefore retains the IGMP routing entry of G1; the multicast router does not receive any Report messages of G2 within a certain period, so it deletes the IGMP routing entry of G2. The IGMP Routing Table shows Multicast Entries *, G1 → IF1 retained, and *, G2 → IF1 struck through/removed. A legend distinguishes General Query message, Report message (member 1), Report message (member 2), and IGMP-capable interface.

- Group Leaving Mechanism
  - Assume that group member 2 wants to leave multicast group G2.
    - When group member 2 receives the General Query messages from the IGMP querier, it does not respond with Report messages for G2. Because G2 no longer has members on this network segment, the IGMP querier will not receive Report messages for G2. After a certain period (130 seconds by default), the IGMP querier **deletes the IGMP routing entry of G2**.
    - When group member 1 receives the General Query messages from the IGMP querier, it responds with Report messages for G1. The IGMP querier then retains the corresponding IGMP routing entry of G1.

#### IGMPv2

- IGMPv1 has the following defects in the group leaving and querier election mechanisms:
  - IGMPv1 uses the timeout mechanism to monitor group leaving status, and group members leave a group in silent mode. Before the timer expires, multicast traffic is still forwarded by the multicast router.
  - IGMPv1 querier election depends on PIM, which makes querier election inflexible.
- IGMPv2 overcomes the defects of IGMPv1.
  - IGMPv2 and IGMPv1 have similar group joining mechanisms.
  - IGMPv2 supports proactive group leaving.
  - IGMPv2 supports querier election.
- IGMPv2 is compatible with IGMPv1.

Diagram description: A box titled "IGMPv1 Defects" showing a multicast network with a PIM DR / IGMP querier router and a second router; a note "Depends on PIM to elect an IGMP querier" points at the querier election, with a "General Query" arrow. Below, a switch connects to a multicast group member that has left the group (marked with an X). A note reads "No group members exist in the group, and no Report messages are responded with," and another note reads "Before a multicast routing entry expires, the multicast router still sends multicast traffic according to the entry." A legend distinguishes multicast traffic, General Query message, Report message, and IGMP-capable interface.

#### IGMPv2 Message Format

- The following two types of messages are added to IGMPv2 to improve the group leaving mechanism:
  - Leave message: sent by a group member to notify the querier on the local network segment that it has left a group. The destination address of Leave messages is 224.0.0.2.
  - Group-Specific Query message: sent by a querier to a specified group on the local shared network to check whether the group has members. The destination address of Group-Specific Query messages is the address of the queried multicast group.
- A new field, Max Response Time, is added to IGMPv2 General Query messages. This field can be configured to control members' response speed to Query messages.
- The IGMPv2 message format is as follows:

Diagram description: A bit-field diagram, 0–31 bits wide, two rows. Row 1: Type (bits 0–7), Max Response Time (bits 8–15), Checksum (bits 16–31). Row 2: Group Address (full 32 bits).

- Fields in an IGMPv2 message:
  - Type
    - Message type. The four message type options are:
    - 0x11: Query message. IGMPv2 Query messages include General Query and Group-Specific Query messages.
    - 0x12: IGMPv1 Report message.
    - 0x16: IGMPv2 Report message.
    - 0x17: Leave message.
  - Max Response Time: maximum time for a member to respond to a Query message with a Report message.
    - For a General Query message, the default maximum response time is 10 seconds.
    - For a Group-Specific Query message, the default maximum response time is 1 second.
  - Group Address:
    - In a General Query message, the group address is set to 0s.
    - In a Group-Specific Query message, the group address is the address of the queried group.
    - In a Report or Leave message, the group address is the address of the group that a member has joined or left.

#### IGMPv2 Querier Election Mechanism

- The IGMPv2 group joining mechanism is the same as the IGMPv1 group joining mechanism, and is not mentioned here.
- The querier election mechanism in IGMPv2 varies greatly from that in IGMPv1. IGMPv2 has an independent querier election mechanism. When multiple multicast routers exist on a shared network segment, the router with the lowest IP address is elected as the querier.

Diagram description: Left diagram: RT1 and RT2 both consider themselves a querier initially (Step ①) and exchange General Query messages with each other (Step ②, "Exchange IGMP General Query messages"), both reaching a switch connected to a multicast group member. A legend distinguishes General Query message (RT1), General Query message (RT2), and IGMP-capable interface. Right diagram, labeled "Querier election": the outcome shows the router with the lowest interface IP address elected as the IGMP querier (sending General Query), while the router with the higher interface IP address becomes the non-querier, reaching a switch and the multicast group member.

- Each non-querier starts a timer (Other Querier Present Timer). If a non-querier receives a Query message from the querier before the timer expires, it resets the timer; otherwise, it triggers a new round of querier election.

#### IGMPv2 Group Leaving mechanism

- IGMPv2 uses Leave messages and Group-Specific Query messages to accelerate the discovery of IGMPv2 group member leaving.

Diagram description: Left diagram: a multicast network reaches an IGMP querier connected via a switch to member 1 (joins multicast group G1) and member 2 (leaves multicast group G1). Numbered steps: ① When a member of G1 leaves the multicast group, G1 sends a Leave message to notify the querier. ② After receiving the Leave message, the querier sends a Group-Specific Query message to check whether G1 has other members. A legend distinguishes Group-Specific Query message, Leave message, and IGMP-capable interface. Right diagram: shows the outcome — ③ there are still other group members on the network segment, they reply with Report messages; ① even if there is only one group member, the multicast router still retains the IGMP routing entry (IGMP Routing Table: Multicast Information *, G1 → Outbound Interface IF1). A legend distinguishes Report message and IGMP-capable interface.

- A member sends a Leave message for G1 to all multicast routers on the local network segment. The destination address of the Leave message is 224.0.0.2.
  - When the querier receives the Leave message, it sends Group-Specific Query messages for G1 to check whether G1 has other members on the network segment. The Group-Specific Query interval and Count are configurable. By default, the querier sends Group-Specific Query messages twice, at an interval of 1s. In addition, the querier starts the group membership timer (Timer-Membership). The value of the timer is the Group-Specific Query interval multiplied by Count.
  - If G1 still has other members on the network segment, when receiving a Group-Specific Query message from the querier, they immediately respond with a Report message for G1. The querier then keeps maintaining the membership of G1 after receiving the Report message.
  - If G1 has no members on the network segment, the querier will not receive any Report message for G1. When the Timer-Membership expires, the querier deletes the (*, G1) entry. Thereafter, if the querier receives multicast data of G1, it does not forward the data downstream.

#### Demand for the SSM Model

*(IGMPv1 → IGMPv2 → IGMPv3)*

- To ensure security, multicast group members can choose to receive only the multicast data from a specific multicast source. In this case, they need to inform the multicast network of the multicast source from which they want to receive multicast data.
- IGMPv1 and IGMPv2 messages cannot carry multicast source information. As a result, IGMPv1 and IGMPv2 cannot meet the demand for source-specific multicast (SSM), unless SSM mapping is used.
- IGMPv3 was developed to support the SSM model. IGMPv3 messages can carry multicast source information so that hosts can receive only data from a specific source.

Diagram description: Multicast source 1 and multicast source 2 both connect into a "Multicast network (SSM)" containing a router; the path from source 2 is blocked (marked with an X), so only source 1's traffic passes through to a second router, which connects to a multicast group member. A callout notes the member "Receives only the multicast data from the specific source." A "Report" arrow is shown going from the member up to the network with the note "Notifies the multicast network that it wants to receive only multicast data from multicast source 1."

- In the SSM model, multicast addresses range from 232.0.0.0 to 232.255.255.255.
- For details about SSM mapping, see the chapter of "IGMP Features."

#### IGMPv3

- Most mechanisms of IGMPv3 are similar to those of IGMPv2.
  - Their querier election mechanisms are the same. The multicast router with the lowest IP address is elected as the querier.
  - General Query messages are used to query group memberships.
  - Group-Specific Query messages are used to query group memberships of a specific multicast group.
- IGMPv3 needs to report multicast source information. Compared with IGMPv2, IGMPv3 has the following changes:
  - In addition to General Query and Group-Specific Query messages, IGMPv3 has a new Query message type: Group-and-Source-Specific Query.
  - Each IGMPv3 Report message contains the group that a host wants to join and the multicast sources from which the host wants to receive data.
  - Different members in the same multicast group may want to receive multicast data from different sources. Therefore, IGMPv3 does not require the Report message suppression mechanism.
  - Unlike IGMPv2, IGMPv3 does not define a Leave message. Group members send Report messages of a specified type to notify multicast routers that they have left a group.

#### IGMPv3 Query Message Format

- There are three types of IGMPv3 Query messages:
  - General Query message. This type of message has the same function as that in IGMPv1 or IGMPv2.
  - Group-Specific Query message. This type of message has the same function as that in IGMPv2.
  - Group-and-Source-Specific Query message. This type of message is used to query whether a group member wants to receive data from specific sources. Each such a message carries one or more multicast source addresses.
- The IGMPv3 Query message format is as follows:

Diagram description: A bit-field diagram, 0–31 bits wide, several rows. Row 1: Type (bits 0–7), Max Resp Code (bits 8–15), Checksum (bits 16–31). Row 2: Group Address (full 32 bits). Row 3: Resv, S, QRV (small sub-fields), QQIC, Number of Sources (N). Row 4 onward: Source Address [1], Source Address [2], ..., Source Address [N].

- Key fields in an IGMPv3 Query message:
  - Type: message type. In IGMPv3 Query messages, this field is set to 0x11.
  - Max Response Time: maximum response time. After receiving a General Query message, hosts must respond with a Report message within the maximum response time.
  - Group Address: address of a multicast group. In a General Query message, this field is set to 0. In a Group-Specific Query or Group-and-Source-Specific Query message, this field is set to the IP address of the queried group.
  - Number of Sources: number of multicast sources contained in the message. In a General Query or Group-Specific Query message, this field is set to 0. In a Group-and-Source-Specific Query message, this field is not 0. This number is limited by the maximum transmission unit (MTU) of the network over which the Query message is transmitted.
  - Source Address: address of the multicast source. The value is subject to the Number of Sources field.

#### IGMPv3 Report Message Format

- IGMPv3 Report messages are used to notify the querier of group memberships and the multicast sources from which the members want to receive multicast data. Multicast source information can be notified in either of the following modes:
  - INCLUDE: The members want to receive multicast data from specified multicast sources.
  - EXCLUDE: The members want to have multicast data from specified multicast sources filtered out.
- The relationship between multicast group information and multicast source information in the Report message is recorded in the Group Record field and sent to the IGMP querier. The destination address of each IGMPv3 Report message is 224.0.0.22. The format of the message is as follows:

Diagram description: Two connected bit-field diagrams. Left (overall message): Type (bits 0–7), Reserved (bits 8–15), Checksum (bits 16–31); then Reserved (bits 0–15), Number of Group Records (M) (bits 16–31); then Group Record [1], Group Record [2], ..., Group Record [N]. Right (expanded Group Record structure): Record Type (bits 0–7), Aux Data Len (bits 8–15), Number of Sources (N) (bits 16–31); then Multicast Address (full 32 bits); then Source Address [1], Source Address [2], ...; then Auxiliary Data.

- An IGMPv3 Report message can carry multiple groups, whereas an IGMPv1 or IGMPv2 Report message can carry only one group. Therefore, the number of IGMPv3 messages needed is greatly reduced.
- The key fields in an IGMPv3 Report message are described as follows:
  - Type: message type. In IGMPv3 Report messages, this field is set to 0x22.
  - Number of Group Records: number of group records contained in a message.
  - Group Record: group record.
- Key fields in Group Record are described as follows:
  - Record Type: type of a group record. There are three group record types.
    - Current-State Record. It is used to respond to Query messages and advertise its current state. There are two types of states. One of the states is MODE_IS_INCLUDE, indicating that the member wants to receive only the multicast data sent from the sources in the source address list to the group. If the specified source address list is empty, the message is invalid. The other state is MODE_IS_EXCLUDE, indicating that the member rejects the multicast data sent from the sources in the source address list to the group.

> ⚠️ **Note: Source PDF gap.** Page 801 is missing from this export (the sequence jumps from page 800, ending mid-description of IGMPv3 Report Message Format group record types, to page 802, which begins "IGMPv3 Group Joining Mechanism" on slide 25). This means **slide 24 of the original deck is missing entirely**. Based on the standard Huawei IGMPv3 curriculum, slide 24 almost certainly continues the "Record Type" list above with the remaining group record types — typically:
>   - **Filter-Mode-Change Record** types: `CHANGE_TO_INCLUDE_MODE` and `CHANGE_TO_EXCLUDE_MODE`, used when a member changes its filter mode for a group.
>   - **Source-List-Change Record** types: `ALLOW_NEW_SOURCES` and `BLOCK_OLD_SOURCES`, used when a member adds or removes specific sources from its interest list without changing its overall filter mode.
>
> This reconstruction is provided for context only — it is **not verbatim source content** and should not be treated as authoritative for quiz purposes. Please re-export/re-upload the PDF with page 801 included so the exact wording can be captured.

#### IGMPv3 Group Joining Mechanism

- The group joining mechanism of IGMPv3 is similar to that of IGMPv2 except the following differences:
  - IGMPv3 Report messages carry multicast source information.
  - IGMPv3 does not have a Report message suppression mechanism.
- The process of group joining in IGMPv3 is as follows:

Diagram description: Multicast source S1 and multicast source S2 both connect into a multicast network reaching an IGMP querier. ① The IGMP querier sends General Query messages. ② Each multicast group member responds to the Query message with a Report message, which contains multicast group and multicast source information; there is no Report message suppression mechanism. Three multicast group members are shown: member 1 joins G1 and wants to receive multicast data from S1; member 2 joins G1 and wants to receive multicast data from S1; member 3 joins G1 and wants to receive multicast data from S2. ③ Each multicast group member sends a Report message, which contains multicast group and multicast source information, resulting in an IGMP Routing Table with entries: IGMP Entry S1, G1 → Outbound Interface IF1; S2, G1 → Outbound Interface IF1. A legend distinguishes Report message (member 1), Report message (member 2), Report message (member 3), and IGMP-capable interface.

#### IGMPv3 Group Leaving Mechanism

- IGMPv3 does not have Leave messages, and group leaving is notified through Report messages.
- After receiving a Report message with updated source-group mapping, the IGMP querier sends Group-and-Source-Specific Query messages to check whether there are still other members in the group.

Diagram description: Left diagram: multicast source S1 connects into a multicast network reaching an IGMP querier, then a switch reaching member 1 (leaves G1, does not want to receive data from S1) and member 2 (joins G1, wants to receive multicast data from S1). Numbered steps: ① The group member sends a Report message with updated source-group mapping. ② After receiving the Report message, the IGMP querier considers that the group member needs to leave the group. A legend distinguishes Report message and IGMP-capable interface. Right diagram: ③ The IGMP querier sends Group-and-Source-Specific Query messages to check whether there are still other members in the group; ④ after receiving the Report message, the querier retains the IGMP routing entry (IGMP Routing Table: IGMP Entry S1, G1 → Outbound Interface IF1). Member 1 has left G1 and does not want to receive data from S1; member 2 responds with a Report message. A legend distinguishes Group-and-Source-Specific Query message and Report message.

- Various Report messages can be used to update source-group mapping. For example:
  - A member used to receive multicast data from S1. It can send a (G1, EXCLUDE, S1) or (G1, CHANGE_TO_EXCLUDE_MODE, S1) message to update source-group mapping.

#### Differences Between IGMP Versions

| Mechanism | IGMPv1 | IGMPv2 | IGMPv3 |
|---|---|---|---|
| Querier election | Depends on another protocol. | Uses its own mechanism. | Uses its own mechanism. |
| Group leaving | Leave silently. | Leave proactively. | Leave proactively. |
| Group-Specific Query | Not supported | Supported | Supported |
| Source-and-Group-Specific Query | Not supported | Not supported | Supported |
| Version mapping | | IGMPv1 | IGMPv1, IGMPv2 |

## 2. IGMP Feature Introduction

### IGMP Snooping Introduction

#### Problem Accompanying Multicast Forwarding on the Ethernet Network

- The multicast data packets sent from the last-hop router to multicast group members usually pass through a switch. The destination MAC addresses of multicast data packets are multicast MAC addresses. By default, the switch floods such data frames. As a result, multicast traffic may be received across groups. IGMP snooping controls the flooding scope of multicast traffic on an Ethernet network, which prevents inter-group multicast traffic receiving.

Diagram description: Two side-by-side topologies. Left, "before IGMP snooping": multicast source S1 sends a "Multicast packet of G1" and a "Multicast packet of G2" into a multicast network, through a multicast router, into a Layer 2 switch. Both multicast group member 1 (joined G1) and member 2 (joined G2) receive traffic of both G1 and G2 (labeled "Receives multicast traffic of G1 and G2"). Right, after "Enable IGMP snooping": the same topology, but the Layer 2 switch has IGMP snooping enabled, so member 1 receives only multicast traffic of G1, and member 2 receives only multicast traffic of G2 (each labeled accordingly). A legend distinguishes multicast traffic of G1 (solid) and multicast traffic of G2 (dashed).

- After receiving multicast data packets from the router, the switch forwards the packets to the group members. Destination addresses of multicast packets are multicast group addresses and cannot be learned by a Layer 2 switch. Therefore, when a Layer 2 switch receives multicast packets from a router, it broadcasts the packets in the broadcast domain. All hosts in the broadcast domain receive the multicast packets, regardless of whether they are group members. This wastes network bandwidth and poses security risks.
- IGMP snooping solves this preceding problem. With IGMP snooping configured, the Layer 2 multicast switch listens to and analyzes IGMP messages exchanged between multicast users and the upstream router, and creates Layer 2 multicast forwarding entries accordingly. Multicast data packets are then forwarded based on the Layer 2 multicast forwarding entries. This prevents multicast data packets from being broadcast on the Layer 2 network.

#### IGMP Snooping Introduction

- IGMP snooping implements forwarding and control of multicast data packets at the data link layer.
- IGMP snooping runs on a Layer 2 multicast device and analyzes received IGMP messages exchanged between a Layer 3 device and hosts to create and maintain a Layer 2 multicast forwarding table. Based on this table, the Layer 2 device forwards multicast packets at the data link layer.

Diagram description: Two side-by-side topologies. Left: multicast source S1 connects into a multicast network reaching an IGMP querier, down to a switch with IGMP snooping enabled. ① Group joining mechanism: General Query sent, IGMP snooping is enabled on the switch. ② The IGMP snooping-enabled device reads IGMP messages and generates a Layer 2 multicast forwarding table (shown: Multicast Group / Outbound Interface — Router Port → IF3, *, G1 → IF1, *, G2 → IF2). Members 1 and 2 send Report messages joining G1 and G2 respectively. Right: shows the result — the switch forwards multicast data packets based on the Layer 2 multicast forwarding table; multicast group member 1 receives only the multicast traffic of G1, and member 2 receives only the multicast traffic of G2. A legend distinguishes multicast flow of G1 and multicast flow of G2.

#### IGMP Snooping Port and Forwarding Table Introduction

- Layer 2 multicast forwarding entries contain the following types of ports:
  - Router port: a port on a Layer 2 multicast device, used to receive multicast packets from a Layer 3 multicast device such as a DR or IGMP querier.
  - Member port: a port on a Layer 2 multicast device, used to send multicast data packets to group members.

Diagram description: A "Layer 2 multicast forwarding table" example is shown as CLI-style output:

```
Layer 2 multicast forwarding table
VLAN ID : 10, Forwarding Mode : IP
-----------------------------------------------------------------
  (Source, Group)            Interface                Out-Vlan
-----------------------------------------------------------------
                              Router-port  IF3 (router port)     10
                              (*, 239.0.0.1)  IF1 (member port)  10
                              (*, 239.0.0.2)  IF2 (member port)  10
-----------------------------------------------------------------
Total Group(s): 2
```

To the right, a topology shows an IGMP querier connected to a multicast network, then to a Layer 2 multicast switch via IF3 (the router port), with IF1 and IF2 as member ports connecting to multicast group member 1 (joins multicast group 239.0.0.1) and multicast group member 2 (joins multicast group 239.0.0.2) respectively. A legend distinguishes router port (open circle) and member port (filled yellow dot).

- Router port:
  - A router port generated by a protocol is called a dynamic router port. A port becomes a dynamic router port when it receives an IGMP General Query message or PIM Hello message with any source address except 0.0.0.0. The PIM Hello messages are sent from the PIM port on a Layer 3 multicast device to discover and maintain neighbor relationships.
  - A manually configured router port is called a static router port.
- Member port:
  - A member port generated by a protocol is called a dynamic member port. A Layer 2 multicast device sets a port as a dynamic member port when the port receives an IGMP Report message.
  - A manually configured member port is called a static member port.

#### Implementation of IGMP Snooping — Forwarding Entry Generation

- An IGMP snooping-enabled device listens for IGMP messages to generate a Layer 2 multicast forwarding table and determines the port type. The detailed process is as follows:

Diagram description: A multicast network reaches an IGMP querier, connecting via a switch with IGMP snooping enabled down to member 1 (joins multicast group 239.0.0.1) and member 2 (joins multicast group 239.0.0.1). Numbered steps: ① Group joining mechanism: General Query sent, IGMP snooping enabled. ② The switch receives a General Query message and functions as a router port; it receives a Report message and functions as a member port; a note states "Report messages of members in the same group no longer suppress each other." The switch reads the Report message to build the "Layer 2 multicast forwarding table": VLAN ID: 10, Forwarding Mode: IP — Router-port → IF3 (router port), (*, 239.0.0.1) → IF1 (member port), IF2 (member port), Total Group(s): 1. A legend distinguishes router port and member port.

- When a router port takes effect, an aging timer (180s by default) is started. When the router port receives a new General Query message, it updates the timer.
- When a member port takes effect, an aging timer (Aging time = Robustness variable x General query interval + Maximum response time for General Query messages) is started. When the member port receives a new Report message, it updates the timer.
- IGMP snooping no longer uses the Report message suppression mechanism.
  - IGMP snooping needs to listen for IGMP messages to determine the port role and guide packet forwarding. Therefore, all group members need to send Report messages.
  - After receiving a Report message, the IGMP snooping-enabled device forwards the Report message only through the router port. This prevents other group members in this group from receiving the Report message, which will not trigger Report message suppression.

#### Implementation of IGMP Snooping — Forwarding Entry Maintenance

- An IGMP snooping-enabled device listens for IGMP Leave messages and IGMP Report messages to determine whether a specific interface needs to send multicast data. The detailed process is as follows:

Diagram description: A multicast network reaches an IGMP querier, connecting via a switch down to multicast group member 1 (leaves multicast group 239.0.0.1) and member 2 (joins multicast group 239.0.0.1). Numbered steps: ① Member 1 sends a Leave message. ② The switch forwards the Leave message through the router port. ③ The IGMP querier responds with a Group-Specific Query message. ④ The switch forwards the Query messages to all member ports and updates the forwarding table. ⑤ Member 2 responds with a Report message. The Layer 2 multicast forwarding table (VLAN ID: 10, Forwarding Mode: IP) shows Router-port → IF3 (router port); (*, 239.0.0.1) → IF1 (member port, struck through) and IF2 (member port); Total Group(s): 1. Notes explain: IF1 does not receive any Report message after the aging timer expires and is deleted; after IF2 receives a Report message, it updates the timer. A legend distinguishes Group-Specific Query, Leave message, Report message, router port, and member port.

- After receiving an IGMP Leave message, the switch uses the following formula to calculate the aging timer of member ports: Aging timer = Robustness variable (2 by default) x Group-Specific Query interval (1s by default).

### IGMP SSM Mapping Introduction

#### IGMP SSM Mapping Introduction

- If terminals on the live network do not support IGMPv3, multicast in SSM mode cannot be deployed because IGMPv1 or IGMPv2 messages cannot carry multicast source information.
- IGMP SSM mapping allows IGMPv1 and IGMPv2 group members to access the SSM network if a multicast source is manually bound to a multicast group.

Diagram description: Multicast source S1 and multicast source S2 both connect into a "Multicast network (SSM)" reaching an IGMP querier. A question-mark callout notes "Does not know the source (S1 or S2) from which each group member wants to receive multicast data." Two paths lead down through a switch to multicast group member 1 (running IGMPv1, joins multicast group G1) and multicast group member 2 (running IGMPv2, joins multicast group G1), each sending a Report message; callouts note that "IGMPv1 or IGMPv2 messages do not carry multicast sources" on both sides. A legend distinguishes Report message (member 1) and Report message (member 2).

- The SSM group addresses range from 232.0.0.0 to 232.255.255.255, regardless of whether IGMPv1, IGMPv2, or IGMPv3 is used.

#### Implementation of IGMP SSM Mapping

- Configure static SSM mapping entries on the IGMP querier to map group information in IGMPv1 or IGMPv2 Report messages to source-specific group information.
- The implementation of IGMP SSM mapping is as follows:

Diagram description: Multicast source 4.0.0.4 connects into a "Multicast network (SSM)" reaching an IGMP querier where IGMP SSM mapping is configured. A box labeled "IGMP SSM-Mapping conversion table" shows:

```
Total 1 entry
1 entry matched
00001. (4.0.0.4, 232.0.0.10/32)   //Static SSM mapping entry
```

An "SSM Mapping" box shows SSM multicast group 232.0.0.10 mapped to multicast source 4.0.0.4. Numbered steps: ① Configure a static mapping entry between a multicast group and a multicast source. ② Group member 1 (running IGMPv1) and group member 2 (running IGMPv2), both joining multicast group 232.0.0.10, send Report messages. ③ The querier creates an IGMP routing entry after receiving the Report message. ④ It generates an IGMP entry based on the SSM mapping entry — shown in the "IGMP Routing Table": IGMP Entry 232.0.0.10 → Outbound Interface IF1. A legend distinguishes Report message (member 1) and Report message (member 2).

- With SSM mapping entries configured, an IGMP querier checks the group address G in each IGMPv1 or IGMPv2 Report message received, and processes the message based on the check result:
  - If G is in the any-source multicast (ASM) group address range, the router provides the ASM service for the corresponding group member.
  - If G is in the SSM group address range (232.0.0.0 to 232.255.255.255 by default):
    - When the IGMP querier has no SSM mapping entry matching G, it does not provide the SSM service and drops the Report message.
    - If the IGMP querier has an SSM mapping entry matching G, it converts (*, G) information in the Report message into (G, INCLUDE, (S1, S2...)) information and provides the SSM service for the corresponding group member.
- IGMP SSM mapping does not apply to IGMPv3 Report messages. To enable hosts running any IGMP version on a network segment to obtain the SSM service, IGMPv3 must run on interfaces of multicast routers on the network segment.

### IGMP Proxy Introduction

#### IGMP Proxy Introduction

- On a live network, an IGMP querier may need to manage a large number of group members. When a large number of hosts frequently join or leave groups, a large number of IGMP Report/Leave messages are sent to the querier, which burdens the querier.
- IGMP proxy reduces the number of IGMP Report/Leave messages received by the IGMP querier, reducing the burden on the IGMP querier.
- IGMP proxy is usually deployed on a Layer 3 device between an IGMP querier and receiver hosts.

Diagram description: Left, "before IGMP proxy": a multicast network reaches an IGMP querier, then a Layer 3 switch, then down to multicast group member 1 and member 2, each sending Report and Leave messages directly up through the switch to the querier; a callout notes "Excessive IGMP Report/Leave messages." Right, after "Configure IGMP proxy": the same topology but IGMP proxy is enabled on the Layer 3 switch; a callout notes "The number of IGMP Report/Leave messages decreases," since the switch now aggregates messages from member 1 and member 2 before forwarding a reduced number upstream to the querier. A legend distinguishes Report message and Leave message.

#### Basic Concepts of IGMP Proxy

- To relieve the burden on the IGMP querier, the IGMP proxy-capable device aggregates Report/Leave messages before sending them to the IGMP querier.
- An IGMP proxy-capable device can also act as an IGMP querier to send Query messages to receiver hosts, maintain group memberships, and forward multicast data based on group memberships.
- To implement the preceding functions, IGMP proxy defines two types of interfaces:
  - Host interface: IGMP proxy-enabled interface on an IGMP proxy-capable device. This interface generally points to an IGMP querier.
  - Router interface: an interface configured with IGMP on an IGMP proxy-capable device. This interface generally points to group members.

Diagram description: A multicast network connects to an IGMP querier, which connects to a Layer 3 switch. The switch's upstream-facing interface (labeled "Host interface," with IGMP proxy enabled on it) points toward the IGMP querier; its downstream-facing interface (labeled "Router interface," with IGMP enabled on it) connects to multicast group member 1 and multicast group member 2. A legend distinguishes host interface (open circle) and router interface (filled yellow dot).

#### Implementation of IGMP Proxy – Group Joining

- IGMP proxy reduces the number of Report messages as follows:
  - A router interface functions as an IGMP interface and is presented as an IGMP querier. The router interface sends Query messages, processes Report messages, generates IGMP entries, and sends Report messages to the upstream IGMP querier through a host interface.
  - When new hosts join the same multicast group, the IGMP proxy-capable device does not send Report messages to the IGMP querier. This reduces the number of Report messages sent to the IGMP querier.

Diagram description: Left, before a new member joins: a multicast network reaches an IGMP querier, then an IGMP proxy-capable device (host interface upstream, router interface downstream). Numbered steps: ① Group joining mechanism: General Query sent, Report message suppression mechanism active (shown crossed out) among existing members. ② The IGMP proxy-capable device sends Report messages to the upstream IGMP querier and generates the IGMP group entry and IGMP proxy routing entry. Multicast group member 1 joins group G1 and multicast group member 2 joins group G1, each responding via Report messages. Right, after "A new member joins the same group": multicast group member 3 (new member) also joins group G1. Numbered steps: ① Group joining mechanism at the router interface. ② The group information in the Report message can be found in IGMP entries. ③ The IGMP proxy-capable device does not forward Report messages of new members in the same multicast group upstream (shown crossed out toward the querier). A legend distinguishes host interface and router interface.

- When the IGMP proxy-capable device receives a Report message for a group, it searches the multicast forwarding table for the group.
  - If the group is not found in the multicast forwarding table, the IGMP proxy-capable device sends a Report message for the group to the access device and adds the group to the multicast forwarding table.
  - If the group is found in the multicast forwarding table, the IGMP proxy device does not send a Report message to the access device.
- IGMPv1, IGMPv2, and IGMPv3 group joining mechanisms are not described here.

#### Implementation of IGMP Proxy – Group Leaving

- IGMP proxy reduces the number of Leave messages as follows:
  - When a group member leaves a multicast group, the IGMP proxy-capable device uses the IGMP group leaving mechanism to determine whether there are still other members of the multicast group. If there is no member of the multicast group, the device sends a Leave message to the upstream IGMP querier.

Diagram description: Left, before all members leave: a multicast network reaches an IGMP querier, then an IGMP proxy-capable device (host interface, router interface). Numbered steps: ② There are still other multicast group members, and no Leave message is sent upstream (shown crossed out toward the querier). ① Group leaving mechanism at the router interface: a Group-Specific Query is sent; member 1 responds with a Leave message (leaving group G1) while member 2 (joining group G1) responds with a Report message. Right, after "All members leave the group": ③ The IGMP querier deletes the corresponding entry. ② The IGMP proxy-capable device sends a Leave message only after all members leave the group. ① Group leaving mechanism at the router interface: a Group-Specific Query is sent; member 1 has left group G1, and member 2 leaves group G1, sending a Leave message. A legend distinguishes host interface, router port, Group-Specific Query, Leave message, and Report message.

- When the IGMP proxy-capable device receives a Leave message for G1, it sends a Group-Specific Query message through the interface where the Leave message was received, to check whether G1 has other members attached to the interface.
  - If there are no other members of G1 attached to the interface, the IGMP proxy-capable device deletes the interface from the forwarding entry of G1. The IGMP proxy-capable device then checks whether G1 has members on other interfaces.
    - If G1 has no members on other interfaces, the IGMP proxy-capable device sends a Leave message for G1 to the access device.
    - If G1 has members on other interfaces, the IGMP proxy-capable device does not send a Leave message for G1 to the access device.
  - If the group has other members attached to the interface, the IGMP proxy-capable device continues forwarding multicast data to the interface.
- IGMPv1, IGMPv2, and IGMPv3 group leaving mechanisms are not described here.

## 3. IGMP Configurations

### Basic Configurations of IGMP (1)

1. Enable IGMP.

```
[Huawei - GigabitEthernet1/0/0] igmp enable
```

2. Configure an IGMP version.

```
[Huawei - GigabitEthernet1/0/0] igmp version number
```

3. Enable IGMP snooping globally.

```
[Huawei] igmp-snooping enable
```

4. Enable IGMP proxy in a VLAN.

```
[Huawei-vlan10] igmp-snooping proxy
```

5. Enable IGMP SSM mapping on an interface.

```
[Huawei - GigabitEthernet1/0/0] igmp ssm-mapping enable
```

### Basic Configurations of IGMP (2)

6. Configure a static SSM mapping entry in the IGMP view.

```
[Huawei-igmp] ssm-mapping group-address group-mask source-address
```

7. Check the IGMP configurations and running information on interfaces.

```
<Huawei>display igmp interface
```

8. Check information about the members of a multicast group.

```
<Huawei>display igmp group
```

9. Check the Layer 2 multicast forwarding table.

```
<Huawei>display l2-multicast forwarding-table vlan vlan-id
```

10. Check static IGMP SSM mapping information.

```
<Huawei>display igmp ssm-mapping
```

### IGMP Basis Experiment

Diagram description: Router RTA has interface GE0/0/1 with IP address 192.168.1.0/24, connected via IGMPv2 to Client A and Client B on the shared network segment.

Configure IGMP on the router to implement IP multicast member management. Enable IGMP on GE 0/0/1 of RTA so that RTA functions as a querier to send and receive IGMP messages.

**Configurations on RTA**

```
[RTA]multicast routing-enable
[RTA]interface g0/0/1
[RTA-GigabitEthernet0/0/1]ip address 192.168.1.1 24
[RTA-GigabitEthernet0/0/1]igmp enable
[RTA-GigabitEthernet0/0/1]igmp version 2
```

### IGMP Configuration Verification

- On RTA, check the IGMP configurations and running information on the interface.

```
<RTA>display igmp interface
Interface information of VPN-Instance: public net
 GigabitEthernet0/0/1(192.168.1.1):
   IGMP is enabled
   Current IGMP version is 2
   IGMP state: up
   IGMP group policy: none
   IGMP limit: -
   Value of query interval for IGMP (negotiated): -
   Value of query interval for IGMP (configured): 60 s
   Value of other querier timeout for IGMP: 0 s
   Value of maximum query response time for IGMP: 10 s
   Querier for IGMP: 192.168.1.1 (this router)
```

- The IGMP version is IGMPv2. (Current IGMP version is 2)
- Configured interval for sending IGMP Query messages. (Value of query interval for IGMP (configured): 60 s)
- Maximum response time in a Query message. (Value of maximum query response time for IGMP: 10 s)

## Quiz

1. (Essay) In IGMPv1, when the last member leaves a group, how long will the multicast router wait before deleting the multicast forwarding entry of the group?
2. (Essay) Is the destination IP address of IGMPv2 Group-Specific Query message 224.0.0.1?
3. (Single) Which IGMP versions are available? ( )
   A. IGMPv1, IGMPv2
   B. IGMPv3
   C. IGMPv2, IGMPv3
   D. IGMPv1, IGMPv2, IGMPv3

**Answers:**

1. 60 x 2 + 10 = 130s
2. No. The destination IP address of a Group-Specific Query message is the IP address of the group to be queried.
3. D

## Summary

- IGMP enables a multicast network to know the locations of multicast group members and the multicast groups that the members join. In addition, IGMP maintains multicast group memberships.
- There are three IGMP versions:
  - IGMPv1: has a basic group joining mechanism, but the group member leaving mechanism is outdated. In addition, IGMPv1 does not have an independent IGMP querier election mechanism.
  - IGMPv2: improves the group leaving mechanism based on IGMPv1 and provides an independent IGMP querier election mechanism.
  - IGMPv3: is an enhancement of IGMPv2 and supports SSM. IGMPv3 can notify a multicast network of the multicast sources from which multicast data needs to be received.
- IGMP provides the following features to ensure efficient running of IGMP on a network:
  - IGMP snooping: prevents multicast data from being flooded across multicast groups on an Ethernet network.
  - IGMP SSM mapping: solves the problem that IGMPv1 and IGMPv2 group members cannot access the SSM multicast network.
  - IGMP proxy: solves the problem that the IGMP querier is overloaded because a large number of multicast group members frequently join and leave a multicast group.

