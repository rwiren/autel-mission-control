# **Engineering Analysis of the Autel EVO Max Series Edge-Computing and Sensor Fusion Architecture**

The operational landscape for commercial and enterprise unmanned aerial systems (UAS) has transitioned from simple remote-controlled operations to complex, high-interference, and contested environments. The Autel Robotics EVO Max series—comprising the EVO Max 4T, the EVO Max 4T XE, and the updated EVO Max 4T V2 platforms—embodies this shift by moving away from ground-station-dependent computing to a fully decentralized, edge-computing architecture governed by the Autel Autonomy Engine.1 By processing complex spatial, visual, and electronic datasets directly on the aircraft in real time, these platforms maintain operational stability and mission capability under conditions that typically disable conventional commercial UAS.1

## **Onboard Edge-Computing and Neural Processing Unit Architecture**

At the core of the target recognition and dynamic tracking capabilities of the EVO Max series is a dedicated onboard Neural Processing Unit (NPU) \[User Query\]. Traditional systems stream compressed video over a wireless link to a ground control station (GCS) for processing, which introduces significant latency and exposes the system to data loss from radio frequency (RF) interference or active jamming. The Autel Autonomy Engine addresses this vulnerability by executing convolutional neural network (CNN) inference directly on the raw, uncompressed hardware video pipelines before any digital encoding or H.264/H.265 compression occurs \[User Query\].  
This pre-compression processing pipeline is technically significant. Digital video compression algorithms compress files by throwing away high-frequency spatial details and color metadata through chroma subsampling and macroblocking. While these artifacts are minor to human operators, they degrade the performance of deep learning object classification models. By performing inference directly on the raw sensor tap, the onboard NPU preserves pixel-level edge gradients and micro-contrasts, which significantly extends the maximum effective range of target detection and classification.3

### **The Dot Pre-Detection and Target Classification Pipeline**

When an operator switches the payload view into Tripod/Tracking Mode within the Autel Enterprise App, the edge classifier starts a real-time pre-detection cycle.4 Rather than requiring the pilot to guess which targets are within tracking range, the NPU scans the active frame and overlays a geometric pre-detection marker (a small dot) over classified objects that meet high-confidence thresholds.4  
The underlying native classifier is trained on industrial, defense, and public safety datasets \[User Query\]. It classifies up to ![][image1] distinct targets simultaneously with a verified comprehensive classification accuracy exceeding ![][image2].5  
The system classifies targets into three primary categories 5:

* **Pedestrians and Moving Personnel:** The network is optimized to identify human skeletal proportions, high-visibility safety apparel in daylight, and thermal human body heat signatures in low-light environments \[User Query\].  
* **Vehicles:** The model distinguishes civilian cars, commercial trucks, transport vehicles, and naval vessels \[User Query\].  
* **Heat Sources:** The thermal processing pipeline isolates thermal centroids, high-temperature industrial anomalies, and emerging forest fire hotspots.6

The control interface provides a multi-spectral target tracking workflow.4 The pilot can either tap an active pre-detection dot to lock the 3-axis gimbal's coordinate tracking onto that target's centroid, or manually draw a bounding box Region of Interest (ROI) over an unclassified target to force a visual tracking lock.4 Once locked, the gimbal automatically adjusts its pitch, roll, and yaw to keep the target centered.4 Simultaneously, the flight controller coordinates with the gimbal to maintain the aircraft's forward-facing orientation toward the target.4 This leaves manual flight coordinates active so the pilot can perform tracking adjustments or offset maneuvers without losing the target lock.4  
A technical constraint exists within the multi-spectral sensor pipeline: the thermal imaging camera's digital signal processor (DSP) does not natively render the AI pre-detection dots.4 To establish a tracker lock in low-visibility or infrared-dominant missions, the system relies on a multi-spectral handover workflow:  
![][image3]  
The pilot first views the scene through the visible light spectrum camera, taps the pre-detection dot (or draws an ROI bounding box) to lock the tracking system, and then switches the active video feed to the thermal infrared view.4 This coordinates target tracking across both thermal and optical spectral bands.

### **Table 1: Edge-AI Target Tracking and Performance Parameters**

| Parameter | Operational Specification | Functional Implications |
| :---- | :---- | :---- |
| **Onboard NPU Location** | Pre-compression video pipeline \[User Query\] | Minimizes latency, avoids compression artifacts, and maintains tracking under RF jamming. |
| **Max Simultaneous Targets** | **![][image1]** targets 5 | Enables wide-area surveillance and tactical monitoring in dense urban or chaotic environments. |
| **Classifier Accuracy** | **![][image4]** comprehensive accuracy 5 | Reduces false-positive triggers during automated perimeter sweeps or search-and-rescue flights. |
| **Native Target Classes** | Moving people, vehicles, naval vessels, heat sources 5 | Supports multi-domain applications across public safety, coastal security, and utility inspections. |
| **Gimbal Integration** | Dual-mode: Tap AI dot or manual ROI box 4 | Gives operators flexibility to track both standard classified targets and custom objects of interest. |
| **Thermal Tracking Mode** | RGB-to-Thermal multi-spectral coordinate handover 4 | Bypasses thermal-rendering constraints to maintain tracking in complete darkness. |

## **Spatial Awareness and Perceptual Sensor Fusion**

Standard commercial drones rely on binary reactive distance sensors, such as ultrasonic transducers or single-point infrared sensors, which execute basic stop-and-hover routines when an obstacle enters their detection envelope. In contrast, the Autel Autonomy Engine on the EVO Max series uses deep multi-sensor data fusion to generate real-time local semantic models of the surrounding space.7

### **The 720-Degree Omnidirectional Perceptual Loop**

To achieve reliable situational awareness in all weather conditions, the platform fuses data from two complementary sensor modalities 1:

* **Dual-Fisheye Binocular Vision Systems:** These optical arrays map visual disparity, depth, and optical flow in high-contrast, daylight environments.10 They provide high-resolution semantic segmentation of nearby structures, trees, and ground features.  
* **60GHz Millimeter-Wave Radar:** Operating within the ![][image5] to ![][image6] frequency band, this active radar system is unaffected by low light, rain, heavy snow, thick fog, or dense airborne dust.1 It penetrates atmospheric obscurants to detect thin obstacles down to ![][image7] (![][image8]) in diameter, such as overhead power lines, structural wiring, and tree branches.10

By combining these two datasets, the flight computer creates a unified spatial map.1 The optical system provides detailed shape and edge information, while the millimeter-wave radar provides accurate distance measurements through environmental obscurants.1 This dual-sensing system eliminates blind spots across a ![][image9] omnidirectional envelope.1

### **Real-Time 3D Pathfinding and Obstacle Avoidance**

The onboard flight computer feeds this fused spatial map directly into localized pathfinding algorithms.1 If a newly detected physical obstacle blocks a pre-planned waypoint trajectory, the system calculates localized 3D path vectors to navigate around the object in real time.1 This edge rerouting process operates on two distinct algorithms depending on mission requirements 5:

* **High-Speed Rerouting Mode:** Optimized for active obstacle avoidance at flight velocities up to ![][image10], maintaining a minimum safety clearance envelope of ![][image11] from obstacles.5  
* **High-Precision Rerouting Mode:** Configured for tight, complex spaces, allowing flight speeds up to ![][image12] with a localized obstacle safety envelope of ![][image13].5

### **Table 2: Sensor Fusion and Obstacle Sensing Envelopes**

| Sensor Subsystem | Operating Frequency / Spec | Detection Range | Minimum Target Size / Envelope |
| :---- | :---- | :---- | :---- |
| **Binocular Vision Arrays** | Visible Light Optical Flow 10 | ![][image13] to ![][image14] 10 | Requires ![][image15] illumination with surface texture.12 |
| **MMW Radar (Upward)** | **![][image5]** to ![][image6] 10 | ![][image16] to ![][image17] 13 | Detects high-voltage transmission lines down to ![][image7].13 |
| **MMW Radar (Forward/Backward)** | **![][image5]** to ![][image6] 10 | ![][image18] to ![][image17] 13 | Active up to ![][image19] relative flight velocity.13 |
| **MMW Radar (Sidewards)** | **![][image5]** to ![][image6] 10 | ![][image18] to ![][image17] 13 | Active up to ![][image19] relative flight velocity.13 |
| **Visual Depth Sensing (Lateral)** | Multi-Directional Fisheye 1 | ![][image20] to ![][image21] (Sideward) 14 | Requires surface texture and sufficient lighting.12 |

## **Electronic Warfare Countermeasures and GPS-Denied Visual Navigation**

Operating in modern urban zones, near high-voltage energy grids, or in active combat zones exposes UAS platforms to severe electromagnetic interference (EMI), radio frequency interference (RFI), and intentional GNSS spoofing or jamming.1 The EVO Max series utilizes hardened flight control modules running custom anti-spoofing and anti-jamming algorithms.1  
In the event of total GNSS signal loss (complete loss of GPS, GLONASS, Galileo, and BeiDou), the drone switches navigation modes.1 Instead of entering an uncontrolled drift state, the Autel Autonomy Engine engages high-precision visual navigation powered by Simultanous Localization and Mapping (vSLAM) visual odometry.1 This system processes high-contrast visual features and ground-plane optical flow captured by the 50MP wide-angle camera.7

### **Table 3: Spatial Navigation Accuracy under GNSS-Denied and Nominal Conditions**

| Flight Mode / Condition | Vertical Position Accuracy | Horizontal Position Accuracy | Operational Parameters |
| :---- | :---- | :---- | :---- |
| **Visual Positioning Only** | **![][image22]** 7 | ![][image23] 7 | Active in daylight or textured indoor spaces.5 |
| **Standard GNSS Navigation** | **![][image24]** 7 | ![][image24] 7 | Requires stable lock on ![][image25] satellites.16 |
| **RTK Differential Navigation** | **![][image26]** 10 | ![][image26] 10 | Achieves centimeter-level accuracy with base station RTK.10 |
| **Indoor Non-GPS Hovering** | Unstated | ![][image27] drift 5 | Requires contrast or texture in at least one direction.5 |
| **Outdoor Non-GPS Daytime Flight** | Unstated | ![][image28] 5 | Verified stable up to ![][image29] flight altitude.5 |
| **Non-GPS Return-to-Home (RTH)** | Unstated | ![][image30] landing error 5 | Calculated relative to takeoff point within a ![][image29] ceiling.5 |

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
| **Input Voltage Range** | **![][image31]** to ![][image32] 21 | ![][image33] (Default) / up to ![][image32] (Requested) 21 |
| **Current Limit** | **![][image34]** 21 | ![][image35] (Default) / up to ![][image36] (High Power) 21 |
| **Total Power Capability** | **![][image37]** to ![][image38] 21 | ![][image39] (Default) / up to ![][image40] (Requested) 21 |
| **Primary Data Interface** | USB 2.0 (Bulk/RNDIS) & UART 21 | USB 2.0-to-Serial Protocol 21 |
| **Activation Detection** | Pin ON\_DET connected to GND 21 | CC1 or CC2 pulled to GND with ![][image41] 21 |

To draw high-power output through the P-Port Lite interface, the external payload's firmware must transmit an digital request over the serial communication link to the drone's power management module.21 Once approved, the VBUS voltage is raised above its baseline ![][image33] to a designated value between ![][image31] and ![][image32], and the current limit is increased to ![][image36] to provide up to ![][image40] of continuous power to the accessory.21

## **Multi-Spectral Payload Deep Dive: Fusion Gimbals**

The tactical utility of the EVO Max platform is concentrated in its 3-axis stabilized multi-sensor gimbals.7 The sensors are co-aligned, enabling target handovers across different spectral bands and allowing the laser rangefinder to calculate real-time GPS coordinates for any targeted point.7

### **Table 5: Payload Specifications Comparison**

| Sensor Subsystem | Fusion 4T (First Generation) | Fusion 4T V2 / Fusion Light 4T XE |
| :---- | :---- | :---- |
| **Zoom Camera Sensor** | 1/2" CMOS, 48MP Effective 3 | 1/2" CMOS, 48MP Effective 3 |
| **Zoom Lens System** | 10x Optical (160x Hybrid), ![][image42] 3 | 10x Optical (160x Hybrid), ![][image42] 3 |
| **Wide-Angle Sensor** | 1/1.28" CMOS, 50MP Effective 3 | 1/2" CMOS, 48MP Effective 3 |
| **Wide-Angle Optics** | DFOV 85°, 23mm equiv., ![][image43] 3 | DFOV 83.4°, 24mm equiv., ![][image44] 3 |
| **Thermal Imager** | Uncooled VOx Microbolometer 7 | Uncooled VOx Microbolometer 7 |
| **Thermal Resolution** | 640 ![][image45] 512 pixels @ 30 fps 7 | 640 ![][image45] 512 pixels @ 30 fps 7 |
| **Thermal Focal Length** | 13 mm Lens 3 | 9.1 mm Lens (Expanded Field of View) 3 |
| **Thermal Spectral Zoom** | 16x Digital Zoom 7 | 16x Digital Zoom 7 |
| **Thermal Range Modes** | High Gain: \-20°C to 150°C 7; Low Gain: 0°C to 550°C 7 | High Gain: \-20°C to 150°C 7; Low Gain: 0°C to 550°C 7 |
| **Laser Rangefinder** | 905 nm operating wavelength 7 | 905 nm operating wavelength 7 |
| **LRF Envelope & Range** | 5 m to 1200 m 7 | 5 m to 1200 m 7 |
| **LRF Precision Formula** | **![][image46]** 15 | ![][image46] 15 |

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

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAXCAYAAAAGAx/kAAABFElEQVR4Xu2TMYoCQRBFy0AQFDdQ3EBBA1MvIIjJxht5g72BYuABzEXMxXRzL+AdTAQDRcw2WdBMtP50tdR096CI4Tz40P2r+XRN1xClvEKW1WXV3UKAGuvHNUGRdWZdRcN42eOXtXDNL9aFlZF9i0xY+X4iTpNMPRaEdmCiaOmLV1We5p8CQTMxnwUtlSgQtBYTFFg5VQuB2wAvCMaJdSDzEiMy32ugD5H5BHNWRfbBIOhDeZ/iIdiyYU3UPjHIBd5S1t8iTTAIrbnA38ka89VzhPpK1hF/9DjI3jpJEVO9EfBy8FBLwmvNDqR9DdARz056CC8INMgUMAL2unl9QIF2MR571pH8bqjN2rLGFP9dUt7ADXWjUiQhGDBKAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAYCAYAAACWTY9zAAACJ0lEQVR4Xu2VPWhUURCFjxhBiWIhKIKQCEEIiBaioJggwSIgpNCAdimCaGGloG3EXkRQQQnRwkYUhKBISLFoEwgkpSJYJE0KC7FQ/MGfczLv7Z07++KuhWDxPjjsnbmzc2fvzyxQ8/+wk9oYnYHN0fEv6aE+wYo6S93Kp5v0Uq+js4pN1GfqV6HBfHqVeeo+bHHtyDHqDbU/heADddDZWvwb9ZQapR4irdHl4ipZB0voeUuNBN8SUtJSp7MI86nokivUFmcL7WjMXck5WALPLlghfhHZG4IvUlXYDmffheXuCH1ZCdc73zD1AnbEJQ03Xgvl6Xf2Mzfupe44uy3bkI7mMqyYn7Dd8TSKz6vUA2o8TTW5RM0W463UjJv74sYdo1/p7053Pr1Kg3rp7FOwWN1Rjx7OMnXP+abQeoQdtYsn1G1qEam4E1kEcCTYQnFz0RnoQ36EP2DrHKAWnL8FfUm/qGQPUnETzl+FXpji/sR3N56gHiO1igvIH0eGWsXe4NM90oKvnG8MrcfWrrC4W+qFN52tXTvq7Awlrjpv+dUixJnCjm2lXWF+t4TifQ71uJizyVfqcHTCFtRWCz2OSTdXophH0Ql72dPU9uBfQV6Iet5JZ2f0wBbYV9hqEx+pQ80IQ/8GQ8V4N+yFageqeE/diE7YHWsgndA1WFtZE90d9SA98+vIm63nOPUO9udc9UrFeWogOh260yr8IvU8zNXU1NT8Db8BqrByu9dF+tcAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAWCAYAAACPHL/WAAAAi0lEQVR4Xu3UoQ2EQBSE4UcIgiBRJBgU7iyeKk5dGaeoggZIaIYEg7wecFgMDHluOpjc+5Lf7KgVu2YhhBAElejLh+pytKOZB3Up+qEV9bRJS9ALXehDm7zG/GIDD+pGdPKhogkdqOBBSYcW8w8io03O87s9b2Yz//Vkvc0v0vKgpjZ/7BUPIYT/cgP0HBDujAOEKQAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAWCAYAAAB+F+RbAAACXUlEQVR4Xu2Wv0uVYRTHz6UCQ8EhUEMHB3OKQATBFiFqdUgHhTa3qKUh6A8InERFEATBVq3AIVwcLk2igw21hA1JNAgSBDUU/Tjfe865nnt43ve91+4SvB/4cu855/l1nvf5RVRSUvK/c4k1weqIAcc1Vg/rQgw0wQ7rT9Csxn5ZIeWEdRz0SWOridgRa1TjhaDCNusKa571uzFMd0kG1Mm6wTpkbTWUyKaPJLFd1kCI3SbpC/FIhcRvSUbgT9XL5TNr0dk26zZTF9XurpcQfJkssFpQ7m0MODYpe9Dwf4xOBf6seklsMEPOZ8n2q31d7chX1nJ0BiZJ6s7EgGOc0u2Dtia7QsUVnlO6zDuShPPIWqKRrDJtTfY76xtrhM6+6C2S/WJkNVqltN/A/kb8ZwwkWIgOpdVku9QXVcOMe+ZQ25+OmIzYKKhS2m9cJYlnHTDNEAedkgd9fnD2FCWS9eDUhO+B2v+abNFSzwP1W/myODBxc4DLJPE1C8JAMp5n6seeBKlGQZXSfk9qMg2LeaFvT6vJepDXF+84VafHkrVOXqkdwXIp2o97JHXjteUpmpDzJIuviRhumzq4OmIFS86uFVz8sQzA8kTZPOxq248BR7uTHSPx34mB1B13oD57MOCrwI7PSPjy7k/jPUlZnM4p2p3saxJ/RW37rYHBvND/eFygYHwKYllgEgDexU8o7IcCXpK0+4M1qD58dbxpH2rMg/6q6odg20Ezx1p3MTxzl0jatdP3EWuadV/tBm6S7MGnMeAYZr1hbZAs7fPQSzJQvMUfU5j1kpKSEvAX1O7feK155rEAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAWCAYAAAB+F+RbAAACQElEQVR4Xu2WvWsVURDFJ4WgRFCwMEGLFP4DIRBQkEDQUgtNkUC6NCKxEdS/QLASI0IgYGHrF0gIaVI8UolpYyOxiIiQgAgBBRU/5mRm8uYNc82ubCPuDw5v7zl3d++8e7l7iVpaWv51DrDGWAdjkHCEdSOa+7DM+hU0pdkP66Rss94FvddsPsk2WCOa7wtueME6xrrD+tkb93CW9ZXVCX6JAZLCVlgnQ3aO5F3II30kvhUZgZ/d90c+sO65tv3r2T9lA4A6vVEKVgv6rsfA8ZjKg4a/GU0Ffum+FBvMKedZMSecZ2BWn1L1Yi+S9J2MgeM0lQfdaLEPqPoNmFWsggtUvdjSEo2U+jRa7BfWZ9YwdWd0nKSwyCrJSqhabD9Jv+8xSLgbDaVusYfVi9rFGtNmaDvujqOsK3pdtdhBkn6lDaYKcdCZPHjnW9e+TEmxHuya8Gadt+Wu6xa7E4Ma4P46M4tN9ZJeHyLJFyxEA8vY80j919peJFkeRtViQfZnGpZ54d2eusV6UNcnb3xU02PF2kvigKIwgyVekvTBIaSEPSfjb4vFbCLDHrPHfTU9S+ohy7hFkneCn2GftlcxcDRdLPYX+OdjkH3j1tTLDhWgTrHgDUl/7M4ZTReLrwb8Pm3b7y4YzDO9xuECHZ904z1wZsby+EbdAaJ91Hcq8JykP+4dUg+zjjPtNc08eG5HfXuPbTQzrIcuwzF3juS5tvteZ02wrmq7hzMkW/btGDTMcZKB4ix+k/LveUtLy3/ObzNw3nRgVqKlAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEwAAAAWCAYAAABqgnq6AAAC3klEQVR4Xu2XTahNURTH/0IR+SgTr9RNUkoRUYrZy0c+Bj7KQKYmRhQxukNTMZKnDBSRksTA4JaJGJgQQ0yUkhRS8rH+1l7vrr3u2ee+Xvfo0fnVv3fOf++39t5rf50LtLS0tPw/zBZtFS2MBTXMjwY0zqxoVrAnGiNinehX0ulQNjLui55BB3pG9CUvLrIX/c6ZPmY1quFAmhwQx9FY/C3Q4J6nosuiOcGPxITtzouLzBW9QvUKHRWNJeyi6EPwmCx6a4IfYcKo5dCtOJNoLGHfRY+CdwzaIBNXx0ZowmYijSWMgXvBs632IvgRS9i46IFoe15cyRv0t7ANyG9txlwt+in6kTxu4cgFaNlb0WfR9bx4Mv4V0fv0zjqLfSVhUSq7I7qZnjuu/DY0P5fMqEsYB1cHB8d6dhYx6FQOfRJXgB3UTNQp579D3j+2dRf5xcQ2+b8emwBL9tL0/toqQMvorXLetuSxPxzfQA7qEhbPtsiCJMMG3XVeiZgw884Gr4e803xnvf3O48CXuHfCOtcqPJ/oW8mL0NsE3Tl8Xh8Le97A1FdYFZboYRdGKWHxTOwh7wfrUJz9OkrxfcL4bPGidlXU+QO3QDz0T0ArcAbqYJ3nFR4bme6A/mbCOLGTiahhHtwxcQ96Tnh4OzKRXJIGPxv4j55SwngBDPvGKg1oWMIYm/W6ziMrkf9KKcX3CesmL8I43CF2oWUchibH0xM9Rn6jPMTgL4Bv0FvGYEPswBHnlSgNaFjC9kFvz5fOI/ye9P0txfdj4GFPb4XzyE7RWmhfGHcA3jLH07MFiVc5Pcp//R+AXseEK5Bx+CuhjvOiG9BYn0TnoIcq49D7mso70FvX2p1Af4XzoqH3BNrPHaku6aAfn4mlz/PI4lNX0b8kjiaPtyMnfAN0cRA7yw+m94xD0G+ak7FgCFxhbICKM9U0Y9DBxMmdDpuhsfy2Xpb+cqIqk9bS0tLyr/AbSRrlp/oeefsAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAZCAYAAACIA4ibAAACKklEQVR4Xu2WsUsdQRDGv5AICQpqIwoKahGw0YBgkf/AIiDBQtQ6RUgrQipbu5AmIIrY2tqkSPF6wSoQCAhGrBQVArEwJHE+dsedt7l7b+8Z4hX7gw/ezK3r7nc7swdkMpnMv2VRtBon27Ai+uN1KnrS/BgT/tmWaKNAfWFoPZhG2BBVxZBt0XMTH8LN0WtyL32uTA/C0HowKnot6kF1Q36Lukysm39jcm/hTs6xaAfhZOyJds24WlLFEL5ZfcsWxt9FUz5uhEe38G9/xsk6UsUQciDajHKc4wdcKRYxIPqM5rJqxQjCqXqKUGKPRUOieR/zpPI3ZU/tC9EcOizNqobEjMHN8Q7lC/iF9P+xD1dqREtaTySb+Tcf06xJn2dPY24GrkTJK5/74ONk7mrImegyThrYW7ZRbpZlGW49j3yshtBQRS+EBZMjzJ0U5K6iXFvuYsgaWptBOH9ZKcWcw5VeK8bh5qRZFub0dNicnq5kOjVEG+yz+IGBNc8xrPsUOLadIZyrzJB4Hx0bEjubAk/GoInX4a5zyxLc/N1RvozaG/IQ7i3HfMXfNwabYX+Ua6Dagj6ieDzLRA0Yxj0aohNaUz6ZvNV7M0Zhk6uyIF6dHM8bROHNcWFibapFhsT7SDZEj51+TVKMeaXZemcZ8LtD0Z5QpFkzTjlC4oIM7E1fEOblVavfGA3RNdx6efPQAJYYxzHH/fA3v0M0p3tL7WOZTCaTyWQy/4Ub12ytX3Ndb9IAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF8AAAAZCAYAAABXTfKEAAADuUlEQVR4Xu2YTchOWxTHl1Dk+yMfZYCJSHETBgwMJBIJhRiYkWRAcWPySndwDQ0MRJKBut0yQUh6YyLKyFc+Ct3RLRlRyMf+2Wt51rvefR7nwTt5nF/9e85ee5+991ln77XXeUQaGhoaGgoMSpqaNDhWdAOzkz4nnUo6UdBYbYcTHmpbaz9N6zxzpNUGbelb3RE7k95L7ocX0HWsl77OisLp8FFaq2+Eq1+kNvhDbZ7HSUeCrRNGShc7/2DS/0kvk85Ia8V/SvpH20xOuqHXxhPJTrnsbOeSbrkybE16E2yd0NXO742GxP6kta5su+Oisy2X/IL8Suf6gCsDTsM+Ltjr0tXOj0xKuhZsQyU7gPPBWJj0Vu0wSq/XfGuRMeetCvZ20Me6pOnS3vmLJe/SHbFCYd4bk5ZpeVfSM7XbQU79+KQFSSu0nWeC5DGOSr6vxD7JbejjpyC214EQg1PuaXmmlqucH3dECdthM7TM2fJBbd757LrXST1aXi25zRAt41h2L224nqX1U5LeSX4Z85MuqP2B5DG5Piktzkp+WTBGcj3nmkF/1i/ckZyU/BC7k05HY4HhkgdFdiDz1ts5n/OkHfZwc4PdwpY5Hwfb2B7OlWN6zTPEuVAfzyOg3b96fV5ajrTnYf4G/b5yZcKu95c960Rnqw031tk6tur8Npwn/R8Y6q58HBcdCtH59E+ZORAyTI+SXmgbwmacC863VeyJ7YA590qu82P8rTaweWHzbUr9fZdh0vchqyC1JDTZijdsMnFg73zCBVmV101tx2Fex/n0Q7kkc26PlvdqGTifCJWR0pwZixcZ+zeB7YySOjnfvkJKyI3E2SoIDaw4z5/6ay+PuO0hTcW+VNo731ZrJDqfw5WyrfIqSKFpx3NdlfyxVoI20fmEjftaV4V9nMZ7f4heaT8YIQZnRfzLIAb+5cpg4YiX046VktuRNXmi8+1sYKzIIf21NLgOVQ7cLOV573HX1Ns5Y7DTfVZYi/+k2vmEGOpKYoUY26T/BxUfareDrQoykdPBRsbBOP4gJq3DtsnZlkjr24SH52Akm7GPRuJxKVWscj6wsK67MokGu8jYIPl+7AY72bKu2jyXaufbVi/Jp2aA89ji/PfzVNUJvCjrm7PF0kTkMyb+6vBxeburG5103NV5XdI2dnCzm/nC57oEz2P3Xgl1EP/LYuzfGpxwNxqlFbJistDwC8HBpVBnX+qN8wcQ/knFyTFzOyz9s7WGAYAzwb4dEOdH1cHa0NDQ0NAwYHwBX4UuXj6uTV0AAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAZCAYAAACCXybJAAACcElEQVR4Xu2WPWgVQRDHR4ygGMQvEMEmFoIKNqKiYJciIELAFIKNIGgjgogKVs/eQsRKbKwEEesgKV4v2AZSRdEEFBFCtFD8mB87S+Ym+y7v1ATiux/8ebv/29u3s7c7uyItLeuBndH439miehrNphxS/XKiXuKBLLX5odpWfbxmdFR7otmEE6rHrt6RFNQ558FL1TNX3ySp3S7nrQWjqm/RbMqk6oCrD0sKZlqqs4l30tVhXnU7eKvNQ9WraDblq6SAdjvvk3l5BRy0OhPieaL6HrzVZkF1NJpNua56H7x3koIkKLhj9QhfueRnNqv2qiaszpagjChnzqrGVRucV4LJvxpNZaPqruqR/Y6otlda9AGBfFQdtvpz8yI56LgCMjdVbyS1YUBHzD9l3nFZmtjL5g1ZvQRbMT4np3wJ3mdJk9039yX9uf8SXfMiOei6P2Ap0uZ88PFYUdE7FjzPbDQkjeF18Fg5dWOqkPfu1uBPmR9Z6UvDfim3wctf2XsMuMSYKcJq5D3EOG9UH6/MjOpeNCUN7k+DZsZLbfBi5q8Lmqy9I5qS8gB3hhw4elFpUQN77qKrs8cuWfmKpM5ioiG7lybD86+C5pSpg/5JYhxnpb6XcUt1JnicwReszHFGR3GmWU4cb3Xsk78PulfWBvrguYe23eBV4Obll0YWwfjO5qQ8yNPBi+REVgq63z1dytoZxsS29HRMPfkpywNGfEWf0FjaXP9YPl1rc809L9GV9M5bSfuOIDleeBfvg5UJNHuLVvbZd9aVIwTNue/H7q/L6xLu2migmI7GIMBde6DgDs1xOVBwjPbK2i0tLVV+A14FpeVXCxl9AAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAZCAYAAACYY8ZHAAABeElEQVR4Xu2VMS8FQRSFr1CQqEQiEoUfoJAQfoVEoRD+gNAT9Su1Eo1GR6NBo1KJROE3EFEoaGgkwjmZe5O78+x7s/tkn8R8ycnLnj27M2d3Z55IJpPpxhq0E5sdWIfuoAVoElqFjqFDH2qCOejLqUoJZv211Gkh0RDT0CY0Kr2V+IQWoYFCog/UKcE3+aeoWmJJqpfgm+L6WYbG1ON9VqAJC4F59Yadl0SdEi3oDTqRcP11IdHOLHQuIbsF7ao/oh4/7WdoEJpS71UzSdQpseGOZyQMeOm8MjjWTeTdqu95Vy95rVUt8RNHEu4zFJ+IYIYPwXMlYdIeK8GNJ4nfLDEen4goK3EfebVKcBIp8Ekzfxb5VoKLtxN9KcFdgovNsP8VX4KZC/W7fcONl7CnTnk4gJ/stoTMgfPKKCtRa03wtTPEbe1BZRP2nwS3zn13TPhmPqAn/eU1e4VEO5w4cxznRcIk7RN8VN/Gtpx5va7XTCaTyfwzvgFirHbpiKzuwQAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAAB9UlEQVR4Xu2WTyhEURTGj1BEWVAISaGUnSIlWVhYsZFYW7Cws7CwYWtpiZKVsleSxcRG2MoWsSEpsZI/5+ve09w58+5785qa8fR+9WXON/e+Oefde89FlJIShwpWtTaTyhKrS5txaGf9OBol84bKwZs24tDBunLifjIFfTteqWhibWozDgtkku+zcb2NIXwuJROsEW3GQYqZtXGdjaFWGVQCcE4etFksw5Qtxge6TTNrkDVmPazsNKvGxqDBerLqYRyyjrTJDLC2WOusXtZq7td+ZFV27Wcf82R+AGNPWbesSla39Z5ZJ2TeNhrJB+sYE0PAqugudsEacuJx1p0Te5kic/iQzByZ5KLAg/UKfloPKyysWM8Hxk5qk8ycRuUVVIxQRdlthm0SxiXlPxyrgLlu84gq5oaCrwKsMOa9s5bJdN7YSDGL+gtFhvzFuEQVgzlB4AKVXEQtOSMUM6xt5UlCOlFNhvLHxC0G52RNmwo0GuwCKciLDHD3Ji5MeOgwYZxR8cXgN2q1aXnRBpnneO8/dJENJ3Yvzagzg0J8xRR6ZsLuFszpDPC84OA9sr5Y92QGH1D43twjMw6JyJwe+xexeCgCxT05nns+fF1MeCWTi7xcKCyvsnKtjaSCHXGuzaTSRmYb/gv2Kff/uESzo42UlD/OLylNh/lGUdsxAAAAAElFTkSuQmCC>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAWCAYAAABZuWWzAAABwElEQVR4Xu2VvyuFYRTHj1CKwqJE3chiU6KU0SYbsRssJgax+wOUDGIwGVgMWAxvGSSD6f4BpAxCBgr5cb7O87z33OP9cb3dO6j3U9/u+3yf8z7Puc+P8xLl5Pxv6lmjrBbbUQFdrII1a8Ux65JVx1pmPbPGyyKiQYJPrEnWHuvLqVUHVZMRkgk0F85rML7lk2RHPEsk78GvCeuse+NtkUzab3xNE0nMkfJ6WDfOT/ujmXhnnRpvjmRCJB1HM0nMq/F3nN9p/KqAgQPjTTi/aPw02ql0hLDyUfixoUHWGetWeY2sadaba+NOhCQle2X8NHZJ3juxHQZcZMThbOMZ9JIk/cEadh5A3KpuBGGX4JO1ZzmJDpJ37mxHDIhdUW2UzIDkWGpQmeD/kJRspSuLrUN8t+1IAPGYx+OTtXOWJYutsBdsgWSwfePHga3DhfMMsdpUO4pMyR6SnBWNL11jysOF0TXV80Cyshr8ybTSlSnZGfpdxAOSwfSX6JF1rtqgwNogKVNe8BCbRqZkAQafd899JANtlrrD2wt5/EchTnEMsA5IYl5Ya6xZKi0QtE1yjPAbOd4U65q1aDtycnL+zjfzSIOkq1k50AAAAABJRU5ErkJggg==>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAWCAYAAACsR+4DAAABnUlEQVR4Xu2UTytFURTFt6QokUiJEjMDIlF8AhMjQ0MDH0DyKQwYGMjEQAykzA3O2MRIDAyQUooZI//Wemffe8/Z7rvyupS6v1r19jr7vbPf2fsckYqKv6PFGqDDGko/NAi12oWyaYc+cmSLZTH0h6BuaAu6jTJKxha2Hi+ncG3GePfQmvFKg4U5qFc/59EmvrAe459A58YrFWcNw6L4wpqMv6n+r+GgPugQWomXauxKfgFsI/16F8FJPLMv0JPGV5pzBD2od6BeCs0x/TytcTj8Tj1LUli9ESBT4nMujE/vVbJ9utQbTjPAaBiI/2d34m8gcVJcmJ29kEnxOQPGp8cOWW/eeBE34pM4Q+S7VhadGEckL4eevdFRYTxiu2lSGAsiyxrb4d9Rv4iGC3tWI+QReofmNGarmMM5COFzwdwi2MKGCuM7NJGt1WDCqfgXPvRGgphcQ/vGsyQz9uPCOsWfWrPGe9CbfG3bgvi8hFnJb2/IqvhngXln0BK0IdnMcp9taBw6Vo9PRwp/nF+4lOJbwRNk+yhuUlHxL/kElMR1HX8MJzgAAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEMAAAAWCAYAAACbiSE3AAAAj0lEQVR4Xu3VIQ7CQBSE4UeaCoKsIqlB4bD1PQWqx0D1FL1Ak16GBFPZO+BqMTDNcxNs1cyX/GbHrdiNMDMzsx1U6MGHyo7ojSYelBVoQS/U0ibrgG7oizrapF0iL6XnQdmAPnyoZkQrOvGgokHPyMe0pE3K9otsb8Qc+btIukdewpUHJXXkw3jmwczM/vsBthUQ7md5fFEAAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAWCAYAAABZuWWzAAAB1UlEQVR4Xu2VvytGURjHH6GIIkkpRULZlCIx2mQhsRssFgxisPkDlEnMFosii+GWARlMUjZSSkkGBvLj+/Wc877nPl3vfck7yPupb+99vuc55zz3vue5V6RIkb9NKTQAVduBPGiAGq1ZKPagU6gEWoAeoaFYRjJ10DPUDrVA7070C0Kf6AYhJ84rM77lTuJz513Mmy0Iq6KbhqyLbtppfAuLYl6Vi0dcbG/+13iBDow3Jbohi87FKLQZxMui8+zN/xpcPDLesPPPjJ/Gm+i8ZjsQ4NemuqFD6CbwyqFx0V5g/KDTlFzFXho/CR6BW9H8GagyPpwIG5n5vDlek1bRol+hHucR5vEfywRRZkjxxX7377wQncemTYN5i0HMV2YkeixD2Bf0P8lVbD5PNqQJuhadm/aEmcN9PL5Yu2esWP4VtsFmRRfbMr5lB+oPYr+hLSQJm5NXsbuiZyXEv7oGA69C9CvnYXMwh2fMUy/alPTTXns/KnZC9OmGRKKL1QTePXQcxGwI5pwHHgv0H4qCHAPCQqbddZvoQmvZ4Uz3UiFsqCV3zRz/keD79yu6oG3RvCdoBZqU7AOiNqBa95u0r4xBV9CcHUihA9qHjqBeiR+VIkX+LR/s5YoaqM6WKAAAAABJRU5ErkJggg==>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAWCAYAAACsR+4DAAABY0lEQVR4Xu2VPUsDQRCGR1QQTOEHCKKQYGcniLU/QKy1txPbYCNCOlvFys5CsBDBf5DSztLGUiwUBAstxK/3dee8ybjuEfBIinvgKfbdYXdyd7sRqajoDVM+cMzAOhzxE2XAZnbgJ9x2cxmz8FlCU3QXvnZU/DMNuAlrkm7swwdgCx76sAxSjXHOswTbPiyDosbWXNYXT+xOwvwTHIQTOh6wRY62hBo6DF/go45vtOYc3mt2qtkvUo2RB8k34jfHzYrg62b9tcuZvUm+xrhmcz8VhlRjDfgOVyRvji6YmhiLEup4qi3MziLZqsu++aux7MTa17asGU0xLaGGa1hieyUbO/YhOIAnPgSTEt/U0pPGSNET4yssrbF1eOtDMCTxi9eSfWNdNzYGj6TzaHO8p3MZPJEXZjwq4S+pbjJPU8K1wDWv4Abcl/DjmfEwcS8eIK7NjFdH18zDS7Ul6TusoqJv+QKn9Gg/t2udtAAAAABJRU5ErkJggg==>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAWCAYAAACPHL/WAAAB8klEQVR4Xu2WsStFURzHf0IpSlKiGJTFQEmUMhpITEQZDRYTg/wRBjKJwWCzymK4ZTSYxGAhpZQsGCj8vu93Ts77uve+S/dluZ/69u77/n7nnfM7977fPSIFBQV5UqsaVTVxICMYD8VRz4bSzEaeHKvOVTWqddWLarIsI5lOsfGfqg6KAWwQYqydMClPRsQmCDlzXh35zKJqRqyorAVtSHxebmyrHsnbFZu8l/wksMC0giJVm7uuOu+qU/KWxBaIwrKQVhCI2KgmWEhE3pTzL8hPIktBiB2qVlVdZdF4/CMaqeZUb4E3oWp018/uE499ibSCbshPolJBiPW762HVk2RrCneqD7ExngWx3zsJPGwUnrQSaQXxfyuJSgX10fchsfxu8hls6Ct5g2JjWwJvzXkl0grK6w4xPn+LA0QkP9fgCwopKwi3lJvCilgCbmUW/AIxGXMpPxfg8/fJZyL5Q0FHqvvvWAnftscCD6eAhuB7SFpBeEnzAvA6gDdOPoON/nVB82J3KSQSSwiPJ/gTYnFxpBWETjlA3rRYfiv5DIr5dUEAXWfZXfeIBbkLwYPC0wPaJ/IeXMx3r3AsNgUb4c95B2K5fr4k8Bt+zj1Vu/u8dl4kNv+mWOPgImVWdSv2nsgbnBEx8ZVYw4k7rBYUFPwzXze5k/ELoz0fAAAAAElFTkSuQmCC>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAWCAYAAACL6W/rAAACBklEQVR4Xu2WPyhFURzHf4qiDEQk6iGLMigZiN3CwsZmULLKYjEoK4NBSiYGKYMyGN4oi0kWw0uiFBuTf7+vc06Or3vuxXtuvdf71LfX/f7OPfd+7z3nd59ImTJlCsANG0k0sUG0qjKqai6kSK1qi80oEGZR9aZaoJoDYVDvUDWo1lVXX0akx7KqmU2mXTUr5inEBUNtgLxbCY//L0ZUj2wmEQpWI6bWSP6x6py8/wZL8ITNJELBJsXUKshfs36a3Kt62EwiFGxbogNgLPxQI8mKqUNVqifVgz2+tGP2VXfW27VeCASaYVM5VR2oNlSvVPsgFCwr8cGwP0P0ixlz4XnY/PCexQQG9dbrdIMiwBKsJG9MzP05eFV98NdgvPd8+sSMafO8UevteR6Ah1oI/+E48AZxXhcXfELBkpZi3Btrke9jXDC+VlwwdMMhNsW8oRcx5zp9AyZCMO6p8GvetH4chQp2zQaB+ZckcD+hYFhqqGEf+KDdo0vFgSWYbzA0pyM2LZijm00mFAygxhPkVDvkMW6P5RMs1A0B5phjE9SJaZNZMRNDOF6xNce4fP3iD4oZy8vTZ15MW8e4M9W0alU+2zv2Bq7VK6Zdw0ONrx3VDR1unw/b4ymv9mPwHxHLD8JNpkVUN3Rk7C9WxIT9LQpC3bDoybFRCmBfHbJZCuBTge/gr3gHLeCJb1hQvDMAAAAASUVORK5CYII=>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAWCAYAAABZuWWzAAABxUlEQVR4Xu2VvytFYRjHH6Eov4pFBiWLTSlSRptsxG6wmChi9wcoGcRgN5BkMZwyIIPJjoFJMlDIj+/Xc957n/t0nKPbvUrup77d837f533P95zzvu8VqVDhb1MNDUENviOFJm/EtHujlBxA51AVtAg9QiMFFcksQB8J6rRFpWRQ9AaWs9ircb7Hhn2DBkQfuGysQnfO2xAN0ON8D8P2iX72soYMvEJHzpsWDcvQaYyKhv01GCpyHkPQv3C+J4Qdg/ZFlwE3ahphbopjj6Fb49VCE9BL3H7QYUpa2Cvne1jHtRoCHsrPNhiXDOve42vSJRqa8/XHHmHdsm1EuS4lhPVr2dMm+iYCjaJLimOzYM2SafPIjESXpYUnE/0v0sJmvdkktkTH8kHSYA3vEwhh/T0LwvJT+A02KzrZtvMtPNZYs+f8EDbrj6GosNwYXCuWcHQNG69OCjcPJ/dhWcP56GcdZUWFnRR9u5ZIdLJm491Dp6ZNbqB60+6ALqFn431HUWEJg8zE192iE63nu3O7l7LMQ2vxNTcad7J/SE8vtCta9wStQFOSf0HUJtQS/ybdV8aha2jOd2TAtXkC7UCtrq9ChX/LJ398gq038GC4AAAAAElFTkSuQmCC>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAWCAYAAACsR+4DAAABdklEQVR4Xu2VwSpFURSGfwNFmYiUKJGJmZIB72BkaGjgCW4ewAtgYCAGRiQpc4P9BiZkYoCJUgwUI2L97bXv3Xft7dzc7KTOV3/3nO+s216dvc45QE3N37FrRcSYZELSZy+U5ljyaSV8M/STkiHJjuS+raIg0/CL5xqjWzDuQbJuXBF4ty6RNtavbtj4c8mVcb8O79aGxCFtbEVdj/Hb6ovyor8O6WIHGUe4jfTfPQgOrdHolbxJnvX8RmtOJY/qjtQ14VM4oscOaRM5R0JjA/ZCxDx8zbXxdO/wDZNBdVOhYFyyGU6QbyLnSGjMzl7MHHwN14mhO8m4pXDyGl0gDmkTnbay6o6NIl9DZ5/oZmPhT1Uha3psh39PfRVdNZbjDuli3Co6zkEMXxdPxlm4hcUaI3Qzxt1KDo2zhBnrurFZyT78RYZzFX8zl9E+j4vwdXZ7YxrwrwXWXUhWJVtozewH/Bpc+0wdXx0/ht9Ibh/DRWpq/iVfIwh1XrBl29kAAAAASUVORK5CYII=>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAWCAYAAAB64jRmAAABnklEQVR4Xu2WvS8FQRTFr4hCFD4TFCLRqUiEQpQahUZ0dCJCLxK9REuhEI2K1j+g1mklNEQi0agICtzjzjI52dm3I++9rGR+ycl7c/bO7pzdmdkVSSQS/4UWVQ+bBXSppsT6/YUhNprBoOqWzRwQ6lO1rGpV3bl2m18UADW4MS9ifZpO2ZAXqhPydlTX5OVxIBbyWCoe8kO1Rt6cxA260iG7xQY3Sf6o8/vJD1HpkBNig8OvD/rCnyU/REzIZ7FaaEBsJr279qmruVE9OG/DeTKtWiStqp5yfKjdusm8FIfE8TLEhATbYvWHnpfNqlfPm3FekDJPslZIXqshYkNuidXz6wrektfOxhGkTMha07VRTzK7uQyPpS4h+8ROwhvPmPNHyA9R6ZCApwjIe4X0UtsnNuSC5Nc3LOS9ap88rJk3r40vG1xs3fN8YkNma5IpDIldiHfQot21w7p90yl2IvyCI9ce/qn4Xbv4OvLZE9shcQw6d+1Nv4hAn+wz8Ew1LtYH/+E9qnZVK6pL59UFfLPi4ldigXjXSyQSiR++AJJ0fTtFKSDLAAAAAElFTkSuQmCC>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAWCAYAAAB64jRmAAAB/UlEQVR4Xu2WvStHYRTHj2QQ5TUvk7KxUGKQ0WKwyMvAJonVoOzKyoiSCRv/gbKYmJRiIaUsJkJ5Od/O87in87v3udcvv1/R/dS3n+d7z3Pvc56X4yHKycn5K1SwGq0ZoJ41QNLvp7SzWqxZDvDhG2vGgKQ+WTOsStata1fpoAQmWOckEzRJ0u+Nipuoosia5Clrz3irrCvjxYGkzlQb34O3o7ySkjXJD9a88UZIBpsGYnTciWsfK6+kZEmygWRQ/cbvcn6r8S1brCnVvifpt6G8kpIlyT6SQeFXg77wh40foo6ilQ2dySeK4tpIdhLOMdr7LuaaoglbdB4NssaN5liPMT5ULd1olMJJ4nkamAg/yG7zLIkVkvhN5fld9aK8IeclkmUl05K0ZzUEKrNfIT+JSSxT/IrDm1ZtP45EsiSZtl2zrKTGr9C7fWDwk2uxY/mVJJtJXmILT4/zO42vwWpdsGqU5wcP1SrfUtYkgd0iIO5fSJNp75LEHCoP29snGWKM4mNKluQdFZZ8nJlX1cbtBx9bUB4uDPCWlIf3wEvbrv5MWoJJogrZChqqrnqL+dKPX7Dt2h3fEdHZxe3I46+DqOwA92S/iv5dcayznknijli9JFUWf8N7YK2xZkmujHGTURSojPj4JUlCtuqFwP0V/Q6ocEvn5OT8Q74AcvmPhkqHyPIAAAAASUVORK5CYII=>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAWCAYAAAB64jRmAAAB5klEQVR4Xu2Wuy8FQRTGj4hCJN6JRyN0KkQoRCUUCo3o6ESEf0CiU0i0JBqhUBGd/+BGpdOKR0GIRKMiSDzOZ2bc8WV3dsW9Xtlf8mXvfHt2ds7s2bNXJCMj469QoqplM0C1qlfMdWlpZsNSzkaxaFKdsRkBknpRTahKVed2XOYHxYD5Ecv6zEZ9ibRJ7qu2yFtUHZMXhZ/kpary4+nikzbJZ9U0ecNiFp4E5scTx71+hDRJ1ohJpof8dus3kM/k2Phu0iTZLSYZHH1wLfxB8pmcPS6oNlV1+VOx3Eq+xBvFVNKjHW/bmBPVlfVmrSd9qjHSlOomwodc9xuRcJI4HyKn2vPGT5Ku8cyLiVvzPFdV957Xb71Y0jzJpCT5XWWwuT6jYq5DMwsxJ9GbAW/cG7t1xJImyaRyTXqSDOZx5RjCbS7DaylIkvViJuHG02H9NvJ9usTEDHner0wScImAqE8INxW3UD9JNCo0EvSCEK6smaIleaFaIQ/vzIM3xrcQN5vxPHxmNrwxcO/aDvmMi2OCSaILcQcNddcKc9kbVWImwhGs23HLe0T+3eWGcqQasL9bxcSgXEMsq+7ExO6qOsV0WfyGd61aUk2qDqxXEPCfFTc/FJMQd70QKNFT1aqYeTIyMv45r6C0iZnoNfxwAAAAAElFTkSuQmCC>

[image25]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAWCAYAAABHcFUAAAAAkElEQVR4XmNgGAWjYAQBVSB+CMSc6BKDAXQD8S8glkSXGGhQA8T/gVgRXWIwgAgGSJQeB2JGNLkBB8xAfB6Ir0PZgwqAQmsjED9FlxgowA3EH4F4PrrEQABQLvwLxJ3oEgMB1gHxKyBOQpegNwClGVBOAyXqQZGgQQ4COWZQZv9RMCSBMBA/IhJfheoZBQMOAHiTG7DNb03mAAAAAElFTkSuQmCC>

[image26]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAWCAYAAAB0S0oJAAACDElEQVR4Xu2Wvy5EQRjFP0FCCEJFeAAViUQhSo1Cg8QDiIgHECFRegAKhUShEIVKIVGIbEenoVSolEJChPjzHTOTzJ7cmTu7dldzf8mJvWdmzJ2Tme+OSEFBQUF1NKl62YzQqZpUNXNDIkNsWNrZsAywUS/6VfdsBnhXrYsJ71p1rOou65FNq2pc9ar6pjbHjJg2FsY1hNQgjlRX5OFFX8jLYlfMgg4kPYhLqX7XVUVqEI+qHfKeJbywLPKCgPA+DQ3AkRJEi5gFzJJ/a/0R8kPEghgTE8S/kRIE+mAB/KIl6y+THyIliCnVmZjdh9oSwz9OGI/j9KD6tB7GL4ipbXh+MsNEJlTzpCUx2559yFVyTBILYo38EHlBoM3NiUXgOa9YonCj35f97XCB+ONDc/+SsiPyguDaESIWRIeVz6GE+/ugzwZ5JdUHedHCnhJE3tGoxY7IAv8X/Ye5gQi9G6/rz0G0iZmMi+Wd9XHBSiEWBPwb8lwQ2JExGhYEwBncIs99PhGUo8/7zVQaBI4c/NCt09HQIHCZOiUPL+AvzBW4Fc/ziQXxpuoiryTh/j4VB4EtzF+G2FfDL15ukYP2GVdtjPOrsiuqfAPdVu3ZNujCPq96feZUJ/Y3LlTTUj5fFqNixqAfru+YZ1HK59pX9di/KaEmgc8TjgdqA773tQY74txqk9oKCgoK6s4P5pelchF9LQkAAAAASUVORK5CYII=>

[image27]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAWCAYAAACVIF9YAAAAj0lEQVR4XmNgGAWjYBSMgkEE/IH4P7rgcAD5DBCPqaNLDHUgDMQ1QPwXiCXR5IY0UGSAxBjIc3xockMamDNAPBaBLjHUgRgDxGNO6BLDCYDy2y8g7kOXGG6AE4hfAfE6dInhBpiB+DzDCEi6IKDHMEwLH2QAqzqi0SVGwSgYBRQDUB34iEh8FapnFIwCOgAAKTgbI+7btF4AAAAASUVORK5CYII=>

[image28]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIcAAAAWCAYAAADq3Y/sAAACbklEQVR4Xu2YT6gOURjGX2FxI3SvjZCwstEtRSzYkmTJwoqFbClrGxtsKBvZWFgpZaErSXepLGwoKQs2iiSKUP68v3tm+s48d2bunSNdV++vnvrmeef75uucZ+a8Z8yCIAiCIAj+D9a4drqWaGEOlrv2uTZpoYWllYJFwhnXZ9cxSxP32nWpcUY3T113qs8Trl+uyVF5hpWuQ64pS/V1zXLwr7La0oQtEx9vo3jKUdc38bZY+m7OBddW14aqFuFYYMZcj9VsYb/NnkzAO6mmcM/1TLwVlr67VnwgFBGOBYSB/+66qIUOCNAXNZ33rpdqCkz0TTUt+afVtLJwsMT18VGNoAkN5G1LA39canNBr4GUV66fagpc74aalvy7alpZOFj23qlZwf+mGQ5aoHl8Uql0B8BkdYWjbbmpocnsC8e0mlYWDhh3fbC0k6rh6RjBaIFBYfLu2/Btp/K3wqG9CJSGAwjIQ0sBIRj0VIFQd/ybtVBI37LSFw7oC8e0mvZn4QBuBJa6vVoImrCNZKB3aWEg3OFtDekn1xs1Ba7f1ZCeV9NG4dihhXlwxPXD0lOT9yV7muWgDcLBgB+2sr6D7WrbEwLvSnbMXctLrhyCpdvleiu7TXwoDQfBuGbNHoOA5D1I0MF2S4POUjC0SWN56grH7uyYycE7lXnnLG15c9ZbOk9fqkFpOOonRg67GJrUYABXLS0Tq7TQwwPXLUsDDtddL0blGehLmNhH4jNxB7NjJuxsdgwEi97kraXf4By8A/lJHXy12cGo6dvmBj2csNTVzxeWp8uu5zb8zuZavKwiZENCGQRBEARBECwifgPMropzhQpTYwAAAABJRU5ErkJggg==>

[image29]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAWCAYAAABQUsXJAAACKUlEQVR4Xu2WPWsUURSGT1BBMfhBQkQiaAIWFiYEQRACtrHQQsv8gPyAFMEfkDJFUoYUsRAxpE2XYkpJGhtJSpWAIIRUWih+nGfvvTvnnp3dDZvdKvPAy85575mZM3fOvbMiNTXnl0veUK55IzKuuutNx7DqvmrMD/QbbvSvQv6BKBh/QjUSj79mGYFfqteqq6opCXnXs4w+4otfyYebMPbExJOqb6ol471TfTAxzKt+OK9vUHwh4RVzXMUVCcWPGo+Z3VV9Mt6Jas3EMC3h3IFReMPB7FHAkPMpNBV2MR6/LIcb8MD4PMRAKFS3VduqxXyowRupnj1aBv+yhPM5fp5llG254PzEIylblnO3VN8lrB081stT1Z8Y42eTiMnigscxtgu2iJ4nFU+BqYh2xdu1UQU5fyW/7370Xhnvt4RJbvLQBspP1ZGEnQUK6Vw8rdGteL8WPOS8dV7VG/8S1RYG7Q2rLgJ25ru1zWlm3udwX79TZcUfSGthqXhOBvqV2C/YjegDfc+xX7C3oj/rfE9PxTPoiz+W0GtzMU47xs1mRrlVkpvgnGUTQ9oqebhO9FQ8+/RMOdaAC+1J+JJa74GJ+ZvwWcKHKcEHasfE8EJaJ6eKnopnKyLhQoxZNGxLvkVY8fZCfJB8K7FT4N2JMdckZgdrxz3Vewl53Hdd9Sz+pu2Rh7gRPeJsMihgVXUorQvOwpugVVC7P25ci9b5qNqUclJqamrOwH9+FJ1fDYrORwAAAABJRU5ErkJggg==>

[image30]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEEAAAAWCAYAAACffPEKAAAAiUlEQVR4Xu3WoQ2AQAyF4RKCwOBJMFgEliFYAA3joFmGFRBINEsgMPAuRVWjru9LfkNdc2kQISIioh/kaLMfvSjRjWY7iF2CGvSg0cyil6L9qzez6GXoRKvoK3CnEn32tR14NIguo7MDj8ISwjIO0RvhVit6H8KdCPfCvQVdqLADjybRnyYiomi9QW8RKjTXPzYAAAAASUVORK5CYII=>

[image31]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAZCAYAAACLtIazAAACL0lEQVR4Xu2Wvyt/URjHH2EQssiPDFhMBiVK+QO+BotJ/gEli4XF8FkMNkkZZZBCNmX4TiYxKwMDiWJQikJ+PO/OPd1z3+753HNNhvOqd33u+3nO+Zzn3vuce0QikchfZ0q1wGZCg+pF9ZXoPvFC4LEnqppMRpY21bWk+W/JNXw3B77NuVU1OvEMg5ImQnlF1qseybsUk99CPoNieGy36oO8PEbF/McSBxLs3P0cYHpUM6om8Rf5T7VI3oSY/FnyGSxgjU3lU4rfBNxA/MeZqpVioEt1KMXzZPAVuSUmNk0+vCfyGMy3w6Zyo+pkMwc8KfzPBgeUPVUvm0X4isTrhRi/8/CeyWPGxOShDy2483iSIUxK2kpM6BwZfEXmgTuI/BUO5PAg6ULPxfQj+jwE9J0d6/beiKriXAdTpkgsnDcUH7Wqd0kXCw1lMqpzKmbMseOhT0v1oiWkSDyBioQXaDcPPBEsaj65hnrStKrgC4C2sK8s5rpLw+UIKdIucoADHtbl56aB/sQcFfJ94OZgF8WYdjGtsp3JKAEm2WTTYVh1pOpwvGXndx6Ys5lNMTvuFZtVsHsAijsQU+yvqFZkt2qXTTH94oLvrXua8RU5rvrPZgHYTTHfKwfK4CvS9lWeVp08u0G4W/uG5BeDnnaPaSHg5IP5iw4gP8AHGQNxFsX50D0z2o81Xg8uzgrfQQv69EI153hgX0wu5sYhAL/7Mhlh2Jtdx4FIJBKJRCLl+Qb1wpiKyMUYnwAAAABJRU5ErkJggg==>

[image32]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAZCAYAAACLtIazAAACAElEQVR4Xu2WTytGQRTGj7IRkohE+bO2UFaKjWwsrGzEF5BsbCgrG1+CJCslCxbKwkLZKGspbEiUjRXFAufp3OnOPe/cmbnvQhbzq6fe95kzc++ZmTN3iBKJxH9nnrWmzYwf1hFry6FpK85FE+uDZAzooNhcQxfrkfL4r+w/fDsGvol5ZjVb7QVGKQ+EXEm2UjFGqz8PraGRJKbD8lZJXirEOEnfTd2Q0cB6Yw3rBs0Aa4nVQuVJ9lE+m2eUr+A269OKczFGMq5Ne+ZhAny0kcRdszpVG+hlnZLslGjKkpxhDWmTuSWZHB94wQdtkjxrQZsOsFKI3dUNzCFrUJshypJ0scia1aYDjHmuTRIfuyLEHOVlofnWRgyxSWL17rRZgi9J1wprUHcmSbv2UAYb1v9oYpLsZt2QHFgx+JJ812YJVyTxl5aHMqhUi4aYJPEg19Ypw5dkzEoCTCgmxDwXq/uSN1cjJknUwV8niRXDKYo+2Ek4bPYLERXAIHvatDBHf5UkMSkX2iQZA6djLEgMfZDcCUmydRFKEp8SxPhqCYcStpMBL+TaWhhnSpsBzC4KfZu9hJJcJ3+S5oCwj3bcdODZH/6JzKsKbj7ot6wbQvSQdHwludHYd0a02aBe4T8p3zDCumetKH+SpN8O6zj7Xc/JaG5AoZtSIpFIJBKJCH4BQD2Ua6rWMssAAAAASUVORK5CYII=>

[image33]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAYCAYAAABqWKS5AAAB2ElEQVR4Xu2WzStGQRTGj1AWykIpUWIpH9lYWVhYsLCxsrNkK0n+AFtF/gFJNrbKwuIuxVpsFJKFQglF+ThPM6c7c8y9c6+t+dXTe+85Z+Y+77xn5r5EicT/pIn1yZpjdbJGWaesKbeohH7Wt9U9q9FP/+KG9UL5mEfWuldBdGdz0AdrwU/ntFJeKFr2KooZIVMv9Nj7BidWxBqZ2jGdsHSxDnVQA/MZq8NeV2WA9cTaVPHnQCyELNq5TpDphj1Wn06EyHSgAvtkHj6j4mdkvsCwiod4IDMHzLrM23glMjL9DkNLfqqQazIPmFbxzMZhIMYshWtDv2ghmGDIXmPD4r45Twd5pXLzKyoeAnsDtTArtLGO7WclBtX9G+uW1aviLjHzVVcORlEvZrfI7Kc/Iy1RZiDWNlVWHsAo6mEafDm5KOj1cRUTY9sq7oKNWWZeb+QiWsjU49TBxr3yshHeyQx2EfM4i4uQc1qvMMai5bpVvAzUY65F1oTKlYIVxMvGBROdsNqd2BGZPhdkYx04MYCxOEXqMElmnF7EKDABU/Ja3yXzd0G/JWVy90zGiYSYrPIq+SdHHTBP9I0aAkY3WBf0u4djYCxa6JJq/uSKHarXaolEIpEo5wdVdnknkf/O+QAAAABJRU5ErkJggg==>

[image34]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAAWCAYAAABdTLWOAAABrklEQVR4Xu2VTytGQRTGj1CsEJEokY1SlFhZUix8AhbKwkfwAWSPrJQslWyV5V2SraJsKKVslFhI/pync+ade8977515s3rr/urpzpxzZubcOXfmElVUNA+HrGlrLKGbNcfqtY4GOGfdWmMRp6xf1op15NBCErvGamUtar89HRQJxkGYs5Rx8sExSV6yToxth3VvbCEmWO8k6y4ZXx3YxRuKT/KHtWlsyyTjGwFzrJOMO8i6smAXt1kJxSXZQxI3a+zYFdgHjL2ISdartl0VC3nTZ0JxSc6QxOGZZlDtC8ZexAXrWttnJGOHvNuD09yv7YTikoS/LMnQeMcXa17bYyRjj71bGGbtpvoJxS0SStJ+q3mg1DhoaXJL/mH6CcUlGSp3aDxAqV1SVrWSuwnLVEQfid8enCm1o3QhUGrLKMl4e7VleCQJsjvRQXJhp0HcqrHFXkGogC21I7RBhUnimrgytifWvrFtsT6NLQ/EuQNjeSbJoc068K8+Iv8WLySnHrjfn327LrXhCTq1P1KLqAfrPJCfbyPjlTW/1efuz3+DT2CPdafP4L+3oqKZ+QM68neV0CWM3AAAAABJRU5ErkJggg==>

[image35]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAWCAYAAABzCZQcAAACl0lEQVR4Xu2WP+hOYRTHj6Qo+RORDD9syt9EkZFiYDEYGJTBYjMok8VoIBlEMvyyWGwGw92IWZQFkQwGhUL+nM/vPOd9zz333vdVr/c36H7q273Pec59nuc89zznXpGenp7/lUXZoCzLhsJ61Yxqce4IrFBtUa3KHfPIM9WDbHSWqn63KG8EgWLfKBbMddWbmofIAjGfk2LPHyztPNZ84HG0koO+XO8eQN/eZHuvOh/aj1V3QxsuqV4m27Q5oPostmYyrgFBV6o15b6NJWIDrE72h2Jp5PxSnQltOCwjdnxKXFWdEpv3bL1rSJUNiRNiA5C+EQb3gFaW+93D7jk2F/vaZJ8mbD4w75fYEalU61T3VOfqXXPckfa3RWpjp6jtKvdcI4yLnZRr44gMjxbPPhJb9M9iox4cV30v7U9i2dMFm0sc8FTsmdYMpmNbud9T2rH4VMWW8aAZ1BffFTT9XXgBJNiYTdQMgmdNjm9QGzx7TbWptPeL+ca6M2Bran9VvRWr1FBJ+0QeNGd9XND5rGfwuZBslepHspGuXW/vkAxT28G3M8Ujr8WcObMwLr1ZwLj0HvWmoc2nEltLZFTQz8X62lTzd8eIB02wwFuinQvZzWIH3jb3uZBtL3ZPuS4mDZq1cRzyPHxm8b8YjT5I5KNYmpAu4AFRoSN8svB18KHSR/72kzVp0EelObeD/7do4Du7MxrEnJ5I/TcSG5+fyCup/4xQB/xIOByB2oQdTBr0bWm+ZYe6UNv45WIDLSztWbGKmVP5mNQLwj6xgaIfY2HjCv5TMzPwaLJDdV/MjwJ6RbVBdaPY0C2x/3mubqvEsgh9SPZIfOZd7GDhTPZCmrsd4c2T0uh06nPYPB+La968np6enn/GH5gix/qCP5l4AAAAAElFTkSuQmCC>

[image36]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC8AAAAYCAYAAABqWKS5AAABzUlEQVR4Xu2VvStHYRTHj1CK8rIJ/WxKSjJZTAaLhYHyBzCT5A8wKYNYLCaDsiqD4TcaLJRIDKQUg1IWCufbucc9v+O+PNdE3U996z7n5Xk599znEpWU/HtOWX3eGEI369NotNadST/FeY+s+lp3MMg/9MY8elgnZjxAMtG0saUxRBKrVKJxnbGFMEZxAQqxTJK0EI2xMMa3rE4NSgCHfGZtOPtLgi2Pc9YaybqYN5hm1iWrMRq3k0xywGrSoAT2SeImnR0bwQEGnT0NFOuB4nWrNd6C7JBMoodJA28GcRPOXo3sc86exjhrNnp+p1+0DjgjSbyisJ59pezNox1DuGA1RM+rJLnDsbsY+FAxQYd3OPI2H9L32jKKbZ0WYy8EJoDmvcOQ1zYhlUfL6FpeIfmJaFWPvMOADzNr8/5DTmKTtcvaNnoiyT82cal8kARr3wHdPKqbhvanrxBy7kl+fHlgbc8IxdXPRQPt5tVm2wZvAYdSWkmqgyvVgrwZZ0uii+S6TULXx0EymWJdU3w1rpMkVr4jhKRDIgc2rfIKyY8riyXWG8Xz7RhfG2vP+CC0Uq+J+QE2scW6Yy06Xx64MdBCNyS/+ZKSkpKSv8EXPHWDlhZGEV0AAAAASUVORK5CYII=>

[image37]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAWCAYAAABkKwTVAAACZ0lEQVR4Xu2WP0hXURTHj5iQEKYURkNKgVsKgQRC0NJQQw25JK5Bi1tIS4OL4GBDIQ0tEhJCBTXUJvIbo5YGo2hSiYKkJVBwSD1f7z3P8768P7/XD8rhfeAL737Pfffe87vn3vcTqamp+V90sKF0seE4w0YTYI7Lqm4OZHBX9V217vQzxl6TD32MsWPOS4zdDHHCaF9UbUmIV2FFdV81Lgfjv0j1yGZCQt+b5GMtz2NsgGJgzR44uQcWIB5LSO6pVEsOCxwjz+a6Sj5zVEK/zxxQzkmIzXNA+WUPSK6h6o3PZVRN7q2E/n7sb9FbdF4e6LfDpnJeQmyVfPDDNxq+UULV5JYk9B9xno2RlE8B9uOcdB52FP5mjLW5GHYU5Z/QUJ1WvZRwmIuomlwWHySMgQWWYTs07TwsHrtjZ/KKi6FMkXwCOgzFZ5wrtPlCMVpN7oiE96HjFMsDfbddG2V9R9UZY/ixjOS8GYPUxo2IAc6SD1pNDjfnhmqYAwW8kzAnzi1KEDtuu2OlCU6p7sXnXHAW8MIjDkhryT2R9K/cLJckzIkyvCGhVI2pGMOZnhO6FHHN8mItOSTC/G1yo6oF8maoXQTmRMnxZ6Enxhqq3+lQelsNDILrN+s7VJYcPikMzvEseTh7uMCa5ZOEeVGiDNaKmL909sFLF8hDx/eqE+SDouTsMsLN6/mq6os+1K+6LdllnwdKLjMBOUgc5ZsCNxZ2rz22n6n+SPrbAR5KODMYBFqO7UnXZz7GbjnvVfSydM31KwOXBd7x3zsDFZb3g+8ngsV/UV2n2GHC/iAzWP8bNmtqav4de9fhqX0tkBFCAAAAAElFTkSuQmCC>

[image38]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADcAAAAWCAYAAABkKwTVAAACr0lEQVR4Xu2WTciNURDHRyhKSURCL0IphYRIKVGkLFhQ7G3sLFi+G2VhgexvFjakKBbK4l0qGxuRKCSKLCiK8jG/O2funTv3XPd5S2yeX/3rOTNzvuec84i0tLT8b2ardqvmZEdgmWoiGxuyQbUwGyucVr1VvQ56X3y3kh09Kr55wTYAhttinZ8X6yCyXPVFbGLoe1ETaIu6LN4+1S/VhYGIOqfEYg8nO+1cL761yQevYoFVuhjKVGIwW4LtZ/h26PxKNibmi7U3K9jOFduKYKtBBhH3JDuU1WK+TnYoH/2DVSBoTd/XLb8US8Foy2xVTWVjYr8M1z1QbCeTvQZxtYUlxX2cmXf+wcrnzmsQczTZmuzcQ9XXZFsvtrovkr3GXbG+FwUbO4qd7MI3I/jY0eNeoGOCNosFoj3uDJC6+D6pZqrulXJsuAZto8hSsXNR25GM7xCp7DB4dsfP5N7g60i4EH1CJ3puKx8JZeeD9OMnxVJ6HMSOmhy+JhD3LZTfiKX03OIjO5zeeQMfbOR+sbEyzkrVD9XB4nNtCjE1/sbkHojFctWTKaSk746nJixRnSnfXWqdXy32x6VMo5RjCj4vtnED/FNajqvr7JL+Yh8SS1Vnsvh2iJ1/xtqDbcyd++T8vbisutZ39+BN9BUdBQuUL5SNqs8SbrUG0A9jzc/CguKbEmtzAAaeV9BvKHwwanKQ6y5OZc5GjvGnwNtvAotEHVI0w8WEL146XdjO3DkHlN30R/yY2CHO8DDHG2+bWFuknbOq2CKcC0+lpviTNTQB6U+c9B3imepm+eYxJ5A/iwg3Jb9nzlmx36+JYOuI1WUxIlxQN8q333D0OR24LKgX3zun9qMwwE6xR7W2Mg6PL2mB1sn4Ny6yXfVUdUmmVy/iP8gZ2ruTjS0tLf+O31qVxn8e8tmzAAAAAElFTkSuQmCC>

[image39]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAAWCAYAAAC/kK73AAACJklEQVR4Xu2WsUtXURTHT+RQFEYQhFSDCkLQ5tpYEUQuDQo5CEKBq1CrIG5O0tQS7S0NUYP/QWsRBIK6iIIJgiBq6fl47/l13vnd934/o6l+H/iC93vefff+zr3nPEV69Pi/uKy6q7oQAw1cjIZyXnUumo4t1XrQbI5FH43m2GvntThQTatmVMeqn9K8uPFY0vNeO5UnyjxU/ZL0fGRekn8UA8pNcXM+qUZ+x04zT/Cb6rrzS8SNP6qGG1mSNOdO8K+qPucYe/FcUy3YYFvaf7ltZCL4ETaOBiRdkbNwT9Iaz4NPskgaMbsmBnO4zqfsSnroSissspa9t84rwYvZ+J/CGiTOw0ls5hi3wcNJNHIo5WxEbONkgkUeVMMdscz2OY8aIaulGvgaxhUGJU14IZ0LlI3zrHUXKr+b4jTGpHolOXUyDq9ybCiPWYuiroWO8jGaNVzKMvihLDbnvCbINM+v5vFLSQUIN3LsXR5zorWJ/K5ajOYZsXt7OwZq2JA0h039CDF8uy6rzq/AMU+58TNJvb0JXvql4O1Je0eogzpiDrXyJsTINrH7UtPhuM+xB5OJp25Mu4tf1bqNc6ylr2oJ3mmZpb48nJrFfAG3oKDoxSY+Ctx1uoWxLCmTnn1Vvxvbx2vSed1Qtzn/o9qwnhm1ItUvZ+nlT1Tv89+cCAno2GsLcEKxnxu880M0/wZknNNAt0KsW/iXYzyaGa7rcDR79PiXOQEBjI62J51aDQAAAABJRU5ErkJggg==>

[image40]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAZCAYAAACGqvb0AAACYElEQVR4Xu2WTUhVURDHJyhIEiKIVCqIdkHhIkgE3bgyiNZCi5a5aBfR9m1cSRuJttEi/MCt4PKCIGLraKsiCkoFoi6MPubfnOnNnXfve+f4Fi48P/jz3p2Ze++Zc+bMPUSZTOY8cpH1i/WcNcB6xPrMemyDDD0k8SlcYH1l/QkaC7Y6JllbJO9BPH5xDeZY34MdOmStBN8V1p7zPQi+SnqpGax6XYoQ1KcDSgH3jJrrHxT3jHskcR+8g3lG4pvwDpLJmPXGKnzyb8vu/7wnqYqPFDdw5SpJPCpMmQq228ZWxWWSOFSN5y7VT8w3ksnpCJIvvLENqcnPUGv8Q9YRa9HZq0Ai/n7wgpoLZsEk47l2sttSeEMbUpPfJknUgt6yyTpw9ipekrxvxNiw6ruspeDrMz5sA2yXaNDgfpMkhv05XXaXSE3+J9UnH/Mc3ZYYo4KVReL3gw/VpWyY/1Hsu2s88JWzKanJI7ab5AHut7EYr64u7JhggC/Icvh/anRgVU3jLJJvkMSiV9wk2QrKWvChsY6HmK7QgdlyUlKTR+LdJo/9jlgk/ZSk3JVG8A2z3pFsk2j08GHRgSFRT2ryX1jHzjZI0uzQtGLBO9H5/WfvWvAVFNdAS/j9BPASNECUkadT8jfctX6SLDg91lVWHZhE3IMy92Cs8OH8kMQb1pC51kMJyquKT9SajIIuDB8SVtCEYLMHmvVgu2RsncBC4B77yVP0LHHdO2JYYJ2wdkge8qTs/odWCM7YkJ6vCxNzK9h8Uv3BPk9y9l5l3bEBEegkVoHvPFY/k8lkMplMhv4CRPi5i4e30ekAAAAASUVORK5CYII=>

[image41]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAWCAYAAACCAs+RAAACAUlEQVR4Xu2WPyxsURDG5wUJCVEQiShEokQiRKcngkJBopHohIaIVvLySgVRSRQKFSqdalsaDSEqhFJEQSP+zLdz5po37O65u53cX/Jl75mZe+/5zj1/ligjIyOWGh9gGn2gBHWsPz74A4usj6A+lyvEAuuJ5J5t1nW4njI1VB+CXlu2qAjtrBOSe/CsGJoo3sgz64016eIYNMQfNeCNrGkigmXWKKuf0hnRd5YyckhS1+ETgS6SfB48NMdqCdflgA6lMYLRjDHyTlJX7ROBWjJGQM42yiCtERBjRGdJMb4ZaWXts5ZsIpJKjWAdaKch9EVrUhlBoydcD4R27GIHlRqZZt2yxr/See5I6hpcXGkmZ6TbNpgXkoJCi8xTiZER1p7LKZ0kdTD6EytU4ovdkBRs+EQByjVyEH7/upwFW/s1q83FwQPrSBsX9N2VGtlx8UKoEZ3bMaB+hjUWrrFrWnBIY1fCjoX85v/pJJ4cwrrQLHCK2JCJ4aFVpm1Ja0Q7ofVnJIfbRFIh79MZscp6/UrlwQDM28A5q9cGSF4CNZkYTtBj07akNaIHotYPhvZVUiFgWgEcfMkJHvhHbg3jPxW+io72LsnoWLd6gPkvN0uyu+nmcE8yHYvteMMk2z3qT0meMRfaEDqMGMBX0DhkD8aciSego+usS5K/HBkZGb+IT5Dcj7/pGnVrAAAAAElFTkSuQmCC>

[image42]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGwAAAAXCAYAAADug6rPAAACWUlEQVR4Xu2YMWgVQRCGJ2hAUbCIIGKlSAJBCCKCgmJjoQgRTGMpCIGIVUBFqzR2FhY22ouNCCkkKSwEG+0NiiEkSsBCxCqBKEbnZ25x7n+7d1fog+B88MPbf/fuPXbe7s6sSBAEQfCPeMFG0D8GVZuqV6pfqt317h7GVcfYFHvulGoHd3QgPbuNO4JeFlV3VdNiAcsFw/OZ2pdU31VXVdfE3vFTNeAHFbigequ6qNqvmq3aQQFMKiZ4TOzf3Rasnaqn1F5WDTsPqwXvfOe8HPjub2wq86pzbAYGAoXJ7bqNzagOuPZxseehvc7/WnlNYEVtsKncUd1iMzDOS/vEel5LfatLAYf2OP9j5TWBgGHMYfJjhWU4K38m2uuyH0QgUAtsFvgh7QED/rtHVSdVX2ojghpIIF6yWQDBxIS2cVAsADe5IwMyVB80bKVBA5gkZIdd4OywBDLEOTYLoET4JJYt4rkUOL+9BhW7xCbnEHdk4OywxAfVPTYLHFWtkXdD7Detku8ZkvqqbBLef8Ie2/qkDK9LvTQjttU18Uh1xbUn3eccOA9RwzGnxX5XQKBY7jIxSFBQGJdAwHFeYVvz8BaK0sHfZJQCluq4gHgu3Q75B9KcHU6IFcBI05OOiJ1JHox549pPKjFYyW1F938J9vfHbGZYl3J2OCK950bSkhuXblT8yknebbHzFKQME9ljQGBicOHaBBKS62z+ZVAkPxTLFnEfGThw5/detU+6nRO4ddjOZtA/0pUR7uruU1+OFTaC/nJGLGDPuCMDzi1kiMEWYYqNIAgK/AYFiofjLSyjIgAAAABJRU5ErkJggg==>

[image43]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAXCAYAAACS5bYWAAAB20lEQVR4Xu2WMShFURjHP6EUkSiLIkUpRcmmGCyGZ1ZGq0mJ0WIzSAZJvUnKYJFdWWwWRclgkkGiDAbx/Tvn6Nzvfufcez1ehvurf++d/3fuff937jnfe0QlJb9KJ2tZmvWimbXJOmd9stqS5RRVis9pl0YOuli90tS4JRMSq4XX8WQ5xbM0mB7WFpnrK6IWo4PMNdOsPvt+2J/g00BmwiurkbKDjrAWhDfGWmS1UPGwmL/kjXF/eCqjZIqnshDggswXDFEk7CylnyS2VzCsu2BDFgLgCcQoEnaV0mGbrJdgxppS8/4kAfbltjQFtYYFqbCOB9YZxU+345DMgYhRJCxCYv6E52FBgmFRyNsztS4gKRIW4J473nifAmFbyRQGZEFB6wIaRcPisL6wHq3QWdSwWH4UYqfbgS6AzZ8F7oe9+FPw66iGRQdQCwrX0ggQC4tzIRfmg7XnjecokAm99UmaCnm6gCMWFsGOhIf59974hHXljb95Yx1IU4BHn9UF+smsziWZD3ertULmVw24Zv9uxw7MHbTv1+xYBRdPSlOAQ5WnC9QCtuMdKQdziHVDGf3MA0HzdIE/AfvD7Sv8S4qBR1el9KGoG1Nkwh7LgsI6q1ua/5VdaZQofAEHA20jRM2wawAAAABJRU5ErkJggg==>

[image44]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAXCAYAAACS5bYWAAACI0lEQVR4Xu2VvStHYRTHj1BEeclLipKilKKESFksBpNF+QMsJgYvk8VmkIUsMkgZbMpgUBZZGBRlUsokUQbKy/l2XM499zy/+1PI8PvUt9tzzrnPc+7znPNcohw5fpQK1qQ1/hWFrEXWIeuNVRp3J1gnP6ac1U0y33epYTVbo8clSZLYLTw74+4Ed2acx3pljbHmSOZ4jEWEKWO9kCRaz7pnTcUiFFgIkz+w8ik90TaSpDTnrGo1biCZc49VrOwe+HDkoMGHu7STTLxrHQGOKDk53oeKlA0LRqeVCcTYsrk240+GSF5YsI4AOAFLlGyBsqEMYJtWNg/EzBpbYmcH6WsRrVEdZKhlLVtjAMyFRbFOJo5JYp9JSmaVtRKLUNywDsjvbssWSUOk0UuSwIh1BEDNR5u1YXwxEJBWVxH2FgiBOYO7Y6gkie/7eELuTVJC4myyDgfvFvDAB01YYwDUONbXDRaVRYIuEoftbg/cArqBPPYpXqMzJA0cYpzkR2TZtgaAG8D9CgfUVSbWWB3Ghl3uV2P0hd6YULLD1gBwt95ao0PaLYAE0Kh1SvjtYu5WFYc/ld41NOKTGkfMWwNAIW9aowFHn3YLIImoObRQFugLgF2FzSZ3xjqhrx1HX7iNjJf1MXkEX/5BGkk+7JTVox0trAuSo82mXpFoNrfAr3BFkiR+g0vGZ8HRrVN2t8WvMECS7I51OMyzqqzxv4L/dI403gFq/XsH3VB/JQAAAABJRU5ErkJggg==>

[image45]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAWCAYAAADwza0nAAAAfElEQVR4XmNgGAXDDXAB8Wp0QSTACsQ30AVhwAyIt6MLMkA0/UYXRAdWQLwHiU+UJhiAaRZlgGhiRJXGD5YB8X8gFkaXwAfmAHEwlP0aiIWQ5HACZE0wANLMjyaGAkAB8RddEAhMGFADDAWwAPEPdEEkYADE29AFRwEWAABB2xDezKKkYQAAAABJRU5ErkJggg==>

[image46]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAAAXCAYAAACMAETgAAAC40lEQVR4Xu2aT6hOQRjGX4UIyZ9EUaLYWChlIVsLyQZlce0kpWwpKxuFFRtKJAsLSwuRJDsLC6XsWFwLioUoEvnzPndmrulxzpmZ+517ne+c91dPX98z853vnDPPnTPvfFfEMAzDMIwesFz1iE3DmAnzVAvYbAB9v7BJbGFjzJiveqP6Hem796DXql3TvY2RWKfaz2YDb1Ub2FSWijsOBmuS2saV2+KuB4GMWeX9j+QbM6AkgNuk+qYfVV1UbRYXvv8ZwB1ebfBZ9YNND54ECOFZ8o1CSgL4THWcTaJPAUTAMAvWgYB+ZbOCZWwQC6VsGdQrSgKI2SA1uH0J4ApxAWz6g8N1ok+KT6p9bEZgXXmSzaGQG0AUK7jZi7iBqAogAoHCJSzo16p+iVvY4z2qavBK9c57J7xXSlsBnBB3Hqu5IQKzX04AMbtdUx3gBnHhC9ffe1C5HSIdU12o8KHF7mNTIKg5N7sqgIEz4o6BwQjgsY4wfou83VK9+M+hrQDivFLXi/acR3Dguupg9P6DDCh8deTOgBjU1ICApgCeFncMzKaBW97DjBMIYcdrKW0FEN//ks0IFGToc5MbEoQQInwrqW2QzGUAwzZNDAKIx3McmpwAbhXXp0Trpz6ZJmf990BcH2w/lYJZ8wibQ2U2Ali3Ud1mAOtoYwZMrf+wNEH7JW7IANtYeOxeVR2mtkGSG0AMBoeniqYAYhHOx+hiAFPrv5/i+pQSwhdACOM14SDJDeAScYMSr9+qaApgWAPGdDGAOJ+6DehT4s4NlXwJO+Xf389RHdd9Ty9BdcmVblMVjNDF4MZvIg/sFVfZhoICuuM9sFF1Wf5uW9xVbfftmE3gvVedF/erynPv4RXvSxglgFdUj8V9N4oEnB90Q/XC+0+ne+eDY91n04MQYgcgZxIYPPdU59jsGKME0Og4a8Tt2XUZ/CdObrVrjCEPVXvYNIy5BOu2VDFiGLPKEzYMwzA6yR+FAMObHqr5+wAAAABJRU5ErkJggg==>


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
