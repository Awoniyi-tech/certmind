# Introduction to Network Management Protocols

> **Source file note:** This PDF export is missing two pages based on the footer page numbers. Page **8** is missing (footer jumps from 7 to 9) — this likely contains the rest of the "Trends in Network Management Development" slide, since the visible bullet list cuts off mid-sentence at "Full-lifecycle automation." Page **14** is missing (footer jumps from 13 to 15) — this likely contains the rest of "Five Functions of Network Management," specifically the descriptions for Security management and Accounting management, which are shown in the diagram but not described in the visible notes. Please re-export and re-upload a complete version if you want these two pages included; everything below is transcribed exactly as it appears in the rest of the deck.

## Foreword

- With the rapid development of new technologies such as artificial intelligence, big data, and cloud computing, various industries will be marching towards digital transformation in the near future. In addition, enterprise services will become diversified along with digital transformation, making network management one of the most challenging tasks for us. We cannot manage the entire network manually. Instead, we are in desperate need of an automated, smart tool to help us manage devices and resources on the network.
- This course starts with a brief introduction about the development history of network management and the related concepts, followed by a detailed description of the protocols used in network management and their respective application scenarios. Finally, typical application cases of network management are provided.

## Objectives

- On completion of this course, you will be able to:
  - The development trend and functions of network management.
  - The functions of network management protocols.
  - The similarities and differences between the implementation mechanisms and application scenarios of different network management protocols.
  - The application scenarios of network management protocols.

## Contents

1. Development History of Network Management
2. Functions of Network Management
3. Categories of Network Management Protocols
4. Application Scenarios of Network Management

## 1. Development History of Network Management

### Current Situation of Network Development

Diagram description: Four circular icons in a row labeled "Large," "Numerous," "Complex," and "High," each with a caption underneath: "Increasingly larger network scale," "More and more types of devices," "Growing complexity in network maintenance," and "Higher requirements for maintenance personnel," respectively.

- The rapid development of the Internet industry brings about great changes to networks, with multi-service convergence as the major trend in future network development. Network convergence requires management convergence, that is, the unified network management system is required to centrally manage multiple services and devices.

### Challenges Faced by Traditional Network Management

- Large network scale/Slow service provisioning/Low troubleshooting efficiency

Diagram description: Three panels. The first is a bar chart titled "Loss caused by faults," showing dollar-loss figures across industries (Media 0.09, Retail 0.63, Manufacturing 1.1, Telecom 1.6, Energy 2.0, Finance 2.8, and a further Finance figure of 6.48), sourced from Network Computing, the Meta Group, and Contingency Planning Research, all figures in U.S. dollars, with a caption stating system shutdown causes a loss of a million U.S. dollars per hour. The second panel shows three stick figures representing "Manual configuration delivery," "Manual configuration verification," and "Manual service provisioning," sourced from on-site survey data of the 2018 IO Summit, with a caption stating more than 70% of network management tasks are completed using the CLI. The third panel shows an iceberg graphic under the heading "Difficult to locate faults," where the visible tip represents that abnormal flows account for 3.65% of network-wide flows, 30% of which can be identified in traditional O&M, while the submerged 70% cannot be identified in traditional O&M; a caption states that on average it takes 76 minutes to locate a fault.

- As the new technologies such as artificial intelligence, big data, and cloud computing are developing rapidly, industries will undergo digital transformation in the next decade and enterprise services will become diversified during the implementation of digital transformation. Digitalization brings changes to network models, and the traditional network management mode can no longer meet the new requirements of digital services. To be specific, traditional network construction, management, and O&M methods cannot meet new network requirements that arise during digitalization.

### Trends in Network Management Development

Diagram description: Two panels side by side. The left panel, titled "Automated Management," shows a stopwatch icon labeled "Low" for the year 2019 and a stopwatch icon labeled "High" for the year 2022, connected by an arrow labeled "Level of automation." The right panel, titled "Intelligent O&M," shows a circular cycle around a "Big Data + AI" core with a person icon, with surrounding labels reading "Experience visualization/evaluation," "Exception identification/prediction," "Root cause locating/analysis," and "Troubleshooting/network optimization."

- The online network planning, deployment, optimization, and inspection tools significantly reduce the management workload, lowering the OPEX.
- Early warnings about network faults, faster fault rectification, lower service loss, higher fault identification rate.
- OPEX means operating expense, which is the sum of the maintenance cost, marketing expense, labor cost, and depreciation expense during the enterprise operations.
- In April 2019, a well-known consulting firm in the industry released a report about using AI and automation to improve network reliability. According to this report, 65% of the enterprises will have network automation technologies deployed on their campus networks by 2022. The proportion, however, is only 17% today.
- Automated management: Network management is just like domestic washing machines, which evolve from manual to semi-automated, then to fully automated and even intelligent washing today, making it possible for everyone to operate a complex machine and complete complex tasks. This is also true for network management. It starts with commands-based per-device configuration and management, then evolves to the graphical user interface-based management and control system, and finally to today's service language-based automatic network configuration. Among all the time an enterprise spends in network management, almost one third is invested in network planning and deployment. In the future, network automation will be implemented in two aspects:
  - Full-lifecycle automation: means whether tools can be used to implement automation in the full lifecycle covering network planning, deployment, policy provisioning, network status monitoring, maintenance, and management.

> **[Missing page 8 — content below this point on the original slide/notes is not present in this export.]**

## 2. Functions of Network Management

### What Is Network Management?

- Network management is a basic requirement of a network. Currently, users can manage a network using various protocols, tools, applications, or devices. The managed objects include hardware and software on the network.
- The purpose of network management is to ensure that a network runs properly by means of monitoring, testing, configuring, analyzing, evaluating, and controlling the software and hardware on the network.

Diagram description: A network topology showing a network management station connected through a switch to a hierarchy of devices: two firewalls/routers at the top connected to the Internet, below them two switches connected to each other, and below those four access switches. Red annotations show the network management station checking device running status and receiving feedback from the top devices, and an event triggering an alarm from one of the lower switches back to the management station. A legend distinguishes active links (solid black) from standby links (grey).

### Typical Architecture of Network Management Systems

- Network management systems usually have the same basic architecture, which consists of two key elements:
  - Managing device, also called a network management station
  - Managed device, also called an agent

Diagram description: Left side shows three users (User 1, User 2, User 3) connected to a managing device, which connects via network management protocols (SNMP/NETCONF/Telemetry) to a cloud of managed devices arranged in a small mesh network. Right side shows an expanded block diagram of a "Network management station" containing a "Display" block and a "Network management application" block, connected via network management protocols (dashed arrows) to three "Agent" blocks, each residing on a separate "Managed device."

### Four Models of Network Management

- OSI network management comprises four models:
  - Organization model: describes the components of a network management system, their functions, and their infrastructure.
  - Information model: specifies the information database used to describe managed objects and their relationships.
  - Communication model: describes the way information is exchanged between a manager and a managed object.
  - Functional model: comprises five functional areas for network management, namely, configuration management, performance management, fault management, security management, and accounting management.

- The organization model defines the terms manager, agent, and managed object. It describes the components of a network management system, their functions, and their basic architecture.
- The information model is related to the relationship and storage of management information. It specifies the information database that describes the managed objects and their relationships. The structure of management information (SMI) defines the syntax and semantics of the management information stored in the Management Information Base (MIB). Both the agent process and manager process use the MIB to exchange and store management information.
- The communication model deals with the way information is exchanged between agents and managers and between managers. The communication model contains three key elements: transport protocol, application protocol, and the actual message to be transmitted.
- The functional model defines five functional areas for network management: configuration management, performance management, fault management, security management, and accounting management.

### Five Functions of Network Management

Diagram description: Five circular icons in a row, labeled "Configuration management," "Performance management," "Fault management," "Security management," and "Accounting management."

- Network O&M mainly involves the following functions:
  - Configuration: Many management protocols include the capability of performing actions on managed projects.
  - Performance: The idea here is to get the data about the behavior of the platform, from which we can infer its performance.
  - Fault: In this area, the idea is to have programs for detecting faults and solutions to reporting faults.

- OSI defines five functional models for network management:
- Configuration management:
  - Configuration management is concerned with initializing a network, provisioning the network resources and services, and monitoring and controlling the network. More specifically, the responsibilities of configuration management include setting, maintaining, adding, and updating the relationship among components and the status of the components during network operation.
  - Configuration management consists of both device configuration and network configuration. Device configuration can be performed either locally or remotely. Automated network configuration, such as Dynamic Host Configuration Protocol (DHCP) and Domain Name System (DNS), plays a key role in network management.
- Performance management:
  - Performance management is concerned with evaluating and reporting the behavior and the effectiveness of the managed network objects. A network monitoring system can measure and display the status of the network, such as collecting statistics about the traffic volume, network availability, response time, and throughput.

> **[Missing page 14 — the notes describing Fault management (continued), Security management, and Accounting management are not present in this export. Only the icon labels for these functions appear in the diagram above.]**

## 3. Categories of Network Management Protocols

### Network Management Overview

Diagram description: A flow diagram showing three categories of protocols feeding into two management outcomes. On the left, three labeled boxes numbered 1, 2, and 3: "Configuration management protocols," "Performance management protocols," and "Fault management protocols." The performance and fault management protocol boxes both feed into an intermediate box labeled "Network monitoring protocols." Arrows lead from the configuration management protocols box (1) to a "Network Configuration Management" box listing CLI (Telnet/SSH), SNMP, and NETCONF, and from the network monitoring protocols box to a "Network Monitoring Management" box listing CLI (Telnet/SSH), SNMP, NETCONF, NetStream, sFlow, Telemetry, Syslog, LLDP, and Mirroring.

- The command-line interface (CLI) supports both network configuration management and network monitoring management.
- The Set function of the Simple Network Management Protocol (SNMP) supports network configuration management, and its Trap function supports network monitoring management.
- The Edit function of the Network Configuration Protocol (NETCONF) supports network configuration management, and its Get function supports network monitoring management.

### CLI (Telnet/SSH)

*Supports network configuration management and network monitoring management.*

- The CLI is the most widely used user interface before the graphical user interface is popularized. When using the CLI, users input instructions using a keyboard, rather than using a mouse. A device will then execute the instructions they receive.

Diagram description: Two side-by-side protocol stacks. On the left, a network administrator connects to a managed device over Telnet, with a callout labeled "Plain text" above a packet structure showing ETH | IP | TCP 23 | Telnet Data. On the right, a network administrator connects to a managed device over SSH, with callouts labeled "Information security assurance" and "Authentication" above a packet structure showing ETH | IP | SSH 22 | SSH Data.

- A network administrator can use the CLI to configure devices and monitor networks, which are simple and convenient. However, automation tools must be used to perform batch configuration, once large-scale deployment is needed.
- Telnet is an abbreviation of the words "telecom (Telecommunications) networks".
  - Telnet uses the dedicated TCP port 23. Telnet is not a secure communications protocol and it transmits data, including passwords, in plain text over the network or Internet.
  - Telnet does not use any authentication policies or data encryption techniques.
- SSH (Secure Shell)
  - SSH uses the dedicated TCP port 22. It is a secure protocol that transmits encrypted data over the network or Internet. Once encrypted, it is extremely difficult to extract and read the data.
  - SSH uses public keys to authenticate access users, which provides higher security.
- Telnet and SSH are two methods for remotely managing devices, among which SSH is more secure. Therefore, SSH is usually a required protocol on the networks.

### SNMP

*Supports network configuration management and network monitoring management.*

- SNMP is a standardized network management protocol widely used on TCP/IP networks. It uses a central computer — known as a network management station (NMS) — that runs network management software to manage network elements. Three SNMP versions are available: SNMPv1, SNMPv2c, and SNMPv3. Users can select one or multiple versions if needed.

Diagram description: Three panels. "3 Roles" shows icons for Network management station, Agent, and Managed device. "2 Types of Data Organization" shows a tree structure labeled OID feeding into a database labeled MIB. "2 Typical Management Modes" shows a management station exchanging Query/Modify requests and Query/Modify replies with a device, and separately a device sending traps to the management station (with an alarm icon on the device).

- NMS: The NMS sends various query packets to and receives traps from managed devices.
- Managed devices refer to the devices that are managed by the NMS.
- An agent is a process residing on a managed device. An agent provides the following functions:
  - Receives and parses query packets from the NMS.
  - Reads or writes management variables based on the packet type, generates response packets, and sends the response packets to the NMS.
  - Proactively generates a trap when an event occurs (for example, when a port goes up or down, the STP topology changes, or the OSPF neighbor relationship is down) based on the trap triggering conditions defined by each protocol module, and reports the event to the NMS.
- The Management Information Base (MIB) is a database that specifies the variables maintained by managed devices, that is, the information that can be queried and set by the agents. The MIB defines a series of attributes for managed devices, including the name, status, access permission, and data type of the managed objects.
- Object identifier (OID): A MIB uses a tree structure, with each node in the tree indicating a managed object. An object can be uniquely identified by a path, known as the OID, that starts from the root of the tree.

### Application Scenarios of SNMP

Diagram description: A network topology with an NMS connected through a switch to a hierarchy of managed devices (two top-level firewalls/routers connected to the Internet, two switches below them, and four access switches at the bottom). Red arrows show a Set/Get Request and Set/Get Response exchanged between the NMS and the top managed device, and a "Trigger a trap" arrow from one of the lower access switches back toward the NMS. A legend distinguishes active links (solid black) from standby links (grey).

Configure the SNMP management program in the NMS, enable the agent program on the managed device, and configure the SNMP protocol on the network.

After SNMP is configured:
- The NMS can obtain or change device information through the agent to implement remote monitoring and management.
- The agent can report device status to the NMS in a timely manner.

### NETCONF

*Supports network configuration management and network monitoring management.*

- As an XML-based network configuration protocol, NETCONF is designed to automate network configuration in a programmable manner, so as to simplify and accelerate network service deployment.

Diagram description: "2 Roles" panel shows a managed device labeled "NETCONF client" and a management station labeled "NETCONF server." "1 Typical Management Mode" panel shows a management station exchanging NETCONF messages over SSH through an IP network to multiple managed devices.

- NETCONF uses SSH to secure transmission and uses Remote Procedure Calls (RPCs) to implement communication between the client and server.
- NETCONF messages are presented as XML documents.

### Application Scenarios of NETCONF

Diagram description: An iMaster NCE box connected as a NETCONF server, communicating over NETCONF through a network cloud down to a device (acting as NETCONF client) and three additional devices (Device 1, Device 2, Device 3).

Advantages of NETCONF:
- Is a standardized protocol that features structured data and is highly scalable.
- Uses a layered framework and supports a wide range of operations.
- Supports multiple configuration databases, through which operation verification and rollback can be implemented based on a transaction mechanism.
- Allows configuration data and status data to be obtained separately, and allows the data to be compared between devices.
- Provides network-level service configuration capabilities and supports network-level configuration transactions.
- Supports configuration backup and restoration.

- NETCONF provides a set of mechanism for managing network devices. With this mechanism, users can add, modify, delete, back up, restore, lock, and unlock network device configurations. In addition, NETCONF provides transaction and session operation functions to obtain network device configuration and status information.

### NetStream

*Supports network monitoring management.*

- NetStream is a technology that collects statistics about and analyzes service traffic on a network based on network flow information. NetStream can be deployed at the access, aggregation, and core layers of a network.
- NetStream can collect statistics for IP packets (UDP, TCP, ICMP packets) and MPLS packets.

Diagram description: "3 Roles" panel shows icons for NDE (NetStream Data Exporter), NSC (NetStream Collector), and NDA (NetStream Data Analyzer). "1 Typical Management Mode" panel shows a flow of statistics records (versions V5/v8/v9) moving from an NDE to an NSC, and then onward to an NDA.

- A typical NetStream system has three components: NetStream data exporter (NDE), NetStream collector (NSC), and NetStream data analyzer (NDA).
  - NDE: An NDE is a device configured with NetStream functions. It analyzes and processes network flows, extracts flows that meet conditions for statistics collection, and exports the statistics to the NDA. The NDE can perform operations (such as aggregation) on the statistics before exporting them to the NDA.
  - NSC: An NSC is a program running in Windows or UNIX that parses packets from NDEs and saves the statistics to a database for the NDA to parse. It can collect, filter, and aggregate data exported from multiple NDEs.
  - NDA: An NDA is a network traffic analysis tool that extracts statistics from the NSC, processes the statistics, and generates reports. The reports provide reference for various services, such as traffic-based charging, network planning, and attack monitoring. Typically, the NDA provides a graphical user interface for users to easily obtain, display, and analyze collected data.
- Flow statistics can be exported in two modes:
  - Original flow statistics export: After the aging timer expires, the statistics of each flow are exported to the NSC. The advantage of this mode is that the NSC can obtain the detailed statistics of all flows.
  - Aggregation flow statistics export: The device summarizes the original flows with the same aggregation keywords to obtain statistics on the aggregation flow. In this way, originals flows are aggregated before they are exported, significantly saving network bandwidth.

### Application Scenarios of NetStream

Diagram description: A network topology showing a NetStream server (containing NSC/NDA) connected to a managed device configured as an NDE at interface GE0/0/1, which sits below a hierarchy of switches/firewalls connecting to the Internet, and below the NDE additional managed switches. A "Data flow" label and a "Full buffer/flow aging" callout point from the NDE toward the NetStream server, with a Top N report icon shown at the NetStream server end.

How NetStream works:
- The device configured with NetStream (that is, NDE) periodically sends collected flow statistics to the NSC.
- The NSC processes the flow statistics and sends them to the NDA.
- The NDA analyzes the traffic statistics and provides them for use in scenarios such as accounting and network planning.

- In real networking, the NSC and NDA are typically integrated on one NetStream server. The NDE samples packets to obtain outbound traffic information on GE0/0/1 and creates NetStream flows based on certain conditions. When the NetStream buffer is full or a NetStream flow is aged out, the NDE encapsulates statistics in NetStream packets and sends the packets to the NetStream server. The NetStream server analyzes and processes the NetStream packets, and then displays the analysis result.
- Implementation and limitations of traditional traffic statistics collection methods:
  - IP packet-based statistics collection: The collected statistics are simple and include only limited types of information.
  - ACLs: A large number of ACLs are required and statistics about mismatching packets cannot be collected.
  - SNMP: The protocol has limited functions. It collects statistics through continuous polling, wasting CPU and network resources.
  - Port mirroring: This function has high cost and occupies one port of the device. Statistics cannot be collected on ports that do not support mirroring.
  - Physical-layer replication: The cost is high, and dedicated hardware devices need to be purchased.

### sFlow

*Supports network monitoring management.*

- Sampled flow (sFlow) is a network traffic monitoring technology based on packet sampling.
- The sFlow system involves an sFlow agent embedded in a device and a remote sFlow collector. The sFlow agent obtains traffic statistics on an interface using sampling, encapsulates them into sFlow packets, and sends the packets to the designated sFlow collector. The sFlow collector analyzes the sFlow packets and displays the traffic statistics.

Diagram description: "2 Roles" panel shows icons for sFlow collector and sFlow agent. "1 Typical Management Mode" panel shows an sFlow Datagram packet structure (UDP Header | IP Header | Ethernet Header) sent from an sFlow Agent (which internally performs Flow sampling and Counter sampling) to an sFlow collector.

- With flow sampling, an sFlow agent samples packets in the specified direction on the specified interface based on a sampling rate, and analyzes the packets to obtain information about packet data content. Flow sampling focuses on traffic details, facilitating monitoring and analysis of traffic behaviors on the network.
  - With flow sampling, an sFlow agent can obtain the entire packet or part of the packet header.
- With counter sampling, an sFlow agent periodically obtains traffic statistics on an interface. In contrast with flow sampling, counter sampling focuses on traffic statistics on an interface rather than traffic details.

### Application Scenarios of sFlow

Diagram description: A network topology showing an sFlow collector connected to a managed device configured as an sFlow agent, which sits below a hierarchy of switches/firewalls connecting to the Internet, and below the sFlow agent additional managed switches. A "Data flow" label points from the agent toward the collector, with a Top N report icon shown at the collector end.

Enterprise network users often have explicit requirements for traffic on device interfaces and the overall running status of devices. Enterprises require a traffic monitoring technique that samples packets on device interfaces to promptly find abnormal traffic and the source of attack traffic, so that they can quickly rectify faults to ensure networks can run properly. sFlow focuses on traffic on interfaces, traffic forwarding, and the overall device status, so it can be used to monitor and locate network exceptions, especially on enterprise networks.

- As shown in the figure, an sFlow agent is connected to a remote sFlow collector so that traffic statistics can be collected and analyzed based on interfaces.
- NetStream is also a technology that collects and analyzes traffic statistics. In NetStream, a network device preliminarily collects and analyzes traffic statistics and then saves the statistics to a cache. The network device exports the statistics when they expire or when the cache overflows. Different from NetStream, sFlow does not require a cache, because a network device only samples packets and a remote collector will collect and analyze traffic statistics.
- Therefore, sFlow has the following advantages over NetStream:
  - Fewer resources and lower costs: sFlow does not require a cache, so it uses only a small number of resources on network devices, lowering costs.
  - Flexible collector deployment: The collector can be deployed flexibly, enabling traffic statistics to be collected and analyzed based on various traffic characteristics.

### Telemetry

*Supports network monitoring management.*

- Telemetry is also called network Telemetry. It is used to monitor networks, including packet check and analysis, intrusion and attack detection, intelligent data collection, and application performance management.
- Advantages:
  - Supports multiple implementation modes, meeting diversified user requirements.
  - Collects a wide variety of data with high precision to fully reflect network status.
  - Continuously reports data with only one-time data subscription.
  - Locates faults rapidly and accurately.

Diagram description: "3 Roles" panel shows an Analyzer connected to both a Collector and a Controller. Below, a box labeled "Network devices" connects upward to the Collector via a "Subsecond-level, Upload data using Telemetry" arrow, and downward from the Controller via a "Deliver configurations using NETCONF" arrow. Labeled "1 Typical Management Mode."

- With the popularization of networks and emergence of new technologies, the network scale is growing, network deployment is increasingly complex, and users have higher requirements on service quality. To meet user requirements, network O&M must be more refined and intelligent. Network O&M are, however, faced with the following challenges:
  - Ultra-large scale: A large number of devices need to be managed and massive amount of information is monitored.
  - Quick fault locating: Users want faults to be located within seconds or even subseconds on complex networks.
  - Refined monitoring: Various types of data needs to be monitored at a finer granularity to reflect the network status completely and accurately. With the monitoring information, possible faults can be predicted, providing a sound foundation for network optimization. Network O&M involves monitoring not only traffic statistics on interfaces, packet loss on each flow, CPU usage, and memory usage, but also the latency and jitter of each flow, latency of each packet on its transmission path, and buffer usage on each device.
- The collector, analyzer, and controller are components of the network management system.
  - The collector receives and stores monitoring data reported by network devices.
  - The analyzer analyzes the monitoring data received by the collector and processes the data, for example, displays the data on the graphical user interface.
  - The controller uses NETCONF to deliver configurations to devices, so as to manage these devices. To be specific, the controller can deliver configurations to network devices and adjust the forwarding behavior of the network devices based on the data provided by the analyzer. It can also control which data network devices need to sample and report.

### Application Scenarios of Telemetry

Diagram description: A network topology showing a Collector/Analyzer/Controller station connected to a managed device (labeled "Network device") at interface GE0/0/1, which sits below a hierarchy of switches/firewalls connecting to the Internet, and below the network device additional managed switches. A "Report information using gRPC" callout and "Data flow" label point from the network device toward the station, with a Top N report icon shown at the station end.

The gRPC-based Telemetry technology can collect traffic statistics on interfaces, CPU usage, and alarm data of devices, encode the data using Protocol Buffers, and report the data to the collector in real time for storage.

| | Telemetry | SNMP Get | SNMP Trap | CLI | Syslog |
|---|---|---|---|---|---|
| Working mode | Push | Pull | Push | Pull | Push |
| Precision | Subsecond-level | Minute-level | Second-level | Minute-level | Second-level |

- Google Remote Procedure Call (gRPC) is a Google-developed open-source high performance RPC framework that uses HTTP/2 as its underlying transport protocol. It provides multiple methods for configuring and managing network devices that are available in multiple programming languages.
- Traditional network monitoring methods (such as SNMP, CLI, and Syslog) cannot meet network O&M requirements.
  - SNMP and CLI obtain data in pull mode. That is, data is obtained from devices using requests. This method limits the number of network devices that can be monitored, and data cannot be quickly obtained using this method.
  - SNMP Trap and Syslog obtain data in push mode. That is, devices proactively report data to the monitoring device. However, they only report events and alarms. The monitoring data is limited and cannot accurately reflect the actual network status.
- Telemetry is a remote data collection technology that monitors device performance and faults. It obtains abundant monitoring data in push mode in a timely manner. The data helps quickly locate network faults and resolve the preceding network O&M problems.

### Syslog

*Supports network monitoring management.*

- System log (Syslog) is an industry standards-compliant protocol for recording device logs. It logs events that occur at any time on UNIX systems, routers, switches, and other network devices. These logs provide administrators with insights into the system status.
- The Syslog protocol offers a mechanism that allows a host to transmit event messages to a receiver host, known as the Syslog server, over an IP network.

Diagram description: "3 Roles" panel shows icons for Collector, Relay, and Sender. "1 Typical Management Mode" panel shows a Syslog Server (running Syslogd) receiving a syslog Datagram packet structure (UDP Header | IP Header | Ethernet Header) that travels from a Sender through a Relay to the Syslog server.

- While this protocol was originally developed on the University of California Berkeley Software Distribution (BSD) TCP/IP system implementations, its value to operations and management has led it to be ported to many other operating systems as well as being embedded into many other networked devices. RFC 3164 and RFC 3195 provide general-purpose definitions for this protocol. The former describes Syslog messages transmitted over UDP, whereas the latter defines Syslog messages transmitted over TCP.
- Almost all network devices can use the Syslog protocol to transport logs to a remote Syslog server over UDP. The remote Syslog server must use syslogd to listen on UDP port 514, process local logs and logs received from external systems based on the configuration in the syslog.conf file, and write specified events to specific files.
- There are three roles in the Syslog system:
  - Sender: refers to the network element that generates Syslog messages.
  - Relay: refers to the network element or another device that forwards Syslog messages it receives.
  - Collector: refers to the Syslog server that does not forward Syslog messages it receives.

### Others — LLDP

*Supports network monitoring management.*

- The Link Layer Discovery Protocol (LLDP) is a Layer 2 protocol defined in the IEEE 802.1ab standard. LLDP allows a device to send local management information such as its management IP address, device ID, and port ID to its neighbors, which then save the received information in their management information bases (MIBs), so that the network management system (NMS) can search required information in the MIBs to determine link status.

Diagram description: "2 Roles" panel shows icons for Local device and Remote device. "2 Typical Management Modes" panel shows an "LLDP Packet" being exchanged in two scenarios: single-neighbor networking (two devices directly connected, each reporting to an NMS) and link aggregation networking (multiple devices bundled together, reporting to an NMS).

- LLDP is a neighbor discovery protocol. It defines a standard method for Ethernet network devices, such as switches, routers, and Wireless Local Area Network (WLAN) access points, to advertise their presence to neighboring devices and save discovery information about neighboring devices. Detailed device information, including device configurations and identification, can all be advertised using LLDP.
- LLDP data units (DUs) are transmitted periodically and reserved only for a certain period. IEEE has defined a recommended transmission interval of 30 seconds. After receiving an LLDP DU from a neighboring network device, an LLDP-enabled device stores the LLDP DU in an SNMP MIB defined by IEEE and keeps the LLDP DU valid within a certain period defined by the TTL carried in the LLDP DU.
- The protocol enables the NMS to accurately discover and simulate the physical network topology. LLDP-enabled devices transmit and receive advertisements, and they store the information advertised by their neighboring devices. The advertised information of a neighboring device includes its management address, device type, and port number, and this information helps determine the type of the neighboring device and the ports through which they connect to each other.
- Single-neighbor networking:
  - In single-neighbor networking mode, interfaces of two switches are directly connected and each interface has only one neighbor.
- Link aggregation networking:
  - In link aggregation networking, interfaces between switches are directly connected and bundled into a link aggregation group. Each interface in a link aggregation group has only one neighbor.

### Application Scenarios of LLDP

Diagram description: A network management station connected to a hierarchy of managed devices (two top-level switches connected via a link with an LLDP interface/LLDP DU exchange indicated, and below them three access switches, also connected via LLDP interfaces). A callout labeled "Network topology" with a small topology icon points from the discovered link information back to the network management station, alongside a label "Network management protocol packets."

- As shown in the figure on the left, switches are directly connected through a single link or an Eth-Trunk. The network management station is routable with the switches, and the network management protocol has been configured.
- The switches use LLDP to discover link-layer neighbor information and report the information to the NMS through a network management protocol, so that the NMS can display the network topology on its graphical user interface.

- Ethernet link aggregation, also called Eth-Trunk in short, bundles multiple physical links into a logical link to increase available link bandwidth.

### Others — Mirroring

*Supports network monitoring management.*

- Mirroring copies traffic on one or more specified sources to one or more destination ports for analysis. The specified sources are called mirrored sources, and the destination ports are called observing ports.

Diagram description: "3 Roles" panel shows icons for Mirrored port, Observing port, and Observing port group. "2 Typical Management Modes" panel shows two switch diagrams: one illustrating port mirroring, where all traffic on a mirrored port is copied to an observing port connected to a monitoring device, and one illustrating flow mirroring, where only traffic matching a traffic classification rule on a mirrored port is copied to an observing port connected to a monitoring device.

- During network maintenance, you may need to obtain and analyze packets in some circumstances. For example, if you detect suspected attack packets, you need to obtain and analyze the packets without affecting packet forwarding. The mirroring function copies packets on a mirrored port to an observing port for analysis by a monitoring device, without affecting packet processing on the mirrored port. This function facilitates network monitoring and troubleshooting.
- Basic concepts:
  - A mirrored port is a monitored port, on which all the packets or packets matching traffic classification rules are copied to an observing port.
  - An observing port is connected to a monitoring device and transmits the packets copied from a mirrored port.
  - An observing port group is a group of ports connected to multiple monitoring devices. Packets mirrored to an observing port group are copied to all the member ports in the observing port group.
- Port mirroring: enables a device to copy the packets passing through a mirrored port and send them to a specified observing port for analysis and monitoring.
- Flow mirroring: enables a device to copy the specified packets passing through a mirrored port to an observing port for analysis and monitoring. In flow mirroring, a traffic policy containing the mirroring behavior is applied to a mirrored port. If the packets passing through the mirrored port match the traffic classification rule, they are copied to the observing port.

### Application Scenarios of Mirroring

Diagram description: Left side shows a simple switch with PC2 on GE0/0/1, PC1 on GE0/0/2, and a Monitoring PC on GE0/0/3, with a red "Mirroring" arrow from GE0/0/2 to GE0/0/3. Right side shows two switch diagrams: one for flow mirroring, where GE0/0/2 (mirrored port, with a traffic classification icon) copies matching traffic to GE0/0/3 (observing port) connected to a Monitoring PC; and one for port mirroring, where GE0/0/2 (mirrored port) copies all traffic to GE0/0/3 (observing port) connected to a Monitoring PC.

- In some scenarios, we may need to monitor incoming or outgoing packets on a specific interface of a switch or analyze specific traffic. For example, in the figure, the interface GE0/0/2 carries a large amount of traffic, and when a network fault occurs, we need to analyze the packets sent and received by this interface so as to locate the fault. To do so, we can connect a PC to interface GE0/0/3, install protocol analysis software on the PC, and deploy port mirroring to mirror incoming and outgoing traffic of GE0/0/2 to GE0/0/3. Then, all we need to do is using the protocol analysis software on the PC to view packets.
- It should be noted that without port mirroring, packets will not be sent to GE0/0/3 unless the destination of the packets is this interface. Therefore, port mirroring is by essence copying the traffic of a specific port to a monitoring port.

## 4. Application Scenarios of Network Management

### Typical Application Scenarios of Network Management

Diagram description: A "From" panel on the left labeled "NE-oriented management," showing a simple stacked hierarchy of OSS → Management → NE. An arrow points to a "To" panel on the right labeled "All-scenario full-lifecycle management," showing a Commercial application layer (ERP, Video conferencing, Office OS, Ad operations) connected via a Northbound API to an iMaster NCE Cloud platform containing Analysis, Management, and Control functions, flanked by "Automated network" and "Intelligent network" labels. The cloud platform connects downward via SNMP/NETCONF (configuration delivery) and via Telemetry/NetStream/sFlow (data reporting) to a network layer spanning DC, Campus, WAN, and Branch environments.

- With the rapid development of networks, digital transformation is gaining unprecedented importance, and network management is gradually shifting from NE-oriented management to scenario-oriented automation.
- The network management and control system is the evolution direction of autonomous networks and consists of the controller, analyzer, and manager.
- SNMP and NETCONF are used to deliver configurations, whereas Telemetry, NetStream, and sFlow are used to report data.

### What Is iMaster NCE?

Diagram description: A horizontal bar divided into three labeled sections, each with a cycle icon and a number. Section 1 (numbered 2): "Automated + Intelligent," described by "SDN-based automatic service configuration/deployment" and "AI-powered intelligent analysis/prediction/troubleshooting." Section 2 (numbered 3): "Manager + Controller + Analyzer," described by "Unified data base" and "Centralized detection/locating/processing." Section 3 (numbered 4): "Plan + Construct + Maintain + Optimize," described by "Full lifecycle management" and "Simulation/Verification/Monitoring/Optimization."

### iMaster NCE Product Architecture and Customer Benefits

Diagram description: A layered architecture diagram. At the top, "Cloud Platform & Applications" spanning Multi-Tenant, Multi-Service, and Multi-Industry. Below that, a "Design Studio" block sits beside a block containing "Scenario-based Apps" above three sub-blocks — Management, Control, and Analysis — which sit above a "Unified Cloud-based Platform" block, spanning Multi-Layer, Multi-Domain, and Multi-Vendor. At the bottom, "Network Infrastructure." To the right, four labeled customer-benefit callouts with icons:
- Automated network: Intent-driven, model-based, Multi-domain, multi-layer, and multi-vendor
- Intelligent network: Big data- and AI-powered predictive maintenance
- Agile system integration: Programmable design studio, Open REST APIs
- Cloud-based elastic expansion: Public and private cloud support, Elastic expansion & high reliability

### Quiz

1. (Multiple) What are the two key elements in the network management system? ( )
   - A. Managing device
   - B. Managed device
   - C. Agent
   - D. Network management protocol

2. (Multiple) Which of the following statements are true about basic network management functions? ( )
   - A. Configuration management
   - B. Performance management
   - C. Fault management
   - D. Security management
   - E. Accounting management

**Answers:**
1. AB
2. ABCDE

