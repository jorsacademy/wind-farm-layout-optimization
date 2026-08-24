# Wind Farm Layout Optimization

This repository presents a reproducible Operations Research project for discrete wind farm layout optimization.

The model selects turbine locations from a set of candidate sites while balancing baseline energy potential, turbine spacing requirements, and pairwise wake losses. The optimization problem is formulated as a mixed-integer linear program and solved with SciPy's `milp` interface.

## Problem Statement

A wind farm developer has a rectangular site and a predefined set of feasible turbine locations. The goal is to install a fixed number of turbines such that estimated annual energy production is maximized.

The model considers:

1. Baseline energy production at each candidate site.
2. Minimum spacing constraints between selected turbines.
3. Pairwise wake penalties when selected turbines are aligned with the prevailing wind direction.

The prevailing wind direction in the example is west-to-east.

## Scenario

- Farm width: 5,000 m
- Farm height: 3,000 m
- Rotor diameter: 120 m
- Minimum spacing: 600 m
- Required turbines: 12
- Prevailing wind direction: west-to-east
- Candidate sites: regular grid
- Energy values: synthetic and reproducible
- Wake penalties: based on downstream distance and lateral separation

The project is intended for educational and methodological use. It is not a replacement for engineering-grade wake simulation software.

## Mathematical Formulation

Let `x_i` be 1 when a turbine is installed at candidate site `i`, and 0 otherwise. Let `e_i` be the baseline energy score at site `i`. Let `p_ij` be the wake penalty if both candidate sites `i` and `j` are selected. Let `y_ij` be a binary variable equal to 1 when both sites are selected.

Objective:

```text
maximize  sum(e_i * x_i) - sum(p_ij * y_ij)
```

Required turbine count:

```text
sum(x_i) = number_of_turbines
```

For candidate pairs that violate the minimum spacing requirement:

```text
x_i + x_j <= 1
```

Pairwise linearization:

```text
y_ij <= x_i
y_ij <= x_j
y_ij >= x_i + x_j - 1
```

All decision variables are binary.

## Repository Structure

```text
wind-farm-layout-optimization/
├── README.md
├── LICENSE.md
├── requirements.txt
├── .gitignore
├── data/
│   └── candidate_sites.csv
└── src/
    ├── generate_data.py
    ├── model.py
    ├── optimize.py
    └── visualization.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Generate the synthetic candidate-site dataset:

```bash
python src/generate_data.py
```

Run the optimization:

```bash
python src/optimize.py
```

Generate a plot of the optimized layout:

```bash
python src/visualization.py
```

## Modeling Notes

A discrete candidate-site formulation is used instead of continuous turbine coordinates. This keeps the model within MILP structure, makes spacing constraints exact over the candidate set, and avoids dependence on an external nonlinear solver executable.

The wake model is deliberately simplified. A production-grade model would normally account for wind-direction distributions, atmospheric stability, turbine thrust coefficients, terrain, turbulence, and calibrated wake physics.

## License

This repository is licensed for non-commercial use only. See `LICENSE.md` for the complete terms.
