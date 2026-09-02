import time
import random
import itertools
import tracemalloc
import pandas as pd
import numpy as np

from core.data_loader import WardrobeDataLoader
from core.graph_builder import WardrobeGraphBuilder
from core.outfit_search import OutfitSearcher
from core.scoring import compatibility_score


def generate_synthetic_dataset(num_items=100, seed=42):
    """Generate realistic synthetic wardrobe items for scaling benchmarks."""
    random.seed(seed)
    types = ["shirt", "pants", "shoes", "watch", "polo", "tshirt", "jacket"]
    vibes_pool = ["clean", "minimal", "fresh", "airy", "sleek", "sharp", "bold",
                  "classic", "refined", "warm", "earthy", "vintage", "modern", "sporty", "luxury", "urban"]
    
    rows = []
    for i in range(num_items):
        t = types[i % len(types)]
        name = f"Synthetic_{t.capitalize()}_{i+1}"
        r, g, b = random.randint(10, 250), random.randint(10, 250), random.randint(10, 250)
        hue = random.randint(0, 359)
        formality = random.choice([2, 3, 4, 6, 7, 9, 10])
        num_vibes = random.randint(1, 3)
        vibe = random.sample(vibes_pool, num_vibes)
        
        row = {
            "item_name": name,
            "type": t,
            "color_name": "custom",
            "reds": r, "green": g, "blue": b,
            "hue": hue,
            "strap_reds": random.randint(10, 250) if t == "watch" else np.nan,
            "strap_green": random.randint(10, 250) if t == "watch" else np.nan,
            "strap_blue": random.randint(10, 250) if t == "watch" else np.nan,
            "strap_hue": random.randint(0, 359) if t == "watch" else np.nan,
            "dial_reds": random.randint(10, 250) if t == "watch" else np.nan,
            "dial_green": random.randint(10, 250) if t == "watch" else np.nan,
            "dial_blue": random.randint(10, 250) if t == "watch" else np.nan,
            "dial_hue": random.randint(0, 359) if t == "watch" else np.nan,
            "formality": formality,
            "vibe": vibe
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    loader = WardrobeDataLoader()
    df = loader._create_color_vectors(df)
    df = loader._create_watch_vectors(df)
    df = loader._clean_types(df)
    df["formality"] = pd.to_numeric(df["formality"], errors="coerce")
    return df


def benchmark_run(df, required_types=("shirt", "pants", "watch"), outfit_repeats=5):
    """Run a standardized benchmark returning exact metrics."""
    tracemalloc.start()
    t0 = time.perf_counter()
    
    builder = WardrobeGraphBuilder(df)
    G = builder.build_graph()
    
    t_graph = time.perf_counter() - t0
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    searcher = OutfitSearcher(G)
    
    t0_search = time.perf_counter()
    best_res = None
    for _ in range(outfit_repeats):
        best_res = searcher.best_outfit(list(required_types))
    t_search = (time.perf_counter() - t0_search) / outfit_repeats
    
    return {
        "num_items": len(df),
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "graph_time_ms": t_graph * 1000,
        "search_time_ms": t_search * 1000,
        "peak_mem_kb": peak_mem / 1024,
        "best_outfit": best_res["outfit"],
        "best_score": round(float(best_res["score"]), 4) if best_res["score"] is not None else None
    }


def run_full_benchmark():
    print("=" * 70)
    print("WARDROBE RECOMMENDATION ENGINE — STAGE 1 BENCHMARK")
    print("=" * 70)
    
    # 1. Real dataset
    loader = WardrobeDataLoader()
    real_df = loader.load()
    real_metrics = benchmark_run(real_df, required_types=["shirt", "pants", "watch"], outfit_repeats=10)
    
    print(f"\n[Real Dataset: N={real_metrics['num_items']}]")
    print(f"  Nodes: {real_metrics['nodes']}, Edges: {real_metrics['edges']}")
    print(f"  Graph Build Time: {real_metrics['graph_time_ms']:.2f} ms")
    print(f"  best_outfit Time: {real_metrics['search_time_ms']:.4f} ms")
    print(f"  Peak Memory:      {real_metrics['peak_mem_kb']:.1f} KB")
    print(f"  Best Outfit:      {real_metrics['best_outfit']}")
    print(f"  Best Score:       {real_metrics['best_score']}")
    
    # 2. Scaled synthetic datasets
    print("\n" + "-" * 70)
    print("Scaling Benchmarks (N = 50, 100, 250, 500)")
    print("-" * 70)
    print(f"{'N':<6} | {'Nodes':<6} | {'Edges':<8} | {'Graph Build (ms)':<18} | {'best_outfit (ms)':<18} | {'Peak Mem (KB)':<14}")
    print("-" * 70)
    
    for size in [50, 100, 250, 500]:
        synth_df = generate_synthetic_dataset(num_items=size, seed=42)
        m = benchmark_run(synth_df, required_types=["shirt", "pants", "shoes", "watch"], outfit_repeats=3 if size <= 250 else 1)
        print(f"{m['num_items']:<6} | {m['nodes']:<6} | {m['edges']:<8} | {m['graph_time_ms']:<18.2f} | {m['search_time_ms']:<18.4f} | {m['peak_mem_kb']:<14.1f}")
    
    print("=" * 70)


if __name__ == "__main__":
    run_full_benchmark()
