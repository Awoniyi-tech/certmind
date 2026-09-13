> **PAGE-GAP NOTICE:** This PDF export is missing one page. In the first course ("Huawei Firewall Technology"), the deck jumps from slide 17 (PDF page 1027, "Default Security Zones") directly to slide 19 (PDF page 1029, "Interzone Example"). **Slide 18 (PDF page 1028) is missing** and its content is not included below. Please re-upload a complete export of this deck if you need that slide. The second course in this file ("Security Features of Network Devices," slides 2–32, PDF pages 1061–1091) has no gaps.

---

# Huawei Firewall Technology

## Foreword

- The word "firewall" is first used in the construction field. The function of a firewall is to isolate the fire, preventing the fire from spreading from one area to another. In the communications field, a firewall is usually deployed to logically isolate networks for some purposes. The firewall defends against various attacks on the network to ensure transmission of communication packets.
- This course describes what is a firewall in the communications field, why a firewall is required, and the working mechanism and configurations of the firewall.

## Objectives

- On completion of this source, you will be able to:
  - Describe the definition, type, and development history of firewalls.
  - Distinguish firewalls from routers and switches.
  - Describe basic firewall concepts, such as the security zone, security policy, session table, and server map.
  - Perform basic firewall configurations.

## Contents

1. Introduction to Firewalls
2. Basic Firewall Concepts
3. Basic Firewall Configurations

## 1. Introduction to Firewalls

### Why Do We Need Firewalls?

**Diagram description:** External network (Untrust zone) contains two "External Network" clouds, each connected to its own firewall — Firewall 1 and Firewall 2. Firewall 1 and Firewall 2 are interconnected with each other via a dotted line, and each connects downward to Core-Switch 1 and Core-Switch 2 respectively; Core-Switch 1 and Core-Switch 2 are also interconnected. Both core switches connect down to three servers (Server, Server, Server) located in the Internal network (Trust zone).

- Security is required everywhere. Routers and switches construct an interconnected network, which brings convenience and security risks.
- For example, enterprises have the following security requirements at a network border:
  - External network security isolation
  - Internal network security control
  - Content filtering
  - Intrusion prevention
  - Antivirus

### What Is a Firewall?

- In the communications field, a firewall is a security device. It is used to protect a network area against attacks and intrusions from another network area. It is usually deployed at a network border, such as the enterprise Internet egress, enterprise internal service border, and data center border.
- Firewalls are classified into modular firewalls, fixed firewalls, and software firewalls. Firewalls can be flexibly deployed locally and on the cloud.

**Diagram description:** Three firewall form factors are shown side by side: a "Modular firewall" (a large rack-mounted chassis), a "Fixed firewall" (a compact rectangular appliance), and a "Software firewall" (represented by two small server icons feeding into a cloud labeled "Public cloud, private cloud").

- Firewalls have other models, such as desktop firewalls (a type of fixed firewalls). Desktop firewalls apply to small enterprises, industry branches, and chain business organizations. Huawei fixed firewalls support both the traditional and cloud management modes. In cloud management mode, the cloud manages secure access of branches in a unified manner, and supports plug-and-play devices, automatic service configuration, visualized O&M, and network big data analysis.
- This course focuses on modular and fixed physical firewalls, and does not describe desktop firewalls and software firewalls.

### Comparison Between Firewalls and Switches and Routers

**Diagram description:** A left-to-right flow: PCs/terminals connect via dashed lines to Switches, which are labeled "Switches constitute a LAN and perform Layer 2 or Layer 3 fast packet forwarding" and also connect to three Servers. The switches connect onward to a Firewall, labeled "Firewalls control packet forwarding and defend against attacks, viruses, and Trojan," which connects to Routers, labeled "Routers provide addressing and forwarding to ensure network interconnection." The routers connect out to the Internet cloud and additional routers/servers. Red solid arrows labeled "Abnormal traffic" are shown blocked (marked with an X) between the firewall and the routers, while blue dashed arrows labeled "Normal traffic" flow through unobstructed.

- For example, on a campus network, switches are used to connect terminals and summarize internal routes to build a LAN for internal communication.
- Routers are used for route distribution, addressing, and forwarding to construct an external connection network.
- Firewalls are used to implement traffic control and security protection and to distinguish and isolate different security zones.

### Comparison Between Forwarding Processes of a Firewall and a Router

**Diagram description:** Two parallel pipelines are shown. The top pipeline, "Forwarding process of a router," flows: Interface → LPU → SFU → LPU → Outbound interface, with "ACL rule/QoS policy/Traffic management" annotated above the first and second LPU stages. The bottom pipeline, "Forwarding process of a firewall," follows the same Interface → LPU → SFU → LPU → Outbound interface flow, but the SFU stage additionally connects (bidirectional arrows, up and down) to an "SPU" block annotated with "DDoS attack defense/session matching/status detection/authentication policy/security policy/NAT policy/content security/bandwidth policy."

- The forwarding process of a firewall is more complex than that of a router. A modular firewall is used as an example. In addition to interfaces, line processing units (LPUs), and switch fabric units (SFUs), a modular firewall has service processing units (SPUs) to implement security functions.

### Typical Application Scenarios of Firewalls

**Diagram description:** A 2×2 grid of four scenario panels.
- Top-left, "Enterprise Border Protection": a DMZ containing an FTP server connects through a switch; a Trust zone with a truck/branch icon connects through a firewall to an Untrust zone containing a traveling employee, the Internet, and a Branch.
- Top-right, "Intranet Control and Security Isolation": Marketing Dept, Production Dept, and Finance Dept clouds connect through a switch; an R&D area connects through a firewall (egress gateway) to the Internet.
- Bottom-left, "DC Border Protection": an internal area of a DC (multiple switches) connects through a firewall to an Untrust zone containing an individual customer, the Internet, and an enterprise customer (enterprise campus/branch).
- Bottom-right, "DC Security Association": a spine-leaf architecture with Spine switches at the top and Leaf switches below, connecting down to servers and firewalls.

- A Demilitarized Zone (DMZ) is originally a military term, referring to a partially controlled area between a military control area and a public area. A DMZ configured on a firewall is logically and physically separated from internal and external networks. In an enterprise, it is usually used to accommodate servers.
- Data center networks often use the spine-leaf architecture. Spine nodes forward traffic at a high speed, and leaf nodes connect to servers, firewalls, or other devices. Spine and leaf nodes are fully meshed at Layer 3.

### Firewall Development History

- Throughout the firewall development history, the firewall has gone through the process from low-level to high-level and from simple functions to complex functions. Development of network technologies and emergence of new requirements promote the development of firewalls.
- Firewalls develop from the packet filtering firewall, status detection firewall, UTM, and NGFW to AIFW, with the following characteristics:
  - More refined access control
  - More powerful protection capability
  - Higher performance

**Diagram description:** A horizontal timeline arrow runs left (1989) to right (Now), with labeled milestones: "Packet filtering firewall" at 1989 (PC era) — Basic access control; "Stateful inspection firewall" at 1994 (Network era) — Session mechanism introduced; "ASIC-based firewall" at 1998 (Internet era) — Performance improvement by a dedicated chip; "Unified Threat Management (UTM)" at 2004 and "Multi-core distributed architecture" at 2008 (both Web 2.0 era) — Multi-function and Higher performance respectively; "Next-generation firewall (NGFW)" at 2009– (Mobile Internet era) — Control based on applications, users, and contents; "AIFW" at Now (AI era).

### Packet Filtering Firewall

- A packet filtering firewall checks each packet based on the 5-tuple and forwards or discards packets based on the configured security policies.
- The packet filtering firewall uses access control lists (ACLs) to filter data packets.

**Diagram description:** A Trust zone contains an "Office area 192.168.10.0/24" and an "R&D area 192.168.20.0/24," each with a PC, both connecting to a firewall. A security policy callout box reads: "Source address: 192.168.10.0/24 / Destination address: any / Port number: any / Protocol: HTTP / Action: permit." The office area's traffic passes through (checkmark) to the Untrust zone/Internet, while the R&D area's traffic is blocked (X mark). A side note states: "In this example, firewall security policies are configured to allow only IP addresses in the office area to access the Internet," and lists "Problems of the packet filtering firewall:
- Per-packet detection has low performance.
- ACL rules cannot meet dynamic requirements.
- Application-layer data is not checked.
- The packet filtering firewall does not provide packet association analysis, so spoofing may easily occur."
Followed by: "Question: How to solve problems of the packet filtering firewall?"

- A packet filtering firewall filters packets based on information such as the source/destination IP address, source/destination port number, IP identifier, and packet transmission direction in the packets.
- The packet filtering firewall is simple in design, easy to implement, and cost-effective.
- The disadvantages of the packet filtering firewall are as follows:
  - With the increase of ACL complexity and length, filtering performance decreases exponentially.
  - Static ACL rules cannot meet dynamic security requirements.
  - The packet filtering firewall does not check the session status or analyze data, which makes it easy for attackers to escape. For example, an attacker sets the IP address of the host to an IP address permitted by a packet filtering firewall. In this way, packets from this host can easily pass through the packet filtering firewall.

### Stateful Inspection Firewall

- Stateful inspection firewalls are introduced based on packet filtering technology. It considers correlation between packets and detects the connection status but not a single packet.

**Diagram description:** A TCP three-way handshake sequence between hosts 10.0.0.1 and 20.0.0.1: SYN=1,Seq=2288,ACK=0 (checkmark) from 10.0.0.1 to 20.0.0.1; SYN=1,Seq=9955,ACK(Seq=2289) (checkmark) returning; then a "Suspected attack" packet SYN=1,Seq=2289,ACK=10002 (marked with an X) from 10.0.0.1; followed by a legitimate packet SYN=1,Seq=2289,ACK=9956 (checkmark). Session information shown: "tcp 10.0.0.1:52754-->20.0.0.1:4399". Below this, a Trust zone containing an Office area PC connects through a firewall to the Untrust zone/Internet.

Side note: "In this example, the stateful inspection firewall detects that a TCP connection is established between hosts at 10.0.0.1 and 20.0.0.1 and generates session information. The third handshake packet does not match any session entry and is discarded." Also: "The NGFW is also a stateful inspection firewall. The NGFW greatly improves content security and processing performance."

- The stateful inspection firewall detects the first data packet of a connection to determine the status of the connection. Subsequent data packets are forwarded or blocked based on the status of the connection.

### AIFW

- The AIFW is a next-generation firewall that integrates AI technology. It further improves the security protection capability and performance of the firewall by using AI algorithms or AI chips.
- Huawei AIFW has built-in core detection engine (CDE) — malicious file detection engine, deception sensor, APT inspection engine (AIE), and probe. It can interwork with the sandbox and Huawei Cybersecurity Intelligence System (CIS) — big data analytics platform for detection, building an intelligent defense system.

**Diagram description:** "Huawei AIFW" sits in the center, containing four built-in components: CDE, Built-in probe, Built-in deception sensor, and Built-in AIE. On the left it connects (via "File restoration/mirroring" and "Detection and association") to a "Sandbox: APT defense detection system." On the right it connects (via "Collection" and "Joint detection") to a "Big data-based security situation awareness system" containing the CIS.

- Huawei HiSecEngine USG6000E series is the first AIFW launched in the industry. There is no unified standard for AIFWs. For example, firewalls are trained using a large amount of data and algorithms so that they can proactively identify threats. The built-in AI chip of firewalls helps improve application identification and forwarding performance.
- Advanced Persistent Threats (APTs) persistently attack specific targets using advanced attack methods.
- The sandbox is a security device used to detect viruses. It builds a virtual environment for suspected viruses and detects viruses by observing their subsequent behaviors. The sandbox is an important device for APT detection. Huawei FireHunter is a sandbox.
- The CIS can effectively collect network traffic, and network and security logs of various devices. Based on real-time and offline analysis of big data and machine learning technology, expert reputation, and intelligence, the CIS can effectively detect potential and advanced threats on a network, implement security situation awareness of the entire network, and effectively complete the closed-loop handling of threats with the help of Huawei HiSec solution.
- Huawei-developed CDE uses the PE Class 2.0 AI algorithm to restore all files and perform in-depth detection on file content. (Flow detection is the mainstream in the industry. This technology is fast, but it restores only the file header and does not check the file content.
- Huawei's unique AIE APT detection engine uses AI algorithms to continuously defend against the latest threats.

### Section Summary

- This section describes the basic concepts, application scenarios, and development history of firewalls.
  - Firewalls are security devices and fall into fixed, modular, desktop, and software firewalls.
  - Firewalls can be used for but not limited to enterprise border protection, intranet control and security isolation, DC border protection, and DC security association.
  - The firewall technology is developing from the early packet filtering firewall to the current AIFW.

## 2. Basic Firewall Concepts

### Basic Firewall Concepts: Security Zone

- A security zone is an important concept of a firewall. Most security policies are implemented based on security zones.
- A security zone is a set of networks connected through interfaces. Users in a zone have the same security attributes.

**Diagram description:** A Trust zone contains two PCs connected to firewall interface GE1/0/1. The firewall also has interface GE1/0/3 connecting to the Untrust zone/Internet, and interface GE1/0/2 connecting down to a DMZ zone containing Servers. A callout notes: "GE1/0/1 of the firewall is added to the trusted zone, so the network connected to GE1/0/1 is considered to be in the trusted zone." Followed by: "Question: Does a firewall interface belong to a security zone?"

### Default Security Zones

- Four security zones have been created on Huawei firewalls: untrusted, DMZ, trusted, and local zones. Security zones have the following characteristics:
  - The default security zone cannot be deleted, and the security priority cannot be changed.
  - Each security zone must be configured with a security priority. A larger value indicates a higher priority of the security zone.
  - You can create customized zones as required.

**Diagram description:** A Trust zone (priority 85) contains two PCs connected via GE1/0/1 (Local priority 100) to the firewall; the firewall also connects via GE1/0/2 (Local priority 100) down to a DMZ zone (priority 50) containing Servers, and via GE1/0/3 (Local priority 100) to the Untrust zone (priority 5)/Internet.

| Security Zone Name | Default Security Priority |
|---|---|
| Untrusted zone | 5 (low security level) |
| DMZ | 50 (medium security level) |
| Trusted zone | 85 (high security level) |
| Local zone | A local zone is a device itself, including interfaces on the device. The local zone has the highest security level, and its priority is 100. |

- The default security zones are as follows:
- Untrusted zone: defines an insecure network, such as the Internet.
- DMZ: defines the zone where internal network servers reside. Internal network servers are frequently accessed by external network devices but cannot proactively access the external network, which causes huge security risks. These servers are deployed in a DMZ with a lower level than a trusted zone but a higher level than an untrusted zone.
  - A DMZ is originally a military term, referring to a partially controlled area between a military control area and a public area. A DMZ configured on a firewall is logically and physically separated from internal and external networks.
  - Devices that provide network services for external users are deployed in the DMZ. These devices such as web servers and FTP servers provide services for extranet devices. If the servers are placed on an internal network, their security vulnerabilities may be used by external malicious users to attack the internal network. If the servers are deployed on the external network, security cannot be ensured.
- Trusted zone: defines the zone where internal network terminals reside.

> **[Note: PDF page 1028 / slide 18 is missing from this export. The deck jumps directly from "Default Security Zones" (slide 17, page 1027) to "Interzone Example" (slide 19, page 1029) below.]**

### Interzone Example

- The source and destination addresses of the traffic determine the zones that can access each other. For ①, traffic from the PC to the firewall interface is transmitted from the trusted zone to the local zone. For ②, the traffic from the PC to Internet is transmitted from the trusted zone to the untrusted zone.

**Diagram description:** A PC in the Trust zone connects to a Firewall that contains interfaces GE0/0/1, GE0/0/2, and others, all within its Local zone; the firewall connects onward to the Untrust zone/Internet. Two numbered red arrows are shown: arrow ① goes from the PC to the firewall's local zone (interfaces); arrow ② arcs from the PC directly over the firewall to the Untrust zone/Internet.

### Basic Firewall Concepts: Security Policy

- A security policy is used by a firewall to control traffic forwarding and perform integrated detection over the traffic content.
- When receiving traffic, the firewall identifies traffic attributes (5-tuple, user, and time range) and matches them with the conditions of the security policy. If the traffic matches the conditions, the corresponding action is performed on the traffic.

**Diagram description:** A Trust zone contains an "Office area 192.168.10.0/24" and "R&D area 192.168.20.0/24," each with a PC, both connecting to a firewall. A security policy callout box reads: "Source address: 192.168.10.0/24 / Destination address: any / User: office area / Time range: 9:00 to 17:00 / Action: permit." Office area traffic passes through (checkmark) to the Untrust zone/Internet, while R&D area traffic is blocked (X mark).

### Security Policy Composition

- A security policy consists of matching conditions, actions, and security profiles (optional). The security profile ensures content security. If the action of the security policy is permit, the profile can be configured. If the action of the security policy is deny, the feedback packet can be configured.

**Diagram description:** A left-to-right flow: "Traffic" flows into a "Condition" block listing VLAN ID, Source security zone, Destination security zone, Source address/region, Destination address/region, ..., Time range; this flows into an "Action" block with two options, "Permit" and "Deny." The "Deny" option branches down into a "Response packet" block with options "Send" and "Do not send." The "Permit" path flows right into a "Security Profile" block listing Antivirus, Intrusion prevention, URL filtering, File filtering, Content filtering, ..., DNS filtering.

- Permit: If the action is permit, a firewall processes the traffic as follows:
  - If content security detection is not configured, the firewall allows the traffic to pass through.
  - If content security detection is configured, the firewall determines whether to permit the traffic based on the content security detection result. Content security detection includes antivirus and intrusion prevention, which are implemented by referencing security profiles in security policies. If one security profile blocks the traffic, the firewall blocks the traffic. If all security profiles permit the traffic, the firewall allows the traffic to pass through.
- Deny: The firewall does not allow the traffic that matches a security policy to pass through.
  - If the action is deny, the firewall discards the packet and can send a corresponding feedback packet based on the packet type. After the client/server receives the blocking packets from the firewall, it can rapidly terminate sessions and users can detect that the requests have been blocked.
    - Reset client: The firewall sends a TCP reset packet to the TCP client.
    - Reset server: The firewall sends a TCP reset packet to the TCP server.
    - ICMP unreachable: The firewall sends an ICMP unreachable packet to the client.

### Security Policy Matching Process

- When multiple security policies are configured, they are matched according to their configuration sequence. That is, the security policies are matched one by one from the top of the security policy list. If a packet matches a security policy, it will no longer match the following security policies.
- Therefore, the configuration sequence of security policies is important. You need to configure policies with precise conditions and then policies with loose conditions.

**Diagram description:** A vertical "Matching Sequence" arrow points downward alongside a table of multiple security policy rules, each row showing columns: Rule, Source zone/Destination zone, Source address/Destination address, User, Application, Service, Time range, Action, Content security profile, Enable log recording. The arrow indicates rules are matched from top to bottom.

- The system has a default security policy named default. The default security policy is located at the bottom of the policy list and has the lowest priority. All matching conditions of the default security policy are any and the default action is deny. If all the configured policies are not matched, the default security policy is used.

### Basic Firewall Concepts: Session Table

- A session table is used to record the connection status of protocols such as TCP, UDP, and ICMP.
- The firewall uses a stateful inspection mechanism which determines the status of a connection based on the first packet or the first several packets. Subsequent packets are then processed based on the connection status. The stateful inspection mechanism improves the detection and forwarding efficiency. The session table is used for maintaining the connection status. To forward TCP, UDP, and ICMP packets, the firewall must look up the session table for the connection status and process the packets accordingly.

**Diagram description:** PC1 (192.168.1.1/24, gateway 192.168.1.254) sits in the Trust zone, connected via firewall interfaces GE1/0/1 and GE1/0/2 to PC2 (an HTTP server, 10.1.1.1/24, gateway 10.1.1.254) in the Untrust zone. A six-step numbered sequence is shown: ① PC1 sends a packet; ② after the first packet reaches the firewall, the firewall creates a session entry; ③ the firewall permits the first packet; ④ PC2 replies with a packet; ⑤ return packets match session entries; ⑥ the firewall forwards the packet. The session table display shown at steps ② and ⑤ is:

```
[FW] display firewall session table
http  VPN:public --> public  192.168.1.1:52754-->10.1.1.1:80
```

- In this example, PC1 initiates an HTTP connection to PC2, so the firewall marks the HTTP protocol and connection information in the session table and identifies that the traffic is forwarded based on the public routing table (VPN:public in the figure).

### Session Table Creation and Packet Processing

**Diagram description:** A flowchart: "Receive the packet and perform basic processing" → "Query the session table" → a decision diamond "Match a session," with "Yes" branching to "Update session" → "Enforce security policy" → "Perform subsequent packet processing." The "No" branch enters a sub-process box containing, in sequence: "Determine whether a session can be set up through stateful detection" → "Query server map table" → "Query routing table" → "Query security policy" → "Query NAT policy" → "Use other first-packet processing" → "Create session"; this sub-process then flows into "Use security inspection" → "Forward the packet," which also receives the "Yes" branch's final output.

- When stateful inspection is enabled on the firewall, a session entry is created for the first packet of the traffic, and subsequent packets can directly match the session entry.
- The flowchart shows the basic processing sequence of each module of a Huawei firewall. In practice, packet processing may be different from the preceding flowchart (if there is no corresponding configuration) and depends on specific product implementation.
- For details, see "Packet Forwarding Process" in the product documentation of the specified firewall model.

### Aging Time and Persistent Connection of the Session Table

- Firewalls provide the session aging mechanism for protocols. A session that is not matched by any packet will be deleted from the session table. This mechanism prevents firewall resources from being consumed by a large number of useless and outdated session entries.
- For some special services, however, the interval between two consecutive packets of a session can be very long. For example:
  - When a user downloads large files through FTP, the interval between control packets along the control channel can be very long.
  - A user may query the data on a database server now and then, and the interval between query operations may be far greater than the aging time of the TCP session.
- If a session entry is deleted, the service is interrupted. The persistent connection mechanism can set an overlong aging time for some connections.

### Problems of Multi-Channel Protocols on a Firewall

- If a strict unidirectional security policy is configured on a firewall, the firewall allows only unidirectional access. As a result, some special protocols, such as FTP, cannot work.
- In FTP active mode, the client initiates a control connection to the server, and then the server initiates a data connection to the client. If the security policy configured on the firewall allows only packets from the client to pass through in one direction, FTP file transfer fails.
- Similar to FTP, a multi-channel protocol occupies two or more interfaces during communication. This problem needs to be considered for all multi-channel protocols.

**Diagram description:** An FTP Client connects through a firewall to an FTP Server, with a rule table entry "From FTP Client to FTP Server: Permit" labeled a "Unidirectional security policy." Step ① shows the client initiating a control connection toward the server (checkmark, allowed). Step ② shows the server initiating a data connection back toward the client, which is blocked (marked with a prohibition/no-entry symbol).

- Single-channel protocol: uses only one port during communication. For example, WWW uses only port 80.
- Multi-channel protocol: uses two or more ports for communication.
- FTP is a typical multi-channel protocol. Two connections are set up between the FTP client and server: control and data connections. A control connection is used to transmit FTP instructions and parameters, including information required for establishing a data connection. A data connection is used to obtain server directories and transfer data. The port number used for the data connection is negotiated during the control connection. FTP works in either active (PORT) or passive (PASV) mode, determined by the mode of initiating a data connection. In active mode, port 20 of the FTP server initiates a data connection to the FTP client. In passive mode, the FTP server accepts the data connection initiated by the FTP client. The mode can be set on the FTP client. Here, the active mode is used as an example.
- When multi-channel protocols exist, a firewall can be configured with security policies that define loose conditions to solve the problem of protocol unavailability. However, this brings security risks.

### Multi-Channel Protocol — FTP Process

**Diagram description:** An FTP Client connects through a firewall to an FTP Server. Step ①: the client uses a random port (xxxx) to send a control connection setup request to port 21 of the server, shown as a three-way handshake (SYN, SYN+ACK, ACK) followed by user name/password exchange, labeled "Three-way handshake for the control connection." A dashed line separates this from step ②: port 20 of the server sends a data connection setup request to the port (yyyy) negotiated by the client, shown first as a "PORT Command (IP 192.168.1.2 Port yyyy)" exchange labeled "Port negotiation by running the PORT command," followed by another three-way handshake (SYN, SYN+ACK, ACK) labeled "Three-way handshake for the data connection," then a LIST Command and data transmission. A legend defines solid arrows as "Control connection," dashed arrows as "Data connection," and notes "xxxx/yyyy Random port." A callout asks: "Question: How does a firewall permit data connections in a refined manner?"

- Most multimedia application protocols (such as H.323 and SIP), FTP, and NetMeeting use prescribed ports to initialize a control connection and then dynamically negotiate a port for data transmission. The port selection is unpredictable. Some applications may even use multiple ports at one time. Packet filtering firewalls can use ACLs to match applications of single-channel protocols to protect internal networks against attacks. However, ACLs can block only applications using fixed ports, and cannot match multi-channel protocol applications that use random ports, bringing security risks.

### ASPF and Server Map

- To solve problems of multi-channel protocols, a firewall needs to identify addresses and ports negotiated at the application layer. The Application Specific Packet Filter (ASPF) function must be enabled.
- ASPF is also called status-based packet filtering. It can automatically detect application-layer information of certain packets and define corresponding permit rules according to application-layer information. That is, a server map is generated.
- The server map also records the connection status similar to that in the session table. The server map is equivalent to a simplified session table and is generated before actual traffic arrives. When the traffic reaches the firewall, the firewall generates a session table based on the server map and forwards the traffic.
- ASPF is enabled to solve the multi-channel protocol problem. It is a method of generating a server map.

- When ASPF, NAT server, or source NAT (SNAT) in No-PAT mode is configured on a firewall, the firewall generates corresponding server map entries.

### Example of ASPF and Server Map

- After ASPF is configured on a firewall, the firewall checks the negotiated data connection port information in the FTP control connection and generates a server map entry. The server map entry contains information about the data channel negotiated in the FTP control channel. Then the firewall creates a session table for the packets that match server map entries.

**Diagram description:** An FTP client (192.168.1.2/24, gateway 192.168.1.1) sits in the Trust zone, connected via firewall interfaces GE1/0/1 and GE1/0/2 to an FTP server (10.1.1.2/24, gateway 10.1.1.1) in the Untrust zone. Step ①: "Create a server map on the firewall." Step ②: "Create a session table on the firewall."

```
[FW] display firewall server-map
Type: ASPF,  10.1.1.2 -> 192.168.1.2:2097,  Zone:---
Protocol: tcp(Appro: ftp-data),  Left-Time:00:00:10
Vpn: public --> public
```

```
[FW] display firewall session table
ftp  VPN: public --> public   192.168.1.2:2095 <-> 10.1.1.2:21
ftp-data  VPN: public --> public   10.1.1.2:20 --> 192.168.1.2:2097
```

- The relationship between a server map and a session table:
  - A server map records key information about application-layer data. If a packet matches the server map, the security policy is invalid for the packet.
  - A session table represents the connection status of two communication parties.
  - The server map does not represent the current connection status. It predicts subsequent packets based on the analysis of an existing connection.
  - When receiving a packet, a firewall first checks whether the packet matches the session table.
  - If not, the firewall checks whether the packet matches the server map.
  - The security policy is invalid for the packet matching the server map.
  - Then the firewall creates a session table for the packet matching the server map.

### Server Map and Simplified Packet Forwarding Process

- When a firewall receives a packet that does not match a session table, the firewall starts the first-packet processing to check whether the packet matches the server map. If so, the firewall generates a session table to forward packets. If not, the firewall performs other packet processing.

**Diagram description:** A flowchart: "Receive a packet" → decision "Does the packet match the session table?" — "Y" branches to "Forward the packet"; "N" branches to decision "Does the packet match the server map?" — "Y" branches to "Generated a session table," which then flows into "Forward the packet"; "N" branches to "Perform other first-packet processing."

### Section Summary

- This section describes basic concepts and features of firewalls, including:
  - Security zone
  - Security policy
  - Session table
  - Server map

## 3. Basic Firewall Configurations

### Basic Firewall Configurations — Interface

1. Create an interface or enter the interface view.

```
[Huawei] interface interface-type interface-number
```

The **interface** command on a firewall is used to create an interface or enter the view of a specified interface, which is similar to that on switches and routers.

2. Configure the protocol allowed by the interface.

```
[Huawei-GigabitEthernet0/0/1] service-manage { http | https | ping | ssh | snmp | netconf | telnet | all } { permit | deny }
```

The **service-manage** command allows or blocks access to a firewall through HTTP, HTTPS, ping, SSH, SNMP, NETCONF, or Telnet.
By default, an interface has the access control and management function enabled. HTTP, HTTPS, and ping permissions are enabled on the management interface only. All permissions on non-management interfaces are disabled.

### Basic Firewall Configurations — Security Zone

1. Create a security zone and enter the security zone view.

```
[Huawei] firewall zone name zone-name [ id id ]
```

**firewall zone name** creates a security zone and displays the security zone view. *id* specifies the ID of a security zone. The value ranges from 4 to 99 and increases in ascending order.
**firewall zone** displays the security zone view. The default four security zones of a firewall cannot be deleted.

2. Set the priority of the security zone.

```
[Huawei-zone-name] set priority security-priority
```

The priority value ranges from 1 to 100. It is unique. A larger value indicates a higher priority. Default security zones cannot be deleted, and their priorities cannot be reconfigured or deleted.

3. Add an interface to the security zone.

```
[Huawei] add interface interface-type { interface-number | interface-number.subinterface-number }
```

A security zone needs to be associated with a specific interface of a firewall. That is, the interface needs to be added to the security zone. The interface can be a physical or logical one.

### Basic Firewall Configurations — Security Policy (1)

1. Enter the security policy view.

```
[Huawei] security-policy
```

You can create, copy, move, or rename a security policy rule in the security policy view.

2. Configure a security policy rule in the security policy view and enter the security policy rule view.

```
[Huawei-policy-security] rule name rule-name
```

3. Configure the source security zone of the security policy rule in the security policy rule view.

```
[Huawei-policy-security-rule-name] source-zone { zone-name &<1-6> | any }
```

The security zone must exist in the system. You can add or delete a maximum of six security zones in a security policy rule at a time.

4. Configure the destination security zone of the security policy rule in the security policy rule view.

```
[Huawei-policy-security-rule-name] destination-zone { zone-name &<1-6> | any }
```

### Basic Firewall Configurations — Security Policy (2)

5. Configure the source IP address of the security policy rule.

```
[Huawei-policy-security-rule-name] source-address ipv4-address { ipv4-mask-length | mask mask-address}
```

In the command, *mask-address* is a wildcard mask.

6. Configure the destination IP address of the security policy rule.

```
[Huawei-policy-security-rule-name] destination-address ipv4-address { ipv4-mask-length | mask mask-address}
```

In the command, *mask-address* is a wildcard mask.

7. Configure a service.

```
[Huawei] service { service-name &<1-6> | any }
```

The **service** command configures a service. For example, the **service protocol** command references a TCP/UDP/SCTP port or an IP-layer protocol in a security policy.

8. Configure an action in the security policy rule.

```
[Huawei] action { permit | deny }
```

The default action of a firewall is deny.

- The source and destination IP addresses specified in the security policy rule view can have many optional parameters, such as the IP address group, region, and region group. This course does not describe these optional parameters. For more information, see the product documentation.

### Firewall Configuration Examples

**Description:**
- The firewall isolates the network into three security zones: trusted, untrusted, and OM. The priority of the OM zone is 95. The requirements are as follows:
  - GE1/0/1 of the firewall can respond to ping requests.
  - ICMP traffic in the OM zone can reach the untrusted zone.

**Diagram description:** A firewall has three connections: GE1/0/1 to a Trust zone containing a PC; GE1/0/2 to an "OM" zone (priority 95) containing a server icon; and GE1/0/3 to an Untrust zone/Internet.

The configuration process consists of four steps:
- Configure a firewall interface.
- Configure a security zone.
- Configure a security policy.
- Verify the configuration.

### Configuration Example — Interface

Task list:
- Configure an IP address for a firewall interface according to the planning.
- Configure GE1/0/1 to allow the ping service.

**Diagram description:** Same firewall/zone layout as above, now with GE1/0/1 addressed 1.1.1.1/24 (Trust side), GE1/0/2 addressed 2.2.2.1/24 (OM zone, priority 95), and GE1/0/3 addressed 3.3.3.1/24 (Untrust side).

```
# Configure an IP address for the interface and allow the ping service on GE1/0/1.
[FW] interface GigabitEthernet 1/0/1
[FW-GigabitEthernet1/0/1] ip address 1.1.1.1 24
[FW-GigabitEthernet1/0/1] service-manage ping permit
[FW-GigabitEthernet1/0/1] interface GigabitEthernet 1/0/2
[FW-GigabitEthernet1/0/2] ip address 2.2.2.1 24
[FW-GigabitEthernet1/0/2] interface GigabitEthernet 1/0/3
[FW-GigabitEthernet1/0/3] ip address 3.3.3.1 24
```

### Configuration Example — Security Zone

Task list:
- Create security zone OM and set its priority to 95.
- Add interfaces to the planned security zones.

```
# Create a security zone.
[FW] firewall zone name OM
[FW-zone-OM] set priority 95
[FW-zone-OM] quit

# Add interfaces to corresponding security zones.
[FW] firewall zone trust
[FW-zone-trust] add interface GigabitEthernet 1/0/1
[FW] firewall zone OM
[FW-zone-OM] add interface GigabitEthernet 1/0/2
[FW] firewall zone untrust
[FW-zone-untrust] add interface GigabitEthernet 1/0/3
```

### Configuration Example — Security Policy Configuration

Task list:
- Create security policy R1.
- Configure a security policy rule, including the source and destination zones, service type, and action.

```
# Create a security policy.
[FW-policy-security] rule name R1
[FW-policy-security-rule-R1] source-zone OM
[FW-policy-security-rule-R1] destination-zone untrust
[FW-policy-security-rule-R1] service icmp
[FW-policy-security-rule-R1] action permit
```

### Configuration Example — Verification (1)

1. The PC in the trusted zone initiates a ping test to GE1/0/1 of the firewall.

```
# Check the session table on the firewall.
[FW]display firewall session table
2020-03-11 10:31:21.010
Current Total Sessions : 4
icmp  VPN: public --> public  1.1.1.2:14265 --> 1.1.1.1:2048
icmp  VPN: public --> public  1.1.1.2:15289 --> 1.1.1.1:2048
icmp  VPN: public --> public  1.1.1.2:14777 --> 1.1.1.1:2048
icmp  VPN: public --> public  1.1.1.2:15033 --> 1.1.1.1:2048
```

### Configuration Example — Verification (2)

2. The device at 2.2.2.2 in security zone OM initiates a ping request to the device at 3.3.3.2 in the untrusted zone.

```
# Check the session table on the firewall.
[FW]display firewall session table
2020-03-11 10:30:15.150
Current Total Sessions : 4
icmp  VPN: public --> public  2.2.2.2:63928 --> 3.3.3.2:2048
icmp  VPN: public --> public  2.2.2.2:63672 --> 3.3.3.2:2048
icmp  VPN: public --> public  2.2.2.2:63416 --> 3.3.3.2:2048
icmp  VPN: public --> public  2.2.2.2:62904 --> 3.3.3.2:2048
```

Callout: "Question: ICMP does not have a port number. What is the port number in the firewall session table?"

- ICMP does not have a port. However, the firewall generates a port number when generating the session table corresponding to ICMP traffic to meet status detection requirements.

### Section Summary

- This section describes basic configuration commands of the firewall. After learning basic firewall configurations, you can use commands to perform the following configurations:
  - Configure firewall interfaces.
  - Assign firewall security zones.
  - Configure security policies.
  - Check firewall session information.

## Quiz

1. (Single) By default, a firewall has ( ) security zones.
   A. 1
   B. 2
   C. 3
   D. 4
2. (TorF) The firewall must generate a server map before generating a session table. ( )

**Answers:** 1. D  2. F

3. (Multiple) Which of the following statements about Huawei AIFWs are correct? ( )
   A. Built-in CDE - malicious file detection engine
   B. Built-in probe
   C. Built-in APT detection engine (AIE)
   D. Built-in deception sensor

**Answer:** 3. ABCD

## Summary

- Firewalls are one of the most important security devices in the communications field. This course helps you learn basic concepts, development history, and basic configurations of firewalls.
- The security zone, security policy, session table, and server map are basic and important concepts of firewalls and are the prerequisite for further learning the firewall technology.
- Firewalls provide more security functions, such as content security filtering, antivirus, and intrusion prevention. For more information about firewall technologies, see Huawei Certification — Security.

## More Information

Huawei HiSecEngine USG6000E series AIFW documents.
https://support.huawei.com/enterprise/en/security/usg6600e-pid-23176231

## Recommendations

- For more training materials and videos, visit https://e.huawei.com/en/talent/#/home.

---

# Security Features of Network Devices

## Foreword

- IP networks of large scales usually have numerous network devices and various communication protocols, adding complexity to network management. It is difficult to balance security and service flexibility, as well as security and management & maintenance convenience. When striking a balance between these, administrators with varying degrees of technical and management expertise perform differently. Administrators may ignore security protection capabilities in the pursuit of service availability, resulting in the failure to configure necessary security measures. The devices, therefore, cannot effectively defend against attacks as they are designed to.
- This course describes common security hardening policies of network devices and provides examples for common security configurations.

## Objectives

- On completion of this course, you will be able to:
  - Learn common device security hardening policies.
  - Configure STelnet.
  - Configure local attack defense.

## Contents

1. Common Security Hardening Policies
2. Examples for Security Hardening Policy Deployment

## 1. Common Security Hardening Policies

### Why Is Security Vital to Network Devices?

**Diagram description:** A hierarchical network is shown with two edge routers connected to the Internet at the top; below them a layer of devices; below that another layer including a highlighted device labeled "R2" performing "ping x.x.x.x" (marked ②); at the bottom, user icons connect to devices including highlighted devices "R1"..."Rn," where a user runs "telnet x.x.x.x ... reboot" (marked ①).

- Network security is a systematic project. Everything on the network may become a target of attacks, and network devices are no exception.
- Common attacks on network devices include the following:
  1. Malicious users log in to network devices to perform unauthorized operations (for example, restarting the devices), leading to malfunctioning networks.
  2. A large number of control packets (for example, ICMP packets) are forged and sent to the CPU of a target device, leading to a surge in CPU usage.

### Common Security Hardening Policies

- Common security hardening policies on network devices include the following:
  - Disabling unused services and ports
  - Discarding insecure access channels
  - Access control based on trusted paths
  - Local attack defense

### Disabling Unused Services and Ports

- Based on service requirements analysis and the minimum authorization principle, disable unused services and ports.
  - Disable unused physical ports, which then cannot be used for communication even when network cables are connected.
  - Disable unused protocol ports, for example, common Telnet, FTP, and HTTP ports, which then cannot be accessed from external systems.

**Diagram description:** Four PCs (PC1–PC4) each connect via ports GE0/0/0 through GE0/0/3 to a switch labeled SW1.

Caption: "Disable the FTP function and unused ports on SW1."

```
<SW1> system-view
[SW1] undo ftp server
Warning: The operation will stop the FTP server. Do you want to continue? [Y/N]:y
Info: Succeeded in closing the FTP server.
[SW1]port-group protgroup1
[SW1-port-group-protgroup1]group-member GigabitEthernet 0/0/4 to GigabitEthernet0/0/48
[SW1-port-group-protgroup1]shutdown
```

### Discarding Insecure Access Channels

- The access requirements of services must be preferentially fulfilled based on service requirements analysis. When an access requirement involves multiple access channel services, secure channels must be selected and insecure ones must be discarded.

| Access Requirement | Insecure Channel | Secure Channel |
|---|---|---|
| Remote login | Telnet | SSHv2 |
| File transfer | FTP and TFTP | SFTP |
| NE management | SNMPv1 and SNMPv2 | SNMPv3 |
| NMS login | HTTP | HTTPS |

- When you log in to a device through the CLI, web UI, or NMS, you are advised to use the corresponding SSH, HTTPS, or SNMPv3 channel.
- SFTP is recommended for data transmission between devices and between devices and terminals.

### Secure Data Access Channel

- To ensure device security, select secure access channels as long as conditions permit.
- Common scenarios and protocols for device data transmission security:
  - Remote login:
    - Telnet: transmits data in clear text using TCP.
    - STelnet: provides secure information protection and powerful authentication functions based on SSH.
  - File operations:
    - FTP: supports file transfer and file directory operations, provides authorization and authentication functions, and transmits data in clear text.
    - TFTP: supports only file transfer and transmits data in clear text. It does not support authorization or authentication.
    - SFTP: supports file transfer and file directory operations; strictly encrypts data and protects data integrity.

### SSH Overview

- Secure Shell (SSH) provides secure remote login, file transfer, and TCP/IP tunnels on insecure networks. It encrypts not only the password during login, but also the executed command data after login.
- After an authorized user logs in from the client and the user name and password are verified, the client attempts to establish a session with the server. Each session is an independent logical channel and can be used by different upper-layer applications.
- STelnet and SFTP each use a logical channel to encrypt data through SSH, implementing secure data transmission.

**Diagram description:** Two boxes, "STelnet" and "SFTP," both connect down into a shared "SSH channel" box.

- SSH is developed by the IETF. The latest version is V2.0. Earlier versions 1.3 and 1.5 have security risks and are gradually obsolete.
- SSH supports two-way authentication between the server and client, and provides security services such as confidentiality and integrity protection.

### SSH Protocol Structure

- The SSH protocol framework has three pillar protocols: transport protocol, user authentication protocol, and connection protocol.
  - Transport protocol: provides version negotiation, encryption algorithm negotiation, key exchange, server authentication, and information integrity verification.
  - User authentication protocol: authenticates clients for the server.
  - Connection protocol: multiplexes an encrypted information tunnel into multiple logical channels, which are provided for upper-layer application protocols (STelnet and SFTP). Various upper-layer application protocols can be relatively independent of the SSH basic system. They also rely on this basic system to use the SSH security mechanism through the connection protocol.

**Diagram description:** A Client and a Server each run a stack of three protocol layers connected over "SFTP/STelnet": SSH connection protocol, SSH user authentication protocol, and SSH transport protocol, all layered over a shared TCP connection at the bottom.

- SSH uses the following types of algorithms:
  - MAC algorithms for data integrity protection, such as HMAC-MD5 and HMAC-MD5-96
  - Data encryption algorithms, such as 3DES-CBC, AES128-CBC, and DES-CBC
  - Key exchange algorithm used to generate session keys, such as diffle-hellman-group-exchange-sha1
  - Host public key algorithm used for digital signature and authentication, such as RSA and DSA

### Access Control Based on Trusted Paths

- Configure access control policies based on trusted paths on network devices to improve network security.
- Deploy URPF to determine whether the source address of a packet is valid. If the path of the packet is inconsistent with the path learned by URPF, the packet is discarded. In this way, URPF helps to prevent network attacks with spoofed IP source addresses.

**Diagram description:** PC1 connects through router R1, and PC2 connects through router R2, both feeding into router R3 (interface GE0/0/1 toward R1, interface GE0/0/0 toward R2), which connects to a Server. Step ①: PC2 "Forges the source address of PC1 to initiate access" (blue arrow toward R3). Step ②: "R3 checks FIB information and finds that the outbound interface to PC1 is GE0/0/1." Step ③: R3 "Discards the packet" (shown with a red arrow and a discard icon).

- The openness of IP networks determines that anyone can access or attack the target host as long as routes are reachable.
- For a host, the path of the packets sent to it from a client is fixed, especially at the edge of a network.
- Unicast Reverse Path Forwarding (URPF) can be classified into strict URPF and loose URPF, and the mode in which matching the default route is allowed can be configured. During the URPF check, the device checks whether source IP addresses of packets are valid based on the routing table.
  - In strict mode, if a packet matches a specific route and the inbound interface of the packet is the same as the outbound interface of the route, the packet is allowed to pass. Otherwise, the packet is discarded.
  - In loose mode, if a packet matches a specific route, the packet is allowed to pass. Otherwise, the packet is discarded. In this mode, the interface is not checked. By default, the device does not match packets with the default route. You can configure the device to match packets with the default route.
  - Matching the default route must work with strict URPF. When a packet matches a specific route or the default route and the inbound interface of the packet is the same as the outbound interface of the matched route, the packet is allowed to pass. Otherwise, the packet is discarded. Matching the default route cannot be configured with loose URPF because attack defense cannot be achieved in this way. Loose URPF and strict URPF are mutually exclusive.

### Local Attack Defense

- In addition to numerous normal service packets, CPUs of devices on a network may also receive large numbers of attack packets. If a CPU is busy processing attack packets for an extended period, other services, or even the system itself, will experience interruption. Similarly, if a large number of normal packets are sent to the CPU, the CPU usage will surge and device performance will deteriorate, adversely affecting services.
- To ensure that the CPU can properly process and respond to normal services, the device provides the local attack defense function, which has been specifically designed for packets sent to the CPU and is primarily used to protect the device from attacks and ensure consistency of existing services when an attack occurs.
- Local attack defense includes CPU attack defense and attack source tracing.
  - CPU attack defense can rate-limit packets destined for the CPU so that only a limited number of packets are sent to the CPU within a certain period of time. This ensures that the CPU can properly process services.
  - Attack source tracing defends against Denial of Service (DoS) attacks. A device enabled with attack source tracing analyzes packets sent to the CPU, collects statistics on the packets, and allows a packet rate threshold to be set for the packets. Packets sent at a threshold-crossing rate are considered as attack packets. The device finds the source user address or source interface of the attacker by analyzing the attack packets and generates logs or alarms to alert a network administrator. The network administrator then takes measures to protect the device against the attack or configure the device to discard packets sent by the attack source.

### CPU Attack Defense

- Network devices employ four-level security mechanisms to protect their security:
  - Level 1: filter invalid packets sent to the CPU by using blacklists.
  - Level 2: Use Control Plane Committed Access Rate (CPCAR) to rate-limit the packets sent to the CPU based on the protocol type, preventing excess packets of a protocol from being sent to the CPU.
  - Level 3: schedule packets sent to the CPU based on the protocol priority to ensure that packets with higher protocol priorities are preferentially processed.
  - Level 4: uniformly rate-limit all packets sent to the CPU and randomly discard the excess packets to ensure CPU security.
- Regarding rate limiting on packets sent to the CPU in active link protection, when a device detects the establishment of an SSH, Telnet, HTTP, FTP, or BGP session, it enables active link protection for the session. Subsequent packets that match the session characteristics will be sent to the CPU at a high rate, ensuring the reliability and stability of services related to the session.

### Working Mechanism of Attack Source Tracing

- Attack source tracing involves four steps: parsing packets, analyzing traffic, identifying an attack source, and sending logs or alarms to a network administrator or taking punishment measures.

**Diagram description:** A box labeled "Attack source tracing" contains four sequential sub-steps connected by arrows: "Packet parsing" → "Traffic analysis" → "Attack source identification" → "Log & alarm/Punishment." Below this, a "Chip-based forwarding" box feeds upward into the "Packet parsing" step.

- The device locates the attack source, and the network administrator rate-limits the packets sent from the attack source by configuring ACLs or blacklists to protect the CPU.

## 2. Examples for Security Hardening Policy Deployment

### STelnet Configuration

#### Basic SSH Configuration (1)

1. Enable the SSH server function.

```
[Huawei] stelnet server enable
```

2. Configure the authentication mode for an SSH user.

```
[Huawei] ssh user user-name authentication-type { password | rsa | password-rsa | all }
```

If RSA authentication is used, configure the public key of the SSH client on the SSH server. When the SSH client connects to the SSH server, the SSH client passes the authentication if its private key matches the configured public key.

3. Configure the public key generated by the SSH client.

```
[Huawei] rsa peer-public-key key-name [ encoding-type { der | openssh | pem } ]
[Huawei-rsa-key-code] public-key-code begin
```

The public key must be a hexadecimal character string in the public key encoding format, and generated by the SSH client.

4. Exit the public key editing view, edit the public key view, and return to the system view.

```
[Huawei-rsa-key-code] public-key-code end
[Huawei-rsa-public-key] peer-public-key end
```

#### Basic SSH Configuration (2)

1. Assign an RSA public key to the SSH user.

```
[Huawei] ssh user user-name assign { rsa-key | ecc-key } key-name
```

2. Generate the local RSA host and server key pairs.

```
[Huawei] rsa local-key-pair create
```

If an RSA key pair exists, the system prompts you to confirm whether to replace the original key pair. After you run this command, the system prompts you to enter the number of bits of the host key. The difference between the bits in the server and host key pairs must be 128 bits or more. The host key pair length and server key pair length both range from 512 to 2048, in bits, and their default values are both 2048.

3. Enable first authentication on the SSH client.

```
[Huawei] ssh client first-time enable
```

When an SSH client accesses an SSH server for the first time and the public host key of the SSH server is not configured on the SSH client, enable the first authentication function. The SSH client then can access the SSH server and save the public host key on the SSH client. When the SSH client accesses the SSH server next time, the saved public host key is used to authenticate the SSH server.

#### SSH Configuration Example

- Configure STelnet for secure remote login to R3.
- Configure two login users client001 and client002 on R3. R1 uses client001 to log in to R3 in password authentication mode, and R2 uses client002 to log in to R3 in RSA authentication mode. Configure a security policy to ensure that only users from R1 and R2 can log in to R3.

**Diagram description:** R1 (192.168.1.2) and R2 (192.168.1.3) both connect to a switch SW1, which connects (192.168.1.1) to R3.

Procedure:
1. Configure the SSH server (R3) to generate a local key pair for secure data exchange between the server and clients (R1 and R2).
2. Configure SSH users client001 and client002 on the SSH server.
3. Enable the STelnet server function on the SSH server.
4. Set the service type of SSH users client001 and client002 to STelnet on the SSH server.
5. Customize an SSH service port number on the SSH server. Then attackers cannot connect to the server through the standard SSH service port, ensuring security.
6. Log in to the SSH server as users client001 and client002 through STelnet.

#### SSH Configuration Commands (1)

```
[R3] rsa local-key-pair create
The key name will be: Host
RSA keys defined for Host already exist. Confirm to replace them? (y/n):y
The range of public key size is (512 ~ 2048).
NOTES: If the key modulus is less than 2048,
       It will introduce potential security risks.
Input the bits in the modulus[default = 2048]:2048
Generating keys...  ................................................+++ ...+++
     ................................+++++++ ...........+++++++
```

#### SSH Configuration Commands (2)

```
[R3] user-interface vty 0 4
[R3-ui-vty0-4] authentication-mode aaa
[R3-ui-vty0-4] protocol inbound ssh
[R3-ui-vty0-4] quit
[R3] aaa
[R3-aaa] local-user client001 password irreversible-cipher Huawei@123
[R3-aaa] local-user client001 privilege level 3
[R3-aaa] local-user client002 password irreversible-cipher Huawei@123
[R3-aaa] local-user client002 privilege level 3
[R3-aaa] quit
[R3] ssh user client001 authentication-type password
[R3] ssh user client002 authentication-type rsa

[R3] stelnet server enable

[R3] aaa
[R3-aaa] local-user client001 service-type ssh
[R3-aaa] local-user client002 service-type ssh
[R3-aaa] quit

[R3] ssh server port 1025
```

#### SSH Configuration Commands (3)

- The configurations in this slide and the following two slides enable user client002 to log in to R3.

```
# Generate a local key pair on R2.
[R2] rsa local-key-pair create
The key name will be: Host
RSA keys defined for Host already exist.
Confirm to replace them? (y/n):y
The range of public key size is (512 ~ 2048).
NOTES: If the key modulus is less than 2048,
       It will introduce potential security risks.
Input the bits in the modulus[default = 2048]:2048
Generating keys... ................................................
+++ ....+++ .................................+++++++ ...........+++++++
```

#### SSH Configuration Commands (4)

```
# Display the public key in the RSA key pair generated by R2.
[R2] display rsa local-key-pair public
Key code: 30820109 02820100 CB0E88EC A1C2CFEA F97126F9 36919C08
0455127B A3A48594 69517096 35626F55 E4FAF0EB FDA2B9E9 5E417B2B
E09F3B80 D26FCA73 FE2E3FC4 DFBEC8CF 4ED0C909 E8D975E6 FFC73C81
D13FE71E 759DC805 B0F0E877 4FC9288E BE1E197C 2A7186B0 B56F5573
3A5EA588 29C63E3B 20D56233 8E63278D F941734F 6B359C69 BBAE5A52
D264CEB9 5BADA92C CDE9F116 D6D99C48 CEBA3A1D 868B053A
32941D85 CCAA9796 A4B55760 0A8108ED DB45DA12 F61634C9
59431600 341FEDEF 5379D565 A8D1953D DEA018A2 72F99FFC 63DE04BF
2A6219BD DF13D705 27D63DEF 83D556BC 5B44D983 8D5EA126
C1EB71CB 0203 010001

=======================================================
Time of Key pair created: 2012-08-06 17:17:44+00:00 Key name: Server Key
type: RSA encryption Key
=======================================================
Key code: 3067 0260 DF8AFF3C 28213894 2292852E E98657EE 11DE5AF4
8A176878 CDD4BD31 55E05735 3080F367 A83A9034 47D534CA 81250C1D
35401DC3 464E9E5F A50202CF A7AD09CD AC3F531C A763F0A0 4C8E51B9
18755400 76AF4A78 225C92C3 01FE0DFF 06908363 0203 010001
```

#### SSH Configuration Commands (5)

```
# Copy the RSA public key (the information in bold in the display command output in the previous slide) generated on R2 to the server.
[R3] rsa peer-public-key rsakey001
[R3-rsa-public-key] public-key-code begin
[R3-rsa-key-code] 30820109
[R3-rsa-key-code] 02820100
[R3-rsa-key-code] CB0E88EC A1C2CFEA F97126F9 36919C08 0455127B
[R3-rsa-key-code] ......
[R3-rsa-key-code] 010001
[R3-rsa-key-code] public-key-code end
[R3-rsa-public-key] peer-public-key end

# Bind the RSA public key of R2 to client002 on R3.
[R3] ssh user client002 assign rsa-key rsakey001
```

#### Verifying the SSH Configuration

```
[R1] ssh client first-time enable
[R1] stelnet 192.168.1.1 1025
Please input the username:client001
Trying 192.168.1.1 ...
Press CTRL+K to abort
Connected to 192.168.1.1 ...
The server is not authenticated. Continue to access it?(y/n)[n]:y
Save the server's public key?(y/n)[n]:y
The server's public key will be saved with the name 192.168.1.1. Please wait...
Enter password:
<R3>                                        # The login is successful.

[R2] ssh client first-time enable
[R2] stelnet 192.168.1.1 1025
Please input the username:client002
Trying 192.168.1.1 ... Press CTRL+K to abort Connected to 192.168.1.1 ...
The server is not authenticated. Continue to access it?(y/n)[n]:y
Save the server's public key?(y/n)[n]:y
The server's public key will be saved with the name 192.168.1.1. Please wait...
<R3>                                        # The login is successful.
```

### Local Attack Defense Configuration

#### Basic Configuration of Local Attack Defense (1)

1. Create an attack defense policy and enter the attack defense policy view.

```
[Huawei] cpu-defend policy policy-name
```

2. Configure a blacklist.

```
[Huawei-cpu-defend-policy-test] blacklist blacklist-id acl acl-number
```

If multiple blacklists need to be configured in an attack defense policy, Layer 2 ACLs and basic ACLs, Layer 2 ACLs and advanced ACLs, or all the three types of ACLs cannot be used together in the blacklist group of the attack defense policy.

3. Configure the rate limit for packets sent to the CPU.

```
[Huawei-cpu-defend-policy-test] packet-type packet-type rate-limit rate-value
```

If a device receives attack packets or a large number of normal packets of a protocol type destined for the CPU, you can rate-limit the packets of this protocol type within a small range to reduce the impact on CPU's processing of normal services.

4. Configure the priority for packets of a specified protocol type sent to the CPU.

```
[Huawei-cpu-defend-policy-test] packet-type packet-type priority priority-level
```

#### Basic Configuration of Local Attack Defense (2)

1. Enable active link protection.

```
[Huawei-cpu-defend-policy-test] cpu-defend application-appceive [ ssh | telnet |  bgp | ftp | http ] enable
```

By default, active link protection is enabled for SSH, Telnet, SSHv6, Telnetv6, FTP, BGP, and HTTP.

2. Enable attack source tracing.

```
[Huawei-cpu-defend-policy-test] auto-defend enable
```

3. Set the rate threshold of attack source tracing.

```
[Huawei-cpu-defend-policy-test] auto-defend threshold threshold
```

4. Enable the event reporting function for attack source tracing.

```
[Huawei-cpu-defend-policy-test] auto-defend alarm enable
```

5. Apply the attack defense policy.

```
[Huawei] cpu-defend-policy policy-name [ global | slot slot-id ]
```

#### Configuration Example of Local Attack Defense

- As shown in the figure, users on different LANs access the Internet through R1. To locate attacks on R1, attack source tracing needs to be configured to trace the attack source. The existing network conditions are as follows:
  - A user on Net1 frequently initiates attacks to R1.
  - R1 receives a large number of ARP Request packets, degrading its CPU performance.
  - R1 cannot provide the FTP service.
  - LAN users obtain IP addresses through DHCP, whereas R1 does not preferentially process DHCP packets sent to the CPU.
  - R1 receives a large number of Telnet packets.
- To address these issues, proper configurations are required on R1.

**Diagram description:** Three networks, Net1, Net2, and Net3, each connect through router R1 via interfaces GE2/0/1, GE2/0/2, and GE2/0/3 respectively; R1 connects onward to R2, which connects to the Internet.

- Net: network

#### Local Attack Defense Configuration Commands (1)

Task list:
1. Configure a blacklist and add the attacker (0001-c0a8-0102) on network segment Net1 to the blacklist to prevent the attacker from accessing the network.
2. Configure the rate limit for ARP Request packets sent to the CPU, reducing the impact on CPU's processing of normal services.
3. Configure active link protection for FTP so that R1 can provide the FTP service.
4. Configure a high priority for DHCP client packets so that R1 preferentially processes DHCP client packets sent to the CPU.
5. Disable the Telnet server function on R1 so that R1 discards received Telnet packets.

```
# Configure an ACL to be referenced by a blacklist.
[R1] acl number 4001
[R1-acl-L2-4001] rule 5 permit source-mac 0001-c0a8-0102
[R1-acl-L2-4001] quit

# Create an attack defense policy.
[R1] cpu-defend policy devicesafety

# Configure attack source tracing.
[R1-cpu-defend-policy-devicesafety] auto-defend enable
[R1-cpu-defend-policy-devicesafety] auto-defend threshold 50

# Configure the blacklist.
[R1-cpu-defend-policy-devicesafety] blacklist 1 acl 4001
```

#### Local Attack Defense Configuration Commands (2)

```
# Set the rate limit for ARP Request packets sent to the CPU.
[R1-cpu-defend-policy-devicesafety] packet-type arp-request rate-limit 64

# Set the rate limit for FTP packets after active link protection is enabled.
[R1-cpu-defend-policy-devicesafety] application-appceive packet-type ftp rate-limit 2000
# Enable active link protection for FTP.
[R1] cpu-defend application-appceive ftp enable

# Apply the attack defense policy.
[R1] cpu-defend-policy devicesafety

# Disable the Telnet server function.
[R1] undo telnet server enable
```

- Application layer association does not need to be enabled. You only need to disable the Telnet server function on the router so that the router discards received Telnet packets.

#### Verifying the Local Attack Defense Configuration

```
# Check the statistics on packets sent to the MPU. That some packets are discarded indicates that the rate limit is set for ARP Request packets.
<R1> display cpu-defend statistics
   Packet Type          Pass Packets           Drop Packets

     8021X                    0                      0
    arp-miss                  5                      0
    arp-reply               8090                      0
   arp-request            1446576                 127773
      bfd                     0                      0
      bgp                     0                      0
    bgp4plus                  0                      0
   dhcp-client                879                      0
   dhcp-server                 0                      0
```

```
# Check the configured attack defense policy.
[R1] display cpu-defend policy devicesafety
Related slot   : <0>
...
Slot<0>        : Success
Configuration :
     Blacklist 1 ACL number             : 4001
     Packet-type arp-request rate-limit : 64(pps)
     Packet-type dhcp-client priority   : 3
     Rate-limit all-packets             : 2000(pps)(default)
     Application-appceive packet-type ftp  : 2000(pps)
     Application-appceive packet-type tftp : 2000(pps)
```

