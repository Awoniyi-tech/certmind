<!--
PAGE-GAP CHECK NOTES:
- VRRP deck (pages 1175–1208): COMPLETE, no gaps.
- DHCP deck (pages 1209–1243): Originally missing pages 1215, 1217, 1236.
  - Page 1215: user confirmed there is no content on this page (blank/transition page).
  - Page 1217: content supplied by user and inserted below (Discovery/Offer/Request/Acknowledgment stage detail under "DHCP Working Mechanism When a DHCP Client Connects to a Network for the First Time").
  - Page 1236: content supplied by user and inserted below (DHCP relay agent processing of the DHCP Offer message, under "Working Mechanism of DHCP Relay").
  This file is now considered COMPLETE based on user-supplied text for the two non-blank gaps.
-->

# VRRP Implementation and Configuration

## Foreword

- User terminals on a LAN usually use a default gateway to access an external network. If the default gateway fails, all user terminals' traffic to the external network will be interrupted. Multiple gateways can be deployed to prevent single points of failure. To this end, the conflict between multiple gateways must be resolved.
- The Virtual Router Redundancy Protocol (VRRP) can implement gateway backup and solve the conflict between multiple gateways, thus improving network reliability.
- This course describes the working mechanism, basic configuration, and typical application scenarios of VRRP on a network.

## Objectives

- On completion of this course, you will be able to:
  - Analyze problems faced by a single gateway on a LAN.
  - Explain the basic concepts and working mechanism of VRRP.
  - Describe the active/standby VRRP switchover process.
  - Perform basic VRRP configurations.

## Contents

1. Introduction to VRRP
2. VRRP Implementation
3. Typical Application Scenarios of VRRP
4. Basic VRRP Configurations

## 1. Introduction to VRRP

### Problems Faced by a Single Gateway

Diagram description: Two side-by-side topology diagrams. Left diagram: Internet connected to a single Router (IP 192.168.1.254/24), which connects to a Switch, which connects to three hosts — HostA (192.168.1.1/24), HostB (192.168.1.2/24), HostC (192.168.1.3/24) — each configured with gateway 192.168.1.254. Right diagram: identical topology, but the Router is marked with a red "X" (faulty) and a thought bubble asks "Is it feasible to configure multiple gateways to implement redundancy?" The caption below states: When the gateway (router) is faulty, the hosts that use the router as the gateway cannot communicate with the Internet.

### Overview of VRRP

- VRRP groups several routers into a virtual router. If one of routers fails, traffic can be switched to another router, ensuring service continuity and reliability.

Diagram description: Two side-by-side diagrams labeled "Physical network topology" and "Logical network topology." Physical topology: Internet connects to two routers R1 (GE0/0/0, 192.168.1.251/24) and R2 (GE0/0/0, 192.168.1.252/24), shown inside an oval labeled "VRRP" connecting them; both connect down to a Switch, which connects to PC1 (192.168.1.1/24), PC2 (192.168.1.2/24), PC3 (192.168.1.3/24), each with gateway 192.168.1.254. Logical topology: Internet connects to a single virtual router icon labeled "Virtual router / Virtual IP address: 192.168.1.254/24," which connects to the Switch and the same three PCs with the same gateway.

- VRRP sets up a virtual router on a LAN.
- In this example:
  - There are two routers on the LAN: R1 and R2. The IP addresses of R1 and R2 are 192.168.1.251/24 and 192.168.1.252/24, respectively.
  - Configure R1 and R2 to constitute a virtual router. The virtual router uses IP address 192.168.1.254.
  - All PCs use IP address 192.168.1.254 as the default gateway address.

### Basic VRRP Concepts (1)

Diagram description: Internet connects to R1 (GE0/0/0, 192.168.1.251/24) and R2 (GE0/0/0, 192.168.1.252/24), joined by a VRRP oval labeled "VRRP VRID: 1." Both connect to a Switch, which connects to PC1 (192.168.1.1/24), PC2 (192.168.1.2/24), PC3 (192.168.1.3/24), all with gateway 192.168.1.254.

- VRRP router: A router running VRRP, such as R1 and R2. VRRP is configured on interfaces of routers and works based on interfaces.
- Virtual router ID (VRID): A VRRP group consists of multiple routers (interfaces) that work together and are identified by the same VRID. Routers in the same VRRP group exchange VRRP packets and form a virtual router. Only one master router can exist in a VRRP group.

### Basic VRRP Concepts (2)

Diagram description: Same topology as above, but the VRRP oval is labeled "Virtual IP address: 192.168.1.254 / Virtual MAC address: 0000-5e00-0101."

- Virtual router: Each VRRP group forms a virtual router that is a logical device. A VRRP group forms only one virtual router.
- Virtual IP address and virtual MAC address: A virtual router has its own IP address and MAC address. The IP address is specified by the network administrator during VRRP configuration. A virtual router can have one or more addresses. Generally, this IP address is used as the gateway address. The format of the virtual MAC address is 0000-5e00-01xx, where xx is the VRID.

### Basic VRRP Concepts (3)

Diagram description: Same topology; R1 is labeled "Master" (Priority: 200) and R2 is labeled "Backup" (Priority: 100), connected via a "VRRP" oval, both connecting to the Switch and the same three PCs.

- Master router: The master router forwards packets in a VRRP group. In each VRRP group, only the master router responds to the ARP Request packet destined for the virtual IP address. The master router periodically sends VRRP packets to notify the backup router in the same VRRP group of its own status.
- Backup router: The backup router listens to the VRRP packets sent by the master router in real time and is ready to take over services of the master router.
- Priority: The priority value is used to elect the master and backup routers. The priority value ranges from 0 to 255. A larger value indicates a higher priority. If the values are the same, the interface IP addresses are compared. The interface with the largest IP address is preferred.

### VRRP Packet Format

- VRRP has only one packet type — Advertisement packets. Advertisement packets are multicast packets and can be transmitted only in the same broadcast domain. The destination multicast address of Advertisement packets is 224.0.0.18.

Diagram description: A layered packet structure: Ethernet Header → IP Header → VRRP Packet. Callouts show: Ethernet Header contains DMAC 01-00-5E-00-00-12 (multicast MAC address) and SMAC 00-00-5E-00-01-XX (virtual router MAC address). IP Header contains DIP 224.0.0.18 and SIP (IP address of the master router's port), Protocol 0x70 (VRRP protocol number: 112). VRRP Packet fields table: Ver, Type, Virtual Rtr ID, Priority, Count IP Addrs (row 1); Auth Type, Adver Int, Checksum (row 2); IP Address (1) ... IP Address (n); Authentication Data (1); Authentication Data (2).

- Fields in a VRRP Advertisement packet:
  - Ver: VRRP has two versions. VRRPv2 applies only to IPv4 networks, and VRRPv3 applies to both IPv4 and IPv6 networks.
  - Virtual Rtr ID: Virtual router ID associated with the packet.
  - Priority: Priority of the VRRP router that sends the VRRP packet.
  - Count IP Addrs: Number of virtual IP addresses contained in the VRRP packet.
  - Auth Type: VRRP supports non-authentication, plain-text password authentication, and MD5 authentication, corresponding to values 0, 1, and 2, respectively.
  - Adver Int: Interval for sending VRRP Advertisement packets. The default value is 1s.
  - IP Address: Virtual IP address of the associated virtual router. Multiple IP addresses can be configured.
  - Authentication Data: Password required for authentication.

### VRRP Timers

- VRRP defines two timers:
  - ADVER_INTERVAL timer: specifies the interval at which the master router sends VRRP Advertisement packets. The default value is 1s.
  - MASTER_DOWN timer: indicates that the backup router preempts the Master state after the MASTER_DOWN timer expires. The MASTER_DOWN timer is calculated as follows:
    - MASTER_DOWN = (3*ADVER_INTERVAL) + Skew_time (offset time)
    - Skew_Time = (256 – Priority)/256

## 2. VRRP Implementation

### VRRP State Machine

- The VRRP state machine has three states: Initialize, Master, and Backup.

Diagram description: A state diagram with three states: Initialize (top), Master (bottom-left), Backup (bottom-right). From Initialize, an arrow to Backup is labeled "Receive the startup event with the priority lower than 255"; an arrow to Master is labeled "Receive the startup event with the priority of 255." Arrows back to Initialize from both Master and Backup are labeled "Receive the shutdown message." Between Master and Backup, an arrow from Backup to Master is labeled "The MASTER_DOWN timer expires, or a VRRP Advertisement packet with the priority of 0 or a VRRP Advertisement packet with a priority lower than the local priority is received." An arrow from Master to Backup is labeled "Receive a packet with a priority higher than the local priority."

- A startup event can be automatically triggered by the system after VRRP is configured or triggered by the change of the lower-layer link from unavailable to available on the interface configured with VRRP.

### VRRP States

**Device in Master State**

1. Sends a VRRP Advertisement packet each time the ADVER_INTERVAL timer expires.
2. Uses the virtual MAC address to respond to ARP Request packets destined for the virtual IP address.
3. Forwards IP packets sent to the virtual MAC address.
4. Allows a virtual IP address to be pinged by default.
5. When multiple devices are in Master state, they compare their IP addresses in received packets with the same priority. If the IP address in the packet is greater than the local IP address, the device switches to the Backup state. If the IP address in the packet is less than or equal to the local IP address, the device remains in the Master state.

**Device in Backup State**

1. Receives VRRP Advertisement packets from the master router and checks whether the master router is working properly based on information in the packets.
2. Does not respond to an ARP Request packet carrying a virtual IP address.
3. Discards IP packets sent to the virtual MAC address.
4. Discards IP packets sent to the virtual IP address.
5. Resets the MASTER_DOWN timer but does not compare IP addresses if it receives a VRRP Advertisement packet carrying a VRRP priority higher than or equal to the local VRRP priority.

### VRRP Master/Backup Election (1)

Diagram description: Internet connects to R1 (GE0/0/0, 192.168.1.251/24, Priority: 200, labeled "Master") and R2 (GE0/0/0, 192.168.1.252/24, Priority: 100, labeled "Backup"), joined via a VRRP oval; both connect to a Switch, which connects to PC1, PC2, PC3 (same as before). Numbered callouts (1–4) trace the election sequence, with a dashed arrow showing a Gratuitous ARP packet sent from R1 down to the Switch/PCs.

Master/Backup election when VRRP priorities are different:
1. The VRRP priority of R1's interface is 200, and that of R2's interface is 100. When the two devices are initialized, they both switch to the Backup state.
2. R1 and R2 switch from the Backup state to the Master state after the MASTER_DOWN timer expires. Therefore, R1 switches to the Master state faster than R2.
3. R1 and R2 send VRRP packets to each other to elect the master. The router with a higher priority is elected as the master, so R1 is elected as the master.
4. After R1 is elected as the master, it immediately sends gratuitous ARP packets to advertise the virtual MAC address to the connected devices and hosts.

- If a VRRP-enabled device in Initialize state receives an interface Up message and its priority is lower than 255, it switches to the Backup state. The device switches to the Master state when the MASTER_DOWN timer expires.
- If the device with a higher priority and the device with a lower priority start in sequence, the device with a higher priority enters the Master state first. After receiving a VRRP Advertisement packet with a higher priority, the device with a lower priority remains in Backup state.
- If the device with a lower priority and the device with a higher priority start in sequence, the device with a lower priority switches from the Backup state to the Master state first. After receiving the VRRP Advertisement packet with a lower priority, the device with a higher priority switches to the Master state.

### VRRP Master/Backup Election (2)

Diagram description: Same topology, but both R1 and R2 GE0/0/0 interfaces have Priority: 200. R1 is labeled "Backup" and R2 is labeled "Master." A dashed Gratuitous ARP arrow now originates from R2.

Master/Backup election when VRRP priorities are the same:
1. The VRRP priorities of GE0/0/0 interfaces on R1 and R2 are both 200. When the two devices are initialized, they both switch to the Backup state.
2. Because the priorities of R1 and R2 are the same, R1 and R2 switch from the Backup state to the Master state after the MASTER_DOWN timer expires.
3. R1 and R2 exchange VRRP packets with the same priority. R1 and R2 compare their interface IP addresses to select the master. Because the interface IP address of R2 is greater than that of R1, R2 is selected as the master.
4. After R2 is elected as the master, it immediately sends gratuitous ARP packets to advertise the virtual MAC address to the connected devices and hosts.

(Same three general election-behavior bullets as above apply here as well: initial priority-based switch to Backup, higher-priority-starts-first behavior, and lower-priority-starts-first behavior.)

### VRRP Master/Backup Election (3)

Diagram description: Internet connects to R1 (GE0/0/0, 192.168.1.254/24, labeled "Master") and R2 (GE0/0/0, 192.168.1.253/24, labeled "Backup"), both connecting to a Switch and the same three PCs. Callout boxes show: R1 — VRRP VRID: 1, Priority: 100; R2 — VRRP VRID: 1, Priority: 100.

- When a router interface is configured as the VRRP IP address owner (the interface IP address is the same as the virtual IP address), the router can directly switch to the Master state without waiting for any timer to expire.

Master/Backup election process when a device interface is configured as the IP address owner:
1. The VRRP priorities of GE0/0/0 interfaces on R1 and R2 use the default value — 100. However, the IP address of GE0/0/0 on R1 is the same as the virtual IP address.
2. R1's GE0/0/0 directly switches to the Master state, and R1 becomes the master.

- In most cases, the interface IP address of a VRRP router does not overlap with the IP address of a virtual router. That is, an independent IP address is planned for the virtual router instead of the interface IP address of a router. There is also an exception. For example, if IP addresses are insufficient on some networks, the interface IP address of a router may be used as the IP address of the virtual router. In this case, the router becomes the master.
- The priority of a VRRP-enabled interface cannot be manually set to 255. When the IP address of an interface is configured as the IP address owner, the priority of the interface automatically changes to 255.

### VRRP Active/Standby Switchover

Diagram description: Two side-by-side scenario diagrams. Left ("The Master Is Deleted from the VRRP Group"): R1 (labeled Master, shown deleted from the VRRP group — e.g., VRRP config removed from the interface) sends a VRRP packet with priority = 0 to R2 (labeled "Backup → Master"), both connected to Switch and PC1/PC2/PC3. Caption: "Switching time = Skew_time." Right ("The Master or Link Fails"): R1 (labeled Master) is marked with a red X because VRRP packets cannot reach R2 due to a link fault; R2 (labeled "Backup → Master"). Caption: "Switching time = 3*ADVER_INTERVAL + Skew_time."

- If the master gives up the master role (for example, the master is deleted from the VRRP group), it sends VRRP Advertisement packets carrying a priority of 0 to the backups. Without waiting for the MASTER_DOWN timer to expire, the backup router with the highest priority switches to the Master state after a specified switching time. This switching time is called Skew_Time.
- If the master cannot send VRRP Advertisement packets due to network faults, the backups cannot learn the running status of the master immediately. In this situation, the backup router with the highest priority switches to the Master state after the MASTER_DOWN timer expires.

### VRRP Active/Standby Switchback (1)

Diagram description: Two side-by-side diagrams. Left: R1 (Master, Priority = 200) and R2 (Backup, Priority = 150) connected via VRRP, both connecting to Switch and PC1/PC2/PC3; a dashed blue arrow shows all user traffic flowing from PC2 through the Switch to R1 to the Internet. Right: R1 is marked with a red X (failed); R2 is now labeled "Master," and traffic flows through R2 instead.

1. In normal situations, the master forwards user packets. As shown in the figure, all user traffic reaches the Internet through R1.
2. When R1 fails, a new VRRP master/backup election is performed. As shown in the figure, R2 becomes the new master to forward user packets.

### VRRP Active/Standby Switchback (2)

Diagram description: Continuation showing R1 (Priority = 200) and R2 (Priority = 150) again connected via VRRP; traffic flows back through R1 after it recovers.

3. After R1 recovers, a new VRRP master/backup election is performed. R1 becomes the new master to forward user packets because R1 has a higher priority than R2.

VRRP preemption mode:
- Preemption mode (enabled by default): If the backup is enabled with the preemption function, it immediately switches to the Master state when detecting that the priority of the master is lower than its own priority.
- Non-preemption mode: If the preemption function is disabled on the backup, the backup remains in Backup state until the master fails even when detecting that the priority of the master is lower than that of the backup.

- When the preemption mode is enabled for a VRRP group and an active/standby switchover is performed, the switching time is as follows:
  - Switching time = 3*ADVER_INTERVAL + Skew_time + Delay_time
- In preemption mode, if the master is unstable or the network quality is poor, the VRRP group frequently switches, causing frequent update of ARP entries. To resolve this problem, you can set a preemption delay. After the preemption delay plus the value of the MASTER_INTERVAL timer, if the master becomes stable, a switchback is performed.

## 3. Typical Application Scenarios of VRRP

### VRRP Load Balancing

- In the scenario where multiple virtual routers (VRRP groups) are created and each physical router plays different roles in different VRRP groups, the virtual IP addresses of different virtual routers function as different intranet gateway addresses to implement load balancing.

Diagram description: Internet connects to R1 and R2, joined by a VRRP oval. Left callout box: "Vrid 1 Master — Virtual ip: 192.168.1.254, Priority: 200" and "Vrid 2 Backup — Virtual ip: 192.168.1.251, Priority: 100" (associated with R1). Right callout box: "Vrid 1 Backup — Virtual ip: 192.168.1.254, Priority: 100" and "Vrid 2 Master — Virtual ip: 192.168.1.251, Priority: 200" (associated with R2). Both routers connect to a Switch, which connects to PC1 (192.168.1.1/24, gateway 192.168.1.254), PC2 (192.168.1.2/24, gateway 192.168.1.254), and PC3 (192.168.1.3/24, gateway 192.168.1.251).

### VRRP Monitoring the Uplink Interface Status

Diagram description: Internet connects to two upstream routers, which connect to R1 (Master) and R2 (Backup) respectively, joined via a VRRP oval. R1's uplink interface GE0/0/1 is marked with a red X (fault). R1 and R2 both connect down to a Switch, which connects to PC1, PC2, PC3. A callout explains: "VRRP can monitor the status of the uplink interface. When a device detects a fault on the uplink interface or link, the device reduces the VRRP priority. This ensures that the backup with a normal uplink can be elected as the Master to forward packets."

- If association between VRRP and the uplink interface is not configured and the uplink interface or link of R1 (master) in the VRRP group fails, the VRRP group cannot detect the fault and the master cannot forward traffic. In this case, the active/standby switchover cannot be performed, causing a traffic blackhole.

### Association Between VRRP and BFD

- With association between VRRP and BFD enabled, when the backup detects a fault through BFD, the backup switches to the Master state immediately without waiting for the MASTER_DOWN timer to expire. This implements millisecond-level active/standby switchover.

Diagram description: Internet connects to R1 (GE0/0/0, 192.168.1.251/24, labeled Master) and R2 (GE0/0/0, 192.168.1.252/24, labeled Backup), joined by a VRRP oval containing a "BFD session" label. Both connect to a Switch, which connects to PC1, PC2, PC3.

- If the link between devices in a VRRP group fails, VRRP Advertisement packets cannot be exchanged to negotiate the Master or Backup state. A backup switches to the Master state when the MASTER_DOWN timer expires. During the waiting period, user traffic is still forwarded to the master, resulting in user traffic loss.
- A BFD session is established between the master and backup in a VRRP group and is bound to the VRRP group. BFD immediately detects communication faults in the VRRP group and instructs the VRRP group to perform an active/standby switchover, minimizing service interruptions.
- For association between VRRP and BFD, a VRRP group adjusts priorities according to the BFD session status and determines whether to perform an active/standby switchover according to the adjusted priorities. In practice, delayed preemption is configured on the master and immediate preemption is configured on the backup. When the backup detects that the BFD session goes Down, it increases its priority to be higher than the priority of the master to implement a fast switchover. After the fault is rectified and the BFD session goes Up, the new master reduces its priority and sends a VRRP Advertisement packet. After the delay, the new master becomes the backup again.

### Application of VRRP and MSTP

Diagram description: SW1 and SW2 at the top, connected to each other by a Trunk link and joined by a VRRP oval labeled "VRRP." Both SW1 and SW2 connect down via Trunk links to SW3. SW3 connects to HostA (192.168.1.1/24, gateway 192.168.1.254, VLAN 10) and HostB (192.168.2.1/24, gateway 192.168.2.254, VLAN 20). Callout boxes: SW1 — "Instance 1 vlan 10 primary / Instance 2 vlan 20 secondary" and "VRID 1: Master / VRID 2: Backup." SW2 — "Instance 1 vlan 10 secondary / Instance 2 vlan 20 primary" and "VRID 1: Backup / VRID 2: Master." Small icons indicate a blocked port in MSTI 1 and a blocked port in MSTI 2 on SW3's links. A callout box states: "MSTP prevents loops. VRRP active/standby switchover can be used."

- MSTP maps one or more VLANs to an MSTI. Multiple VLANs share a spanning tree, and MSTP implements load balancing.
- The VRRP-enabled gateway can be automatically switched based on network topology changes, improving network reliability.
- VRRP+MSTP can implement load balancing while ensuring network redundancy.

## 4. Basic VRRP Configurations

### Basic VRRP Configuration Commands (1)

1. Create a VRRP group and configure a virtual IP address for the VRRP group.
```
[interface-GigabitEthernet0/0/0] vrrp vrid virtual-router-id virtual-ip virtual-address
```
The virtual IP address of a VRRP group must be unique. Interfaces in the same VRRP group must use the same VRID.

2. Configure a priority for each device in the VRRP group.
```
[interface-GigabitEthernet0/0/0] vrrp vrid virtual-router-id priority priority-value
```
In most cases, the priority of the master is higher than that of the backup.

3. Configure a preemption delay for the VRRP group.
```
[interface-GigabitEthernet0/0/0] vrrp vrid virtual-router-id preempt-mode timer delay delay-value
```

4. Configure the VRRP group to work in non-preemption mode.
```
[interface-GigabitEthernet0/0/0] vrrp vrid virtual-router-id preempt-mode disable
```
By default, the preemption mode is enabled.

### Basic VRRP Configuration Commands (2)

5. Associate the VRRP group with an interface.
```
[interface-GigabitEthernet0/0/0] vrrp vrid virtual-router-id track interface interface-type interface-number [increased value-increased | reduced value-decreased]
```
You can configure the device to increase or decrease its priority when detecting an uplink interface or link fault. The IP address owner and Eth-Trunk member interfaces cannot be associated with VRRP.

6. Associate the VRRP group with a BFD session.
```
[interface-GigabitEthernet0/0/0] vrrp vrid virtual-router-id track bfd-session { bfd-session-id | session-name bfd-configure-name } [increased value-increased | reduced value-reduced]
```
If session-name bfd-configure-name is specified, the VRRP group can be associated only with static BFD sessions with automatically negotiated discriminators or static BFD session discriminators.
If bfd-session-id is specified, a VRRP group can be bound to only static BFD sessions.

### VRRP Configuration Example

Diagram description: Internet connects to R1 (GE0/0/0, 192.168.1.253/24, labeled "Master") and R2 (GE0/0/0, 192.168.1.252/24, labeled "Backup"), both connecting to a Switch, which connects to HostA (192.168.1.1/24, gateway 192.168.1.254), HostB (192.168.1.2/24, gateway 192.168.1.254), and HostC (192.168.1.3/24, gateway 192.168.1.254). R1 also has an uplink interface GE0/0/1 toward the Internet.

Requirements:
- R1 and R2 form a VRRP group. R1 is the master and R2 is the backup.
- The preemption mode is used when the master recovers. The preemption delay is 10 seconds.
- The master monitors the status of the uplink interface to implement automatic VRRP active/standby switchover.

**R1 configuration:**
```
[R1] interface GigabitEthernet0/0/0
[R1-GigabitEthernet0/0/0] ip address 192.168.1.253 24
[R1-GigabitEthernet0/0/0] vrrp vrid 1 virtual-ip 192.168.1.254
[R1-GigabitEthernet0/0/0] vrrp vrid 1 priority 120
[R1-GigabitEthernet0/0/0] vrrp vrid 1 preempt-mode timer delay 10
[R1-GigabitEthernet0/0/0] vrrp vrid 1 track interface GigabitEthernet0/0/1 reduced 30
```

**R2 configuration:**
```
[R2] interface GigabitEthernet0/0/0
[R2-GigabitEthernet0/0/0] ip address 192.168.1.252 24
[R2-GigabitEthernet0/0/0] vrrp vrid 1 virtual-ip 192.168.1.254
[R2-GigabitEthernet0/0/0] vrrp vrid 1 priority 110
```

### Verifying Basic VRRP Configurations

**R1 output:**
```
[R1]display vrrp
 GigabitEthernet0/0/0 | Virtual Router 1    # Set the VRID to 1.
  State : Master        The device is in Master state in the VRRP group.
  Virtual IP : 192.168.1.254
  Master IP : 192.168.1.253
  PriorityRun : 120      #Set the priority of the interface in the VRRP group to 120.
  PriorityConfig : 120
  MasterPriority : 120
  Preempt : YES   Delay Time : 10 s   # Enable the preemption mode and set the preemption delay to 10s.
  TimerRun : 1 s
  TimerConfig : 1 s
  Auth type : NONE
  Virtual MAC : 0000-5e00-0101
  Check TTL : YES
  Config type : normal-vrrp
  Track IF : GigabitEthernet0/0/1   Priority reduced : 30
  IF state : UP
```

**R2 output:**
```
[R2]display vrrp
 GigabitEthernet0/0/0 | Virtual Router 1
  State : Backup        # The device is in Backup state in the VRRP group.
  Virtual IP : 192.168.1.254
  Master IP : 192.168.1.253
  PriorityRun : 110      #The priority of the interface in the VRRP group is 110.
  PriorityConfig : 110
  MasterPriority : 120
  Preempt : YES   Delay Time : 0 s   # Enable the preemption mode and set the preemption delay to 0.
  TimerRun : 1 s
  TimerConfig : 1 s
  Auth type : NONE
  Virtual MAC : 0000-5e00-0101
  Check TTL : YES
  Config type : normal-vrrp
```

## Quiz

**1. (Multiple) Which of the following statements about the IP address in VRRP packets are true? ( )**

A. The source IP address is the IP address of an interface on the master.
B. The source IP address is the virtual IP address of the virtual router.
C. The destination IP address is a broadcast IP address.
D. The destination IP address is the IP address of the multicast group.

Answer: AD

**2. (Multiple) Which statements about VRRP timers are true? ( )**

A. The default interval for sending VRRP Advertisement packets is 1s. The interval for sending VRRP Advertisement packets associated with a VRRP router must be the same.
B. If the preemption delay is set to 4s, the backup becomes the new master if it does not receive a VRRP Advertisement packet from the master within 4 seconds.
C. Set the preemption delay to 4s and the interval for sending VRRP Advertisement packets to 2s. If the backup does not receive a VRRP Advertisement packet from the master within 6s, the backup becomes the new master.
D. On a busy network, set the preemption delay to a large value to prevent VRRP flapping.

Answer: AD

## Summary

- As an important reliability technology, VRRP is often used to implement gateway redundancy. VRRP improves network reliability and implements load balancing.
- The VRRP priority is used to control VRRP master/backup election, and active/standby switchover and switchback. To ensure network stability, the preemption delay mechanism is designed for VRRP to reduce network flapping.
- VRRP can monitor the status of uplink interfaces to detect network faults and associate with VRRP to ensure network reliability. VRRP can also be bound to BFD sessions to implement fast convergence. In addition, VRRP can be used together with MSTP, which is a common networking solution in campus networks.

---

# DHCP Implementation and Configuration

## Foreword

- As the network scale increases continuously and networks become increasingly complex, locations of terminals such as hosts, mobile phones, and tablets on networks change frequently. When a terminal accesses a network, the IP address, gateway address, and DNS server address need to be configured. Manually configuring these parameters for terminals is inefficient and inflexible.
- The Internet Engineering Task Force (IETF) released the Dynamic Host Configuration Protocol (DHCP) in 1993. DHCP implements automatic configuration of network parameters, reducing the configuration and maintenance costs of clients.
- This course describes the working mechanism, application scenarios, and basic configurations of DHCP.

## Objectives

- On completion of this course, you will be able to:
  - Describe DHCP implementation.
  - Describe DHCP address allocation rules.
  - Differentiate application scenarios of DHCP and DHCP relay.
  - Perform basic DHCP configurations.

## Contents

1. DHCP Background
2. DHCP Working Mechanism and Configuration
3. DHCP Relay Working Mechanism and Configuration

## 1. DHCP Background

### Problems in Manually Configuring Network Parameters

- Manually configuring network parameters has the following problems:
  - Inflexibility
  - Being vulnerable to errors
  - Low IP address usage
  - Heavy workload
  - High requirements on personnel skills

Diagram description: A cloud containing several computer icons, some highlighted (orange/blue) to indicate manually configured devices among many. An arrow labeled with "IP address, Network mask, Gateway address, DNS server address" points from a person icon (labeled "Manually configure network parameters") to a checklist box listing: Address planning, Address allocation, Address configuration, Address maintenance.

- When network parameters such as the host IP address, network mask, gateway address, and DNS server address are manually configured, complex operation processes such as address planning, allocation, configuration, and maintenance are required. As a result, address allocation is inflexible, the IP address resource usage is low, the configuration is error-prone due to heavy workload, and there are high requirements on personnel skills.

### Basic Concepts of DHCP

- The Dynamic Host Configuration Protocol (DHCP) dynamically assigns IP addresses to hosts and centrally manages host configurations.
- DHCP uses the client/server (C/S) communication mode. Protocol packets are exchanged in UDP mode. Port 67 (DHCP server) and port 68 (DHCP client) are used.
  - In normal cases, a client applies for configurations from the server.
  - The server returns the configuration such as the IP address allocated to a client.
- Compared with manual configuration, DHCP has the following advantages:
  - High efficiency
  - Strong flexibility
  - Easy management

Diagram description: A box containing icons for a laptop, phone, and printer/wireless device labeled "DHCP client," connected bidirectionally to a "DHCP server" icon, with arrows labeled "Request" (client to server) and "Response" (server to client).

- Network terminals, such as hosts, printers, laptops, mobile phones, and APs, function as DHCP clients to request network parameters from the DHCP server. The DHCP server dynamically allocates network parameters based on the requests from the DHCP clients.

## 2. DHCP Working Mechanism and Configuration

### DHCP Working Mechanism When a DHCP Client Connects to a Network for the First Time

Diagram description: A DHCP client and DHCP server separated by a "Layer 2 broadcast domain" cloud. Four numbered message exchanges are shown as arrows: (1) Discovery stage — the DHCP client broadcasts a DHCP Discover message across the broadcast domain to the server; (2) Offer stage — the DHCP server unicasts or broadcasts a DHCP Offer message back to the client; (3) Request stage — the DHCP client broadcasts a DHCP Request message; (4) Acknowledgment stage — the DHCP server unicasts a DHCP ACK message to the client.

- Discovery stage: The DHCP client detects DHCP servers.
  - The DHCP client broadcasts a DHCP Discover message to detect DHCP servers. The DHCP Discover message carries the client's MAC address, parameter request list, and broadcast flag.
- Offer stage: A DHCP server offers network parameters to the DHCP client.
  - A DHCP server selects an address pool on the same network segment as the IP address of the interface receiving the DHCP Discover message, and selects an idle IP address from the address pool. The DHCP server then sends a DHCP Offer message carrying the allocated IP address to the DHCP client.
- Request stage: The DHCP client selects an IP address.
  - If multiple DHCP servers reply with a DHCP Offer message to the DHCP client, the client accepts only the first received DHCP Offer message. The client then broadcasts a DHCP Request message carrying the selected DHCP server identifier and IP address.
- Acknowledgment stage: The DHCP server acknowledges the IP address offered to the client.
  - After receiving the DHCP ACK message, the DHCP client broadcasts a gratuitous ARP packet to detect whether other terminals on the network segment use the IP address allocated by the DHCP server.

- The DHCP Request message is broadcast so as to notify all the DHCP servers that the DHCP client has selected the IP address offered by a DHCP server. Then the other servers can allocate IP addresses to other clients.
- In the acknowledgement stage, IP address conflicts may occur in the following situations:
  - After receiving the DHCP Discover message, the DHCP server sends a ping packet to the client before assigning an IP address to the client. If the IP address can be pinged, the IP address is unavailable and another IP address is assigned to the client.
  - After the client successfully obtains an IP address, it immediately sends a gratuitous ARP packet. If a response packet is received, the client sends a DHCP Decline message to notify the DHCP server that the allocated IP address conflicts. The DHCP server then sets the IP address status to conflicting. Then, the client sends another DHCP Discover message to request a new IP address.

### DHCP Message Format (1)

Diagram description: A field-layout diagram of the DHCP message format, showing rows: Op | Htype | Hlen | Hops; Xid; Secs | Flags; Ciaddr; Yiaddr; Siaddr; Giaddr; Chaddr; Sname; File; Options(variable).

- Key fields:
  - Op (Operation Code): indicates the message type:
    - 1: DHCP Request message
    - 2: DHCP Reply message
  - Secs (seconds): is filled by a client, indicating the number of seconds elapsed since a client obtained or renewed an IP address. The default value is 3600s.
  - Flags: indicates the format of the response message sent by a server, which is requested by a client. Only the leftmost bit in this field is used, and the other 15 bits are set to 0. The leftmost bit specifies the mode a DHCP server uses to transmit a DHCP Offer message.

- Htype (hardware type): indicates the type of the hardware address.
- Hlen (hardware length): indicates the length of the hardware address.
- Hops: indicates the number of DHCP relay agents that DHCP messages pass through. This field is set to 0 by a client. The value of this field is increased by 1 each time the DHCP message passes a DHCP relay agent. This field is used to limit the number of DHCP relay agents that DHCP messages pass through.
- Xid: indicates a random number selected by a DHCP client to exchange messages with a DHCP server.
- Sname (server host name): indicates the name of the server from which a client obtains the configuration. This field is optional and is filled in by a DHCP server. This field must be filled in with a character string that ends with 0.
- File (file name): indicates the name of the configuration file for starting DHCP on the client. The DHCP server fills this field and delivers it together with the IP address to the client. This field is optional and must be filled in with a character string that ends with 0.

### DHCP Message Format (2)

Diagram description: Same DHCP message format field layout as above (Op | Htype | Hlen | Hops; Xid; Secs | Flags; Ciaddr; Yiaddr; Siaddr; Giaddr; Chaddr; Sname; File; Options(variable)).

- Key fields:
  - Yiaddr (your client ip address): indicates the IP address that a DHCP server allocates to client. The DHCP server fills this field into a DHCP Reply message.
  - Siaddr (server ip address): indicates the IP address of the DHCP server.
  - Chaddr (client hardware address): indicates the MAC address of a DHCP client.
  - Options: contains the configuration allocated by the DHCP server to a client.

### Options Field

- The options field has variable length and a maximum of 312 bytes. It contains the DHCP message type and configuration parameters allocated by a DHCP server to a client. The configuration parameters include the gateway IP address, DNS server IP address, and IP address lease.
- The options field consists of Type, Length, and Value. The value of the Type sub-field ranges from 1 to 255. The following table lists the common values of Type, Length, and Value.

| Type | Length (Byte) | Value | Function |
|---|---|---|---|
| 1 | 4 | Subnet Mask | Specifies a subnet mask. |
| 3 | 4 | Router (gateway) | Specifies a gateway address. |
| 50 | 4 | Requested IP Address | Specifies a requested IP address. |
| 51 | 4 | IP Address Lease Time | Specifies an IP address lease. |
| 53 | 1 | Message Type | Specifies a DHCP message type. |
| 54 | 4 | DHCP Server Identifier | Specifies a DHCP server identifier. |
| 55 | 9 | Parameter Request List | Sets the parameter request list. A DHCP client uses this option to request specified configuration parameters. |
| 58 | 4 | Rebinding Time Value | Specifies the lease renewal time (T1), which is 50% of the lease time. |
| 59 | 4 | Renewal Time Value | Specifies the extended period of the lease (T2). Generally, the value is 87.5% of the lease time. |

### DHCP Message Types

- The Type subfield in the Options field of a DHCP message is set to 53, indicating the DHCP message type. In the figure, when Type is 53 and Length is 1, the Value sub-field ranges from 01 to 08, indicating a DHCP message type.

Diagram description: A small TLV diagram showing Type (53, 1 Byte) | Length (1 Byte) | Value (N Byte), pointing to a list of the eight DHCP message types: 1-DHCP DISCOVER, 2-DHCP OFFER, 3-DHCP REQUEST, 4-DHCP DECLINE, 5-DHCP ACK, 6-DHCP NAK, 7-DHCP RELEASE, 8-DHCP INFORM.

- DHCP Discover message: A DHCP client broadcasts this message to locate a DHCP server when the client attempts to connect to a network for the first time.
- DHCP Offer message: A DHCP server sends this message in response to a DHCP Discover message. A DHCP Offer message carries configuration information.
- DHCP Request message: A DHCP client broadcasts a DHCP Request message to respond to a DHCP Offer message sent by a DHCP server after the client starts; a DHCP client broadcasts a DHCP Request message to confirm the configuration (including the allocated IP address) after the client restarts; a DHCP client unicasts or broadcasts a DHCP Request message to renew the IP address lease after the client obtains an IP address.
- DHCP Decline message: A DHCP client sends this message to notify the DHCP server when detecting that the IP address assigned by the DHCP server conflicts with another IP address.
- DHCP ACK message: A DHCP server sends this message to acknowledge a DHCP Request message sent from a DHCP client.
- DHCP NAK message: A DHCP server sends this message to reject a DHCP Request message from a DHCP client.
- DHCP Release message: A DHCP client sends this message to release its allocated IP address.
- DHCP Inform message: A DHCP client sends this message to obtain network configuration parameters, such as the gateway address and DNS server address, after it has obtained an IP address.

### User-defined Options

- In addition to the options specified in the standard protocol, some options, such as Option 82 and Option 43, are not specified uniformly and are referred to as user-defined options.
  - Relay agent information option (Option 82)
    - The Option 82 field contains a maximum of 255 sub-options. If the Option 82 field is defined, at least one sub-option must be defined.
    - The DHCP relay agent or a device enabled with DHCP snooping appends the Option 82 field to the DHCP Request message sent from a DHCP client, and then forwards the DHCP Request message to the DHCP server. An administrator can obtain information about the DHCP client from the Option 82 field, such as the VLAN ID of the switch interface connected to the DHCP client, Layer 2 port number, and MAC address of the relay agent.
  - Vendor-specific information option (Option 43)
    - DHCP servers and DHCP clients exchange vendor-specific information through Option 43. When a DHCP server receives a DHCP Discover message with parameter 43 encapsulated in Option 55, it encapsulates Option 43 in a DHCP Offer message and sends the message to the DHCP client.
    - When a device functions as the DHCP server on a WLAN, it can deliver the AC's IP address to connected APs, which facilitates the connection setup between the AC and APs.

- Commonly used sub-options:
  - Sub-Option1 (Agent Circuit ID Sub-option) The sub-option is usually configured on the DHCP relay agent. It defines the VLAN ID and Layer 2 port number of the switch interface connected to the DHCP client when messages are transmitted. Sub-Option 1 and Sub-Option 2 are used together to identify the DHCP source.
  - Sub-Option 2 (Agent Remote ID Sub-option) This sub-option is usually configured on the DHCP relay agent. It defines that the MAC address of the DHCP relay agent carried in the messages to be transmitted.
  - Sub-Option 5 (Link-selection Suboption): This sub-option contains the IP address added by the DHCP relay agent. In this way, the DHCP server can assign an IP address that is on the same network segment as the IP address to the DHCP client.

### Application Example of Option 43

- On a Layer 3 WLAN, when an AP goes online, it needs to obtain the IP address of the AC and establish a CAPWAP tunnel with the AC.
- The IP address of the AP allocated by the DHCP server. If the IP address of the AC and that of the AP are in different broadcast domains, the AP cannot obtain the IP address of the AC in broadcast mode. As a result, the CAPWAP tunnel cannot be set up.
- The AP obtains the AC's IP address from the Option 43 field in DHCP messages. After obtaining the AC's IP address, the AP establishes a CAPWAP tunnel with the AC and goes online.

Diagram description: An AC (IP 10.23.101.2) connects to a switch (SW), which connects to AP1 and AP2 (DHCP clients, network 10.23.100.0/24). A callout labeled "Option 43 / AC IP: 10.23.101.2" points from the switch/DHCP Server area toward the APs. A note box states: The IP address of the AC is 10.23.101.2, and the gateway address of the network where the AP is located is 10.23.100.1. The AP obtains the IP address from the IP address pool Huawei1 through DHCP. The DHCP server advertises the IP address of the AC to the AP through the Option 43 field.

### DHCP Address Lease Renewal

Diagram description: A DHCP Client and DHCP Server separated by a Layer 2 broadcast domain cloud, with a timeline showing two renewal attempts labeled T1 and T2. At T1, the client unicasts a DHCP Request message to the server. At T2, the client broadcasts a DHCP Request message.

- When the lease reaches 50% (T1) of its validity period, the DHCP client sends a unicast DHCP Request message to the DHCP server to request lease renewal. If the DHCP client receives a DHCP ACK message from the DHCP server, the lease is successfully renewed.
- If no response is received from the DHCP server when the lease reaches 87.5% (T2) of its validity period, the DHCP client sends a broadcast DHCP Request message to request lease renewal. If the DHCP client receives a DHCP ACK message from the DHCP server, the lease is successfully renewed.
- If no response is received when the lease expires, the DHCP client stops using the IP address and sends a DHCP Discover message to apply for a new IP address.

Question: Why is the same IP address assigned to a computer each time?

- The DHCP server defines a validity period for each IP address allocated to a DHCP client. The validity period is called the lease. If the DHCP client still needs to use the IP address before the lease expires, the DHCP client can request to extend the lease. If the IP address is not required, the DHCP client can release it. If no idle IP address is available, the DHCP server assigns the IP address released by the client to another client.
- If the DHCP client receives a DHCP NAK message after sending a DHCP Request message at T1 or T2, the DHCP client sends a DHCP Discover message to request a new IP address.
- If a DHCP client does not need to use the allocated IP address before the lease expires, the DHCP client sends a DHCP Release message to the DHCP server to request IP address release. The DHCP server saves the configuration of this DHCP client and records the IP address in the allocated IP address list. The IP address can then be allocated to this DHCP client or other clients. A DHCP client can send a DHCP Inform message to the DHCP server to request configuration update.
- The DHCP client generates different renewal requests based on the remaining lease of the IP address.

### DHCP Client Reuse of an IP Address

Diagram description: A DHCP Client and DHCP Server separated by a Layer 2 broadcast domain cloud. (1) DHCP Request (broadcast) in the request stage — sent from client to server. (2) DHCP ACK (unicast) in the acknowledgment stage — sent from server to client.

- Request stage
  - The DHCP client broadcasts a DHCP Request message carrying the IP address that the client has used. The requested IP address is added in the Option 50 field.
- Acknowledgment stage
  - After receiving the DHCP Request message, the DHCP server checks whether there is a lease record based on the MAC address in the message. If there is a lease record matching the MAC address, the DHCP server replies with a DHCP ACK message to notify DHCP client that the requested IP address can be used. If there is no lease record, the DHCP server does not respond to the message.

- Not all clients can reuse IP addresses that have been allocated to them.
- If a DHCP client reconnects to the network, it can reuse an IP address that has been allocated to it. For example, a host on a network functions as a DHCP client. When the host is powered off and then powered on, it needs to obtain related network parameters again. In this case, the host can request to allocate an IP address that has been used.

### IP Address Allocation Sequence

Diagram description: A vertical flowchart of five boxes connected top-to-bottom by arrows: "IP address statically bound to the MAC address" → "Used IP address" → "IP address in idle state" → "IP address whose lease expires" → "Conflicting IP address."

- A DHCP server assigns IP addresses to a client in the following sequence:
  - IP address that is in the database of the DHCP server and is statically bound to the MAC address of the client
  - IP address that has previously been assigned to the client, that is, IP address in the requested IP Addr Option of the DHCP Discover message sent by the client
  - IP address that is first found when the DHCP server searches the DHCP address pool for available IP addresses
  - If the DHCP address pool has no available IP address, the DHCP server searches the expired IP addresses and conflicting IP addresses, and then assigns a valid IP address to the client. If all the IP addresses are in use, an error message is reported.

### DHCP Configuration Commands (1)

1. Create a global address pool.
```
[Huawei]ip pool ip-pool-name
```
2. Configure the gateway address of the DHCP client.
```
[Huawei-ip-pool-HW]gateway-list ip-address
```
3. Configure the range of IP addresses that can be allocated dynamically in the global address pool.
```
[Huawei-ip-pool-HW]network ip-address [ mask { mask | mask-length } ]
```
4. Configure the IP addresses that are not automatically allocated in the address pool.
```
[Huawei-ip-pool-HW]excluded-ip-address start-ip-address [ end-ip-address ]
```
5. Set the lease for IP addresses in the address pool.
```
[Huawei-ip-pool-HW] lease { day day [ hour hour [ minute minute ] ] | unlimited }
```
6. Configure the DHCP server to allocate a fixed IP address to specified DHCP client.
```
[Huawei-ip-pool-HW] static-bind ip-address ip-address mac-address mac-address [ option-template template-name | description description ]
```

- In this example, the name of the IP address pool is HW.
- By default, a DHCP server does not allocate fixed IP addresses to specified clients.

### DHCP Configuration Commands (2)

1. Configure an interface address pool.
```
[Huawei]interface interface-type interface-number [subinterface-number]
[Huawei-GigabitEthernet0/0/1]ip address ip-address { mask | mask-length }
```
The IP address segment of the interface is the interface address pool. The interface address mask cannot be set to 31; otherwise, the interface address pool may fail to be configured.

2. Configure a gateway IP address in the interface address pool.
```
[Huawei-GigabitEthernet0/0/1]dhcp server gateway-list ip-address
```
3. Configure the DHCP server to allocate a fixed IP address to a specified DHCP client.
```
[Huawei-GigabitEthernet0/0/1]dhcp server static-bind ip-address ip-address mac-address mac-address [description description]
```
4. Configure the IP addresses that are not automatically allocated in the address pool.
```
[Huawei-GigabitEthernet0/0/1]dhcp server excluded-ip-address start-ip-address [end-ip-address]
```
5. Set the lease for IP addresses in the address pool.
```
[Huawei-GigabitEthernet0/0/1]dhcp server lease { day day [ hour hour [ minute minute ] ] | unlimited }
```

- GigabitEthernet0/0/1 is used as an example.

### DHCP Configuration Example

Diagram description: Internet connects to R1 (functioning as DHCP server) via GE0/0/0 and GE0/0/1. GE0/0/0 connects to SW1, which connects to PC1 (DHCP client). GE0/0/1 connects to SW2, which connects to PC2 and PC3 (PC3 has a fixed IP address 192.168.2.2/24, MAC address 00e0-fc00-00aa).

Requirements:
- Assign an IP address to PC1 based on the global address pool.
- Assign IP addresses to PC2 and PC3 based on the interface address pool, and assign fixed IP addresses to PC3.

**Global address pool configuration (for PC1, via GE0/0/0):**
```
[R1]dhcp enable
[R1]ip pool HW
[R1-ip-pool-HW]gateway-list 192.168.1.1
[R1-ip-pool-HW]network 192.168.1.0 mask 24
[R1-ip-pool-HW]excluded-ip-address 192.168.1.200 192.168.1.254
[R1]interface GigabitEthernet 0/0/0
[R1-GigabitEthernet0/0/0]dhcp select global   # Select a global address pool.
```

**Interface address pool configuration (for PC2 and PC3, via GE0/0/1):**
```
[R1]interface GigabitEthernet 0/0/1
[R1-GigabitEthernet0/0/1]ip address 192.168.2.1 24
[R1-GigabitEthernet0/0/1]dhcp select interface    # Select an interface address pool.
[R1-GigabitEthernet0/0/1]dhcp server excluded-ip-address 192.168.2.254
[R1-GigabitEthernet0/0/1]dhcp server static-bind ip-address 192.168.2.2 mac-address 00e0-fc00-00aa #Assign a fixed IP address to PC3.
```

### DHCP Configuration Result

**On R1:**
```
[R1]display ip pool
 Pool-name    :       HW
 Gateway-0    :       192.168.1.1
 Mask         :       255.255.255.0
 IP address Statistic
   Total:        253
   Used:          2      Idle:      198
   Expired:       0      Conflict:  0      Disable: 55
```

**On PC3:**
```
PC3>ipconfig
IPv4 address...................: 192.168.2.2
Subnet mask.....................: 255.255.255.0
Gateway.........................: 192.168.2.1
Physical address.................: 54-89-98-86-2B-F4
```
PC3 obtains a statically bound IP address.

- IP addresses in an address pool can be in one of the following states:
  - Used: indicates that the IP address is used.
  - Idle: indicates that the IP address is idle.
  - Expired: indicates that the lease of the IP address expires and the IP address is idle.
  - Conflict: indicates that the IP address conflicts with another IP address on the network.
  - Disable: indicates that the IP address cannot be used.

## 3. DHCP Relay Working Mechanism and Configuration

### Introduction to DHCP Relay

- As the network scale expands and the number of network devices increases, different users in an enterprise may be distributed on different network segments. In normal cases, a DHCP server cannot meet address allocation requirements of multiple network segments. If the DHCP server is required to allocate IP addresses, DHCP messages need to be sent across network segments.
- A DHCP relay agent transparently transmits DHCP messages between a DHCP client and a DHCP server that reside in different broadcast domains. The DHCP relay function allows DHCP clients and DHCP server that are in different broadcast domains to communicate.

Diagram description: Two side-by-side diagrams. Left (without DHCP relay): Client A (Layer 2 broadcast domain A, via SW1) and Client B (Layer 2 broadcast domain B, via SW2) both connect to R1, which connects to a DHCP server in Layer 2 broadcast domain C. Client A's DHCP Discover message is marked with a red X reaching R1, and Client B's DHCP Discover message is also blocked — meaning broadcast DHCP Discover messages cannot cross R1 to reach the server. Right (with DHCP relay): Same topology, but R1 is labeled "DHCP relay," and a blue checkmark shows Client A's and Client B's DHCP Discover messages successfully being relayed through R1 to the DHCP server.

### DHCP Relay Message Format

- A DHCP relay agent forwards DHCP messages between a DHCP client and a DHCP server, so the DHCP relay agent modifies only some fields in DHCP messages. The message format remains unchanged, as shown in the following figure.

Diagram description: The same DHCP message format field layout as before (Op | Htype | Hlen | Hops; Xid; Secs | Flags; Ciaddr; Yiaddr; Siaddr; Giaddr; Chaddr; Sname; File; Options(variable)), with Hops and Giaddr fields highlighted as the ones modified by the relay agent.

**Hops:** indicates the number of DHCP relay agents that a DHCP message passes through. This field is set to 0 by a DHCP client or server. Its value increases by 1 each time the message passes through a DHCP relay agent.

**Giaddr (gateway ip address):** indicates the IP address of the first DHCP relay agent. When a client sends a DHCP Request message, the first DHCP relay agent fills its IP address in this field when forwarding the message to the DHCP server.

- The Hops field limits the number of DHCP relay agents that a DHCP message can pass through. A maximum of 16 DHCP relay agents are allowed between a DHCP server and a DHCP client. If the value of this field is larger than 16, DHCP messages are discarded.
- The DHCP server determines the network segment address of a client based on the Giaddr field, so the DHCP server can select an appropriate address pool and assign an IP address on the network segment to the client. The DHCP server returns a DHCP Offer message to the DHCP relay agent. The DHCP relay agent then forwards the DHCP Offer message to the client. If the DHCP Discover message passes through multiple DHCP relay agents before reaching the DHCP server, the value of this field is the IP address of the first DHCP relay agent and remains unchanged. However, the value of the Hops field increases by 1 each time the DHCP Discover message passes through a DHCP relay agent.

### Working Mechanism of DHCP Relay

Diagram description: A DHCP Client, DHCP Relay, and DHCP Server shown left to right, with four numbered message exchanges. (1) Discovery stage: DHCP Discover message from client to relay; the relay unicasts the DHCP Discover message to the server. (2) Offer stage: DHCP Offer message sent by the DHCP server, forwarded to the client by the relay. (3) Request stage: DHCP Request message from client, unicast to the server by the relay. (4) Acknowledgment stage: DHCP ACK message sent by the server, forwarded to the client by the relay.

- Discovery stage: After receiving the DHCP Discover message broadcast by a DHCP client, the DHCP relay agent unicasts the DHCP Discover message to the DHCP server or the next-hop relay agent through routing.
- Offer stage: The DHCP server selects an address pool based on the Giaddr field in the DHCP Discover message to allocate network parameters to the DHCP client. After receiving the DHCP Offer message, the DHCP relay agent unicasts or multicasts the message to the DHCP client.
- Request stage: The DHCP relay agent processes the DHCP Request message from the client using the same method described in the Discovery stage.
- Acknowledgment stage: The DHCP relay agent processes the DHCP ACK message from the server using the same method described in the Offer stage.

- After receiving a DHCP Discover message, the DHCP relay agent processes the message as follows:
  - Checks the value of the Hops field. If this value exceeds 16, the DHCP relay agent discards the message. Otherwise, the DHCP relay agent increases this value by 1 and proceeds to the next step.
  - Checks the value of the Giaddr field. If this value is 0, the DHCP relay agent sets the Giaddr field to the IP address of the interface receiving the DHCP Discover message. If not, the DHCP relay agent does not change the field and proceeds to the next step.
  - Changes the destination IP address of the DHCP Discover message to the IP address of the DHCP server or the next-hop DHCP relay agent, and changes the source IP address to the IP address of the interface connecting the DHCP relay agent to the client. The message is then unicast to the DHCP server or the next-hop DHCP relay agent.
- After receiving the DHCP Discover message, the DHCP server selects an address pool on the same network segment as the value of the Giaddr field in the message, allocates parameters such as an IP address to the client, and unicasts a DHCP Offer message to the DHCP relay agent identified by the Giaddr field. After receiving the DHCP Offer message, the DHCP relay agent performs the following operations:
  - Checks the value of the Giaddr field. If this value is not the IP address of the interface receiving the DHCP Offer message, the DHCP relay agent discards the message. Otherwise, the DHCP relay agent proceeds to the next step.
  - Checks the value of the Flags field. If this value is 1, the DHCP relay agent sends a broadcast DHCP Offer message to the DHCP client. Otherwise, the DHCP relay agent sends a unicast DHCP Offer message.

### DHCP Relay Configuration Commands

1. Enable the DHCP relay function on an interface.
```
[Huawei-GigabitEthernet0/0/0]dhcp select relay
```
2. Specify an IP address for the DHCP server in the interface view.
```
[Huawei-GigabitEthernet0/0/0]dhcp relay server-ip ip-address
```
3. Create a DHCP server group.
```
[Huawei]dhcp server group group-name
```
4. Add DHCP servers to the DHCP server group.
```
[Huawei-dhcp-server-group-HW]dhcp-server ip-address [ ip-address-index ]
```
5. Configure a DHCP server group for the interface.
```
[Huawei-GigabitEthernet0/0/0]dhcp relay server-select group-name
```
6. Enable the DHCP client function on the interface.
```
[Huawei-GigabitEthernet0/0/0]ip address dhcp-alloc
```

### DHCP Relay Configuration Example (1)

Diagram description: DHCP Client (R1, GE0/0/0), DHCP Relay (R2, network 192.168.1.0/24 side via GE0/0/0, and 10.1.1.0/24 side via GE0/0/1), and DHCP Server (R3), connected in a chain: R1 — GE0/0/0(R1)/GE0/0/0(R2), 192.168.1.0/24 — R2 — GE0/0/1(R2)/GE0/0/1(R3), 10.1.1.0/24 — R3.

The configuration requirements are as follows:
- R1 obtains an IP address through DHCP.
- The DHCP relay function is enabled on GE0/0/0 of R2 and the IP address of the DHCP server is set to 10.1.1.2.
- An address pool named HW-1 is created on R3, with the IP address range of 192.168.10/24 and gateway address of 192.168.1.1.

**Configuration of R1 and R2:**
```
[R1]interface GigabitEthernet0/0/0
[R1-GigabitEthernet0/0/0]ip address dhcp-alloc
[R1-GigabitEthernet0/0/0]quit

[R2]dhcp server group HW
[R2-dhcp-server-group-HW]dhcp-server 10.1.1.2
[R2-dhcp-server-group-HW]quit
[R2]interface GigabitEthernet0/0/1
[R2-GigabitEthernet0/0/1]ip address 10.1.1.1 24
[R2-GigabitEthernet0/0/1]quit
[R2]interface GigabitEthernet0/0/0
[R2-GigabitEthernet0/0/0]ip address 192.168.1.1 24
[R2-GigabitEthernet0/0/0]dhcp select relay
[R2-GigabitEthernet0/0/0]dhcp relay server-select HW
[R2-GigabitEthernet0/0/0]quit
```

- Before configuring DHCP on each device, run the dhcp enable command in the system view to enable DHCP.

### DHCP Relay Configuration Example (2)

Diagram description: Same topology as above (DHCP Client R1 — DHCP Relay R2 — DHCP Server R3).

The configuration requirements are as follows:
- GE0/0/0 on R1 obtains an IP address through DHCP.
- The DHCP relay function is enabled on GE0/0/0 of R2 and the IP address of the DHCP server is set to 10.1.1.2.
- An address pool named HW-1 created on R3, with the IP address range of 192.168.10/24 and gateway address of 192.168.1.1.

**Configuration of R3:**
```
[R3]ip pool HW-1
[R3-ip-pool-HW-1]network 192.168.1.0 mask 24
[R3-ip-pool-HW-1]gateway-list 192.168.1.1
[R3-ip-pool-HW-1]quit
[R3]interface GigabitEthernet 0/0/1
[R3-GigabitEthernet0/0/1]ip address 10.1.1.2 24
[R3-GigabitEthernet0/0/1]dhcp select global
[R3-GigabitEthernet0/0/1]quit
[R3]ip route-static 192.168.1.0 255.255.255.0 10.1.1.1
```

### DHCP Relay Configuration Verification

**Check the IP address obtained by GE0/0/0 on R1:**
```
<R1>display dhcp client
 DHCP client lease information on interface GigabitEthernet0/0/0 :
   Current machine state       : Bound
   Internet address assigned via : DHCP
   Physical address             : 00e0-fce6-4691
   IP address                   : 192.168.1.254
   Subnet mask                  : 255.255.255.0
   Gateway ip address           : 192.168.1.1
   DHCP server                  : 10.1.1.2
   ......
```
The command output shows that GE0/0/0 on R1 has obtained an IP address and a gateway address.

**Check the DHCP relay information on R2:**
```
<R2>display dhcp relay all
 DHCP relay agent running information of interfaceGigabitEthernet0/0/0 :
   Server group name    : HW
   Gateway address in use  : 192.168.1.1

<R2>display dhcp relay statistics
 The statistics of DHCP RELAY:
   DHCP packets received from clients   : 2
   DHCP packets sent to clients         : 2
   DHCP packets received from servers   : 2
   DHCP packets sent to servers         : 2
   ......
```
The command output shows that the DHCP relay function is enabled on GE0/0/0 of R2, and R2 functions as the DHCP relay agent to exchange messages with the DHCP client and DHCP server four times.

## Quiz

**1. (Single) Which of the following messages is sent by the DHCP client to the DHCP server to renew the lease? ( )**

A. DHCP DISCOVER
B. DHCP OFFER
C. DHCP REQUEST
D. DHCP ACK

Answer: C

**2. (Single) Which of the following commands can be used to enable the DHCP relay function on a router interface? ( )**

A. dhcp select server
B. dhcp select global
C. dhcp select interface
D. dhcp select relay

Answer: D

## Summary

- This course describes the format of DHCP messages and functions of key fields. It describes how a DHCP server assigns network parameters, such as IP addresses, to DHCP clients through message exchange. In addition, this course describes how a DHCP client renews its IP address lease and obtains an IP address after restart.
- When a DHCP client and a DHCP server are in different broadcast domains, the DHCP relay function enables DHCP messages to be transmitted across network segments. This function implements message negotiation between the DHCP client and the DHCP server.

