from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


@dataclass(frozen=True)
class ModelConfig:
    number_of_turbines: int = 12
    rotor_diameter_m: float = 120.0
    minimum_spacing_m: float = 600.0
    wake_lateral_limit_m: float = 360.0
    wake_decay_length_m: float = 1800.0
    maximum_pairwise_wake_loss_gwh: float = 2.2


def _pair_distance(row_i: pd.Series, row_j: pd.Series) -> float:
    dx = float(row_j.x_m - row_i.x_m)
    dy = float(row_j.y_m - row_i.y_m)
    return float(np.hypot(dx, dy))


def wake_penalty(row_i: pd.Series, row_j: pd.Series, config: ModelConfig) -> float:
    """Return a simplified directional wake penalty for a west-to-east wind regime."""
    if row_i.x_m == row_j.x_m:
        return 0.0

    upstream, downstream = (row_i, row_j) if row_i.x_m < row_j.x_m else (row_j, row_i)

    downstream_distance = float(downstream.x_m - upstream.x_m)
    lateral_separation = abs(float(downstream.y_m - upstream.y_m))

    if lateral_separation > config.wake_lateral_limit_m:
        return 0.0

    longitudinal_factor = np.exp(-downstream_distance / config.wake_decay_length_m)
    lateral_factor = 1.0 - lateral_separation / config.wake_lateral_limit_m

    return float(config.maximum_pairwise_wake_loss_gwh * longitudinal_factor * lateral_factor)


def solve_layout(sites: pd.DataFrame, config: ModelConfig = ModelConfig()) -> dict:
    """Solve the discrete wind farm layout problem as a MILP."""
    if config.number_of_turbines > len(sites):
        raise ValueError("The requested number of turbines exceeds the number of candidate sites.")

    site_pairs = list(combinations(range(len(sites)), 2))
    wake_pairs = []
    spacing_conflicts = []

    for i, j in site_pairs:
        row_i = sites.iloc[i]
        row_j = sites.iloc[j]

        if _pair_distance(row_i, row_j) < config.minimum_spacing_m:
            spacing_conflicts.append((i, j))

        penalty = wake_penalty(row_i, row_j, config)
        if penalty > 0:
            wake_pairs.append((i, j, penalty))

    n_sites = len(sites)
    n_wake = len(wake_pairs)
    n_variables = n_sites + n_wake

    # scipy.optimize.milp minimizes, so energy benefits are negated.
    c = np.zeros(n_variables, dtype=float)
    c[:n_sites] = -sites["baseline_energy_gwh"].to_numpy(dtype=float)

    for k, (_, _, penalty) in enumerate(wake_pairs):
        c[n_sites + k] = penalty

    integrality = np.ones(n_variables, dtype=int)
    bounds = Bounds(np.zeros(n_variables), np.ones(n_variables))

    rows = []
    lower = []
    upper = []

    # Select exactly the required number of turbines.
    row = np.zeros(n_variables)
    row[:n_sites] = 1.0
    rows.append(row)
    lower.append(float(config.number_of_turbines))
    upper.append(float(config.number_of_turbines))

    # Minimum spacing constraints.
    for i, j in spacing_conflicts:
        row = np.zeros(n_variables)
        row[i] = 1.0
        row[j] = 1.0
        rows.append(row)
        lower.append(-np.inf)
        upper.append(1.0)

    # Linearize y_ij = x_i * x_j for wake pairs.
    for k, (i, j, _) in enumerate(wake_pairs):
        y = n_sites + k

        row = np.zeros(n_variables)
        row[y] = 1.0
        row[i] = -1.0
        rows.append(row)
        lower.append(-np.inf)
        upper.append(0.0)

        row = np.zeros(n_variables)
        row[y] = 1.0
        row[j] = -1.0
        rows.append(row)
        lower.append(-np.inf)
        upper.append(0.0)

        row = np.zeros(n_variables)
        row[y] = 1.0
        row[i] = -1.0
        row[j] = -1.0
        rows.append(row)
        lower.append(-1.0)
        upper.append(np.inf)

    matrix = lil_matrix(np.vstack(rows)).tocsr()
    constraints = LinearConstraint(matrix, np.array(lower), np.array(upper))

    result = milp(
        c=c,
        integrality=integrality,
        bounds=bounds,
        constraints=constraints,
        options={"disp": False},
    )

    if not result.success or result.x is None:
        raise RuntimeError(f"Optimization failed: {result.message}")

    selected_mask = result.x[:n_sites] > 0.5
    selected_sites = sites.loc[selected_mask].copy().reset_index(drop=True)

    baseline_total = float(selected_sites["baseline_energy_gwh"].sum())
    wake_loss_total = 0.0

    for k, (_, _, penalty) in enumerate(wake_pairs):
        if result.x[n_sites + k] > 0.5:
            wake_loss_total += penalty

    optimized_energy = baseline_total - wake_loss_total

    return {
        "result": result,
        "selected_sites": selected_sites,
        "baseline_energy_gwh": baseline_total,
        "wake_loss_gwh": wake_loss_total,
        "optimized_energy_gwh": optimized_energy,
        "spacing_conflicts": spacing_conflicts,
        "wake_pairs": wake_pairs,
    }
