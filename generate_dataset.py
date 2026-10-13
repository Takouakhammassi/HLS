import os
import numpy as np
import pandas as pd

SEED = 42
N_FILES = 1000
N_SITES = N_FILES // 100
ZIPF_S = 1.2
DIRICHLET_ALPHA = 0.5
OUTPUT_DIR = "dataset"

BUCKETS = [
    (1 * 1024, 50 * 1024, 0.40), 
    (50 * 1024, 500 * 1024, 0.30),   
    (500 * 1024, 1 * 1024 * 1024, 0.20),  
    (1 * 1024 * 1024, 5 * 1024 * 1024, 0.10),   
]
BUCKET_LABELS = ["1KB-50KB", "50KB-500KB", "500KB-1MB", "1MB-5MB"]

VOCAB = [
    "hadoop", "hdfs", "mapreduce", "spark", "cluster", "node", "block",
    "replication", "namenode", "datanode", "partition", "shuffle", "sort",
    "community", "louvain", "modularity", "graph", "weight", "edge",
    "file", "pack", "offset", "index", "compress", "snappy", "parquet",
    "access", "site", "frequency", "probability", "hellinger", "similarity",
]

def generate_popularity(n_files, seed, zipf_s):
    np.random.seed(seed)
    raw = np.random.zipf(zipf_s, n_files)
    raw = np.log1p(raw)
    return (raw / raw.max() * 1000).astype(int) + 1

def generate_sizes(n_files, seed):
    rng = np.random.default_rng(seed)
    probs = [b[2] for b in BUCKETS]
    bucket_ids = rng.choice(len(BUCKETS), size=n_files, p=probs)
    sizes = np.empty(n_files, dtype=np.int64)
    for i, bid in enumerate(bucket_ids):
        lo, hi, _ = BUCKETS[bid]
        sizes[i] = int(rng.integers(lo, hi, endpoint=True))
    return sizes, bucket_ids

def generate_access_matrix(n_files, n_sites, total_access, seed, alpha):
    np.random.seed(seed)
    ct = np.zeros((n_files, n_sites), dtype=np.int32)
    for i in range(n_files):
        probs = np.random.dirichlet([alpha] * n_sites)
        ct[i] = (probs * total_access[i]).astype(np.int32)
    return ct

def write_text_files(out_dir, file_ids, sizes, seed):
    os.makedirs(out_dir, exist_ok=True)
    n = len(file_ids)
    real_sizes = {}
    print(f"\nGenerating {n} files in {out_dir} ...")
    for idx, fname in enumerate(file_ids):
        target = int(sizes[idx])
        rng = np.random.default_rng(seed + idx)
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            written, line_no = 0, 0
            while written < target:
                n_words = int(rng.integers(6, 15))
                words = rng.choice(VOCAB, size=n_words, replace=True)
                line = f"[{fname}|L{line_no:06d}] " + " ".join(words) + "\n"
                f.write(line)
                written += len(line.encode("utf-8"))
                line_no += 1
        real_sizes[fname] = os.path.getsize(path)
        if (idx + 1) % 500 == 0:
            print(f"  {idx + 1}/{n} files generated ...")
    return real_sizes


def check_distribution(bucket_ids, n_files):
    print("\nSize distribution check:")
    print(f"  {'Bucket':<14} {'# files':>9} {'actual %':>9} {'target %':>9}")
    print("  " + "-" * 44)
    for k, label in enumerate(BUCKET_LABELS):
        count = int((bucket_ids == k).sum())
        print(f"  {label:<14} {count:>9} {count / n_files * 100:>8.1f}% "
              f"{BUCKETS[k][2] * 100:>8.0f}%")

def main():
    files_dir = os.path.join(OUTPUT_DIR, "small_files")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_ids = [f"small_{i:04d}.txt" for i in range(N_FILES)]
    sites = [f"S{j + 1}" for j in range(N_SITES)]

    total_access = generate_popularity(N_FILES, SEED, ZIPF_S)
    sizes, bucket_ids = generate_sizes(N_FILES, SEED)
    ct = generate_access_matrix(N_FILES, N_SITES, total_access, SEED, DIRICHLET_ALPHA)

    real = write_text_files(files_dir, file_ids, sizes, SEED)
    size_col = np.array([real[f] for f in file_ids], dtype=np.int64)
    print(f"\n  Min size : {size_col.min():,} B")
    print(f"  Max size : {size_col.max():,} B")
    print(f"  Total size : {size_col.sum() / 1024 / 1024:.1f} MB")

    df_index = pd.DataFrame({
        "file_id": file_ids,
        "size_bytes": size_col,
        "total_access": total_access,
    })
    for j, s in enumerate(sites):
        df_index[s] = ct[:, j]
    df_index.to_csv(os.path.join(OUTPUT_DIR, "dataset_index.csv"), index=False)

    check_distribution(bucket_ids, N_FILES)


if __name__ == "__main__":
    main()