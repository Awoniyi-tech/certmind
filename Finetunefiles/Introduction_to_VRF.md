# Introduction to VRF

## Foreword

- Looking back on the previous courses, would you recall certain protocols or technologies whose names contain the letter "V"? What are the characteristics or similarities of these protocols or technologies?
- Virtual routing and forwarding (VRF) technology creates multiple routing tables on a Layer 3 forwarding device to isolate data or services. This technology is often used in isolation-related scenarios, such as when Multiprotocol Label Switching (MPLS) VPN and firewalls are deployed.
- This course describes basic concepts and configurations of VRF technology.

## Objectives

On completion of this course, you will be able to:
- Understand basic VRF concepts.
- Understand typical VRF applications.
- Implement basic VRF configurations.

## Contents

1. Basic Concepts of VRF
2. Typical VRF Configuration Examples

## 1. Basic Concepts of VRF

### Network Requirements

- An enterprise network has a production network and a management network. Each network exclusively uses an aggregation switch and access switches and shares a core switch with the other one.
- The core switch connects to a server cluster on each of the production and management networks. The two network segments are 192.168.100.0/24.
- Requirements: Implement data communication within the production and management networks and isolate the communication between the two networks.

**Diagram description:** Production network servers (192.168.100.0/24) connect to an aggregation switch on the left; Management network servers (192.168.100.0/24, an overlapping/duplicate segment) connect to an aggregation switch on the right. Both aggregation switches connect down to a single shared core switch. Below each aggregation switch are two access switches, each connecting to clients — "Clients on the production network" on the left and "Clients on the management network" on the right. A green checkmark marks communication within the production network side as allowed; a red X marks communication between the production and management sides (through the shared core switch) as something that must be blocked.

### Implementation by Deploying ACLs

- Configure an ACL on the core switch to prevent mutual access between the production and management networks.
- Disadvantages:
  - The configuration is complex, and scalability is poor.
  - The problem that two networks use overlapping network segments cannot be resolved. Additional configurations must be performed to prevent the use of overlapping network segments.

**Diagram description:** Same topology as the previous slide (production and management server clusters, aggregation switches, one shared core switch, access switches, clients), but now a red dashed vertical line is drawn through the core switch, separating the production side from the management side — representing the ACL-based logical separation configured on the core switch.

### Adding a Core Switch

- Add a core switch so that an exclusive core switch serves each network to physically isolate the two networks.
- Disadvantage: Additional equipment expenditures are required.

**Diagram description:** The production network servers and management network servers now each connect to their own separate, dedicated core switch (two core switches total instead of one shared core switch). Each core switch connects down to its own aggregation switch, access switches, and clients. A red vertical line separates the two now fully independent, physically isolated network stacks.

### Using VRF Technology

- VRF, also called VPN instance, is a virtualization technology. Multiple VPN instances are created on a physical device. Each VPN instance has its own interfaces, a routing table, and routing protocol processes.

**Diagram description:** The production network servers and management network servers connect to their respective aggregation switches, which connect via VLANIF100 (production side) and VLANIF200 (management side) into a *single* physical core switch. Inside this one physical core switch, two logical VPN instances are shown side by side: VPN instance VPNA (serving the production network via VLANIF101 down to the production network clients) and VPN instance VPNB (serving the management network via VLANIF201 down to the management network clients). PC1 (192.168.1.1, gateway 192.168.1.254) sits on the production side; PC2 (172.16.1.1, gateway 172.16.1.254) sits on the management side.

**VPNA's routing table**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 192.168.100.0/24 | OSPF | VLANIF100 | 192.168.100.1 |
| 192.168.1.0/24 | OSPF | VLANIF101 | 192.168.101.1 |

**VPNB's routing table**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 192.168.100.0/24 | OSPF | VLANIF200 | 192.168.100.1 |
| 172.16.1.0/24 | Static | VLANIF201 | 192.168.201.1 |

### VRF Implementation

A VRF is a logical unit on a physical device. Each logical unit is called a VPN instance, and instances are isolated on the routing plane. VRF implementation is as follows:

1. Create an instance and bind each involved Layer 3 interface (physical interface, sub-interface, or VLANIF interface) to the instance.
2. (Optional) Configure a routing protocol or static route and bind it to the VPN instance.
3. A VPN instance routing table is created using information about the interfaces and routing protocols bound to the instance. Then data is forwarded using entries contained in the instance routing table, and instance isolation is implemented.

**Diagram description:** Four small topology panels illustrate VRF logical partitioning. The top-left panel shows one physical device with four interfaces (GE0/0/1, GE0/0/3 on top; GE0/0/0, GE0/0/2 on bottom) as a single, undivided device. Numbered callout arrows (1, 2, 3) point down to two bottom panels: the bottom-left panel shows the same physical device split into logical routers/instances with OSPF deployed, and the bottom-right panel shows another logical split with IS-IS deployed, with one interface marked with a red X (unbound/unreachable). The top-right panel shows the physical device split into two labeled VPN instances — VPN instance: VPNA and VPN instance: VPNB — each with its own set of interfaces (GE0/0/0–GE0/0/3, logically partitioned per instance). Below this, two document icons represent "VPNA's routing table" and "VPNB's routing table," with a small cartoon character asking, "How many routing tables are there on this router?"

**Notes:**
- By default, all interfaces on a network device belong to the same forwarding instance, that is, the root instance of the device.

### Example: Before VRF Deployment

**Background:** PC1, R1, and network segment 1.1.1.0/24 connected R1 belongs to a service network. PC2, R2, and network segment 2.2.2.0/24 connected to R2 belong to the management network. All direct routes on the core switch and routes destined for remote networks and discovered by the core switch are stored in the core switch's routing table (also called the global routing table). With such a routing table, the core switch enables the service and management networks to communicate.

**Requirements:** Configure the core switches to isolate the service and management networks.

**Diagram description:** Network segment 1.1.1.0/24 connects to router R1, which connects via GE0/0/0 (IP 192.168.100.2) to a core switch. Network segment 2.2.2.0/24 connects to router R2, which connects via GE0/0/0 (IP 172.16.100.2) to the same core switch. On the core switch, VLANIF11 (192.168.100.1) and VLANIF10 (192.168.1.254) serve the R1/PC1 side, while VLANIF201 (172.16.100.1) and VLANIF200 (172.16.1.254) serve the R2/PC2 side. PC1 (192.168.1.1, gateway 192.168.1.254) connects below VLANIF10; PC2 (172.16.1.1, gateway 172.16.1.254) connects below VLANIF200.

**Core switch's routing table**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 192.168.1.0/24 | Direct | VLANIF10 | 192.168.1.254 |
| 172.16.1.0/24 | Direct | VLANIF200 | 172.16.1.254 |
| 192.168.100.0/24 | Direct | VLANIF11 | 192.168.100.1 |
| 172.16.100.0/24 | Direct | VLANIF201 | 172.16.100.1 |
| 1.1.1.0/24 | Static | VLANIF11 | 192.168.100.2 |
| 2.2.2.0/24 | Static | VLANIF201 | 172.16.100.2 |

### Example: Creating VPN Instances

**Diagram description:** Same topology as the previous slide, but now VLANIF201 (172.16.100.1) and VLANIF200 (172.16.1.254) on the core switch are grouped inside a highlighted box labeled "VPN instance 1," showing that these two interfaces have been moved into a newly created VPN instance, separate from the root/global instance (which still holds VLANIF11 and VLANIF10 for the R1/PC1 side).

**Core switch global routing table (Root device's routing table)**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 192.168.1.0/24 | Direct | VLANIF10 | 192.168.1.254 |
| 192.168.100.0/24 | Direct | VLANIF11 | 192.168.100.1 |
| 1.1.1.0/24 | Static | VLANIF11 | 192.168.100.2 |

**VPN instance 1's routing table on the core switch**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 172.16.1.0/24 | Direct | VLANIF200 | 172.16.1.254 |
| 172.16.100.0/24 | Direct | VLANIF201 | 172.16.100.1 |

### Example: Configuring a Dynamic Routing Protocol

**Diagram description:** Same topology as the previous slide, with an added "Deploy OSPF" annotation and a curved arrow near R2's GE0/0/0 interface, indicating OSPF is now configured between the core switch's VPN instance 1 and R2 (in place of the earlier static route).

**Core switch's global routing table (Root device's routing table)**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 192.168.1.0/24 | Direct | VLANIF10 | 192.168.1.254 |
| 192.168.100.0/24 | Direct | VLANIF11 | 192.168.100.1 |
| 1.1.1.0/24 | Static | VLANIF11 | 192.168.100.2 |

**VPN instance 1's routing table on the core switch**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 172.16.1.0/24 | Direct | VLANIF200 | 172.16.1.254 |
| 172.16.100.0/24 | Direct | VLANIF201 | 172.16.100.1 |
| 2.2.2.0/24 | OSPF | VLANIF201 | 172.16.100.2 |

*(The row "2.2.2.0/24 | OSPF | VLANIF201 | 172.16.100.2" is highlighted in red in the source slide, marking it as the newly learned route.)*

Either multiple dynamic routing protocols or multiple processes of a specific dynamic routing protocol can run on a device. A dynamic routing protocol process associated with a VPN instance serves the instance, and the device installs the routes learned from the process to the routing table of the VPN instance.

### Common Usage Scenarios

**Firewall Virtual System**

Virtual systems (VSs) are logical devices divided from a physical device and are working separately. A virtual system has the following characteristics:
- Resource virtualization: Each VM has exclusive resources, including interfaces, VLANs, policies, and sessions.
- Route virtualization: Each VM has its own routing table and is isolated from the other VMs.

Route virtualization is implemented by creating VPN instances.

**Diagram description (Firewall Virtual System):** A single physical firewall device icon on the left has an arrow pointing to a box divided into three virtual systems — Virtual system A, Virtual system B, Virtual system C, ... — all sitting on top of a shared "Root system" bar, illustrating that virtual systems are logical partitions of one physical device's root system.

**BGP/MPLS IP VPN**

BGP/MPLS IP VPN is a PE-based L3VPN technology. It runs BGP to advertise VPN routes and MPLS to forward VPN packets over the backbone network of a service provider (SP). VPN instances are created on PEs to distinguish routes of different VPNs.

**Diagram description (BGP/MPLS IP VPN):** VPN1 site connects via a CE (customer edge) router to a PE (provider edge) router; VPN2 site similarly connects via its own CE to a PE. The two PE routers sit at the edges of an "MPLS VPN network" cloud, which also contains intermediate P (provider core) routers. On the far side, the MPLS network connects out to another set of PE routers, which connect to CE routers serving VPN1 site and VPN2 site on the right-hand side. This illustrates that two independent customer VPNs (VPN1 and VPN2) share the same MPLS backbone while remaining isolated via VPN instances configured on the PE routers.

**Notes:**
- For more information about BGP/MPLS IP VPN, see the related HCIP-Datacom-Advance courses.

## 2. Typical VRF Configuration Examples

### Basic VRF Configuration Commands (1)

1. Create a VPN instance and enter the VPN instance view.

```
[Huawei] ip vpn-instance vpn-instance-name
```

The **ip vpn-instance** command creates a VPN instance and displays the VPN instance view. By default, no VPN instance is configured.

2. Enable IPv4 route advertisement and data forwarding for the VPN instance.

```
[Huawei-vpn-instance-InstanceName] ipv4-family
```

The **ipv4-family** command creates an IPv4 address family for a VPN instance and displays the VPN instance IPv4 address family view. An interface cannot be bound to a VPN instance that has no address family created.

3. Bind an interface to the VPN instance.

```
[Huawei-GigabitEthernet0/0/0]ip binding vpn-instance vpn-instance-name
```

The **ip binding vpn-instance** command binds an interface on a PE to a VPN instance. By default, an interface is not bound to any VPN instance and belongs to the root instance. After an interface is bound to a VPN instance or unbound from a VPN instance, the IP address, Layer 3 features, and IP-related routing protocols on the interface are deleted. You have to reconfigure them if needed.

### Basic VRF Configuration Commands (2)

4. Add a static route to the routing table of the VPN instance.

```
[Huawei] ip route-static vpn-instance vpn-instance-name ip-address { mask | mask-length } { nexthop-address | interface-type interface-number }
```

5. Create a dynamic routing protocol process (for example, OSPF) bound to the VPN instance.

```
[Huawei] ospf [ process-id | router-id router-id ] vpn-instance vpn-instance-name
```

Note: The process IDs of different VPN instances must be different.

6. Use the following commands to maintain VPN instances.

```
[Huawei] display ip routing-table vpn-instance vpn-instance-name
[Huawei] ping -vpn-instance vpn-instance-name host
[Huawei] tracert -vpn-instance vpn-instance-name host
```

Note: If the ping command does not carry the vpn-instance keyword, the ping is performed on the root device by default, and the generated ICMP messages are forwarded using entries in the global routing table, which also applies to the tracert operation.

### Configuration Case — Background and Requirement Analysis

**Background:** An enterprise has a production network and a management network, shown on the left figure.
- PC1 belongs to the production network, PC2 belongs to the management network, and S1 is the access switch for the two PCs. PC1 is added to VLAN 10, and PC2 is added to VLAN 20.
- Sub-interfaces are configured on R1 functioning as a gateway for PC1 and PC2.

**Requirements:** Isolate the production network from the management network and use static routes for communication within each network.

**Diagram description:** Production network (192.168.100.0/24) and management network (192.168.200.0/24) clouds both connect to router R1 — production via interface GE0/0/1 (IP 192.168.101.1/24) and management via GE0/0/2 (IP 192.168.102.1/24). R1 connects down via GE0/0/0 to switch S1 (also via GE0/0/0). Below S1 are two clients: PC1 (192.168.1.1, gateway 192.168.1.254, VLAN 10) and PC2 (192.168.2.1, gateway 192.168.2.254, VLAN 20).

**Routing table before VRF is deployed on R1**

| Destination/Mask | Protocol | Interface | NextHop |
|---|---|---|---|
| 192.168.100.0/24 | Static | GE0/0/1 | 192.168.101.254 |
| 192.168.200.0/24 | Static | GE0/0/2 | 192.168.102.254 |
| 192.168.1.0/24 | Direct | GE0/0/0.1 | 192.168.1.254 |
| 192.168.2.0/24 | Direct | GE0/0/0.1 | 192.168.2.254 |

*(Note: the source table lists the interface for both the 192.168.1.0/24 and 192.168.2.0/24 direct routes as "GE0/0/0.1." Given PC1/PC2 are on separate VLANs (10 and 20) behind separate sub-interfaces, the second row is very likely meant to read "GE0/0/0.2" — this looks like a typo/OCR artifact in the source slide. Transcribed here exactly as it appears; flagging rather than correcting.)*

### Configuration Example — Procedure (1)

1. Configure VLANs on the switch. The configuration details are not provided.
2. Create VPN instances for the production and management networks and configure the IPv4 address family for each VPN instance.

```
[R1]ip vpn-instance production
[R1-vpn-instance-production]ipv4-family
[R1-vpn-instance-production-af-ipv4]quit
[R1-vpn-instance-production]quit
[R1]ip vpn-instance management
[R1-vpn-instance-management]ipv4-family
[R1-vpn-instance-management-af-ipv4]quit
[R1-vpn-instance-management]quit
```

### Configuration Example — Procedure (2)

3. Bind involved interfaces to the VPN instances.

```
[Huawei]interface GigabitEthernet 0/0/0.1
[Huawei-GigabitEthernet0/0/0.1]ip binding vpn-instance production
Info: All IPv4 related configurations on this interface are removed!
//After an interface is bound to an instance, the IP address of the
interface is deleted and has to be reconfigured.
[Huawei-GigabitEthernet0/0/0.1]ip address 192.168.1.254 24
[Huawei-GigabitEthernet0/0/0.1]quit
[Huawei]interface GigabitEthernet 0/0/0.2
[Huawei-GigabitEthernet0/0/0.2]ip binding vpn-instance management
Info: All IPv4 related configurations on this interface are removed!
[Huawei-GigabitEthernet0/0/0.2]ip address 192.168.2.254 24
[Huawei-GigabitEthernet0/0/0.2]quit
```

### Configuration Example — Procedure (3)

4. Configure static routes and bind them to the instance.

```
[R1]ip route-static vpn-instance production 192.168.100.0 24 192.168.101.254
[R1]ip route-static vpn-instance management 192.168.200.0 24 192.168.102.254
```

5. Verify the configuration.

```
[R1] display ip routing-table vpn-instance production
Route Flags: R - relay, D - download to fib
------------------------------------------------------------------------------
Routing Tables: production
        Destinations : 5        Routes : 5
Destination/Mask    Proto  Pre  Cost  Flags  NextHop         Interface
192.168.100.0/24    Static 60   0     RD     192.168.101.254 GigabitEthernet0/0/1
```

## Quiz

1. (Single) At which of the following layers can VRF technology be used to implement isolation? ( )
   A. Physical layer
   B. Network layer
   C. Data link layer
   D. Application layer

2. (T or F) By default, all Layer 3 interfaces on Huawei data communication products belong to the root instance. ( )
   A. True
   B. False

**Answers:**
1. B
2. A

## Summary

- VRF technology implements logical isolation between different networks on the same physical device. When multiple VRF instances are deployed on the physical device, each VRF instance is equivalent to a virtual network device. The interfaces and routes between VRF instances are isolated. When a physical device is connected to the same network segment that belongs to different VPN instances, you have no worries about IP address conflicts.
- The VRF technology is widely used in firewall virtual systems and BGP/MPLS IP VPN scenarios.

