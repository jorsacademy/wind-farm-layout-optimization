from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data" / "candidate_sites.csv"
    selected_path = root / "results" / "selected_sites.csv"

    if not data_path.exists():
        raise FileNotFoundError("Run 'python src/generate_data.py' first.")
    if not selected_path.exists():
        raise FileNotFoundError("Run 'python src/optimize.py' first.")

    candidates = pd.read_csv(data_path)
    selected = pd.read_csv(selected_path)

    plt.figure(figsize=(11, 7))
    plt.scatter(
        candidates["x_m"],
        candidates["y_m"],
        s=20,
        alpha=0.35,
        label="Candidate sites",
    )
    plt.scatter(
        selected["x_m"],
        selected["y_m"],
        s=90,
        marker="^",
        label="Selected turbines",
    )

    plt.title("Optimized Wind Farm Layout")
    plt.xlabel("East-West Position (m)")
    plt.ylabel("North-South Position (m)")
    plt.xlim(-200, 5200)
    plt.ylim(-200, 3200)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()

    output_dir = root / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "optimized_layout.png"
    plt.savefig(output_path, dpi=160)
    plt.show()

    print(f"Saved layout figure to: {output_path}")


if __name__ == "__main__":
    main()
