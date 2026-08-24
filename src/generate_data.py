from pathlib import Path

import numpy as np
import pandas as pd


FARM_WIDTH = 5000
FARM_HEIGHT = 3000
GRID_STEP_X = 500
GRID_STEP_Y = 500
RANDOM_SEED = 42


def generate_candidate_sites() -> pd.DataFrame:
    """Generate a reproducible grid of candidate turbine locations."""
    rng = np.random.default_rng(RANDOM_SEED)

    x_coords = np.arange(0, FARM_WIDTH + 1, GRID_STEP_X)
    y_coords = np.arange(0, FARM_HEIGHT + 1, GRID_STEP_Y)

    records = []
    site_id = 0

    for x in x_coords:
        for y in y_coords:
            # Synthetic local resource multiplier.
            resource_factor = 0.92 + 0.12 * rng.random()

            # Mild deterministic spatial effect to avoid a flat landscape.
            spatial_factor = 1.0 + 0.04 * np.sin(x / 900.0) + 0.03 * np.cos(y / 700.0)

            baseline_energy = 18.0 * resource_factor * spatial_factor

            records.append(
                {
                    "site_id": site_id,
                    "x_m": float(x),
                    "y_m": float(y),
                    "baseline_energy_gwh": float(baseline_energy),
                }
            )
            site_id += 1

    return pd.DataFrame(records)


def main() -> None:
    output_path = Path(__file__).resolve().parents[1] / "data" / "candidate_sites.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_candidate_sites()
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} candidate sites.")
    print(f"Saved dataset to: {output_path}")


if __name__ == "__main__":
    main()
