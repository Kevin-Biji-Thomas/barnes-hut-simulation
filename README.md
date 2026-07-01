# Barnes-Hut N-body Simulation
Barnes–Hut N-body gravitational simulation implemented in Python using VPython

This project implements the Barnes-Hut algorithm in Python to simulate gravitational interactions in an N-body system. It uses a quadtree structure to approximate distant particle clusters, reducing computational complexity from O(N²) to approximately O(N log N).

## Features

- Barnes-Hut quadtree implementation
- Gravitational force approximation using center of mass
- Velocity Verlet integration for improved numerical stability
- 2D simulation with VPython visualization
- Center of mass tracking over time

## Physics Concepts Used

- Newtonian gravity
- Numerical integration (Velocity Verlet method)
- Center of mass calculation
- Softening parameter to avoid singularities
- Angular approximation criterion (θ)

## Requirements

- Python 3
- VPython
- Math library
- 
## How to Run

Run the simulation using:

```bash
python "Barnes Hut Simulation.py"
