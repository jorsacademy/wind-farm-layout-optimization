from pathlib import Path

import pandas as pd

from model import ModelConfig, solve_layout


def load_sites() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parents[1] / "data" / "candidate_sites.csv"
    if not data_path.exists():
        raise FileNotFoundError(
            "Candidate-site data was not found. Run 'python src/generate_data.py' first."
        )
    return pd.read_csv(data_path)


def main() -> None:
    sites = load_sites()
    config = ModelConfig()
    solution = solve_layout(sites, config)

    selected = solution["selected_sites"]

    print("Wind Farm Layout Optimization")
    print("=" * 32)
    print(f"Candidate sites: {len(sites)}")
    print(f"Selected turbines: {len(selected)}")
    print(f"Minimum spacing: {config.minimum_spacing_m:.0f} m")
    print()
    print("Selected sites:")
    print(selected.to_string(index=False, formatters={"baseline_energy_gwh": "{:.3f}".format}))
    print()
    print(f"Baseline energy:  {solution['baseline_energy_gwh']:.3f} GWh")
    print(f"Wake loss:       {solution['wake_loss_gwh']:.3f} GWh")
    print(f"Optimized energy:{solution['optimized_energy_gwh']:9.3f} GWh")
    print(f"Solver message:  {solution['result'].message}")

    results_dir = Path(__file__).resolve().parents[1] / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    selected.to_csv(results_dir / "selected_sites.csv", index=False)


if __name__ == "__main__":
    main()
