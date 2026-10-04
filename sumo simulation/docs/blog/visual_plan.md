# Visual Assets and Figure Plan
## "Quantum-Inspired Intelligent Traffic Route Optimization in Transportation Systems Using Metaheuristic Optimization"

This document outlines the 12 figures, architecture diagrams, and empirical charts designed to accompany the technical Medium article. Each entry specifies the visual type, conceptual layout, detailed caption, technical purpose, and implementation/generation recommendations.

---

### Figure 1: The Fleet Routing Dilemma — Independent Point-to-Point Navigation vs. Combinatorial Fleet Optimization
* **Type**: High-resolution Vector Infographic / Split Conceptual Diagram
* **Placement**: Section 1 / Section 2 (The Routing Dilemma: Fleet Optimization vs. Point-to-Point Navigation)
* **Layout**:
  * **Left Panel ("The Google Maps Trap")**: Three delivery vans independently querying point-to-point shortest paths (A* / Dijkstra) to 12 customer destinations. All 3 vehicles converge onto the exact same arterial corridor ("Jangali Maharaj Road"), inducing self-inflicted bottlenecking, localized congestion, and uncoordinated customer visitation (vehicle routes crossing each other repeatedly).
  * **Right Panel ("Centralized Combinatorial Fleet Optimization")**: Coordinated multi-vehicle routing (CVRP). Customer destinations are spatially partitioned based on vehicle payload capacities and dynamic travel times. Vehicles follow non-overlapping, optimized circuits with load balancing, minimizing total fleet travel time and system-wide congestion.
* **Caption**: **Figure 1**: *Independent point-to-point shortest path navigation versus centralized combinatorial fleet optimization. While individual shortest path queries minimize single-trip latency assuming a static network, uncoordinated fleets induce self-inflicted congestion and redundant travel. Centralized Capacitated Vehicle Routing (CVRP) partitions demand across vehicle capacities and optimizes overall network throughput.*
* **Technical Purpose**: Immediately grounds the reader on why Dijkstra/A* alone is mathematically inadequate for multi-vehicle logistics, establishing the boundary between low-level pathfinding and combinatorial fleet routing.

---

### Figure 2: The Two-Tier Hierarchical Routing Architecture
* **Type**: Architectural Block Diagram / Flowchart
* **Placement**: Section 3 (System Architecture: Two-Tier Hierarchical Design)
* **Layout**:
  * **Upper Tier (Combinatorial Fleet Allocation)**: ProblemInstance (Depot, Customers, Vehicle Capacities, Demands) fed into Metaheuristic / Quantum-Inspired Solvers (QPSO, QAOA, ALNS, HGS, MIP CBC). Solvers operate on an abstract complete distance/time matrix between stops. Output: Customer visit sequences per vehicle $\pi_k = [\text{depot}, c_1, c_2, \dots, \text{depot}]$.
  * **Inter-Tier Interface (`VRPEvaluator`)**: Translates consecutive customer stops $(u, v)$ into dynamic graph queries.
  * **Lower Tier (Dynamic Physical Road Network)**: Dynamic Traffic Graph $G(t) = (V, E, W(t))$ built from SUMO/OSM. Computes road-level shortest paths using live time-varying weights $w_e(t)$.
  * **Output Translation Layer (`RoadMetadataResolver`)**: Converts raw SUMO edge sequences (`"-43424#1"`, `"-43424#2"`) into human-readable OpenStreetMap street sequences (*"Shivaji Road ➔ Jangali Maharaj Road"*).
* **Caption**: **Figure 2**: *Two-tier hierarchical architecture of the optimization platform. Combinatorial solvers operate on an abstract topological stop graph to determine vehicle assignments and visit orderings, while the dynamic graph engine resolves underlying road trajectories using real-time microscopic traffic conditions and extracts OSM street names.*
* **Technical Purpose**: Clarifies the separation of concerns between NP-hard combinatorial sequencing and low-level road network traversal, preventing confusion about where Dijkstra fits relative to VRP solvers.

---

### Figure 3: SUMO-TraCI Closed-Loop Microscopic Simulation Pipeline
* **Type**: Sequence / Cyclic Dataflow Diagram
* **Placement**: Section 4 (Dynamic Traffic Graph Engine and Microscopic SUMO/TraCI Integration)
* **Layout**:
  * Circular closed loop with 4 discrete stages:
    1. **SUMO Microscopic Core**: Advances vehicle physics, car-following models (Krauß), lane changing (LC2013), and traffic signal phases by time step $\Delta t = 1.0\text{ s}$.
    2. **TraCI State Extraction**: `TrafficStateExtractor` invokes `traci.edge.getLastStepMeanSpeed()`, `getLastStepVehicleNumber()`, `getLastStepHaltingNumber()`, and `getTraveltime()`, filtering out internal junction connectors (`:edge`).
    3. **Dynamic Graph Weight Update**: NetworkX graph edge weights $w_e(t)$ recomputed using live speeds, halting vehicle queues, and active incident penalties.
    4. **Fleet Optimization & Vehicle Actuation**: Algorithms query updated edge weights, re-evaluate routes, and feed rerouting commands back to active simulation vehicles via `traci.vehicle.setRoute()`.
* **Caption**: **Figure 3**: *The real-time TraCI simulation-optimization feedback loop. Traffic state telemetry is extracted at each simulation step, transformed into dynamic edge impedance weights $W(t)$, and utilized by optimization algorithms to synthesize or dynamically adjust fleet trajectories.*
* **Technical Purpose**: Explains the precise mechanics of how dynamic traffic updates flow into the NetworkX graph and how the platform avoids static snapshot assumptions.

---

### Figure 4: Dynamic Edge Impedance Response Curves
* **Type**: Multi-Panel Function Plot / Mathematical Visualization
* **Placement**: Section 4 (Dynamic Graph Formulation & Cost Functions)
* **Layout**:
  * **Plot A**: Edge Weight $w_e(t)$ vs. Mean Vehicle Speed $v_e(t)$ across varying road speed limits ($30\text{ km/h}, 50\text{ km/h}, 80\text{ km/h}$), demonstrating the hyperbolic latency escalation as speed approaches zero ($v \to 0.1\text{ m/s}$).
  * **Plot B**: Congestion Ratio Penalty $C_e(t)$ scaling with halting vehicle count (queue buildup at intersections).
  * **Plot C**: Step-function response of edge weight under synthetic incident injection ($100\times$ penalty multiplier) followed by incident clearance.
* **Caption**: **Figure 4**: *Dynamic edge impedance formulation. (A) Travel time latency as a function of mean vehicle velocity; (B) Queuing penalty scaling with halted vehicle accumulation; (C) Edge cost trajectory before, during, and after an incident injection event.*
* **Technical Purpose**: Provides mathematical transparency for the cost function $w_e(t) = \alpha T_e(t) + \beta D_e + \gamma C_e(t)$ and illustrates how incident penalties force route recalculation.

---

### Figure 5: QPSO Continuous-to-Permutation Rank Discretization Mapping
* **Type**: Technical Infographic with Coordinate Projections
* **Placement**: Section 6 (Quantum-Inspired Particle Swarm Optimization: Continuous Delta Well to Discrete Routes)
* **Layout**:
  * **Top**: 1D quantum delta potential well showing particle bound state and probability density $|\psi(x)|^2 = \frac{1}{L} e^{-2|x - p| / L}$, with the wave collapse trajectory producing continuous coordinate vector $\mathbf{x}_i(t) \in \mathbb{R}^N$.
  * **Middle**: Numerical vector example for $N=5$ customers: $\mathbf{x}_i = [0.82, -0.45, 1.34, -1.12, 0.21]$.
  * **Bottom**: Rank Discretization Operator $\text{argsort}(\mathbf{x}_i)$. Ascending sorting indices map directly to customer permutation $\pi = [C_4, C_2, C_5, C_1, C_3]$.
  * **Evaluation**: Customer sequence evaluated via `VRPEvaluator` to obtain dynamic cost $f(\pi)$. Local best $\mathbf{p}_i$ and global swarm best $\mathbf{g}^*$ updated in continuous space.
* **Caption**: **Figure 5**: *Rank Discretization Mapping in Quantum-Behaved Particle Swarm Optimization (QPSO). Continuous coordinates sampled from the quantum delta potential well wave function collapse are transformed into discrete customer visit sequences via ascending index rank sorting.*
* **Technical Purpose**: Demystifies how continuous quantum-behaved swarm search explores discrete combinatorial permutation spaces, highlighting both its exploration strength and loss of gradient locality.

---

### Figure 6: QAOA Variational Circuit, Ising Hamiltonian, and COBYLA Optimization
* **Type**: Quantum Circuit Schematic + Algorithmic Flowchart
* **Placement**: Section 7 (Quantum Approximate Optimization Algorithm: QUBO, Ising, and Statevector Simulation)
* **Layout**:
  * **Panel A**: Position-based decision matrix $x_{i, p} \in \{0, 1\}$ for $N=3$ customers ($3^2 = 9$ qubits).
  * **Panel B**: Quantum Circuit diagram:
    * Initial state preparation: Hadamard gates on all 9 qubits ($H^{\otimes 9} |0\rangle = |+\rangle^{\otimes 9}$).
    * Problem unitary $U(H_C, \gamma) = e^{-i \gamma H_C}$: parameterized $R_Z$ rotations (linear costs) and CNOT-$R_Z$-CNOT ladders (quadratic coupling terms $J_{ij} Z_i Z_j$).
    * Mixer unitary $U(H_M, \beta) = e^{-i \beta H_M}$: parameterized $R_X(2\beta)$ rotations on all qubits.
  * **Panel C**: Classical feedback loop: Statevector probability measurement $\to$ expectation energy evaluation $\langle H_C \rangle \to$ Classical COBYLA optimizer updating $(\boldsymbol{\gamma}, \boldsymbol{\beta})$.
  * **Panel D**: Probability distribution histogram over $2^9 = 512$ bitstrings, highlighting valid permutation bitstrings versus invalid penalty-violating states.
* **Caption**: **Figure 6**: *QAOA formulation for VRP. Binary decision variables $x_{i,p}$ mapped to 9 qubits; depth-$p=1$ variational quantum circuit combining problem Hamiltonian $H_C$ and transverse mixer $H_M$; classical parameter optimization via COBYLA; and resulting bitstring probability distribution showing feasible ground-state convergence.*
* **Technical Purpose**: Shows the exact quantum circuit mechanics and explains why exponential Hilbert space scaling ($2^{N^2}$) limits classical statevector simulation to $N \le 4$.

---

### Figure 7: ALNS Destroy/Repair Mechanics and Roulette-Wheel Adaptation
* **Type**: Algorithmic State Diagram / Workflow Infographic
* **Placement**: Section 8 (Adaptive Large Neighborhood Search: Multi-Operator Dynamics)
* **Layout**:
  * **Center**: Current Multi-Vehicle Routing Plan $S = [R_1, R_2, R_3]$.
  * **Left (Destroy Phase)**: Three destroy operator options chosen via roulette-wheel probabilities:
    * *Random Removal*: Drops random subset of stops.
    * *Worst Removal*: Evaluates marginal cost contribution $\Delta(c) = \text{cost}(R) - \text{cost}(R \setminus \{c\})$ and strips high-cost outliers.
    * *Shaw Relatedness*: Removes clusters based on spatial distance and delivery demand similarity.
  * **Right (Repair Phase)**: Three repair operators:
    * *Greedy Insertion*: Inserts customer into cheapest feasible position across fleet.
    * *Regret-2 / Regret-3*: Calculates regret $r(c) = \sum_{j=2}^k (c_j - c_1)$ and inserts maximum-regret customer first.
  * **Bottom Feedback**: Score bonuses ($\sigma_1=33$ global best, $\sigma_2=9$ improving, $\sigma_3=13$ accepted non-improving) updating operator weight vector $\mathbf{w}$ after epoch $\tau=10$ with decay factor $\lambda=0.8$.
* **Caption**: **Figure 7**: *Adaptive Large Neighborhood Search (ALNS) operational framework. Dynamic routes undergo adaptive destruction via spatial/cost heuristics, followed by regret-guided reconstruction, with operator selection weights continually tuned based on solution improvements.*
* **Technical Purpose**: Clearly illustrates how ALNS handles multi-vehicle capacity constraints and explores large combinatorial neighborhoods through competing heuristic operators.

---

### Figure 8: HGS Dual-Population Architecture and Prins Split Algorithm
* **Type**: Conceptual Flowchart / Genetic Algorithm Architecture
* **Placement**: Section 9 (Hybrid Genetic Search: Giant-Tour Chromosomes and Population Diversity)
* **Layout**:
  * **Chromosome Representation**: Giant tour permutation $\pi = [C_3, C_1, C_5, C_2, C_4, C_6]$ without depot markers.
  * **Prins Split DP DAG**: Directed acyclic graph showing shortest path decomposition into capacity-feasible vehicle routes $[R_1, R_2]$.
  * **Dual Subpopulation Pools**:
    * Feasible Pool $P_{\text{feas}}$ (Zero capacity violation, sorted by cost).
    * Infeasible Pool $P_{\text{infeas}}$ (Penalized cost with adaptive weight $\omega_{\text{cap}}$).
  * **Biased Fitness Calculation**: Rank combination formula: $\text{BF}(I) = \text{rank}_{\text{cost}}(I) + \left(1 - \frac{\mu}{|P|}\right) \text{rank}_{\text{div}}(I)$, where diversity is quantified by broken-pairs distance.
  * **Local Search Education**: Relocate, Swap, and 2-Opt neighborhood improvements applied to offspring before population insertion.
* **Caption**: **Figure 8**: *Hybrid Genetic Search (HGS) architecture. Giant-tour chromosomes are partitioned into fleet routes via Prins' dynamic programming split; individuals populate dual feasible and infeasible pools; survivor selection balances solution quality with sequence diversity using biased fitness ranking.*
* **Technical Purpose**: Demonstrates how HGS explores the boundaries of the feasible search space and maintains population diversity to prevent premature convergence.

---

### Figure 9: Benchmark Performance Trade-Off: Solution Cost vs. Computation Time
* **Type**: Empirical Scatter Plot + Grouped Bar Chart (KaTeX Data Grounded)
* **Placement**: Section 10 (Empirical Benchmark Analysis: Real Road Network Evaluation)
* **Layout**:
  * **Chart A (Cost vs. Runtime Scatter)**: Log-scale x-axis (Computation Time in ms: $1\text{ ms}$ to $200\text{ ms}$), linear y-axis (Total Solution Cost).
    * Exact MIP CBC: Cost $937.02$, Runtime $152.90\text{ ms}$.
    * HGS: Cost $937.02$, Runtime $29.02\text{ ms}$ ($5.3\times$ faster than MIP, $0.0\%$ optimality gap).
    * QPSO: Cost $937.02$, Runtime $175.70\text{ ms}$ ($0.0\%$ gap, higher variance in convergence time).
    * ALNS: Mean Cost $976.20$, Runtime $1.05\text{ ms}$ ($145\times$ faster than MIP, $4.18\%$ optimality gap).
    * Point-to-Point Dijkstra: Cost $937.02$ (on 5-destination unconstrained sequence), Runtime $23.07\text{ ms}$.
  * **Chart B (Algorithm Efficiency Frontier)**: Radar plot comparing Runtime, Solution Quality, Multi-Vehicle Scalability, Dynamic Adaptability, and Mathematical Feasibility.
* **Caption**: **Figure 9**: *Empirical benchmark performance across 5 destination nodes on the Pune road network (3,559 nodes, 8,263 edges). HGS achieved exact MIP optimality in 29.02 ms, while ALNS delivered a near-optimal solution (4.18% gap) in just 1.05 ms, highlighting its viability for sub-second dynamic dispatch.*
* **Technical Purpose**: Visualizes the hard benchmark data from `benchmark_results.json`, providing empirical evidence for the engineering trade-offs between metaheuristic and exact solvers.

---

### Figure 10: Computational Complexity and Scaling Horizon: Quantum vs. Classical
* **Type**: Asymptotic Complexity Plot / Scaling Curves
* **Placement**: Section 11 (The Quantum Reality Check: Theory, Hardware Limits, and Honest Limitations)
* **Layout**:
  * X-axis: Number of Delivery Customers $N$ ($1$ to $50$).
  * Y-axis: Computational State Space / Operations (Logarithmic scale).
  * **Curve 1 (QAOA Statevector Simulation)**: $2^{N^2}$ complex amplitudes. Explodes from $512$ ($N=3$) to $65,536$ ($N=4$) to $33.5 \times 10^6$ ($N=5$), hitting classical memory exhaustion at $N=5$.
  * **Curve 2 (Exact MIP Branch-and-Cut)**: Worst-case $O(2^N)$ with combinatorial explosion past $N \approx 25-30$ customers in real-time dispatch settings.
  * **Curve 3 (ALNS / HGS Metaheuristics)**: Polynomial scaling $O(I \cdot K \cdot N^2)$, remaining fully tractable ($< 500\text{ ms}$) up to hundreds of stops.
  * **Annotated Boundary ("The NISQ Wall")**: Marks the boundary where quantum simulation becomes intractable and physical quantum hardware suffers from gate noise, qubit cross-talk, and decoherence.
* **Caption**: **Figure 10**: *Computational complexity scaling across solver paradigms. QAOA position-based QUBO requires $N^2$ qubits, causing statevector simulation memory requirements to explode as $O(2^{N^2})$, rendering it intractable on classical workstations for $N > 4$. Metaheuristics scale polynomially, maintaining sub-second performance at production scales.*
* **Technical Purpose**: Provides visual justification for our honest technical assessment of quantum computing in logistics, countering industry hype with computational reality.

---

### Figure 11: Real-Time Human-Readable Road Resolution Pipeline
* **Type**: Data Transformation Pipeline Infographic
* **Placement**: Section 12 (From Graph Edges to Human Drivers: Real-World OSM Road Name Resolution)
* **Layout**:
  * Step 1: Raw SUMO Edge Path: `["4342481629#0", "4342481629#1", "10225049025#0", "10225049025#1", "-558231#0"]`.
  * Step 2: OpenStreetMap Metadata Resolution: XML attribute lookup yielding road names: `["Shivaji Road", "Shivaji Road", "Jangali Maharaj Road", "Jangali Maharaj Road", "FC Road"]`.
  * Step 3: Adjacent Collinear Filtering & Deduplication: Consecutive identical road segments collapsed into single driver legs.
  * Step 4: Driver Dispatch Manifest UI Card:
    * *Leg 1*: Travel via **Shivaji Road** ($340\text{ m}, 42\text{ s}$) ➔ Deliver $2.0\text{ pkgs}$ to Customer 10225049025.
    * *Leg 2*: Travel via **Jangali Maharaj Road** ➔ **FC Road** ($1.2\text{ km}, 118\text{ s}$) ➔ Deliver $1.5\text{ pkgs}$ to Customer 10230365803.
* **Caption**: **Figure 11**: *Road name resolution pipeline. The system maps internal SUMO edge identifiers to authoritative OpenStreetMap tags, collapses adjacent identical street segments, and synthesizes human-readable turn-by-turn dispatch manifests for operational fleet drivers.*
* **Technical Purpose**: Explains how the platform bridges the gap between low-level simulator IDs and human logistics operations, fulfilling a critical requirement for real-world enterprise deployment.

---

### Figure 12: Complete End-to-End System Deployment Architecture
* **Type**: Full-Stack System Architecture Diagram
* **Placement**: Section 13 (Full-Stack Platform Architecture and Real-Time Operator UI)
* **Layout**:
  * **Simulation Layer**: SUMO Microscopic Simulator running background process, TraCI TCP socket server, Pune network configuration (`osm.net.xml`, `osm.sumocfg`).
  * **Backend Core (FastAPI / Python 3.10+)**:
    * `SumoManager`: TraCI process supervisor, vehicle tracking, incident injector.
    * `DynamicTrafficGraph`: NetworkX DiGraph holding dynamic edge impedance $W(t)$.
    * `RoadMetadataResolver`: OSM XML parser, caching resolver, turn manifest generator.
    * `VRPEvaluator`: Unified evaluation engine for cost, time, feasibility, and bottleneck detection.
    * `Solver Suite`: QPSO, QAOA, ALNS, HGS, MIP CBC, Dijkstra solvers.
    * REST API & WebSocket Streaming endpoints (`/ws/traffic`, `/api/vrp/optimize`, `/api/incidents`).
  * **Frontend UI (Vue 3 / Vite / Pinia)**:
    * Interactive Leaflet Map with real-time vehicle markers, dynamic route polylines, and incident overlays.
    * Multi-Vehicle Fleet Control Center with live capacity gauges, dispatch manifests, and operational steps.
    * Algorithm Research & Benchmark Hub with real-time convergence charts, Wilcoxon statistics, and quantum circuit inspect modals.
* **Caption**: **Figure 12**: *Full-stack platform architecture. The reactive frontend interfaces with a high-performance FastAPI backend, orchestrating microscopic SUMO simulation over TraCI, dynamic NetworkX graph updates, and a modular vehicle routing solver suite.*
* **Technical Purpose**: Serves as the overarching architectural reference for software engineers and systems architects evaluating the production readiness of the platform.

---

## Guidelines for Asset Production & Export

1. **Vector Diagrams (Figures 2, 3, 7, 8, 11, 12)**:
   * Recommended tool: Figma, draw.io, or Mermaid/PlantUML exported to high-resolution SVG/PNG ($2400 \times 1600$ minimum).
   * Color palette: Professional dark/light contrast; Navy blue primary (`#1E293B`), Emerald green for feasible routes (`#10B981`), Amber for warnings/penalties (`#F59E0B`), Rose red for incidents (`#EF4444`), Indigo for quantum components (`#6366F1`).
2. **Empirical Data Plots (Figures 4, 9, 10)**:
   * Generated directly using Python (`matplotlib` / `seaborn` / `plotly`) from actual runs recorded in `benchmark_results.json`.
   * Maintain clean typographic styling (serif/sans-serif font consistency, labeled axes with units, distinct marker styles).
3. **Quantum Circuit & Infographics (Figures 5, 6)**:
   * Circuit schematics exported from Qiskit circuit drawer (`circuit.draw(output='mpl')`) or customized in vector graphic software.
