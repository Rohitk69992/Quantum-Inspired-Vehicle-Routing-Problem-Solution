# Authoritative Bibliography and References
## "Quantum-Inspired Intelligent Traffic Route Optimization in Transportation Systems Using Metaheuristic Optimization"

This document provides verified, complete bibliographic citations for all theoretical, algorithmic, and engineering foundations implemented in this project. Every reference includes full author details, publication venue, year, persistent identifier (DOI/arXiv/URL), and an explicit summary of the exact mathematical concepts or architectural components it supports in the codebase.

---

### 1. Classical Vehicle Routing & Combinatorial Optimization Foundations

#### [Dantzig & Ramser, 1959]
* **Authors**: George B. Dantzig and John H. Ramser
* **Title**: *The Truck Dispatching Problem*
* **Journal**: Management Science, Vol. 6, No. 1, pp. 80–91
* **Year**: 1959
* **DOI**: [10.1287/mnsc.6.1.80](https://doi.org/10.1287/mnsc.6.1.80)
* **Concepts Supported**: 
  * Foundational formulation of the Capacitated Vehicle Routing Problem (CVRP).
  * Multi-vehicle fleet dispatching from a centralized supply depot to spatially distributed demand points.
  * Linear programming relaxation and combinatorial complexity of vehicle capacity constraints.

#### [Clarke & Wright, 1964]
* **Authors**: G. Clarke and J. W. Wright
* **Title**: *Scheduling of Vehicles from a Central Depot to a Number of Delivery Points*
* **Journal**: Operations Research, Vol. 12, No. 4, pp. 568–581
* **Year**: 1964
* **DOI**: [10.1287/opre.12.4.568](https://doi.org/10.1287/opre.12.4.568)
* **Concepts Supported**:
  * Savings algorithm heuristic for vehicle route consolidation: $s(i, j) = c(0, i) + c(0, j) - c(i, j)$.
  * Baseline greedy route initialization used in fleet construction.

#### [Miller, Tucker, & Zemlin, 1960]
* **Authors**: Clair E. Miller, Albert W. Tucker, and Richard A. Zemlin
* **Title**: *Integer Programming Formulation of Traveling Salesman Problems*
* **Journal**: Journal of the ACM (JACM), Vol. 7, No. 4, pp. 326–329
* **Year**: 1960
* **DOI**: [10.1145/321043.321046](https://doi.org/10.1145/321043.321046)
* **Concepts Supported**:
  * Subtour elimination constraints (MTZ auxiliary variables $u_i - u_j + q \cdot x_{ij} \le q - d_j$).
  * Exact Mixed-Integer Linear Programming (MILP) mathematical formulation solved by our backend Coin-OR CBC solver.

#### [Dijkstra, 1959]
* **Authors**: Edsger W. Dijkstra
* **Title**: *A note on two problems in connexion with graphs*
* **Journal**: Numerische Mathematik, Vol. 1, No. 1, pp. 269–271
* **Year**: 1959
* **DOI**: [10.1007/BF01386390](https://doi.org/10.1007/BF01386390)
* **Concepts Supported**:
  * Single-source shortest path computation on weighted directed graphs.
  * Underlying lower-tier network traversal engine in `VRPEvaluator.evaluate_leg()` for road-level pathfinding.

---

### 2. Quantum-Inspired Swarm Optimization (QPSO)

#### [Sun et al., 2012]
* **Authors**: Jun Sun, Wenbo Fang, Vasile Palade, Xiaojun Wu, and Wei Xu
* **Title**: *Quantum-behaved particle swarm optimization: Analysis of individual particle behavior and parameter selection*
* **Journal**: Evolutionary Computation, Vol. 20, No. 3, pp. 349–393
* **Year**: 2012
* **DOI**: [10.1162/EVCO_a_00049](https://doi.org/10.1162/EVCO_a_00049)
* **Concepts Supported**:
  * Theoretical derivation of particle trajectories governed by the Schrödinger equation in a quantum $\delta$-potential well.
  * Derivation of the wave function $\psi(x)$ and probability density function yielding the double-exponential distribution.
  * Definition of the mean best position $m_{\text{best}} = \frac{1}{M} \sum_{i=1}^M p_{i,\text{best}}$ across the swarm.
  * Linear decay schedule for the contraction-expansion coefficient $\alpha(t) = \alpha_{\max} - \frac{t}{T_{\max}} (\alpha_{\max} - \alpha_{\min})$.

#### [Herrera, Coelho, & Steiner, 2015]
* **Authors**: Manuel Herrera, Leandro dos Santos Coelho, and Maria Teresinha Arns Steiner
* **Title**: *Particle swarm optimization applied to the vehicle routing problem with simultaneous delivery and pickup*
* **Journal**: Pesquisa Operacional, Vol. 35, No. 3, pp. 509–540
* **Year**: 2015
* **DOI**: [10.1590/0101-7438.2015.035.03.0509](https://doi.org/10.1590/0101-7438.2015.035.03.0509)
* **Concepts Supported**:
  * Continuous-to-permutation Rank Discretization Mapping ($\text{argsort}$) for mapping real-valued continuous positions $x_{i,d} \in \mathbb{R}$ to valid discrete customer visit sequences $\pi$.
  * Adaptation of particle swarm mechanics to multi-vehicle routing problems.
  * Direct structural blueprint for our `backend/vrp/qpso_vrp.py` solver.

---

### 3. Quantum Approximate Optimization Algorithm (QAOA) & QUBO

#### [Farhi, Goldstone, & Gutmann, 2014]
* **Authors**: Edward Farhi, Jeffrey Goldstone, and Sam Gutmann
* **Title**: *A Quantum Approximate Optimization Algorithm*
* **Archive**: arXiv:1411.4028 [quant-ph]
* **Year**: 2014
* **URL**: [https://arxiv.org/abs/1411.4028](https://arxiv.org/abs/1411.4028)
* **Concepts Supported**:
  * Original variational quantum circuit ansatz: $|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{l=1}^p e^{-i \beta_l H_M} e^{-i \gamma_l H_C} |+\rangle^{\otimes n}$.
  * Problem Hamiltonian $H_C$ phase separation operator and transverse-field mixer Hamiltonian $H_M = \sum_{i=1}^n X_i$.
  * Hybrid quantum-classical optimization loop where classical optimizers (COBYLA) tune continuous rotation angles.

#### [Azfar et al., 2025]
* **Authors**: M. T. Azfar, M. Raisuddin, J. Ke, and José Holguín-Veras
* **Title**: *Formulations and Algorithms for the Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm*
* **Journal / Archive**: ACM Transactions on Quantum Computing (also arXiv:2505.01614 [quant-ph])
* **Year**: 2025
* **URL**: [https://arxiv.org/abs/2505.01614](https://arxiv.org/abs/2505.01614)
* **Concepts Supported**:
  * Position-based QUBO formulation for VRP using binary variables $x_{i,p} \in \{0, 1\}$ (customer $i$ visited at position $p$).
  * Exact quadratic cost term: $\sum_{p=0}^{N-2} \sum_{i \ne j} c_{ij} x_{i,p} x_{j,p+1}$.
  * Mathematical penalty multiplier formulation: $P = 2 \sum_{i,j} |c_{ij}|$ ensuring constraint dominance over routing cost.
  * Uniqueness penalty terms for customer assignment $\sum_i (\sum_p x_{i,p} - 1)^2$ and position assignment $\sum_p (\sum_i x_{i,p} - 1)^2$.
  * Direct structural blueprint for our `backend/vrp/qaoa_vrp.py` solver and Qiskit circuit synthesis.

#### [Lucas, 2014]
* **Authors**: Andrew Lucas
* **Title**: *Ising formulations of many NP problems*
* **Journal**: Frontiers in Physics, Vol. 2, Article 5
* **Year**: 2014
* **DOI**: [10.3389/fphy.2014.00005](https://doi.org/10.3389/fphy.2014.00005)
* **Concepts Supported**:
  * Binary variable transformation to Pauli spin operators: $x_i = \frac{I - Z_i}{2}$.
  * Derivation of Ising Hamiltonian coefficients: $H_C = c_0 I + \sum_i h_i Z_i + \sum_{i<j} J_{ij} Z_i Z_j$.
  * QUBO-to-Ising translation mechanics implemented in `QAOAVRPSolver._qubo_to_ising()`.

---

### 4. Adaptive Large Neighborhood Search (ALNS)

#### [Ropke & Pisinger, 2006]
* **Authors**: Stefan Ropke and David Pisinger
* **Title**: *An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows*
* **Journal**: Transportation Science, Vol. 40, No. 4, pp. 455–472
* **Year**: 2006
* **DOI**: [10.1287/trsc.1050.0135](https://doi.org/10.1287/trsc.1050.0135)
* **Concepts Supported**:
  * Multi-operator destroy and repair framework.
  * Shaw / Relatedness destroy operator measuring spatial and temporal affinity.
  * Worst removal operator targeting highest marginal insertion cost contribution $\Delta(c) = \text{cost}(R) - \text{cost}(R \setminus \{c\})$.
  * Regret-2 and Regret-3 repair heuristics evaluating lookahead opportunity loss: $r(c) = \sum_{j=2}^k (c_j(c) - c_1(c))$.
  * Roulette wheel adaptive operator weight updates: $w_{j}^{t+1} = \lambda w_j^t + (1 - \lambda) \frac{\pi_j}{\theta_j}$ with scoring parameters $\sigma_1 = 33, \sigma_2 = 9, \sigma_3 = 13$.
  * Simulated annealing acceptance criterion: $P(\text{accept}) = \exp\left(-\frac{f(S') - f(S)}{T}\right)$.
  * Direct structural blueprint for our `backend/vrp/alns_vrp.py` solver.

#### [Pisinger & Ropke, 2007]
* **Authors**: David Pisinger and Stefan Ropke
* **Title**: *A general heuristic for vehicle routing problems*
* **Journal**: Computers & Operations Research, Vol. 34, No. 8, pp. 2403–2435
* **Year**: 2007
* **DOI**: [10.1016/j.cor.2005.09.012](https://doi.org/10.1016/j.cor.2005.09.012)
* **Concepts Supported**:
  * Unified neighborhood exploration across rich vehicle routing variants.
  * Fast evaluation of capacity constraints during greedy insertion.

---

### 5. Hybrid Genetic Search (HGS)

#### [Vidal et al., 2012]
* **Authors**: Thibaut Vidal, Teodor Gabriel Crainic, Michel Gendreau, Nadia Lahrichi, and Walter Rei
* **Title**: *A hybrid genetic algorithm for multidepot and periodic vehicle routing problems*
* **Journal**: Operations Research, Vol. 60, No. 3, pp. 611–624
* **Year**: 2012
* **DOI**: [10.1287/opre.1120.1048](https://doi.org/10.1287/opre.1120.1048)
* **Concepts Supported**:
  * Dual-subpopulation management maintaining separate Feasible ($P_{\text{feas}}$) and Infeasible ($P_{\text{infeas}}$) solution pools.
  * Biased fitness ranking combining solution cost ranking and population diversity ranking: $\text{BF}(I) = \text{rank}_{\text{cost}}(I) + \left(1 - \frac{\mu}{|P|}\right) \text{rank}_{\text{div}}(I)$.
  * Broken-pairs distance metric measuring structural sequence disparity between chromosomes.
  * Dynamic penalty adaptation for capacity violations based on target feasibility ratio: $\omega_{\text{cap}} \leftarrow \omega_{\text{cap}} \cdot 1.2$ or $\omega_{\text{cap}} \cdot 0.85$.
  * Direct structural blueprint for our `backend/vrp/hgs_vrp.py` solver.

#### [Vidal, 2022]
* **Authors**: Thibaut Vidal
* **Title**: *Hybrid genetic search for the vehicle routing problem with time windows: A unifying review and modern implementation*
* **Journal**: Computers & Operations Research, Vol. 140, Article 105643
* **Year**: 2022
* **DOI**: [10.1016/j.cor.2021.105643](https://doi.org/10.1016/j.cor.2021.105643)
* **Concepts Supported**:
  * Open-source algorithmic standardization of HGS.
  * Neighborhood exploration protocols (Relocate, Swap, 2-Opt) and survivor selection truncation.

#### [Prins, 2004]
* **Authors**: Christian Prins
* **Title**: *A simple and effective hybrid genetic algorithm for the two-dimensional packing problem and the vehicle routing problem*
* **Journal**: Computers & Operations Research, Vol. 31, No. 12, pp. 1985–2002
* **Year**: 2004
* **DOI**: [10.1016/S0305-0548(03)00158-8](https://doi.org/10.1016/S0305-0548(03)00158-8)
* **Concepts Supported**:
  * Giant-tour chromosome representation without trip delimiters.
  * Optimal $O(N \cdot C)$ Dynamic Programming Split algorithm decomposing permutations into fleet vehicle routes respecting vehicle capacity constraints.

---

### 6. Microscopic Traffic Simulation & Network Engineering

#### [Lopez et al., 2018]
* **Authors**: Pablo Alvarez Lopez, Michael Behrisch, Laura Bieker-Walz, Jakob Erdmann, Yun-Pang Flötteröd, Robert Hilbrich, Leonhard Lücken, Johannes Rummel, Peter Wagner, and Evamarie Wießner
* **Title**: *Microscopic Traffic Simulation using SUMO*
* **Conference**: The 21st IEEE International Conference on Intelligent Transportation Systems (ITSC 2018), pp. 2575–2582
* **Year**: 2018
* **DOI**: [10.1109/ITSC.2018.8569938](https://doi.org/10.1109/ITSC.2018.8569938)
* **Concepts Supported**:
  * Simulation of Urban MObility (SUMO) microscopic simulation framework.
  * Krauß car-following and LC2013 lane-changing microscopic behavioral models.
  * Road network topology compilation and traffic light control.

#### [Wegener et al., 2008]
* **Authors**: Axel Wegener, Michał Piórkowski, Maxim Raya, Horst Hellbrück, Stefan Fischer, and Jean-Pierre Hubaux
* **Title**: *TraCI: An Interface for Coupling Road Traffic and Network Simulators*
* **Conference**: Proceedings of the 11th Communications and Networking Simulation Symposium (CNS '08), pp. 155–163
* **Year**: 2008
* **DOI**: [10.1145/1400713.1400740](https://doi.org/10.1145/1400713.1400740)
* **Concepts Supported**:
  * Traffic Control Interface (TraCI) TCP client-server protocol.
  * Real-time telemetry extraction (`getLastStepMeanSpeed`, `getLastStepVehicleNumber`, `getLastStepHaltingNumber`).
  * Dynamic vehicle rerouting actuation (`traci.vehicle.setRoute`).

#### [Haklay & Weber, 2008]
* **Authors**: Mordechai Haklay and Patrick Weber
* **Title**: *OpenStreetMap: User-Generated Street Maps*
* **Journal**: IEEE Pervasive Computing, Vol. 7, No. 4, pp. 12–18
* **Year**: 2008
* **DOI**: [10.1109/MPRV.2008.80](https://doi.org/10.1109/MPRV.2008.80)
* **Concepts Supported**:
  * OpenStreetMap (OSM) topological data model: nodes, ways, and semantic highway tags (`name`, `highway`).
  * Road metadata resolution engine mapping raw SUMO IDs to human-readable street names.

---

### 7. Statistical Methodology & Benchmark Verification

#### [Wilcoxon, 1945]
* **Authors**: Frank Wilcoxon
* **Title**: *Individual comparisons by ranking methods*
* **Journal**: Biometrics Bulletin, Vol. 1, No. 6, pp. 80–83
* **Year**: 1945
* **DOI**: [10.2307/3001968](https://doi.org/10.2307/3001968)
* **Concepts Supported**:
  * Wilcoxon signed-rank non-parametric paired hypothesis testing.
  * Rigorous multi-seed statistical significance testing across solver stochastic runs ($p$-values computed in `benchmark_results.json`).
