# **Engineering Analysis of the Autel EVO Max Series Edge-Computing and Sensor Fusion Architecture**

The operational landscape for commercial and enterprise unmanned aerial systems (UAS) has transitioned from simple remote-controlled operations to complex, high-interference, and contested environments. The Autel Robotics EVO Max series—comprising the EVO Max 4T, the EVO Max 4T XE, and the updated EVO Max 4T V2 platforms—embodies this shift by moving away from ground-station-dependent computing to a fully decentralized, edge-computing architecture governed by the Autel Autonomy Engine.1 By processing complex spatial, visual, and electronic datasets directly on the aircraft in real time, these platforms maintain operational stability and mission capability under conditions that typically disable conventional commercial UAS.1

## **Onboard Edge-Computing and Neural Processing Unit Architecture**

At the core of the target recognition and dynamic tracking capabilities of the EVO Max series is a dedicated onboard Neural Processing Unit (NPU) \[User Query\]. Traditional systems stream compressed video over a wireless link to a ground control station (GCS) for processing, which introduces significant latency and exposes the system to data loss from radio frequency (RF) interference or active jamming. The Autel Autonomy Engine addresses this vulnerability by executing convolutional neural network (CNN) inference directly on the raw, uncompressed hardware video pipelines before any digital encoding or H.264/H.265 compression occurs \[User Query\].  
This pre-compression processing pipeline is technically significant. Digital video compression algorithms compress files by throwing away high-frequency spatial details and color metadata through chroma subsampling and macroblocking. While these artifacts are minor to human operators, they degrade the performance of deep learning object classification models. By performing inference directly on the raw sensor tap, the onboard NPU preserves pixel-level edge gradients and micro-contrasts, which significantly extends the maximum effective range of target detection and classification.3

### **The Dot Pre-Detection and Target Classification Pipeline**

When an operator switches the payload view into Tripod/Tracking Mode within the Autel Enterprise App, the edge classifier starts a real-time pre-detection cycle.4 Rather than requiring the pilot to guess which targets are within tracking range, the NPU scans the active frame and overlays a geometric pre-detection marker (a small dot) over classified objects that meet high-confidence thresholds.4  
The underlying native classifier is trained on industrial, defense, and public safety datasets \[User Query\]. It classifies up to 64 distinct targets simultaneously with a verified comprehensive classification accuracy exceeding 95%.5  
The system classifies targets into three primary categories 5:

* **Pedestrians and Moving Personnel:** The network is optimized to identify human skeletal proportions, high-visibility safety apparel in daylight, and thermal human body heat signatures in low-light environments \[User Query\].  
* **Vehicles:** The model distinguishes civilian cars, commercial trucks, transport vehicles, and naval vessels \[User Query\].  
* **Heat Sources:** The thermal processing pipeline isolates thermal centroids, high-temperature industrial anomalies, and emerging forest fire hotspots.6

The control interface provides a multi-spectral target tracking workflow.4 The pilot can either tap an active pre-detection dot to lock the 3-axis gimbal's coordinate tracking onto that target's centroid, or manually draw a bounding box Region of Interest (ROI) over an unclassified target to force a visual tracking lock.4 Once locked, the gimbal automatically adjusts its pitch, roll, and yaw to keep the target centered.4 Simultaneously, the flight controller coordinates with the gimbal to maintain the aircraft's forward-facing orientation toward the target.4 This leaves manual flight coordinates active so the pilot can perform tracking adjustments or offset maneuvers without losing the target lock.4  
A technical constraint exists within the multi-spectral sensor pipeline: the thermal imaging camera's digital signal processor (DSP) does not natively render the AI pre-detection dots.4 To establish a tracker lock in low-visibility or infrared-dominant missions, the system relies on a multi-spectral handover workflow:  
  
The pilot first views the scene through the visible light spectrum camera, taps the pre-detection dot (or draws an ROI bounding box) to lock the tracking system, and then switches the active video feed to the thermal infrared view.4 This coordinates target tracking across both thermal and optical spectral bands.

### **Table 1: Edge-AI Target Tracking and Performance Parameters**

| Parameter | Operational Specification | Functional Implications |
| :---- | :---- | :---- |
| **Onboard NPU Location** | Pre-compression video pipeline \[User Query\] | Minimizes latency, avoids compression artifacts, and maintains tracking under RF jamming. |
| **Max Simultaneous Targets** | **64** targets 5 | Enables wide-area surveillance and tactical monitoring in dense urban or chaotic environments. |
| **Classifier Accuracy** | **95%** comprehensive accuracy 5 | Reduces false-positive triggers during automated perimeter sweeps or search-and-rescue flights. |
| **Native Target Classes** | Moving people, vehicles, naval vessels, heat sources 5 | Supports multi-domain applications across public safety, coastal security, and utility inspections. |
| **Gimbal Integration** | Dual-mode: Tap AI dot or manual ROI box 4 | Gives operators flexibility to track both standard classified targets and custom objects of interest. |
| **Thermal Tracking Mode** | RGB-to-Thermal multi-spectral coordinate handover 4 | Bypasses thermal-rendering constraints to maintain tracking in complete darkness. |

## **Spatial Awareness and Perceptual Sensor Fusion**

Standard commercial drones rely on binary reactive distance sensors, such as ultrasonic transducers or single-point infrared sensors, which execute basic stop-and-hover routines when an obstacle enters their detection envelope. In contrast, the Autel Autonomy Engine on the EVO Max series uses deep multi-sensor data fusion to generate real-time local semantic models of the surrounding space.7

### **The 720-Degree Omnidirectional Perceptual Loop**

To achieve reliable situational awareness in all weather conditions, the platform fuses data from two complementary sensor modalities 1:

* **Dual-Fisheye Binocular Vision Systems:** These optical arrays map visual disparity, depth, and optical flow in high-contrast, daylight environments.10 They provide high-resolution semantic segmentation of nearby structures, trees, and ground features.  
* **60GHz Millimeter-Wave Radar:** Operating within the 60 GHz to 64 GHz frequency band, this active radar system is unaffected by low light, rain, heavy snow, thick fog, or dense airborne dust.1 It penetrates atmospheric obscurants to detect thin obstacles down to 0.5 in (12.7 mm) in diameter, such as overhead power lines, structural wiring, and tree branches.10

By combining these two datasets, the flight computer creates a unified spatial map.1 The optical system provides detailed shape and edge information, while the millimeter-wave radar provides accurate distance measurements through environmental obscurants.1 This dual-sensing system eliminates blind spots across a 720° omnidirectional envelope.1

### **Real-Time 3D Pathfinding and Obstacle Avoidance**

The onboard flight computer feeds this fused spatial map directly into localized pathfinding algorithms.1 If a newly detected physical obstacle blocks a pre-planned waypoint trajectory, the system calculates localized 3D path vectors to navigate around the object in real time.1 This edge rerouting process operates on two distinct algorithms depending on mission requirements 5:

* **High-Speed Rerouting Mode:** Optimized for active obstacle avoidance at flight velocities up to 15 m/s, maintaining a minimum safety clearance envelope of 1.5 m from obstacles.5  
* **High-Precision Rerouting Mode:** Configured for tight, complex spaces, allowing flight speeds up to 8 m/s with a localized obstacle safety envelope of 0.5 m.5

### **Table 2: Sensor Fusion and Obstacle Sensing Envelopes**

| Sensor Subsystem | Operating Frequency / Spec | Detection Range | Minimum Target Size / Envelope |
| :---- | :---- | :---- | :---- |
| **Binocular Vision Arrays** | Visible Light Optical Flow 10 | 0.5 m to 40 m 10 | Requires > 100 lux illumination with surface texture.12 |
| **MMW Radar (Upward)** | **60 GHz** to 64 GHz 10 | 0.5 m to 30 m 13 | Detects high-voltage transmission lines down to 0.5 in.13 |
| **MMW Radar (Forward/Backward)** | **60 GHz** to 64 GHz 10 | 1.5 m to 30 m 13 | Active up to 15 m/s relative flight velocity.13 |
| **MMW Radar (Sidewards)** | **60 GHz** to 64 GHz 10 | 1.5 m to 30 m 13 | Active up to 15 m/s relative flight velocity.13 |
| **Visual Depth Sensing (Lateral)** | Multi-Directional Fisheye 1 | 0.5 m to 30 m (Sideward) 14 | Requires surface texture and sufficient lighting.12 |

## **Electronic Warfare Countermeasures and GPS-Denied Visual Navigation**

Operating in modern urban zones, near high-voltage energy grids, or in active combat zones exposes UAS platforms to severe electromagnetic interference (EMI), radio frequency interference (RFI), and intentional GNSS spoofing or jamming.1 The EVO Max series utilizes hardened flight control modules running custom anti-spoofing and anti-jamming algorithms.1  
In the event of total GNSS signal loss (complete loss of GPS, GLONASS, Galileo, and BeiDou), the drone switches navigation modes.1 Instead of entering an uncontrolled drift state, the Autel Autonomy Engine engages high-precision visual navigation powered by Simultanous Localization and Mapping (vSLAM) visual odometry.1 This system processes high-contrast visual features and ground-plane optical flow captured by the 50MP wide-angle camera.7

### **Table 3: Spatial Navigation Accuracy under GNSS-Denied and Nominal Conditions**

| Flight Mode / Condition | Vertical Position Accuracy | Horizontal Position Accuracy | Operational Parameters |
| :---- | :---- | :---- | :---- |
| **Visual Positioning Only** | **±0.1 m** 7 | ±0.3 m 7 | Active in daylight or textured indoor spaces.5 |
| **Standard GNSS Navigation** | **±1.5 m** 7 | ±1.5 m 7 | Requires stable lock on 12+ satellites.16 |
| **RTK Differential Navigation** | **±0.01 m** 10 | ±0.01 m 10 | Achieves centimeter-level accuracy with base station RTK.10 |
| **Indoor Non-GPS Hovering** | Unstated | ±0.3 m drift 5 | Requires contrast or texture in at least one direction.5 |
| **Outdoor Non-GPS Daytime Flight** | Unstated | ±1.0 m 5 | Verified stable up to 50 m flight altitude.5 |
| **Non-GPS Return-to-Home (RTH)** | Unstated | ±0.5 m landing error 5 | Calculated relative to takeoff point within a 50 m ceiling.5 |

This visual navigation loop allows the drone to perform precise return-to-home and landing procedures without satellite signals, protecting the platform from GNSS-spoofing countermeasures.1

## **Network-Centric Telemetry, Security Architecture, and Developer Integration**

The communications and data-distribution system of the EVO Max series uses a highly decoupled, network-centric stack to support secure, real-time telemetry and payload control.17

### **SkyLink 3.0 RF Output and Range Profile**

The platform's primary wireless link is the SkyLink 3.0 transmission system, which incorporates six antennas and supports adaptive frequency hopping across four primary frequency bands: 900MHz, 2.4GHz, 5.2GHz, and 5.8GHz.10 This multi-band capability allows the system to automatically bypass localized RF jamming by hopping to the cleanest available channel.18 The real-time video link delivers a 1080p stream at 30 frames per second with a transmission bitrate of 64 Mbps and an end-to-end latency of less than 150 milliseconds.18

### **Decentralized Mesh Topology (A-Mesh 1.0)**

A major innovation in the platform's communication stack is the integration of A-Mesh 1.0, a decentralized mobile ad-hoc network (MANET) system.1 Traditional drone swarms operate on a master-slave or linear chain topology, where the loss of a single relay node breaks the entire network link. A-Mesh 1.0 enables peer-to-peer communication, networking, and collaborative data transfer directly between multiple aircraft and ground terminals.1  
If any single aircraft exits the network unexpectedly due to a system failure, kinetic impact, or localized electronic warfare, the surrounding nodes automatically re-route telemetry and video feeds through alternative paths.1 This self-healing architecture supports collaborative mission profiles, including:

* **One Remote, Multiple Aircraft:** A single pilot controls multiple UAS assets.1  
* **Lead-Member Dual Control:** Two separate ground operators seamlessly hand off control of an active asset over long distances.1  
* **Beyond-Line-of-Sight (BVLOS) Relay:** Drones act as physical node extenders, repeating signals to penetrate terrain obstructions or mountain ranges.1

### **Telemetry Streaming and Cloud Integration Protocols**

For enterprise management, the platform integrates with the Autel Integrated Command System (AICS) and third-party flight management platforms such as Aloft Air Control.19 Telemetry streaming and remote commands are managed via an onboard MQTT bridge.19  
To connect the Smart Controller V3 to AICS, the operator retrieves the site's unique MQTT address, port, and credentials from the AICS portal.19 These credentials are input into the controller's Cloud Service menu.19 Once connected, the drone publishes an MQTT telemetry stream containing real-time pitch/roll/yaw, gimbal orientation, sensor state, battery cell voltage, and visual target coordinates.19 Flight logs and live telemetry are also synchronized to Aloft via an API Token, automating compliance and fleet logging.19

### **Hardware Customization and the Payload SDK**

The rear of the EVO Max fuselage features a physical P-Port and P-Port Lite interface to allow third-party physical integrations via the Payload SDK (PSDK).21 This allows organizations to build custom payloads, such as gas sniffers, specialized multispectral sensors, or drop mechanisms.1

### **Table 4: Hardware P-Port and P-Port Lite Interfaces**

| Interface parameter | P-Port Core Interface | P-Port Lite Interface |
| :---- | :---- | :---- |
| **Physical Connector** | Custom Multi-Pin Array 21 | Standard USB-C Connector 21 |
| **Input Voltage Range** | **12 V** to 25.2 V 21 | 5 V (Default) / up to 25.2 V (Requested) 21 |
| **Current Limit** | **4 A** 21 | 1 A (Default) / up to 4 A (High Power) 21 |
| **Total Power Capability** | **48 W** to 100 W 21 | 5 W (Default) / up to 100 W (Requested) 21 |
| **Primary Data Interface** | USB 2.0 (Bulk/RNDIS) & UART 21 | USB 2.0-to-Serial Protocol 21 |
| **Activation Detection** | Pin ON\_DET connected to GND 21 | CC1 or CC2 pulled to GND with 5.1 kΩ 21 |

To draw high-power output through the P-Port Lite interface, the external payload's firmware must transmit an digital request over the serial communication link to the drone's power management module.21 Once approved, the VBUS voltage is raised above its baseline 5 V to a designated value between 12 V and 25.2 V, and the current limit is increased to 4 A to provide up to 100 W of continuous power to the accessory.21

## **Multi-Spectral Payload Deep Dive: Fusion Gimbals**

The tactical utility of the EVO Max platform is concentrated in its 3-axis stabilized multi-sensor gimbals.7 The sensors are co-aligned, enabling target handovers across different spectral bands and allowing the laser rangefinder to calculate real-time GPS coordinates for any targeted point.7

### **Table 5: Payload Specifications Comparison**

| Sensor Subsystem | Fusion 4T (First Generation) | Fusion 4T V2 / Fusion Light 4T XE |
| :---- | :---- | :---- |
| **Zoom Camera Sensor** | 1/2" CMOS, 48MP Effective 3 | 1/2" CMOS, 48MP Effective 3 |
| **Zoom Lens System** | 10x Optical (160x Hybrid), f/2.8–f/4.8 3 | 10x Optical (160x Hybrid), f/2.8–f/4.8 3 |
| **Wide-Angle Sensor** | 1/1.28" CMOS, 50MP Effective 3 | 1/2" CMOS, 48MP Effective 3 |
| **Wide-Angle Optics** | DFOV 85°, 23mm equiv., f/1.9 3 | DFOV 83.4°, 24mm equiv., f/2.8 3 |
| **Thermal Imager** | Uncooled VOx Microbolometer 7 | Uncooled VOx Microbolometer 7 |
| **Thermal Resolution** | 640 × 512 pixels @ 30 fps 7 | 640 × 512 pixels @ 30 fps 7 |
| **Thermal Focal Length** | 13 mm Lens 3 | 9.1 mm Lens (Expanded Field of View) 3 |
| **Thermal Spectral Zoom** | 16x Digital Zoom 7 | 16x Digital Zoom 7 |
| **Thermal Range Modes** | High Gain: \-20°C to 150°C 7; Low Gain: 0°C to 550°C 7 | High Gain: \-20°C to 150°C 7; Low Gain: 0°C to 550°C 7 |
| **Laser Rangefinder** | 905 nm operating wavelength 7 | 905 nm operating wavelength 7 |
| **LRF Envelope & Range** | 5 m to 1200 m 7 | 5 m to 1200 m 7 |
| **LRF Precision Formula** | **±(0.5 m + D×0.15%)** 15 | ±(0.5 m + D×0.15%) 15 |

The first-generation Fusion 4T gimbal used a 13mm thermal lens, which provided higher angular resolution but limited the field of view.3 The Fusion 4T V2 and Fusion Light 4T XE gimbals utilize a wider 9.1mm thermal lens, expanding the field of view to capture larger thermal profiles in search-and-rescue and industrial inspection operations.3  
The laser rangefinder (LRF) provides slant-range distance data to target centers.24 When fused with the aircraft's internal GPS coordinates, altitude, and relative gimbal angles, the system instantly geolocates target coordinates up to 1.2 kilometers away.15 This coordinate data is written directly to the XMP metadata of captured images 19 and synchronized across the A-Mesh network.19

## **Decentralized Swarm Intelligence (A-Mesh 1.0)**

Under active RF jamming conditions, point-to-point communication links are easily severed. A-Mesh 1.0 provides a decentralized network architecture that allows multiple drones to share telemetry, coordinates, and video streams.2

### **Self-Healing MANET Mechanics**

Unlike a master-slave network, which fails if the primary controller goes offline, A-Mesh 1.0 utilizes a mobile ad-hoc network (MANET) protocol where every aircraft acts as an autonomous routing node.1  
If an active drone is disabled, the remaining nodes automatically restructure the routing path.1 This self-healing mechanism preserves the data link and ensures that telemetry and video feeds from surviving drones are routed back to the ground control station.1  
In this mesh topology, drones can act as signal relays to extend operation range past physical line of sight (BVLOS).1 For example, a middle drone can hover on a ridge line to relay signals from a lead drone operating deep within a valley, overcoming line-of-sight RF limits in complex terrain.1

## **Augmented Reality Scene Engine and Situational Awareness**

To help pilots maintain spatial awareness during complex operations, the Autel Enterprise App includes an Augmented Reality (AR) Scene Engine.13 This engine projects live information directly onto the pilot's primary camera feed.13  
The AR Engine uses the onboard ADS-B receiver to track manned aviation transponders in the area, projecting identified aircraft locations onto the live map and camera overlay.13 Localized terrain elevation databases are also integrated to display structural profiles of nearby mountains and obstacles \[User Query\].  
When operating in A-Mesh networking mode, the coordinates of other active drones in the swarm are shared via peer-to-peer telemetry.19 The AR Engine displays these positions as virtual overlays on the controller screen, helping operators avoid mid-air collisions in multi-aircraft search-and-rescue or patrol missions.13

## **Strategic Synthesis**

The Autel EVO Max series marks a shift from reactive commercial drones to proactive, edge-computing tactical platforms.1 By moving sensor fusion and artificial intelligence models from ground stations onto the aircraft's hardware, the platform achieves operational autonomy that remains resilient under severe signal interference.1  
In contested environments, traditional point-to-point communication links are highly vulnerable to RF jamming and GNSS denial.10 The EVO Max platform addresses these vulnerabilities through its underlying hardware and software design:

* **Visual SLAM odometry** prevents drift and maintains flight stability under complete GNSS denial, calculating precise relative coordinates through optical flow mapping.1  
* **Millimeter-wave radar and binocular vision fusion** provides continuous, all-weather 720-degree obstacle avoidance, resolving small obstacles like utility lines down to 0.5 inches even in zero-light or rainy conditions.1  
* **A-Mesh 1.0 ad-hoc networking** eliminates single points of failure in communication links, allowing dynamic self-healing telemetry routing across multi-drone fleets.1  
* **Onboard NPU edge inference** enables low-latency target classification for up to 64 targets simultaneously, processing uncompressed video feeds to maximize tracking accuracy in the field.4

While running these onboard systems simultaneously places high thermal and processing demands on the platform, physical hardware adaptations—such as the V2 chassis's dedicated cooling slots—demonstrate the engineering solutions used to support these edge operations in demanding environments.3 The EVO Max series provides a highly capable, resilient platform for public safety, industrial inspection, and defense applications.1

#### **Works cited**

1. Autel Evo Max 4T XE Bundle \- Agri Spray Drones, accessed on June 13, 2026, [https://shop.agrispraydrones.com/products/evo-max-4t-xe-bundle](https://shop.agrispraydrones.com/products/evo-max-4t-xe-bundle)  
2. Autel EVO Max 4T XE Drone, accessed on June 13, 2026, [https://www.dominiondrones.com/products/autel-robotics-evo-max-4t](https://www.dominiondrones.com/products/autel-robotics-evo-max-4t)  
3. EVO Max 4T vs. 4T XE vs. 4T V2: A Full Comparison | Autelpilot, accessed on June 13, 2026, [https://www.autelpilot.com/blogs/news/evo-max-4t-vs-4t-xe-vs-4t-v2-a-full-comparison](https://www.autelpilot.com/blogs/news/evo-max-4t-vs-4t-xe-vs-4t-v2-a-full-comparison)  
4. Autel Evo Max4T, Tracking \- ASD Knowledge Hub \- Agri Spray Drones, accessed on June 13, 2026, [https://knowledgebase.agrispraydrones.com/autel-evo-max4t-tracking](https://knowledgebase.agrispraydrones.com/autel-evo-max4t-tracking)  
5. Autel Autonomy Engine of Autel MAX 4T | Autelpilot, accessed on June 13, 2026, [https://www.autelpilot.com/blogs/news/autel-autonomy-engine-of-autel-max-4t](https://www.autelpilot.com/blogs/news/autel-autonomy-engine-of-autel-max-4t)  
6. Applications of the EVO Lite Enterprise Series \- Aerogence.com, accessed on June 13, 2026, [https://aerogence.com/autel-drones/autel-evo-lite-enterprise-series/applications-of-the-evo-lite-enterprise-series/](https://aerogence.com/autel-drones/autel-evo-lite-enterprise-series/applications-of-the-evo-lite-enterprise-series/)  
7. EVO Max Series | Industrial Drone with AI, Zoom & Night Vision, accessed on June 13, 2026, [https://aerogence.com/product/autel-evo-max-series-4t-v2/](https://aerogence.com/product/autel-evo-max-series-4t-v2/)  
8. Autel Max Evo 4T | Drone Nerds Enterprise, accessed on June 13, 2026, [https://enterprise.dronenerds.com/commercial-drone-platforms/autel-max-evo-4t/](https://enterprise.dronenerds.com/commercial-drone-platforms/autel-max-evo-4t/)  
9. Autel EVO Max 4T XE Bundle \- Altitude Hobbies, accessed on June 13, 2026, [https://www.altitudehobbies.com/products/autel-evo-max-4t-bundle](https://www.altitudehobbies.com/products/autel-evo-max-4t-bundle)  
10. Autel EVO Max 4T Drone Overview | PDF | Unmanned Aerial Vehicle | 4 G \- Scribd, accessed on June 13, 2026, [https://www.scribd.com/document/710455278/Evo-Max-4T](https://www.scribd.com/document/710455278/Evo-Max-4T)  
11. Autel Robotics EVO Max 4T \- E38 Survey Solutions, accessed on June 13, 2026, [https://e38surveysolutions.com/products/evo-max-4t](https://e38surveysolutions.com/products/evo-max-4t)  
12. EVO Max Series \- Autel Robotics, accessed on June 13, 2026, [https://www.autelrobotics.com/wp-content/uploads/2024/02/EVO-Max-Series\_Brochure-1.pdf](https://www.autelrobotics.com/wp-content/uploads/2024/02/EVO-Max-Series_Brochure-1.pdf)  
13. EVO MAX 4N V2 \- Autel Drones Baltic, accessed on June 13, 2026, [https://auteldronesbaltic.com/en/enterprise-drones/evo-max-4n/](https://auteldronesbaltic.com/en/enterprise-drones/evo-max-4n/)  
14. EVO Max 4T V2 \- Autel Drones Baltic, accessed on June 13, 2026, [https://auteldronesbaltic.com/en/enterprise-drones/evo-max-4t/](https://auteldronesbaltic.com/en/enterprise-drones/evo-max-4t/)  
15. Meet New Upgraded Generation of EVO MAX: Autel EVO MAX V2 ..., accessed on June 13, 2026, [https://www.autelpilot.com/blogs/news/meet-the-new-autel-evo-max-v2](https://www.autelpilot.com/blogs/news/meet-the-new-autel-evo-max-v2)  
16. EVO Max 4T Maintenance Manual | PDF | Battery Charger | Manufactured Goods \- Scribd, accessed on June 13, 2026, [https://www.scribd.com/document/721375807/EVO-Max-4T-Maintenance-Manual](https://www.scribd.com/document/721375807/EVO-Max-4T-Maintenance-Manual)  
17. \[PDF\] Autel EVO Max Series V2 User Manual Download \- Autelpilot, accessed on June 13, 2026, [https://www.autelpilot.com/blogs/support/pdf-autel-evo-max-series-v2-user-manual-download](https://www.autelpilot.com/blogs/support/pdf-autel-evo-max-series-v2-user-manual-download)  
18. EVO Max Series \- Autel Robotics, accessed on June 13, 2026, [https://www.autelrobotics.com/productdetail/evo-max-series-old/](https://www.autelrobotics.com/productdetail/evo-max-series-old/)  
19. Explore the New Features of the EVO Max V1.9 series | Autelpilot, accessed on June 13, 2026, [https://www.autelpilot.com/blogs/news/explore-the-new-features-of-the-evo-max-v1-9-series](https://www.autelpilot.com/blogs/news/explore-the-new-features-of-the-evo-max-v1-9-series)  
20. Product Support \- Cloud API \- Autel Robotics, accessed on June 13, 2026, [https://doc.autelrobotics.com/cloud\_api/en/10/30/](https://doc.autelrobotics.com/cloud_api/en/10/30/)  
21. UAV Hardware Interfaces | Autel Developer Technologies, accessed on June 13, 2026, [https://developer.autelrobotics.com/doc/payload\_sdk/v1.1/psdk\_docs/en/60/2](https://developer.autelrobotics.com/doc/payload_sdk/v1.1/psdk_docs/en/60/2)  
22. UAV Hardware Connection | Autel Developer Technologies, accessed on June 13, 2026, [https://developer.autelrobotics.com/doc/payload\_sdk/v1.1/psdk\_docs/en/60/3](https://developer.autelrobotics.com/doc/payload_sdk/v1.1/psdk_docs/en/60/3)  
23. UAV / Drone News \- Unmanned Systems Technology, accessed on June 13, 2026, [https://www.unmannedsystemstechnology.com/category/news/uav-news/page/64/](https://www.unmannedsystemstechnology.com/category/news/uav-news/page/64/)  
24. EVO+Max+4T+User+Manual en | PDF \- Scribd, accessed on June 13, 2026, [https://www.scribd.com/document/777526246/EVO-Max-4T-User-Manual-En](https://www.scribd.com/document/777526246/EVO-Max-4T-User-Manual-En)  
25. Autel Robotics EVO Max 4T V2 2026 Industry Flagship drone | Autelpilot, accessed on June 13, 2026, [https://www.autelpilot.com/products/autel-robotics-evo-max-4t](https://www.autelpilot.com/products/autel-robotics-evo-max-4t)
















































---

## **Appendix: Field Validation Results (Ericsson Jorvas, 2026-06-12)**

*Author: Richard Wirén, Lead Solution Architect — Ericsson*

The following findings were obtained during a controlled test flight at the Ericsson campus in Jorvas, Finland (60.13°N, 24.52°E) using firmware v1.9.1.219. These results validate the platform's AI capabilities and document calibration parameters for integrating the MQTT detection stream with post-flight image analysis.

### **Test Configuration**

| Parameter | Value |
|:---|:---|
| **Platform** | Autel EVO MAX 4T V2 xe (SN: 1748FEV3HMM825351343) |
| **Controller** | Smart Controller V3 (SN: TH7825451059) |
| **Firmware** | v1.9.1.219 |
| **Flight Duration** | 510 seconds (8.5 minutes) |
| **Altitude Range** | 15.3 m – 134.7 m AGL |
| **Max Speed** | 15.0 m/s |
| **MQTT Telemetry Rate** | ~1 Hz OSD, ~19 detections/sec |
| **AI Detection Classes** | Vehicle (cls_id=3), Person (cls_id=30), Bicycle (cls_id=2) |

### **Onboard AI Detection Performance**

The onboard NPU successfully detected and tracked targets throughout the flight:

| Metric | Result |
|:---|:---|
| **Total AI detections** | 8,297 detection reports via MQTT |
| **Vehicle detections** | ~6,500 (cls_id=3), including 75 unique tracked vehicles at peak |
| **Person detections** | ~1,200 (cls_id=30), 1 actual person tracked across 123 unique IDs |
| **Detection range (person)** | Verified at 18.8 m – 134.7 m AGL |
| **False positive rate (vehicles)** | <5% (dumpsters occasionally classified as trucks) |
| **False positive rate (persons)** | 0% observed in controlled test |

**ID Fragmentation:** The tracker assigned 123 unique IDs to a single stationary person across the 5.5-minute detection window. Spatial clustering confirmed all detections within a 10 m radius represent the same individual. This fragmentation occurs as the drone changes altitude, heading, and distance — a known limitation of the onboard tracker's re-identification logic.

### **Firmware OSD Label Discrepancy**

A critical discovery for developers integrating with the Autel MQTT telemetry: **the camera field labels in the OSD topic are swapped**.

| OSD Field Name | Firmware Reports | Actual Physical Camera |
|:---|:---|:---|
| `cameras[0].ir_focal_length` | 9.1 mm | Zoom/Telephoto lens |
| `cameras[0].ir_fov_h` | 48.1° | Zoom/Telephoto FOV |
| `cameras[0].zoom_focal_length` | 4.49 mm | Wide-angle camera |
| `cameras[0].zoom_fov_h` | 58.6° | Wide-angle FOV |
| Actual thermal camera (13 mm, DFOV 42°) | — | **Not reported in OSD** |

This was confirmed by cross-referencing datasheet specifications with the MQTT schema captured via the [Autel Mission Control](https://github.com/rwiren/autel-mission-control) infrastructure. The AI detection stream uses the wide camera coordinate space (58.6° FOV) internally, regardless of which sensor is being recorded.

### **MQTT Detection Coordinate Calibration**

When overlaying MQTT bounding boxes on saved images, an affine correction is required due to the FOV mismatch between the AI processing stream and the actual camera sensors.

**Calibration Model (validated to <2.5 px at nadir):**

```
Thermal JPEG (640×512):
  x_corrected = 0.8384 × x_mqtt + 0.0915
  y_corrected = y_mqtt + 0.049

RGB JPEG (4000×3000):
  x_corrected = 0.5 + (x_mqtt - 0.5) × 1.218
  y_corrected = 0.5 + (y_mqtt - 0.5) × 1.184
```

| View Geometry | Calibration Error | Notes |
|:---|:---|:---|
| Nadir (0° pitch, 80 m) | **< 2.5 px** | Affine model is sufficient |
| Angled (-33° pitch, 19 m) | ~87 px | Requires projective homography; use GPS position instead |

**Root Cause:** The firmware's AI pipeline maps detection coordinates using the wide-camera FOV (58.6°), but the thermal sensor has a narrower FOV (42° DFOV, 13 mm lens). This creates non-linear compression that manifests as inward radial squeeze at nadir and severe keystone distortion at angled views.

### **Lateral Distance Rule Validation (Patent WO2025034145A1)**

The flight served as a validation of patent WO2025034145A1 ("Calculating Lateral Distance from Uncrewed Autonomous Vehicle to Object"), demonstrating the end-to-end system:

1. **Detection:** Onboard AI classified person (cls_id=30) at ranges from 6 m to 200+ m
2. **Distance Measurement:** LRF provided ground-truth slant range (±1 m accuracy)
3. **Rule Evaluation:** `lateral_distance < safety_value × altitude` → violation alert
4. **Message Issuance:** Detection + GPS position published via MQTT to controller

| Image | Altitude (m) | LRF Slant (m) | Lateral Distance (m) | Ratio | Status |
|:---|:---|:---|:---|:---|:---|
| MAX_0043 | 18.8 | 6.05 | 5.09 | 0.27× | ✗ VIOLATION |
| MAX_0044 | 21.7 | 12.19 | 10.27 | 0.47× | ✗ VIOLATION |
| MAX_0045 | 21.7 | 12.23 | 10.30 | 0.47× | ✗ VIOLATION |
| MAX_0046 | 25.8 | 19.87 | 16.97 | 0.66× | ✗ VIOLATION |

**Full timeline:** 3,873 measurements over 5.5 minutes, with 99.6% flagged as violations. Only 14 brief passes occurred during lateral traverses at altitude.

### **Parking Occupancy Monitoring**

At 134 m nadir (GSD ~3.4 cm/px), the system detected **104 vehicles** across the Ericsson Jorvas parking lot — approximately 59% occupancy. Post-processing with aspect ratio filtering (`width/height > 1.4 = non-vehicle`) eliminated false positives from dumpsters, skylights, and HVAC equipment visible on rooftops.

### **Model Comparison**

Three detection approaches were evaluated on the same imagery:

| Model | Strengths | Weaknesses | Best For |
|:---|:---|:---|:---|
| YOLOv8s (VisDrone fine-tuned) | Aerial/nadir vehicle detection (75.7% mAP50 cars) | Misclassifies persons at close range | Parking occupancy, vehicle counting |
| YOLOv8s (COCO pretrained) | Person detection (0.91 conf at 19 m) | False positives from nadir ("TV", "cell phone") | Angled person detection |
| Autel Onboard AI (NPU) | Zero false positives, provides GPS per target | Conservative (fewer total detections) | Real-time safety monitoring, ID tracking |

### **Thermal vs. RGB Detection Insights**

| Object | RGB Signature | Thermal Signature | Detection Notes |
|:---|:---|:---|:---|
| Parked car (cold engine) | Clear color/shape | Dark rectangle, blends with shadows | Thermal may miss cold vehicles |
| Person | Clothing visible | Very bright (37°C body heat) | Thermal excels in all conditions |
| Dumpster/container | Green/blue, clearly not a car | Variable temperature | Both modalities produce FPs from nadir |
| Pavement shadow | Visible as dark area | Cool patch ≈ cold car signature | **Thermal can confuse shadow with vehicle** |

### **References**

- Patent: [WO2025034145A1](https://patents.google.com/patent/WO2025034145A1/en) — "Calculating Lateral Distance from Uncrewed Autonomous Vehicle to Object" (Wirén, Grancharov — Ericsson, 2025)
- Companion repository: [autel-mission-control](https://github.com/rwiren/autel-mission-control) — MQTT bridge, DVR, telemetry dashboards
- Detection pipeline: `lmfwire/detection-with-drone` (Ericsson internal GitLab)
- EU Regulation: [Commission Implementing Regulation (EU) 2019/947](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32019R0947)
