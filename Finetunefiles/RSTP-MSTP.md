# RSTP Implementation and Configuration

## Foreword

- On an Ethernet switching network, redundant links are used to implement link backup and enhance network reliability. The downside of this is that it may produce loops, leading to broadcast storms and an unstable MAC address table. As a result, communication on the network may deteriorate or even be interrupted. To prevent loops, IEEE introduced the Spanning Tree Protocol (STP), which is standardized as IEEE 802.1d.
- The convergence speed of an STP topology slows as the number of LANs increases. Therefore, IEEE introduced the Rapid Spanning Tree Protocol (RSTP), standardized as 802.1w, in 2001 to improve the network convergence speed.
- This document describes the improvements of RSTP compared with STP, working mechanism of RSTP, and RSTP configurations.

## Objectives

- On completion of this course, you will be able to:
  - Describe defects of STP technology.
  - Describe RSTP improvements compared with STP.
  - Describe the working mechanism of RSTP.
  - Perform basic RSTP configurations.

## Contents

1. **Introduction to RSTP**
   - STP Review and Defects
   - RSTP Overview
2. Improvements Made in RSTP
3. Working Mechanism of RSTP
4. RSTP Configurations

---

## 1. Introduction to RSTP

### STP Review and Defects

### Review: STP Implementation

**Diagram description:** A triangle topology with three switches: SW1 (root bridge) at the top, SW2 at bottom left, SW3 at bottom right. SW1 connects to both SW2 and SW3, and SW2 connects to SW3. Each link between SW1-SW2 and SW1-SW3 is labeled "Hello Time: 2s" with a configuration BPDU circle icon shown flowing from SW1 outward. The SW2-SW3 link shows a configuration BPDU icon flowing in one direction (from SW2 to SW3, marked with an arrow), representing the downlink relationship.

**STP Configuration BPDUs (side panel):**
- STP transmits configuration BPDUs between switches to elect the root switch (or root bridge) and determine the role and status of each switch port.
  - Each switch actively sends configuration BPDUs during initialization.
  - After the network topology becomes stable, only the root bridge proactively sends configuration BPDUs. Other bridges send configuration BPDUs only after receiving configuration BPDUs from uplink devices.
- A configuration BPDU contains parameters such as the bridge ID, path cost, and port ID.

**Format of configuration BPDUs (table):**

| PID | PVI | BPDU Type | Flag | Root ID | RPC | Bridge ID | Port ID | Message Age | Max Age | Hello Time | Forward Delay |
|-----|-----|-----------|------|---------|-----|-----------|---------|--------------|---------|------------|----------------|

**Handwritten annotation on slide:** "Very important, after the stp is formed, only the root bridge will be sending BPDU but before or let say before STP form, na all of them"

**Body text below the slide:**

- Flooding of configuration BPDUs:
  - During generation of the STP tree, all STP switches generate and send configuration BPDUs periodically (Hello Time, 2s by default). All STP switches consider themselves as the root bridge.
  - When BPDUs are flooded and collected, switches compare information in BPDUs and elect the root bridge.
  - After the STP tree is formed, only the root bridge generates and sends configuration BPDUs periodically (2s by default). A non-root bridge periodically receives configuration BPDUs from its root port, immediately generates configuration BPDUs, and sends the configuration BPDUs through its designated port. During the process, configuration BPDUs from the root bridge pass through the other switches hop by hop. As shown in the figure, the link between SW1 and SW2 is the uplink of SW2, and the link between SW2 and SW3 is the downlink of SW2.
- Packet format:
  - Parameters in BPDUs are classified into the following types:
  - Type 1: BPDU identifiers, including Protocol ID, Protocol version ID, BPDU Type, and Flag.
    - Protocol ID (PID): The value has 2 bytes and is always 0x000.
    - Protocol version ID (PVI): The value has 1 byte and is always 0x00.
    - BPDU Type: The value has 1 byte and is always 0x00.

> **[PAGE GAP — page 606 missing from source PDF]**
> The export jumps from page 605 directly to page 607. Based on context, the missing page likely continues the "packet format" discussion of configuration BPDU parameter types (Type 2 and beyond — Root ID, RPC, Bridge ID, Port ID, Message Age, Max Age, Hello Time, Forward Delay field definitions) that was in progress at the end of page 605. Please re-upload a complete export to fill this gap.

### Review: STP Tree Generation Process

**Diagram description:** A triangle topology with SW1 (root bridge) at top with two Designated (D) ports, SW2 at bottom left with a Root (R) port and a Designated (D) port, and SW3 at bottom right with a Root (R) port and a Non-designated (blocked, shown with a red "no" circle icon) port. The link between SW2 and SW3 shows the blocked port on the SW3 side. A callout arrow labeled "role elected things to use" points to the "Four Steps of STP Calculation" panel.

**Four Steps of STP Calculation (side panel):**
- Roles are elected by comparing the following four parameters:
  - Root bridge ID, root path cost, bridge ID, and port ID
1. Elect the root bridge.
2. Elect the root port.
   - Elect a root port on each non-root-bridge.
3. Elect a designated port.
   - Elect a designated port for each network segment.
4. Block non-designated ports.
   - Block all the remaining non-root and non-designated ports on switches.

**Legend:** R = Root port, D = Designated port, ⊘ = Non-designated port

**Body text below the slide:**

- STP working mechanism:
  - On a switching network with loops, switches run STP to automatically generate a loop-free working topology, which is also called an STP tree. A tree node is a specific switch, and a tree branch is a specific link.
- STP uses the following four steps to prevent Layer 2 loops (a spanning tree is generated):
  - Elect a root bridge on a switching network; elect a root port on each non-root bridge; elect a designated port for each network segment; block all the remaining non-root and non-designated ports (alternate ports) on switches.
- How is an STP tree generated?
  - Compare the root bridge ID, root path cost, bridge ID, and port ID. A smaller value indicates a higher priority. These parameters are all fields in BPDUs.
    - Root bridge election: The device with the smallest root bridge ID is the root bridge.
    - Root port election: The system compares the RPC, peer BID, peer PID, and local PID in sequence and selects the port with the smallest value.
    - Designated port election: The system compares the RPC, local BID, and local PID in sequence and selects the port with the smallest value.
    - After the root port and designated port are determined, all the remaining non-root ports and non-designated ports on the switch are blocked.

### Review: STP Port State Transition

**Diagram description:** A state machine diagram showing five states in a vertical flow: Disabled → Blocking → Listening → Learning → Forwarding, with numbered transition arrows (1–5) connecting them, including loop-back arrows returning to Disabled/Blocking from any state. Two eye icons appear at the top of the slide (decorative "watch carefully" markers).

**STP Port State Transition (side panel):**
1. The port is initialized or enabled and enters the Blocking state.
2. If the port is selected as the root port or designated port, it enters the Listening state.
3. The port enters the Learning state after the Forward Delay timer expires. After another Forward Delay timer, the port enters the Forwarding state.
4. If a port is no longer the root port or designated port, it enters the Blocking state.
5. The port is disabled or the link is terminated.

**Body text below the slide:**

- STP defines five port states: Disabled, Blocking, Listening, Learning, and Forwarding, depending on whether the port can receive and send STP BPDUs and whether the port can forward user data frames.
  - Disabled: The port cannot receive or send any frame. That is, the port does not process BPDUs or forward user data frames. The port is in Down state.
  - Blocking: The port can only receive and process BPDUs but cannot send BPDUs or forward user data frames.
  - Listening: The port can receive and send BPDUs but cannot learn MAC addresses or forward user data frames. This is a transitional state. It is used to determine the port role, elect the root bridge, root port, and designated port, and prevent temporary loops.
  - Learning: The port can receive and send BPDUs, learn MAC addresses, and create a MAC address table based on received user data frames. However, the port cannot forward user data frames. This is a transitional state, which is used to prevent the flooding of a large number of user data frames on the network when the MAC address table is not created.
  - Forwarding: Ports can receive and send BPDUs, or they can learn MAC addresses, while forwarding user data frames. Only the root port and designated port can enter the Forwarding state.

**Continued body text (next page):**

- Port state transition:
  - When an STP switch port is initially started, it changes from the Disabled state to the Blocking state. In the Blocking state, the port only receives and analyzes BPDUs, but does not send BPDUs.
  - During the entire process, a port enters a Disabled state once it is shut down or a link fault occurs.
  - If the port is selected as the root port or designated port, the port enters the Listening state. In this state, the port receives and sends BPDUs. This state lasts for an interval of the Forward Delay timer (15s by default), which prevents temporary loops. Temporary loops may occur on the network because the calculation processes of the STP trees are not synchronized.
  - If a port is determined as a non-root port or a non-designated port during port state transition, the port immediately returns to the Blocking state.
  - If the port does not return to the Disabled state due to an exception, the port enters the Learning state. In this case, the port can receive and send BPDUs and start to construct a MAC address table to prepare for forwarding user data frames. This state lasts for an interval of the Forward Delay timer. This prevents a large number of user data frames from being flooded before the MAC address table of the switch is established.
  - Finally, the port enters the Forwarding state and starts to forward user data frames.

### Disadvantages of STP

- STP ensures a loop-free network but is slow to converge, leading to service quality deterioration. If the network topology changes frequently, connections on the STP network are frequently torn down, causing frequent service interruption.
- STP has the following disadvantages:
  - STP does not differentiate between port roles according to their states, making it difficult for less experienced administrators to learn about and deploy this protocol.
    - Ports in Listening, Learning, and Blocking states are the same for users because they are all prevented from forwarding service traffic.
    - In terms of port use and configuration, the essential differences between ports lie in the port roles but not port states.
  - The STP algorithm does not determine topology changes until the timer expires, delaying network convergence.
  - The STP algorithm requires the root bridge to send configuration BPDUs after the network topology becomes stable, and other devices process and spread the configuration BPDUs through the entire network. This also delays convergence.

### STP Dependency on Timers

**Diagram description:** Two side-by-side triangle topologies. Left panel "Initialization": SW1 (root bridge) at top with two Designated (D) ports, SW2 bottom-left with Root (R) and Designated (D) ports, SW3 bottom-right with Root (R) and blocked port. Right panel "Terminal Access": same topology, but a new access device "HostA" is shown connecting to SW2 via its Designated port, with an arrow pointing from the note text down to that connection point.

**Left panel text:** STP uses a timer to prevent temporary loops. After STP elects a port role, even if the port is a designated port or a root port, it still needs to wait for two intervals of the Forward Delay timer (30s) before forwarding packets.

**Right panel text:** In the STP environment, after a terminal or server is connected to the network, the port needs to switch from the Disabled state to the Blocking, Listening, Learning, and Forwarding states in sequence. In this case, HostA needs to wait for two intervals of the Forward Delay timer before accessing the network service.

**Handwritten annotation:** "Read it, very important. Assume a host connect to a network now, and the port is in blocking state, the host has to wait till the port transit from blocking state to forwarding state."

### Slow STP Reconvergence

**Diagram description:** Two side-by-side triangle topologies. Left panel "Direct Link Fault": SW1 (root bridge) at top with two Designated (D) ports connecting down to a single switch SW2, one link marked with an "X" (fault) and the port shown blocked (red no-entry icon) on SW2's other port. Right panel "Indirect Link Fault": full triangle SW1-SW2-SW3, with the SW1-SW2 link marked with an "X" fault, and SW3's blocked port shown with a red no-entry icon; a blue arrow indicates the path SW3 would need to re-route through.

**Direct Link Fault (side panel):**
- The blocked port changes from the Blocking state to the Listening and Learning states in sequence, and finally enters the Forwarding state.
- If the directly connected link is faulty, the port status changes to Forwarding after 30s.

**Indirect Link Fault (side panel):**
- Because the blocked port does not receive BPDUs with a higher priority, the port changes from Blocking to Listening, Learning, and Forwarding in sequence after 20s.
- If the indirect link is faulty, the recovery time is about 50s, which is equal to the value of the Max Age timer plus twice the value of the Forward Delay timer.

**Handwritten annotation:** "Confusing, not clear."

**Body text below the slide:**

- Direct link fault:
  - There are two links between two switches. When the network is stable, SW2 detects that the link of the root port is faulty. The blocked port starts the port state transition and finally enters the Forwarding state to forward user traffic.
- Indirect link fault:
  - When the network is normal, the blocked port of SW3 periodically receives BPDUs from the root bridge.
  - When the link between SW1 and SW2 is faulty, SW2 can detect the fault immediately. In this case, SW2 considers itself as the new root bridge and sends its own configuration BPDU to SW3. The root bridge ID is its own bridge ID.
  - The blocked port on SW3 receives the configuration BPDU, but the configuration BPDU is inferior to the configuration BPDU buffered on the port. Therefore, SW3 ignores the configuration BPDU.

  **Handwritten annotation:** "Not clear."

  - When the Max Age timer expires, the configuration BPDUs buffered on SW3 age and SW3 starts to send configuration BPDUs to SW2. The configuration BPDUs are triggered by the configuration BPDUs sent by the root bridge SW1. The value of the root bridge ID field in the configuration BPDUs is the bridge ID of SW1.
  - After SW2 receives the configuration BPDU, it parses the BPDU and determines that SW1 is the root bridge. Therefore, SW2 changes the port connected to SW3 to the root port.

### STP Topology Change Mechanism

**Diagram description:** Two tree topologies shown side by side illustrating a before/after topology change scenario. Left tree: Root bridge at top branching into multiple switches, with a "New switch" (highlighted in orange/red) added at a lower level; arrows labeled "1. TCN BPDU," "2. Configuration BPDU with the TCA bit set to 1," and "3. Configuration BPDU with the TC bit set to 1" show the notification flowing up toward the root bridge. Right tree: same topology, showing the root bridge flooding "Delete MAC address entries" instructions and a "Configuration BPDU with the TC bit set to 1" cascading down to all switches, with "New switch" highlighted, and a "TCN BPDU" arrow flowing back up from a leaf switch.

**Caption under the two trees:** "Send TCN BPDUs and configuration BPDUs with the TCA bit set to 1" (left) / "Root bridge sends configuration BPDUs with the TC bit set to 1" (right)

**Body text below the slide:**

- The STP topology change mechanism transmits topology change information to the root bridge, and then the root bridge floods the topology change information to downlink devices.
- STP processing when the topology changes:
  - When a switch detects a topology change, it notifies the root bridge of the spanning tree. The root bridge then floods the topology change information to the entire network.
  - Topology change process:
    - If a switch is added to the network and the working topology changes, the switch at the change point can directly detect the change through the port status, but other switches cannot directly detect the change.

    **Handwritten annotation:** "How? let lab it. or read about it."

    - The switch at the change point continuously sends TCN BPDUs to the uplink device through the root port at an interval of Hello time (2s by default) until it receives the configuration BPDUs with the TCA bit set to 1 from the uplink switch. The TCA bit is set to 1 to instruct the downlink device to stop sending TCN BPDUs.

    **Handwritten annotation:** "The switch that detect the topology changes keep sending the TCN BPDU to the root bridge through the root port of it until the root bridge reply with TCN bit set to 1"

    - After receiving a TCN BPDU, the uplink switch replies with a configuration BPDU with the TCA bit set to 1 through the designated port and sends TCN BPDUs to the uplink switch through the root port at an interval of Hello time.

    **Handwritten annotation:** "Uplink will reply with config BPDUs with TCA bit been set to 1 though the designated port. And send TCN BPDUs to the uplink switch through the root port"

    - This process repeats until the root bridge receives a TCN BPDU.

    **Handwritten annotation:** "this is talking about downlink switch that changes occur there"

    - After receiving the TCN BPDU, the root bridge sends a configuration BPDU in which the TC bit is set to 1 to notify all switches of the network topology change and instruct downlink devices to delete the bridge MAC address entries.

    **Handwritten annotation (bottom of page):** "So the other process is in bet the downlink and the uplink, the last line note is where the root bridge will work, read it well"

---

## Contents (repeated)

1. **Introduction to RSTP**
   - STP Review and Defects
   - RSTP Overview
2. Improvements Made in RSTP
3. Working Mechanism of RSTP
4. RSTP Configurations

### RSTP Overview

*(Slide header includes decorative clown emoji row: "Exam Part 🤡🤡🤡🤡🤡🤡🤡🤡🤡🤡" — likely indicating this slide/topic is emphasized as exam-relevant.)*

- RSTP defined in IEEE 802.1w was developed based on STP. RSTP optimizes STP in many aspects, provides a faster convergence speed, and is compatible with STP.
- RSTP has the following improvements:
  - Defines additional port roles to simplify the learning and deployment of STP.
  - Redefines port states.
  - Changes the configuration BPDU format and uses the Flags field to describe port roles.
  - Processes configuration BPDUs differently from STP.
  - Provides fast convergence.
  - Adds protection functions.

**Caption:** "Take note of this very well 👀"

**Body text below the slide:**

- RSTP can interoperate with STP, but doing so causes RSTP to lose its advantages, such as fast convergence.
  - On a network with both STP-capable and RSTP-capable devices, STP-capable devices discard RST BPDUs. If a port on an RSTP-capable device receives a configuration BPDU from an STP-capable device, the port switches to the STP mode and starts to send configuration BPDUs after two Hello timer intervals.
  - After STP-capable devices are removed, Huawei RSTP-capable devices can be switched back to the RSTP mode.

### RSTP Application on a Campus Network

**Diagram description:** A hierarchical campus network diagram. At the top, an "Internet" cloud connects to a pair of redundant firewall/security devices. Below that, a pair of Layer 3 switches/routers. Below that is the "Layer 3 network" boundary line. Below the boundary, the "Layer 2 network / RSTP" zone contains multiple pairs of aggregation switches, each connecting down to multiple access switches (shown with "..." indicating repeated access-layer switches), forming a redundant, meshed Layer 2 access topology where RSTP would run to prevent loops.

---

## Contents (repeated)

1. Introduction to RSTP
2. **Improvements Made in RSTP**
3. Working Mechanism of RSTP
4. RSTP Configurations

### Improvement 1: Port Role

**Annotations on slide (top right):**
- "NOTE: Root Port: Receives BPDUs from upstream (toward the root). Designated Port: Sends BPDUs downstream (away from the root)."
- "Only one Designated Port per segment, but each switch has one Root Port (except the root bridge)."
- "Alternate port: It's connected to a Designated Port on another switch" *(partial annotation, cut off at slide edge)*

**Diagram description:** Two side-by-side triangle topologies. Left panel "Alternate port": SW1 (root bridge) at top with two Designated (D) ports, SW2 bottom-left with Root (R) and Designated (D) ports, SW3 bottom-right with Root (R) port and an Alternate (A) port (highlighted). Right panel "Backup port": same topology, but SW2 and SW3 are both connected down to a shared network segment; SW2 has a Designated (D) port to that segment while SW3 has a Backup (B) port (highlighted) to the same segment.

**Left panel caption:** The alternate port is blocked after learning a configuration BPDU sent by another bridge. It is a backup of the root port and provides an alternate path from the designated bridge to the root switch.

**Right panel caption:** The backup port is blocked after learning a configuration BPDU sent by itself. It is a backup of the designated port and provides a backup path from the root switch to the corresponding network segment.

**Handwritten annotation:** "We normally use alternate port in a situation where we have another link to reach the root bridge, check the alternate port image on the right, purpose of it is to let it change to forwarding state immediately the root port failed. In simpler meaning, we use it in a situation where we have redundant link."

**Body text below the slide:**

- RSTP defines four port roles: root port, designated port, alternate port, and backup port.
- The functions of the root port and designated port are the same as those defined in STP. The alternate port and backup port are defined as follows:
  - From the perspective of configuration BPDU transmission:
    - An alternate port is blocked after learning a configuration BPDU sent from another bridge.
    - A backup port is blocked after learning a configuration BPDU sent from itself.
  - From the perspective of user traffic:
    - An alternate port acts as a backup of the root port and provides an alternate path from the designated bridge to the root bridge.
    - A backup port backs up a designated port and provides a backup path from the root bridge to the related network segment.
- After roles of all RSTP ports are determined, the topology convergence is completed.

**Handwritten annotations (bottom of page):**
- "In STP, only the Root Bridge sends BPDUs after convergence."
- "In RSTP, every switch sends BPDUs continuously."
- "Each port may send slightly different BPDUs based on its role and path"

### Improvement 2: Port States

- RSTP defines three states, depending on whether a port forwards user traffic and learns MAC addresses.
  - Discarding: The port does not forward user traffic or learn MAC addresses.
  - Learning: The port does not forward user traffic but learns MAC addresses.
  - Forwarding: The port forwards user traffic and learns MAC addresses.

**Table — STP vs RSTP port state / port role mapping:**

| STP Port State | RSTP Port State | Port Role |
|---|---|---|
| Forwarding | Forwarding | Root port or designated port |
| Learning | Learning | Root port or designated port |
| Listening | Discarding | Root port or designated port |
| Blocking | Discarding | Alternate port or backup port |
| Disabled | Discarding | Disabled port |

### Improvement 3: Configuration BPDU — RST BPDU

- RSTP configuration BPDUs use the Flag field in STP BPDUs to determine the port role.
- RSTP has the following changes except that the format of RSTP is the same as that of STP:
  - The value of the Type field is changed from 0 to 2. Devices running STP will discard configuration BPDUs sent from devices running RSTP.
  - The Flags field uses the six bits reserved in STP. This configuration BPDU is called a Rapid Spanning Tree Bridge Protocol Data Unit (RST BPDU).
- RST BPDU format (table with a callout showing 0x02 pointing to the BPDU Type field):

| PID | PVI | BPDU Type | Flag | Root ID | RPC | Bridge ID | Port ID | Message Age | Max Age | Hello Time | Forward Delay |
|---|---|---|---|---|---|---|---|---|---|---|---|

**Flag byte bit breakdown (table):**

| Bit7 | Bit6 | Bit5 | Bit4 | Bit3 | Bit2 | Bit1 | Bit0 |
|---|---|---|---|---|---|---|---|
| TCA | Agreement | Forwarding | Learning | Port Role (2 bits: Bit3–Bit2) | | Proposal | TC |

Port Role = 00 Unknown / 01 Alternate/Backup port / 10 Root port / 11 Designated port

**Body text below the slide:**

- The format of an RST BPDU is different from that of an STP configuration BPDU, including the BPDU type and Flag field.
  - BPDU Type: 1 byte. The value of an RST BPDU is 0x02.
  - Flag: 1 byte
    - Bit 7: TCA, indicating that the topology change is acknowledged
    - Bit 6: Agreement, which is used in the P/A mechanism
    - Bit 5: Forwarding
    - Bit 4: Learning
    - Bits 3 and 2: port role
      - 00 — unknown port
      - 01 — alternate or backup port
      - 10 — root port
      - 11 — designated port
    - Bit 1: Proposal, which is used in the P/A mechanism
    - Bit 0: TC, indicating a topology change

### Improvement 4: Configuration BPDU Processing (1)

**Diagram description:** Triangle topology SW1 (root bridge) at top, SW2 bottom-left, SW3 bottom-right, all links labeled "Hello Time: 2s" with RST BPDU circle icons flowing along all three links (SW1→SW2, SW1→SW3, and SW2→SW3), indicating all switches actively send BPDUs continuously, not just the root.

**Configuration BPDU Transmission After the Topology Becomes Stable (side panel):**
- RSTP improves the transmission mode of configuration BPDUs.
- RSTP allows non-root bridges to send configuration BPDUs at an interval of Hello Time after the topology becomes stable, regardless of whether they received configuration BPDUs from the root bridge.
- In STP, the root bridge sends configuration BPDUs at an interval of Hello Time after the topology becomes stable. Non-root bridges send configuration BPDUs only after they have received configuration BPDUs from uplink devices. This complicates the STP calculation and slows down network convergence.

### Improvement 4: Configuration BPDU Processing (2)

**Diagram description:** Triangle topology SW1 (root bridge) at top, SW2 bottom-left, SW3 bottom-right. The SW1-SW2 link is drawn as broken/faulty ("Unidirectional link fault," shown via a break icon in the wire at the top of the frame with an X mark), while an RST BPDU is shown flowing SW2→SW3 (dashed arrow) and a note box points from SW2 down.

**Note box on slide:** "After 6s, the device considers the neighbor invalid and sends its own RST BPDU."

**Shorter BPDU Timeout Interval (side panel):**
- If a port does not receive any configuration BPDU from the uplink device within the timeout interval (three intervals of the Hello timer), the device considers that the negotiation with the neighbor fails.
- STP needs to wait for the time specified by the Max Age timer.

### Improvement 4: Configuration BPDU Processing (3)

**Diagram description:** Triangle topology SW1 (root bridge) at top, SW2 bottom-left, SW3 bottom-right. The SW1-SW3 link is marked "Link fault" with an X. Arrows show SW2 sending an RST BPDU circle toward SW3, and SW3 sending a response RST BPDU circle back toward SW2 (shown as a dashed reverse arrow).

**Note boxes on slide:**
1. "If SW2 does not receive any RST BPDU from the uplink device, it considers itself as the root bridge and sends its own BPDU."
2. "After receiving an inferior BPDU, SW3 compares it with the cached RST BPDU and immediately responds with its own RST BPDU."

**Processing an Inferior BPDU (side panel):**
- When a port receives an RST BPDU from the uplink designated bridge, the port compares the cached RST BPDU with its own RST BPDU.
- If the number of RST BPDUs cached on the port is superior to the received RST BPDU, the port discards the received RST BPDU and immediately responds with the cached RST BPDU. This speeds up network convergence.
- In STP, only the designated port can process the inferior BPDU immediately.

**Body text below the slide:**

- STP
  - In STP, only the designated port immediately processes inferior BPDUs. Other ports ignore the inferior BPDUs. After the Max Age timer expires, the buffered inferior BPDUs age out and these ports send their superior BPDUs to implement a new round of topology convergence.
- RSTP
  - RSTP processes inferior BPDUs without using any timer (no longer depending on BPDU aging) to implement topology convergence. In addition, any port in RSTP can process inferior BPDUs to speed up topology convergence.

### Improvement 5: Fast Convergence Mechanism (1)

**Diagram description:** Two side-by-side triangle topologies. Left panel "Fast Switchover of the Root Port": SW1 (root bridge) at top with two Designated (D) ports, SW2 bottom-left with Root (R) and Designated (D) ports, SW3 bottom-right with an Alternate (A) port shown transitioning to a Root (R) port (indicated with an arrow labeled "R"). Right panel "Fast Switchover of the Designated Port": SW1 (root bridge) at top with two Designated (D) ports, SW2 bottom-left with Root (R), Designated (D), and Backup (B) ports, SW3 bottom-right with a Root (R) port; an arrow shows the Backup port on SW2 transitioning to a Designated port, with SW3's designated port shown fading out (dashed "D").

**Left panel caption:** If a root port fails, the best alternate port becomes the root port and enters the Forwarding state. This is due to the fact that the network segment connected to this alternate port has a designated port that can access the root bridge.

**Right panel caption:** If a designated port fails, the best backup port becomes the designated port and enters the Forwarding state. A backup port backs up a designated port and provides a backup path from the root bridge to the related network segment.

**Handwritten annotation (long note):** "the materials said ny port can send config BPDU in RSTP, in the case above at the left, if the alternate port become the root port, then it will be able to reach the root bridge through which port? it will be able to reach root bridge though SW2, which mean the root port will send BPDU right? and we know root port always receive nhi its Designated that do send BPDU, whats going to happened? in these case does that mean when the convergence stable and the root bridge send the BPDU then the non root bridge too will be sending BPDU at an interval of 2s even if they didn't receive from root bridge right? and with this in the case where one port has close on the SW3, how will the other switch know? or because the sw2 can send bpdu to the sw2, sw2 might be able to tell the root bridge the sw3 link has fault? or the sw1 which is the root bride will know if it doesn't receive any bpdu from the sw3 again from sw3 root since it has fault now"

**Second handwritten annotation:** "This is due to the fact that the network segment connected to this alternate port has a designated port that can access the root bridge. But is there any case where the designated port will not have access to the root bridge? or is there a case where the switch will not have a designated port?"

### Improvement 5: Fast Convergence Mechanism (2)

**Diagram description:** Triangle topology SW1 (root bridge) at top, SW2 bottom-left, SW3 bottom-right, with an Edge (E) port shown on SW3 connecting down to a PC/terminal icon.

**Edge Port (side panel):**
- RSTP introduces the edge port. If a port is located at the edge of a network and directly connects to a terminal, it can be configured as an edge port.
- An edge port does not participate in RSTP calculation and can directly enter the Forwarding state from the Discarding state.
- An edge port becomes a common STP port once it is connected to a switching device and receives a configuration BPDU. The spanning tree needs to be recalculated, which leads to network flapping.

**Body text below the slide:**

- The Up and Down states of an edge port do not change the network topology.

### Improvement 5: Fast Convergence Mechanism (3)

**Diagram description:** Triangle topology showing SW1 (root bridge) at top with a Designated (D) port, SW2 at bottom-left with a Root (R) port. Arrows labeled "Proposal=1" (SW1→SW2) and "Agreement=1" (SW2→SW1) illustrate the handshake. Two callout boxes read "Rapidly enter the Forwarding state" pointing at both the SW1 designated port and the SW2 root port.

**P/A Mechanism (side panel):**
- The Proposal/Agreement (P/A for short) mechanism enables the uplink port to quickly transition to Forwarding state.
- In RSTP, after a port is elected as the designated port, the port enters the Discarding state and then rapidly enters the Forwarding state through the P/A mechanism.
- In STP, the port enters the Forwarding state after at least one interval of Forward Delay (Learning state).

**Body text below the slide:**

- Although STP can select designated ports quickly, to prevent loops, all ports must wait at least one interval of the Forward Delay timer before forwarding traffic.
- RSTP solves this problem by blocking non-root ports to prevent loops. The P/A mechanism shortens the time that an uplink port waits before transitioning to Forwarding state.

### P/A Mechanism (1)

**Diagram description:** Two side-by-side diagrams. Left: Root bridge SW1 at top, connected down to SW2 by a single line labeled "① Add a link"; SW2 has three downlink ports shown as Alternate (A), Designated (D), and Edge (E). Right: same topology but now shows two parallel lines between SW1 and SW2, both labeled with port role "D" (designated), and an arrow labeled "② Send RST BPDUs."

**Body text below the slide:**

- A link is added between root bridge SW1 and SW2.
- The three downlink ports of SW2 are the alternate port, designated port in Forwarding state, and edge port, respectively.
- The two ports between SW1 and SW2 become designated ports and send RST BPDUs.

### P/A Mechanism (2)

**Diagram description:** Two side-by-side diagrams continuing the P/A negotiation. Left: SW1 (root bridge) with Designated (D) port sending "Proposal=1" down to SW2, whose corresponding port is labeled Root (R); a callout reads "③ SW1 and SW2 compare the received RST BPDUs." Right: SW1's port shown discarding, then sending/receiving "Agreement=1" back from SW2; SW2's downlink ports shown as Alternate (unchanged), Designated (blocked, in parentheses "Blocked port"), and Edge (unchanged); a callout reads "④ The downlink port enters the synchronization state, and the root port enters the Forwarding state."

**Body text below the slide:**

- SW2's port connected to SW1 receives a superior RST BPDU, so the port becomes a root port and stops sending RST BPDUs.
- The designated port of SW1 enters the Discarding state and sends an RST BPDU with the Proposal bit set to 1.
- After receiving the RST BPDU with the Proposal bit set to 1 from the root bridge, SW2 starts to synchronize all its ports.
- After all ports are synchronized, all downlink ports (except edge ports) enter the Discarding state, and the uplink root port enters the Forwarding state and sends an RST BPDU with the Agreement bit set to 1 to SW1. After SW1 receives the BPDU, the designated port immediately enters the Forwarding state.

**Body text (continued, additional note below diagram):**

- The downlink ports of SW2 are synchronized as follows: The alternate port status remains unchanged; the edge port does not participate in calculation; the non-edge designated port is blocked.

### P/A Mechanism (3)

**Diagram description:** Two side-by-side diagrams. Left: Root bridge SW1 with Designated (D) port shown, connected to SW2 (Root R, Alternate A, Designated D, Edge E ports); callout "⑤ The designated port immediately enters the Forwarding state." Right: same topology with a callout "⑥ The downlink device continues the P/A process."

**Body text below the slide:**

- The RST BPDU with the Agreement bit set to 1 received by SW1 is a response to the sent RST BPDU with the Proposal bit set to 1 on SW1. Therefore, the designated port immediately enters the Forwarding state.
- The downlink device continues P/A negotiation.

### Improvement 6: Topology Change Mechanism

**Diagram description:** Triangle topology with SW1 (root bridge) at top (Designated ports, one shown blocked with a red no-entry icon indicating a link failure), SW2 bottom-left, SW3 bottom-right. Step 1 shows "A link fails" at the top link. Steps 2–4 show, in sequence: SW3 enabling a timer and clearing MAC addresses learned by the port; SW3 sending RST BPDUs with the TC bit set to 1; SW2 clearing MAC addresses learned by all ports except the receive port.

**Topology Change Mechanism (side panel):**
- When detecting a topology change, RSTP devices react as follows:
  - The local device starts a TC While timer on each non-edge designated port and root port. The TC While timer value is twice the Hello Time value. Within the TC While time, the local device deletes MAC address entries learned on ports whose states have changed.
  - These ports send out RST BPDUs with the TC bit set to 1. When the TC While timer expires, the ports stop sending RST BPDUs.
  - When other switches receive RST BPDUs, they clear MAC address entries learned on all their ports except the ports that receive the RST BPDUs. These switches start a TC While timer on each non-edge designated port and repeat the preceding process.
- In this manner, RST BPDUs are flooded on the network.

**Body text below the slide:**

- If the topology of an STP network changes, TCN BPDUs are first sent to the root bridge. Then, the root bridge notifies the topology change and floods the configuration BPDUs with the TC bit set to 1.
- RSTP uses a new topology change mechanism to rapidly flood RST BPDUs with the TC bit set to 1.
- In the figure:
  - If the root port of SW3 cannot receive RST BPDUs from the root bridge, the alternate port quickly becomes the new root port, starts the TC While timer, and clears MAC addresses learned on ports whose states have changed. Then, the new root port sends RST BPDUs with TC bits set to 1.
  - After receiving the RST BPDU, SW2 clears the MAC addresses learned by all ports except the receive port, starts the timer, and sends the RST BPDU with the TC bit set to 1.
  - RST BPDUs are flooded on the entire network.

### Improvement 7: Protection Functions (1)

**Diagram description:** Triangle topology SW1 (root bridge) at top, SW2 bottom-left, SW3 bottom-right, with SW3 having an Edge (E) port connecting down through an intermediary device to a PC. The intermediary device is labeled "Device occupied by malicious user," shown sending a "New device's RST BPDU" up into SW3's edge port. A callout box reads "Enable BPDU protection."

**BPDU protection (side panel):**
- On an RSTP network, an edge port does not receive RST BPDUs in normal situations. If a switching device receives malicious RST BPDUs on an edge port, the switching device automatically sets the edge port to a non-edge port and performs STP calculation. This causes network flapping.
- BPDU protection enables a switch to set the state of an edge port to Error-Down if the edge port receives an RST BPDU. In this case, the port remains as the edge port, and the switch sends a notification to the NMS.

**Body text below the slide:**

- On a switching device, ports directly connected to a user terminal such as a PC or file server are edge ports.
- As shown in the figure:
  - SW3 is connected to a host and is configured as an edge port.
  - Then the host is used by a malicious user to forge RST BPDUs to attack SW3. Therefore, the edge port receives the RST BPDUs, loses the edge port role, and calculates the spanning tree.

### Improvement 7: Protection Functions (2)

**Diagram description:** Triangle topology SW1 (root bridge) at top with two Designated (D) ports, SW2 bottom-left, SW3 bottom-right. A callout box "Enable root protection" points at SW1's designated port. An arrow labeled "Superior RST BPDU" flows from a "Device occupied by a malicious user" annotation near SW2 up toward SW1.

**Root protection (side panel):**
- If root protection is enabled on a designated port, the port role cannot be changed.
- Once a designated port that is enabled with root protection receives superior RST BPDUs, the port enters the Discarding state and does not forward packets. If the port does not receive any superior RST BPDUs within a specified period (two intervals of the Forward Delay timer by default), the port automatically enters the Forwarding state.
- Root protection ensures that the role of the root bridge does not change due to network problems.

**Body text below the slide:**

- The root bridge on a network may receive superior RST BPDUs due to incorrect configurations or malicious attacks. When this occurs, the root bridge can no longer serve as the root bridge and the network topology will incorrectly change. As a result, traffic may be switched from high-speed links to low-speed links, leading to network congestion.
- As shown in the figure:
  - When the network is stable, SW1 functions as the root bridge and sends the optimal RST BPDU to downlink devices.
  - If SW2 is occupied by a malicious user, for example, the bridge priority of SW2 is modified to make SW2 have a higher bridge priority than SW1, SW2 sends its own RST BPDU.
  - After receiving the RST BPDU, the designated port of SW1 recalculates the spanning tree. SW1 then loses its role as the root bridge, causing the topology change.

### Improvement 7: Protection Functions (3)

**Diagram description:** Triangle topology SW1 (root bridge) with two Designated (D) ports; a broken/faulty link icon ("LINK" with an X, "Unidirectional link fault") shown at the top pointing toward SW1's connection to SW3. SW2 bottom-left with Root (R) and Designated (D) ports; SW3 bottom-right with an Alternate (A) port transitioning to Root (R), and a callout box "Enable loop prevention." A circular "Loop" arrow icon is shown between SW2 and SW3 indicating a potential loop condition. Numbered callouts: "① The unidirectional link is faulty, and packets sent by SW1 cannot reach SW3." "② The alternate port of SW3 becomes the root port and enters the Forwarding state. The root port is switched to the designated port."

**Loop Prevention (side panel):**
- If the root port or alternate port does not receive BPDUs from the uplink device for a long time, the device enabled with loop prevention sends a notification to the NMS. If the root port is used, the root port enters the Discarding state and becomes the designated port. If the alternate port is used, the alternate port keeps blocked and becomes the designated port. In this case, loops will not occur.
- After link congestion is cleared or unidirectional link failures are rectified, the port receives BPDUs for negotiation and restores its original role and status.

**Body text below the slide:**

- On an RSTP network, a switching device maintains the states of the root port and blocked ports based on RST BPDUs received from the uplink switching device. If the ports cannot receive RST BPDUs from the uplink switching device because of link congestion or unidirectional link failures, the switching device re-selects a root port.
- As shown in the figure, when the unidirectional link between SW1 and SW3 fails, because the root port on SW3 does not receive BPDUs from the uplink device within the timeout interval, the alternate port becomes the root port and the root port becomes the designated port. As a result, a loop occurs.

### Improvement 7: Protection Functions (4)

**Diagram description:** Triangle topology SW1 (root bridge) at top with two Designated (D) ports. SW2 bottom-left with a Root (R) and Designated (D) port, callout "Enable TC BPDU attack defense" pointing at it. SW3 bottom-right, labeled "Device occupied by a malicious user," with an Alternate (A) port, sending RST BPDUs with TC=1 toward SW2 (shown via a dashed arrow labeled "RST BPDU, TC=1"). Numbered callouts: "① Send a large number of RST BPDUs with the TC bit set to 1." "② Frequently deleting MAC address entries causes a heavy burden on the device."

**TC BPDU attack defense (side panel):**
- After enabling TC BPDU attack defense on a switching device, you can set the number of TC BPDUs that the device can process within a given period of time.
- If the number of TC BPDUs that the switching device receives within a given time period exceeds the specified threshold, the switching device processes only the specified number of TC BPDUs.
- After the time period expires, the device processes all the excess TC BPDUs in a batch. In this way, the switching device does not need to frequently delete MAC entries.

**Body text below the slide:**

- A switching device deletes its MAC address entries after receiving TC BPDUs. If an attacker sends a large number of malicious RST BPDU with the TC bit set to 1 to the switching device within a short period, the device will constantly delete MAC address entries. This increases the load on the switching device and threatens network stability.
- As shown in the figure:
  - If SW3 is occupied by a malicious user, the attacker forges a large number of RST BPDUs with TC bit set to 1 and sends them. After receiving the RST BPDUs, SW2 frequently deletes MAC address entries, which causes a heavy burden.

---

## Contents (repeated)

1. Introduction to RSTP
2. Improvements Made in RSTP
3. **Working Mechanism of RSTP**
4. RSTP Configurations

### RSTP Topology Convergence Process (1)

**Diagram description:** Triangle topology with SW1 (BID: 32768.0c-00-00-0a-00-01) at top, both ports shown as Designated (D). SW2 (BID: 32768.0c-00-00-0a-00-02) at bottom-left, both ports Designated (D). SW3 (BID: 32768.0c-00-00-0a-00-03) at bottom-right, both ports Designated (D). RST BPDU icons shown flowing along all links between all three switches.

**Numbered step (side panel):**
1. After RSTP is enabled on a switch, the switch considers itself as the root bridge and sends RST BPDUs.
   - All ports are designated ports and are in Discarding state.

**Body text below the slide:**

- The RSTP convergence process is similar to the STP convergence process.
- During network initialization, all RSTP switches on the network consider themselves as the root bridge, configure each port as a designated port, and send RST BPDUs. SW1 has the optimal bridge ID and is elected as the root bridge.

### RSTP Topology Convergence Process (2)

**Diagram description:** Triangle topology with SW1 (root bridge) at top with a Designated (D) port. An arrow labeled "Proposal=1" flows from SW1 down toward SW2 (labeled "Uplink"), and an arrow labeled "Agreement=1" flows back up from SW2 to SW1. SW2's port is shown transitioning to Root (R), with a "Downlink" label pointing at SW2's other port (toward SW3, shown as blocked with a red no-entry icon). SW3 is at bottom-right.

**Numbered step (side panel):**
2. The uplink quickly enters the Forwarding state through the P/A mechanism.
   - After receiving a superior RST BPDU, SW2 considers that SW1 is the root bridge and the port on SW2 becomes the root port instead of the designated port. Then SW2 stops sending RST BPDUs.
   - The port on SW1 enters the Discarding state and sends RST BPDUs with the Proposal bit set to 1. After receiving the BPDU, SW2 blocks all ports except the edge port. This process is called synchronization.
   - After ports on SW2 synchronize information, the root port enters the Forwarding state and sends an RST BPDU with the Agreement bit set to 1 to SW1. After SW1 receives the BPDU, the designated port immediately enters the Forwarding state.

**Body text below the slide:**

- Each switch that considers itself as the root bridge generates an RST BPDU to negotiate the port status on the specified network segment. The Proposal bit in the Flag field of the RST BPDU needs to be set.
- When a port receives an RST BPDU, it compares the received RST BPDU with the local RST BPDU. If the local RST BPDU is superior to the received RST BPDU, the port discards the received RST BPDU and sends a local RST BPDU with the Proposal bit set to 1 to reply to the peer device.
- As shown in the preceding figure, the link between SW1 and SW2 is used as an example to describe the uplink convergence process.

### RSTP Topology Convergence Process (3)

**Diagram description:** Triangle topology with SW1 (root bridge) at top with two Designated (D) ports (labeled "Uplink" pointing at each). SW2 bottom-left with Root (R) and Designated (D) ports (labeled "Downlink"). SW3 bottom-right with a Root (R) port and a blocked port (Alternate, shown with red no-entry icon), labeled "Blocked port." An arrow labeled "Proposal=1" flows between SW2 and SW3's downlink interconnection.

**Numbered step (side panel):**
3. The interconnection port of the downlink starts a new round of P/A negotiation.
   - The downlink port of SW2 is configured as the designated port and continuously sends RST BPDUs with the Proposal bit set to 1.
   - After receiving the BPDU, the downlink port of SW3 finds that the received BPDU is not the optimal one. Therefore, SW3 ignores the received BPDU and does not send an RST BPDU with the Agreement bit set to 1.
   - The downlink interface of SW2 does not receive any response packet with the Agreement bit set to 1. SW2 enters the Forwarding state after two intervals of the Forward Delay timer.

**Body text below the slide:**

- The interconnection port of the downlink enters the slow convergence process. SW2 and SW3 are used as an example.

---

## Contents (repeated)

1. Introduction to RSTP
2. Improvements Made in RSTP
3. Working Mechanism of RSTP
4. **RSTP Configurations**

### Basic RSTP Configuration Commands (1)

1. Configure a working mode.

```
[Huawei] stp mode { stp | rstp | mstp }
```

The switch supports three working modes: STP, RSTP, and Multiple Spanning Tree Protocol (MSTP). By default, a switch works in MSTP mode.

2. (Optional) Configure the switch as the root bridge.

```
[Huawei] stp root primary
```

By default, a switch does not function as the root bridge of any spanning tree. After you run this command, the priority value of the switch is set to 0 and cannot be changed.

3. (Optional) Configure the switch as the secondary root bridge.

```
[Huawei] stp root Secondary
```

By default, a switch does not function as the secondary root bridge of any spanning tree. After you run this command, the priority value of the switch is set to 4096 and cannot be changed.

### Basic RSTP Configuration Commands (2)

1. (Optional) Configure the STP priority of a switch.

```
[Huawei] stp priority priority
```

The value ranges from 0 to 61440, with an increment of 4096. By default, the priority value of a switch is 32768.

2. (Optional) Configure a path cost for a port.

```
[Huawei] stp pathcost-standard { dot1d-1998 | dot1t | legacy }
```

Configure a path cost calculation method. By default, the IEEE 802.1t standard (dot1t) is used to calculate the path costs.
All switches on a network must use the same path cost calculation method.

```
[Huawei-GigabitEthernet0/0/1] stp cost cost
```

Set the path cost of the port.

**Body text below the slide:**

- The following describes the supported cost range for different calculation methods:
  - dot1d-1998: Uses the IEEE 802.1d-1998 standard to calculate the path cost. The value ranges from 1 to 65535.
  - dot1t: Uses the IEEE 802.1t standard to calculate the path cost. The value ranges from 1 to 200,000,000.
  - Legacy: Uses Huawei calculation method to calculate the path cost. The value ranges from 1 to 200,000.

### Basic RSTP Configuration Commands (3)

1. (Optional) Configure the interface priority.

```
[Huawei-GigabitEthernet0/0/1] stp priority priority
```

The value is an integer that ranges from 0 to 240, with an increment of 16. By default, the priority of a switch port is 128.

2. Enable STP or RSTP.

```
[Huawei] stp enable
```

By default, STP or RSTP is enabled on a switch.

3. Configure the port as an STP edge port.

```
[Huawei-GigabitEthernet0/0/1] stp edged-port enable
```

By default, all the ports on a switch are non-edge ports.

### RSTP Protection Configuration Commands (1)

1. Enable BPDU protection on an edge port of a switch.

```
[Huawei] stp bpdu-protection
```

By default, BPDU protection is disabled on a switch.

2. Configure root protection.

```
[Huawei-GigabitEthernet0/0/1] stp root-protection
```

By default, root protection is disabled on a port. Root protection takes effect only on designated ports. Root protection and loop prevention cannot be configured on the same port.

3. Configure loop prevention on the root port or alternate port.

```
[Huawei-GigabitEthernet0/0/1] stp loop-protection
```

By default, loop prevention is disabled on a port.

### RSTP Protection Configuration Commands (2)

1. Configure TC BPDU attack defense.

```
[Huawei] stp tc-protection interval interval-value
```

Configure the time for a device to process the maximum number of TC BPDUs. By default, the device processes the maximum number of TC BPDUs at an interval of the Hello timer.

```
[Huawei] stp tc-protection threshold threshold
```

Set the number of times that a switch processes received TC BPDUs and updates forwarding entries within a given period of time. By default, the device processes only one TC BPDU within a specified period of time.

**Body text below the slide:**

- Within the time specified by stp tc-protection interval, the switch processes the number of TC BPDUs specified by stp tc-protection threshold. Packets that exceed this threshold are delayed, so spanning tree convergence may be affected. For example, the period is set to 10s and the threshold is set to 5. After the switch receives TC BPDUs, the switch processes the first five TC BPDUs within 10s. After 10s, the switch processes subsequent TC BPDUs.

### Case: Basic RSTP Configuration (1)

**Diagram description:** Triangle topology: SW1 (root bridge) at top, connected via GE0/0/1 and GE0/0/2 to SW2 (bottom-left) and SW3 (bottom-right) respectively; SW2 and SW3 connect to each other via GE0/0/2 (SW2) and GE0/0/1 (SW3). SW3 additionally connects via an Edge port E0/0/1 down to a PC.

- RSTP is configured on the three switches to eliminate Layer 2 loops.
- The configuration roadmap is as follows:
  - Configure SW1 as the root bridge and SW2 as the secondary root bridge.
  - Configure the port connected to the PC as the edge port because this port does not participate in RSTP calculation.
  - Configure root protection and BPDU protection to protect devices or links.

**Enable RSTP on SW1:**

```
[SW1] stp mode rstp
[SW1] stp enable
[SW1] stp root primary
```

**Enable RSTP on SW2:**

```
[SW2] stp mode rstp
[SW2] stp enable
[SW2] stp root secondary
```

**Enable RSTP on SW3:**

```
[SW3] stp mode rstp
[SW3] stp enable
```

### Case: Basic RSTP Configuration (2)

*(Same topology diagram as previous slide.)*

**Enable the edge port on SW3:**

```
[SW3-Ethernet0/0/1] stp edged-port enable
```

**Enable root protection on SW1:**

```
[SW1-GigabitEthernet0/0/1] stp root-protection
[SW1-GigabitEthernet0/0/2] stp root-protection
```

**Enable BPDU protection on SW3:**

```
[SW3] stp bpdu-protection
```

### Quiz

1. (Multiple) Which of the following are RSTP port states? ( )
   A. Idle
   B. Discarding
   C. Forwarding
   D. Learning

2. (TorF) RSTP root protection must be configured on the root port of the device. ( )

**Answers:**
1. BCD
2. False

### Summary

- STP prevents loops on a LAN. Devices running STP exchange information with one another to discover loops on the network, and block certain ports to eliminate loops. With the growth in scale of LANs, STP has become an important protocol for a LAN.
- Based on STP, RSTP has many improvements and greatly speeds up network convergence.
- This document describes seven improvements of RSTP compared with STP, including the port role, port status, BPDU format, BPDU processing mode, fast convergence mechanism, topology change mechanism, and four protection features.

### Thank you.

*(Closing slide with Huawei copyright/disclaimer boilerplate: "把数字世界带入每个人、每个家庭、每个组织，构建万物互联的智能世界。 Bring digital to every person, home, and organization for a fully connected, intelligent world. Copyright©2025 Huawei Technologies Co., Ltd. All Rights Reserved. The information in this document may contain predictive statements including, without limitation, statements regarding the future financial and operating results, future product portfolio, new technology, etc. There are a number of factors that could cause actual results and developments to differ materially from those expressed or implied in the predictive statements. Therefore, such information is provided for reference purpose only and constitutes neither an offer nor an acceptance. Huawei may change the information at any time without notice.")*

---

# MSTP Implementation and Configuration

## Foreword

- The Rapid Spanning Tree Protocol (RSTP), an enhancement to the Spanning Tree Protocol (STP), allows for fast network topology convergence. When RSTP/STP runs on a VLAN-based network, all VLANs on a local area network (LAN) use the same spanning tree. The blocked link does not carry any traffic, and traffic cannot be load balanced among VLANs. As a result, the link bandwidth usage and device resource usage are low.
- To offset disadvantages of RSTP/STP, IEEE introduced the Multiple Spanning Tree Protocol (MSTP) in 2002, which is standardized as IEEE 802.1s. MSTP is compatible with STP and RSTP. Multiple loop-free trees are set up to prevent broadcast storms and implement redundancy.
- This document describes the improvements of MSTP compared with RSTP/STP, basic concepts and working mechanism of MSTP, and MSTP configurations.

## Objectives

- On completion of this course, you will be able to:
  - Describe weaknesses of RSTP/STP.
  - Describe MSTP improvements compared with RSTP/STP.
  - Describe concepts of MSTP.
  - Describe the working mechanism of MSTP.
  - Complete basic MSTP configurations.

## Contents

1. **Introduction to MSTP**
2. Basic Concepts of MSTP
3. Working Mechanism of MSTP
4. MSTP Configurations

---

## 1. Introduction to MSTP

### Disadvantages of RSTP/STP (1)

**Diagram description:** Two aggregation switches at the top, SW1 (root bridge, left) and SW2 (right), each labeled as the "Gateway of VLAN 2" (SW1) and "Gateway of VLAN 3" (SW2) respectively — shown as separate gateway icons above each switch. SW1 and SW2 both have Designated (D) ports connecting down to SW3, an access switch at the bottom. SW3 has a Root (R) port to SW1 and a Blocked port (red no-entry icon) to SW2. VLAN 2 and VLAN 3 traffic both flow through the links; a note states "The link is blocked, and traffic cannot be load balanced." Below SW3 are two LAN clouds, "LAN A" (VLAN 2) and "LAN B" (VLAN 3).

**Disadvantage 1: Traffic Cannot Be Load Balanced (side panel):**
- Background:
  - SW3 is an access switch connected to a terminal network segment. SW3 is connected to SW1 and SW2 through two links, and all the links allow packets from VLAN 2 and VLAN 3 to pass through.
  - SW1 is configured as the gateway of terminals in VLAN 2 and SW2 as the gateway of terminals in VLAN 3. Terminals in VLAN 2 and VLAN 3 are required to use different links to connect to the corresponding gateways.
- Issue:
  - If there is only one spanning tree on the network and we assume that the port connecting SW3 to SW2 is a blocked port, data of VLAN 2 and VLAN 3 can be transmitted to aggregation switch through only one link. This means that traffic cannot be load balanced.

### Disadvantages of RSTP/STP (2)

**Diagram description:** Same topology as previous slide (SW1 root bridge/Gateway of VLAN 2, SW2/Gateway of VLAN 3, SW3 access switch below with Root port to SW1 and Blocked port to SW2). A curved red arrow shows traffic for VLAN 3 terminals being forced to route through SW1 rather than directly to SW2, illustrating a sub-optimal path. A callout box reads "The path for terminals in VLAN 3 to access the gateway is the sub-optimal path."

**Disadvantage 2: Layer 2 Sub-optimal Path (side panel):**
- Background:
  - SW3 is an access switch connected to a terminal network segment. SW1 and SW2 are aggregation switches. SW1 is configured as the gateway of terminals in VLAN 2 and SW2 as the gateway of terminals in VLAN 3. All links are configured to allow packets from VLAN 2 and VLAN 3 to pass through.
  - After a single spanning tree is run, the loop is broken, and data of VLAN 2 and VLAN 3 is directly sent to SW1.
- Issue:
  - The link between SW3 and SW2 is blocked, so the path from SW3 to the gateway is the sub-optimal path. The optimal path should be the path from SW3 to SW2.

### Overview of MSTP

**Diagram description:** Two side-by-side triangle topologies representing the same physical network calculated as two separate instances. Left ("MSTI 1: VLANs 1, 2, 3, ..., 10"): Root bridge at top (orange highlight) with Designated (D) ports, SW3 at bottom with a Root (R) port and a Blocked port, data traffic flow shown in orange arrows down through the root port. Right ("MSTI 2: VLANs 11, 12, 13, ..., 20"): Root bridge at top (blue highlight, different switch than MSTI 1's root) with Designated (D) ports, SW3 at bottom with a Root (R) port and Blocked port on the opposite link compared to MSTI 1, data traffic flow shown in blue arrows down through its root port.

- MSTP, which is standardized as IEEE 802.1s, is compatible with STP and RSTP. It can implement fast convergence and provide multiple redundant paths for forwarding data, effectively load balancing traffic for VLANs.
- MSTP maps one or more VLANs to a Multiple Spanning Tree Instance (MSTI), and then calculates the spanning tree based on the MSTI. The VLANs mapped to the same MSTI share the same spanning tree.

**Body text below the slide:**

- As shown in the figure, two spanning trees are generated after calculation.
  - The spanning tree corresponding to MSTI 1 uses SW1 as the root bridge to forward packets of VLAN 1 to VLAN 10.
  - The spanning tree corresponding to MSTI 2 uses SW2 as the root bridge to forward packets of VLAN 11 to VLAN 20.
  - Packets of different VLANs are forwarded along different paths, implementing load balancing.
- Note: The spanning tree runs based on MSTIs instead of VLANs.

---

## Contents (repeated)

1. Introduction to MSTP
2. **Basic Concepts of MSTP**
3. Working Mechanism of MSTP
4. MSTP Configurations

### MST Region

*(Breadcrumb trail at top of slide: MSTP Network Hierarchy → MSTP Ports → MST BPDUs, with "MSTP Network Hierarchy" highlighted as current section.)*

**Diagram description:** A large "MSTP Network" boundary containing four labeled MST regions, each a cluster of interconnected switches. "MST region 1" (VLAN 1 → MSTI 1, VLAN 2 → MSTI 2, Other VLANs → MSTI 3) contains two switches connected to each other and to region 2. "MST region 2" (VLAN 1 → MSTI 1, VLAN 2 → MSTI 2) contains two switches. "MST region 3" (VLAN 1 → MSTI 1) contains a single switch. "MST region 4" (VLAN 1 → MSTI 1, VLAN 2 → MSTI 2, Other VLANs → MSTI 3) contains a cluster of four interconnected switches. Lines connect switches within each region and also connect regions 1↔2, 1↔3, 2↔4, and 3↔4.

- MSTP network hierarchy:
  - MSTP divides a switching network into multiple Multiple Spanning Tree (MST) regions, each of which has multiple spanning trees that are independent of each other.
- MST region:
  - An MST region contains multiple switches and their network segments.
  - A LAN can comprise several MST regions that are directly or indirectly connected. You can add multiple switching devices to an MST region using MSTP configuration commands.
  - An MSTP network contains one or more MST regions, and each MST region contains one or more MSTIs.

**Body text below the slide:**

- The switches in one MST region all share the following characteristics:
  - MSTP-enabled
  - Same region name
  - Same VLAN-MSTI mappings
  - Same MSTP revision level

### MSTI

**Diagram description:** MST region 4 shown containing four switches (SW1, SW2, SW3, SW4) interconnected in a mesh, with the VLAN mapping listed: "VLAN 1 -> MSTI 1, VLAN 2 -> MSTI 2, Other VLANs -> MSTI 3." An arrow points from this region to three separate small tree diagrams labeled MSTI 1, MSTI 2, and MSTI 3, each showing four nodes (A, B, C, D) with different spanning tree shapes/root bridges (marked with a red circle) for each instance.

- MSTI:
  - An MST region can contain multiple spanning trees, each of which is called an MSTI.
  - MSTIs are identified by IDs. The value ranges from 0 to 4094 on Huawei devices.
- VLAN mapping table
  - Each MST region has a VLAN mapping table. The VLAN mapping table maps VLANs to MSTIs.
  - As shown in the figure, the VLAN mapping of MST region 4 is as follows:
    - VLAN 1 is mapped to MSTI 1.
    - VLAN 2 is mapped to MSTI 2.
    - Other VLANs are mapped to MSTI 3.

**Body text below the slide:**

- MSTI 0 exists by default. By default, all VLANs on Huawei switches are mapped to MSTI 0.
- MSTP maps VLANs to MSTIs in the VLAN mapping table.
  - Each VLAN can be mapped to only one MSTI. This means that traffic of a VLAN can be transmitted in only one MSTI. An MSTI, however, can correspond to multiple VLANs.

### CST

**Diagram description:** Same four-region MSTP network diagram as the "MST Region" slide, but now the inter-region connecting links (between region 1↔2 and region 1↔3↔4↔2, forming the backbone) are highlighted with dark blue thick lines. An arrow points to a simplified diagram showing four numbered nodes (1, 2, 3, 4 representing the four regions) connected in a diamond/tree shape labeled "CST."

- Common Spanning Tree (CST)
  - A CST connects all MST regions on a switching network.
  - The CST is calculated using a spanning tree protocol, with each MST region being considered as a single node.
  - In the figure, the regions that are connected through dark blue thick lines form a CST.

### IST

**Diagram description:** Same four-region diagram, but this time within "MST region 4" the switches connected by black thin lines are highlighted in yellow/orange. An arrow points to four simplified node diagrams (1, 2, 3, 4) where region 4's diagram is labeled "IST" and shows the yellow-highlighted internal switch connections.

- Internal Spanning Tree (IST)
  - An IST resides within an MST region.
  - An IST is a special MSTI with an MSTI ID of 0.
  - In the figure, the switches that are connected through black thin lines in MST region 4 form an IST.

### CIST

**Diagram description:** Same four-region diagram with the inter-region backbone highlighted in dark blue (as in the CST slide). An arrow points to a diagram showing all four regions' internal nodes and the inter-region connections combined into one unified graph, labeled "CIST," enclosed in a large circle.

- Common and Internal Spanning Tree (CIST)
  - A CIST connects all the switches on a switching network and is calculated using a spanning tree protocol.
  - As shown in the figure, all ISTs and the CST form a CIST.

### SST

**Diagram description:** Same four-region diagram, but "MST region 3" (which contains only a single switch, highlighted in yellow/orange) is called out specifically.

- Single Spanning Tree (SST)
  - A switch running a spanning tree protocol belongs to only one spanning tree.
  - An MST region has only one switch.
  - As shown in the figure, a switch in MST region 3 forms an SST.

### CIST Root, Regional Root, and Master Bridge

**Diagram description:** Same four-region diagram. SW1 (in MST region 1) is highlighted in orange/red as the overall network's CIST root. SW4 (in MST region 2), SW2 (in MST region 3, the single-switch region), and SW3 (in MST region 4) are each highlighted in yellow, representing the regional roots (switches closest to the CIST root within their respective regions).

- CIST root
  - The CIST root is the root bridge of the CIST, for example, SW1 in the figure.
- Regional root
  - Regional roots are classified into IST and MSTI regional roots.
  - The switches that are closest to the CIST root are IST regional roots, for example, SW2, SW3, and SW4 in the figure.
  - An MSTI regional root is the root of the MSTI.
- Master bridge
  - The master bridge is the switch closest to the CIST root in a region, for example, SW1, SW2, SW3, and SW4 in the figure.
  - If the CIST root is in an MST region, the CIST root is the master bridge of the region.

**Body text below the slide:**

- The master bridge consists of the CIST root and the IST regional root.

### Summary (MSTP concepts)

**Table:**

| Role | Description |
|---|---|
| MST region | A switching network is divided into multiple regions. An MST region can contain one or more switches. The switches in the same MST region must be configured with the same region name, revision level, and VLAN mapping table. |
| MSTI | Instance-based spanning tree |
| VLAN mapping table | VLAN-MSTI mappings |
| CST | A spanning tree that connects all MST regions |
| IST | Internal spanning tree with the MSTI ID of 0 in an MST region |
| CIST | It connects all switching devices on a switching network. |
| SST | There is only one switching device in the MST region, and the switching device belongs to only one spanning tree. |
| CIST root | Root bridge of the CIST |
| IST regional root | Switch that is closest to the CIST root in an MST region |
| MSTI regional root | Root bridge in the MSTI |
| Master bridge | Switching device nearest to the CIST root, including the CIST root and IST regional root |

### MSTP Port Roles (1)

*(Breadcrumb: MSTP Network Hierarchy → MSTP Ports [highlighted] → MST BPDUs)*

- MSTP defines the following port roles:
  - Root port, designated port, alternate port, backup port, master port, regional edge port, and edge port.

**Diagram description:** MST region 1 shown with SW1 (master bridge) at top, both ports Designated (D). SW2 at bottom-left with Root (R), Designated (D), and Backup (B) port. SW3 at bottom-right with Root (R), Designated (D), and Alternate (A) port. SW2 and SW3 are connected to a shared segment at the bottom (dashed line between them).

**Table:**

| Port Role | Description |
|---|---|
| Root port | A root port sends data to a root bridge and is the port closest to the root bridge. |
| Designated port | The designated port on a switch forwards BPDUs to a downstream switch. |
| Alternate port | Alternate ports provide an alternate path to the root bridge. This path is different from the path through the root port. An alternate port is blocked from sending BPDUs after a BPDU sent by another bridge is received. |
| Backup port | Backup ports provide a backup path to a segment already connected by a designated port. Backup ports are blocked from sending BPDUs after a BPDU sent by itself is received. |

**Body text below the slide:**

- Except edge ports, all ports participate in MSTP calculation.
- A port can play different roles in different MSTIs.

### MSTP Port Roles (2)

**Diagram description:** MST region 1 contains SW1 (top), SW2 (labeled "master bridge," bottom-left, with a Master port "M" role), SW3 (bottom-right, with a Regional Edge port "RE" role). SW2 connects down to SW4 (labeled "CIST root," in "MST region 2"), and SW3 connects down to SW5 (in "MST region 3").

**Table:**

| Port Role | Description |
|---|---|
| Master port | A master port is on the shortest path connecting MST regions to the CIST root. BPDUs of an MST region are sent to the CIST root through the master port. Master ports are special regional edge ports, functioning as root ports on ISTs or CISTs and master ports in instances. |
| Regional edge port | A regional edge port is located at the edge of an MST region and connects to another MST region or an SST. |

### MSTP Port Roles (3)

**Diagram description:** MST region 1 contains SW1 (master bridge, top), SW2 (bottom-left), SW3 (bottom-right) with an Edge (E) port connecting down to a PC.

**Table:**

| Port Role | Description |
|---|---|
| Edge port | An edge port is located at the edge of an MST region and does not connect to any switching device. Generally, edge ports are directly connected to terminals. |

### MSTP Port States

- MSTP port states are the same as those used in RSTP.
  - Forwarding: A port in this state can send and receive BPDUs. It can also forward user traffic and learns MAC addresses.
  - Learning: A port in this state can send and receive BPDUs. It learns MAC addresses but cannot forward user traffic.
  - Discarding: A port in this state only receives BPDUs. It does not forward user traffic or learn MAC addresses.

**Table:**

| MSTP Port State | Port Role |
|---|---|
| Forwarding | Root port, designated port, master port, and regional edge port |
| Learning | Root port, designated port, master port, and regional edge port |
| Discarding | Root port, designated port, master port, regional edge port, alternate port, and backup port |

**Body text below the slide:**

- A port in Learning state learns MAC addresses from user traffic to construct a MAC address table.

### MST BPDUs

*(Breadcrumb: MSTP Network Hierarchy → MSTP Ports → MST BPDUs [highlighted])*

- MSTP calculates spanning trees based on Multiple Spanning Tree Bridge Protocol Data Units (MST BPDUs).
- Switches on an MSTP network transmit MST BPDUs to calculate spanning tree topologies, maintain network topologies, and communicate topology changes.

**Table — BPDU version/type identification:**

| Version | Type | Name |
|---|---|---|
| 0 | 0x00 | Configuration BPDU |
| 0 | 0x80 | TCN BPDU |
| 2 | 0x02 | RST BPDU |
| 3 | 0x02 | MST BPDU |

**Format of an MST BPDU (field list, with annotation that first 36 bytes match RST BPDUs and fields from the 37th byte onward are MSTP-specific):**

- Protocol ID
- Protocol Version ID = 3
- BPDU Type = 0x02
- CIST Flags
- CIST Root ID
- CIST External Path Cost
- CIST Regional Root ID
- CIST Port ID
- Message Age
- Max Age
- Hello Time
- Forward Delay
- Version 1 Length = 0
- Version 3 Length
- MST Configuration ID
- CIST Internal Root Path Cost
- CIST Bridge ID
- CIST Remaining Hops
- MSTI Configuration Messages

*(Annotation: fields from Protocol ID through Forward Delay = first 36 bytes, same as those of RST BPDUs. Fields from Version 1 Length onward = starting from the 37th byte, MSTP-specific fields.)*

**Body text below the slide:**

- The first 36 bytes of an MST BPDU are the same as those of an RST BPDU. Fields starting from the 37th byte of an MST BPDU are MSTP-specific. The MSTI Configuration Messages field consists of configuration messages of multiple MSTIs.
- Main fields in an MST BPDU:
  - Protocol Identifier: has 2 bytes and identifies a protocol.
  - Protocol Version Identifier: has 1 byte and indicates the protocol version identifier.
    - 0: STP
    - 2: RSTP
    - 3: MSTP
  - BPDU type: has 1 byte and indicates the BPDU type.
    - 0x00: Configuration BPDU for STP
    - 0x80: Topology Change Notification (TCN) BPDU for STP
    - 0x02: Rapid Spanning Tree (RST) BPDU or Multiple Spanning Tree (MST) BPDU
  - CIST Flags: has 1 byte and indicates the CIST flag field.
  - CIST Root Identifier: has 8 bytes and indicates the ID of the CIST root switch.

> **[PAGE GAP — page 671 missing from source PDF]**
> The export jumps from page 670 directly to page 672. Based on context, the missing page likely continues the field-by-field breakdown of the MST BPDU format begun on page 670 — probably covering CIST External Path Cost, CIST Regional Root Identifier, CIST Port Identifier, Message Age, Max Age, Hello Time, Forward Delay, Version 1 Length, Version 3 Length, MST Configuration ID, CIST Internal Root Path Cost, CIST Bridge ID, CIST Remaining Hops, and/or the MSTI Configuration Messages field definitions. Please re-upload a complete export to fill this gap.

---

## Contents (repeated)

1. Introduction to MSTP
2. Basic Concepts of MSTP
3. **Working Mechanism of MSTP**
4. MSTP Configurations

### MSTP Topology Calculation

- MSTP topology calculation:
  - MSTP can divide the entire Layer 2 network into multiple MST regions. The CST is calculated between regions, and the IST is generated in each region. The CST and ISTs constitute the CIST of the entire switching device network.
  - Multiple spanning trees can be generated based on MSTIs in a region. Each spanning tree is called an MSTI.
- Both the CIST and MSTIs are calculated based on vectors, carried in MST BPDUs. Devices exchange MST BPDUs to calculate the CIST and MSTIs.
  - Vectors used in CIST calculation:
    - {Root ID, external root path cost, regional root ID, internal root path cost, designated switch ID, designated port ID, receiving port ID}
  - Vectors used in MSTI calculation:
    - {Regional root ID, internal root path cost, designated switch ID, designated port ID, receiving port ID}
  - The preceding vectors are listed in descending order of priority from left to right.

**Body text below the slide:**

- Vectors are described as follows:
  - Root ID: identifies the root switch for the CIST.
    - The root identifier consists of the priority value (16 bits) and MAC address (48 bits).
    - The priority value is the priority of MSTI 0.
  - External root path cost (ERPC): indicates the path cost from a CIST regional root to the root.
    - ERPCs are the same on all switches in an MST region.
    - If the CIST root is in an MST region, all ERPCs in that MST region are set to 0.
  - Regional root ID: identifies the MSTI regional root.
    - It consists of the priority value (16 bits) and MAC address (48 bits).
    - The priority value is the priority of MSTI 0.
  - Internal root path cost (IRPC): indicates the path cost from the local bridge to the regional root.
    - The IRPC saved on a regional edge port must be greater than the IRPC saved on a non-regional edge port.

> **[PAGE GAP — page 674 missing from source PDF]**
> The export jumps from page 673 directly to page 675. Based on context, the missing page likely continues the vector description bullets begun on page 673 — probably covering the "Designated switch ID," "Designated port ID," and "Receiving port ID" definitions before moving into the "CIST Calculation" slide. Please re-upload a complete export to fill this gap.

### CIST Calculation

**Diagram description:** Same four-region MSTP network diagram used earlier (MST region 1 through 4, interconnected mesh, with orange/blue/yellow switch highlighting per region). An arrow points to a simplified diagram showing the resulting CIST tree: a red node (root), connected to a blue node and a yellow node, which connect further down to additional yellow and blue nodes, labeled "CIST."

- After comparing the vectors, the switch with the highest priority on the entire network is selected as the CIST root.
- MSTP calculates an IST for each MST region, treats each MST region as a single device, and calculates a CST to interconnect MST regions. The CST and ISTs form a CIST for the entire network.

### MSTI Calculation

**Diagram description:** MST region 4 shown with four switches SW1, SW2, SW3, SW4 interconnected (VLAN 1 → MSTI 1, VLAN 2 → MSTI 2, Other VLANs → MSTI 3). An arrow points to three separate small tree diagrams (nodes 1, 2, 3, 4) labeled MSTI 1, MSTI 2, MSTI 3, each with a different root bridge highlighted in red depending on the instance.

- MSTI characteristics:
  - Spanning trees of MSTIs are independent of each other.
  - The spanning tree calculation method of each MSTI is similar to that of STP.
  - Spanning trees of MSTIs can have different roots and topologies.
  - Each MSTI sends BPDUs in its spanning tree.
  - The topology of each MSTI is determined using commands.
  - A port can be configured with different parameters for different MSTIs.
  - A port can play different roles or have different states in different MSTIs.
- MSTP can calculate the root bridge or you can manually configure the root bridge or secondary root bridge for a specified spanning tree.
  - A switch can function as a root bridge or a secondary root bridge in a spanning tree. It can also function as the root bridge or secondary root bridge of another spanning tree. In a spanning tree, a device can function as either the root bridge or secondary root bridge.
  - In a spanning tree: Only one root bridge takes effect. If two or more root bridges are specified in a spanning tree, the device with the smallest MAC address is used.
  - Multiple secondary root bridges can be specified. When the root bridge fails or is powered off, a secondary root bridge becomes the new root bridge unless a new root bridge is specified. If there are multiple secondary root bridges, the one with smallest MAC address becomes the root bridge of the spanning tree.

### MSTP Network Data Forwarding

**Diagram description:** Four-region MSTP network (same layout as prior slides). PC1 connects into MST region 1 via a switch marked with instance node numbers (1, 2, 3, 4 with node "3" highlighted red as root bridge in VLAN 2). Data flows (blue arrows) trace a path for VLAN 2 traffic: from PC1, through MSTI 2 in region 1, across to region 2's MSTI 2 (also showing node 3 as root, highlighted red), and down to PC2. VLAN mapping tables for each region are shown, with "VLAN 2 -> MSTI 2" highlighted in red/orange text across all four regions to trace the path.

- On an MSTP network, a VLAN packet is forwarded as follows:
  - Along MSTI in an MST region
  - Along CST among MST regions

**Body text below the slide:**

- Data transmission in VLAN 2 is used as an example.

---

## Contents (repeated)

1. Introduction to MSTP
2. Basic Concepts of MSTP
3. Working Mechanism of MSTP
4. **MSTP Configurations**

### MSTP Configuration Commands

1. Configure a working mode of a switching device.

```
[Huawei] stp mode mstp
```

A switching device supports three working modes: STP, RSTP, and MSTP. By default, the device works in MSTP mode.

2. Enable MSTP.

```
[Huawei] stp enable
```

Enable STP/RSTP/MSTP on a switching device or an interface. By default, STP, RSTP, or MSTP is enabled globally and on an interface.
Therefore, to ensure rapid and stable spanning tree calculation, before enabling STP, RSTP, or MSTP, perform basic configurations on the switching device and its interfaces.

**Body text below the slide:**

- **stp mode mstp**
  - MSTP can recognize RSTP BPDUs and, conversely, RSTP can recognize MSTP BPDUs. However, MSTP and STP cannot recognize each other's BPDUs. To enable devices running different spanning tree protocols to interwork with each other, interfaces of an MSTP-enabled switch connected to devices running STP automatically transition to STP mode; other interfaces continue to work in MSTP mode.

### Configuring and Activating an MST Region (1)

1. Enter the MST region view.

```
[Huawei] stp region-configuration
[Huawei-mst-region]
```

2. Configure the name of the MST region.

```
[Huawei-mst-region] region-name name
```

By default, the MST region name is the bridge MAC address of a switching device.

3. Configure the mapping between VLANs and MSTIs.

```
[Huawei-mst-region] instance instance-id vlan { vlan-id1 [ to vlan-id2 ] }
```

Map a VLAN to an MSTI. By default, all VLANs are mapped to the CIST, namely, MSTI 0.

**Body text below the slide:**

- **stp region-configuration**
  - By default, three parameters of MST regions use default settings.
- **region-name name**
  - Specifies the region name of a switching device. The value is a case-sensitive string of 1 to 32 characters without spaces.
- **instance instance-id vlan { vlan-id1 [ to vlan-id2 ] }**
  - instance-id specifies the ID of an MSTI. The value is an integer that ranges from 0 to 4094. The value 0 indicates the CIST.

### Configuring and Activating an MST Region (2)

4. (Optional) Configure the revision level of the MST region.

```
[Huawei-mst-region] revision-level level
```

Configure the revision level of the MST region for a switching device. By default, the revision level of an MST region is 0.

5. Activate the configuration of the MST region.

```
[Huawei-mst-region] active region-configuration
```

Make the region name, VLAN mapping table, and MSTP revision level take effect.

**Body text below the slide:**

- **revision-level level**
  - level specifies the revision level of an MST region. The value is an integer that ranges from 0 to 65535.
  - MSTP is a standard protocol; therefore, the MSTP revision level of a device is 0 by default. If the revision level of some devices from a specified manufacturer is not 0, you must change the value to 0 to facilitate tree calculation in an MST region.

### Optional MSTP Configuration Commands (1)

1. Configure the root bridge and secondary root bridge.

```
[Huawei] stp [ instance instance-id ] root { primary | secondary }
```

Configure the switch as the root bridge or secondary root bridge in a spanning tree.

2. Set the priority of a switching device in a specified MSTI.

```
[Huawei] stp [ instance instance-id ] priority priority
```

Set the priority of the switching device in a spanning tree. By default, the priority of a switching device in a spanning tree is 32768.

3. Set the path cost of an interface in the specified MSTI.

```
[Huawei] stp pathcost-standard { dot1d-1998 | dot1t | legacy }
```

Configure the path cost calculation method. By default, IEEE 802.1t is used to calculate the path cost.

```
[Huawei-GigabitEthernet0/0/1] stp [ instance instance-id ] cost cost
```

Set the path cost of a port in a spanning tree. By default, the path cost of a port in a spanning tree is the path cost corresponding to the port rate.

**Body text below the slide:**

- **stp [ instance instance-id ] root { primary | secondary }**
  - instance instance-id specifies the ID of an MSTI. If instance instance-id is not specified, the device in MSTI 0 is a root bridge or a secondary root bridge.
  - primary indicates that the device functions as the root bridge of a spanning tree. After the configuration is complete, the priority of the device is 0 and cannot be changed.
  - secondary: indicates that the device functions as the secondary root bridge of a spanning tree. After the configuration is complete, the priority of the device is 4096 (this value cannot be modified).
- **stp [ instance instance-id ] priority priority**
  - priority specifies the priority of a switching device. A smaller priority value indicates a higher priority of the switching device. The value is an integer that ranges from 0 to 61440 and is a multiple of 4096, such as 0, 4096, and 8192. The default value is 32768.
- **stp pathcost-standard { dot1d-1998 | dot1t | legacy }**
  - dot1d-1998: uses the IEEE 802.1d-1998 standard to calculate the path cost.
  - dot1t: uses the IEEE 802.1t standard to calculate the path cost. The value ranges from 1 to 200,000,000.
  - legacy: uses the Huawei standard to calculate the path cost. The value ranges from 1 to 200,000.

### Optional MSTP Configuration Commands (2)

4. Set a priority for a port in an MSTI.

```
[Huawei-GigabitEthernet0/0/1] stp [ instance instance-id ] port priority priority
```

Sets the priority of a port in a spanning tree. By default, the priority of a port on a switching device is 128.

**Body text below the slide:**

- **stp [ instance instance-id ] port priority priority**
  - priority: specifies the priority of a port when it participates in spanning tree calculation. The value is an integer that ranges from 0 to 240 and is a multiple of 16, such as 0, 16, and 32.

### Case: Single-Region Multi-Instance Configuration (1)

**Diagram description:** MST region 1 containing four switches: SW1 (top-left) and SW2 (top-right), connected to each other via GE0/0/1, and both connected down via GE0/0/2 to SW3 (bottom-left) and SW4 (bottom-right) respectively; SW3 and SW4 are also connected to each other. SW3 has an Edge port E0/0/1 to PC1 (192.168.1.1/24), and SW4 has an Edge port E0/0/1 to PC2 (192.168.2.1/24). Legend: solid orange line = VLAN 2 → MSTI 1 path; dashed blue line = VLAN 3 → MSTI 2 path.

- Scenario:
  - To implement redundancy on a complex network, network designers tend to deploy multiple physical links between two devices, one of which is the primary link and the others are the backup. Loops may occur in this situation. To this end, MSTP can be deployed on the network to prevent loops on the network and trims the network into a loop-free tree. In addition, MSTP can be deployed to implement load balancing among VLANs.
- Requirements:
  - Configure MSTP on SW1, SW2, SW3, and SW4.
  - To load balance traffic from VLANs 2 and 3, configure MSTP multi-instance.
  - Configure a VLAN mapping table to associate VLANs with MSTIs.
  - Configure the port connected to the PC as the edge port because the port does not need to participate in MSTP calculation.

**Body text below the slide:**

- Configure SW1 as the gateway of VLAN 2 (VLANIF 2: 192.168.1.254/24) and SW2 as the gateway of VLAN 3 (VLANIF 3: 192.168.2.254/24). In this way, PC1 can ping VLANIF 2 of SW1 and PC2 can ping VLANIF 3 of SW2.

### Case: Single-Region Multi-Instance Configuration (2)

*(Same topology diagram as previous slide.)*

1. Configure interface-based VLAN assignment to implement Layer 2 communication.

**SW1 configuration:**

```
[SW1] vlan batch 2 to 3
[SW1] interface GigabitEthernet 0/0/1
[SW1-GigabitEthernet0/0/1] port link-type trunk
[SW1-GigabitEthernet0/0/1] port trunk allow-pass vlan 2 to 3
[SW1-GigabitEthernet0/0/1] quit
[SW1] interface GigabitEthernet 0/0/2
[SW1-GigabitEthernet0/0/2] port link-type trunk
[SW1-GigabitEthernet0/0/2] port trunk allow-pass vlan 2 to 3
[SW1-GigabitEthernet0/0/2] quit
```

Note: The configuration of SW2 is similar to that of SW1, and is not provided here.

### Case: Single-Region Multi-Instance Configuration (3)

*(Same topology diagram as previous slides.)*

**SW3 configuration:**

```
[SW3] vlan batch 2 to 3
[SW3] interface GigabitEthernet 0/0/1
[SW3-GigabitEthernet0/0/1] port link-type trunk
[SW3-GigabitEthernet0/0/1] port trunk allow-pass vlan 2 to 3
[SW3-GigabitEthernet0/0/1] quit
[SW3] interface GigabitEthernet 0/0/2
[SW3-GigabitEthernet0/0/2] port link-type trunk
[SW3-GigabitEthernet0/0/2] port trunk allow-pass vlan 2 to 3
[SW3-GigabitEthernet0/0/2] quit
[SW3] interface Ethernet 0/0/1
[SW3-Ethernet0/0/1] port link-type access
[SW3-Ethernet0/0/1] port default vlan 2
[SW3-Ethernet0/0/1] quit
```

Note: The configuration of SW4 is similar to the configuration of SW3, and is not provided here.

### Case: Single-Region Multi-Instance Configuration (4)

*(Same topology diagram as previous slides.)*

2. Configure basic MSTP functions.

Configure an MST region and mapping between VLANs and MSTIs on SW1.

```
[SW1] stp region-configuration
[SW1-mst-region] region-name 1
[SW1-mst-region] instance 1 vlan 2
[SW1-mst-region] instance 2 vlan 3
[SW1-mst-region] active region-configuration
[SW1-mst-region] quit
```

Note: The configurations of SW2, SW3, and SW4 are similar to the configuration of SW1, and are not provided here.

**Body text below the slide:**

- By default, the MSTP function is enabled on the device. If the MSTP function is not enabled, run the **stp enable** command to enable the MSTP function on the switching device or port.

### Case: Single-Region Multi-Instance Configuration (5)

*(Same topology diagram as previous slides.)*

3. Configure the root bridge and secondary root bridge for MSTI 1 and MSTI 2.

Configure SW1 as the root bridge and SW2 as the secondary root bridge in MSTI 1.

```
[SW1] stp instance 1 root primary
[SW2] stp instance 1 root secondary
```

Configure SW2 as the root bridge and SW1 as the secondary root bridge in MSTI 2.

```
[SW1] stp instance 2 root secondary
[SW2] stp instance 2 root primary
```

Note: The configurations of SW2, SW3, and SW4 are similar to the configuration of SW1, and are not provided here.

### Case: Single-Region Multi-Instance Configuration (6)

*(Same topology diagram as previous slides.)*

4. Enable MSTP and configure the port connected to the PC as the edge port.

Configure Ethernet0/0/1 on SW3 as an edge port.

```
[SW3] interface Ethernet 0/0/1
[SW3-Ethernet0/0/1] stp edged-port enable
[SW3-Ethernet0/0/1] quit
```

Note: The edge port configuration of SW4 is similar to that of SW3, and is not provided here.

### Verifying the Configuration (1)

**Command output — SW1:**

```
[SW1] display stp brief
MSTID Port                    Role STP State   Protection
0     GigabitEthernet0/0/1    DESI FORWARDING  NONE
0     GigabitEthernet0/0/2    ROOT FORWARDING  NONE
1     GigabitEthernet0/0/1    DESI FORWARDING  NONE
1     GigabitEthernet0/0/2    DESI FORWARDING  NONE
2     GigabitEthernet0/0/1    ROOT FORWARDING  NONE
2     GigabitEthernet0/0/2    DESI FORWARDING  NONE
```

**Command output — SW2:**

```
[SW2] display stp brief
MSTID Port                    Role STP State   Protection
0     GigabitEthernet0/0/1    ROOT FORWARDING  NONE
0     GigabitEthernet0/0/2    ALTE DISCARDING  NONE
1     GigabitEthernet0/0/1    ROOT FORWARDING  NONE
1     GigabitEthernet0/0/2    DESI FORWARDING  NONE
2     GigabitEthernet0/0/1    DESI FORWARDING  NONE
2     GigabitEthernet0/0/2    DESI FORWARDING  NONE
```

**Command output — SW3:**

```
[SW3] display stp brief
MSTID Port                    Role STP State   Protection
0     Ethernet0/0/1           DESI FORWARDING  NONE
0     GigabitEthernet0/0/1    DESI FORWARDING  NONE
0     GigabitEthernet0/0/2    DESI FORWARDING  NONE
1     Ethernet0/0/1           DESI FORWARDING  NONE
1     GigabitEthernet0/0/1    DESI FORWARDING  NONE
1     GigabitEthernet0/0/2    ROOT FORWARDING  NONE
2     GigabitEthernet0/0/1    ALTE DISCARDING  NONE
2     GigabitEthernet0/0/2    ROOT FORWARDING  NONE
```

**Command output — SW4:**

```
[SW4] display stp brief
MSTID Port                    Role STP State   Protection
0     Ethernet0/0/1           DESI FORWARDING  NONE
0     GigabitEthernet0/0/1    ROOT FORWARDING  NONE
0     GigabitEthernet0/0/2    DESI FORWARDING  NONE
1     GigabitEthernet0/0/1    ALTE DISCARDING  NONE
1     GigabitEthernet0/0/2    ROOT FORWARDING  NONE
2     Ethernet0/0/1           DESI FORWARDING  NONE
2     GigabitEthernet0/0/1    DESI FORWARDING  NONE
2     GigabitEthernet0/0/2    ROOT FORWARDING  NONE
```

*(Note: rows for MSTID 1 in the SW1/SW2 outputs are shown in the original slide with red/orange text highlighting to draw attention to MSTI 1's role assignments; this formatting has no bearing on the values themselves.)*

### Verifying the Configuration (2)

**Diagram description:** Two side-by-side final topology diagrams showing the resulting active paths per instance. Left ("VLAN 2 -> MSTI 1" path, solid orange line): SW1 labeled "Root bridge," with Designated (D) ports to both SW2 and SW3; SW2 has a Root (R) port to SW1 and a Designated (D) port to SW4; SW3 has a Root (R) port to SW1 and an Alternate (A) port to SW4 (shown with red no-entry icon); SW4 has ports Root (R, to SW3) — wait, actually per the diagram SW4's link to SW3 is the alternate/blocked one. PC1 (192.168.1.1/24) connects to SW3, PC2 (192.168.2.1/24) connects to SW4. Right ("VLAN 3 -> MSTI 2" path, dashed blue line): SW2 labeled "Root bridge" this time, with Designated (D) ports to both SW1 and SW4; SW1 has a Root (R) port to SW2; SW4 has a Root (R) port to SW2 and Designated (D) port down to SW3; SW3 has an Alternate (A) port shown blocked toward SW4. PC1 and PC2 connect the same way as in the left diagram.

*(This slide visually confirms the load-balancing result: MSTI 1 traffic roots through SW1, MSTI 2 traffic roots through SW2, with different links blocked in each instance.)*

### Quiz

1. (Single) The following figure shows port roles of a switch running MSTP. What is the state of GigabitEthernet0/0/1 in MSTI 1? ( )
   A. Blocking
   B. Discarding
   C. Forwarding
   D. Learning

**Command output shown in quiz figure:**

```
[Switch] display stp brief
MSTID Port                    Role
0     Ethernet0/0/1           DESI
0     GigabitEthernet0/0/1    ROOT
0     GigabitEthernet0/0/2    DESI
1     GigabitEthernet0/0/1    ALTE
1     GigabitEthernet0/0/2    ROOT
2     Ethernet0/0/1           DESI
2     GigabitEthernet0/0/1    DESI
2     GigabitEthernet0/0/2    ROOT
```

2. (TorF) The CIST is a tree that consists of the ISTs and CST. ( )

**Answers:**
1. B
2. True

