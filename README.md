# HLS - Dataset generation

Code to generate the synthetic datasets and workloads used in the article:

> H. Chettaoui and T. Khammassi, *Integrating Hellinger-based Correlation Assessment with Louvain Community Detection for Solving the Small Files Problem in a Big Data Context*, 2026.

**HLS** (Hellinger and Louvain-based Solution) is a strategy that merges correlated small files into larger files in HDFS. This repository only contains the **dataset and workload generator** described in Section 4 and used in Section 5 of the article. The merging strategies themselves (HLS, CHAC, CSGC) are not included.

## Workload model

The workload is a tuple `W = (F, S, A)`:

| Component | Description | Model |
|---|---|---|
| `F` | set of small text files `small_0000.txt`, `small_0001.txt`, … | — |
| `S` | file sizes, between 1 KB and 5 MB | drawn by size bucket (see below), uniform within each bucket |
| `A` | accesses of each file across `m` sites | total popularity per file: Zipf (`s = 1.2`, log-scaled to `[1, 1001]`); split over sites: Dirichlet (`α = 0.5`) |

Size buckets (Fig. 2 of the article):

| Bucket | Share of files |
|---|---|
| 1 KB – 50 KB | 40 % |
| 50 KB – 500 KB | 30 % |
| 500 KB – 1 MB | 20 % |
| 1 MB – 5 MB | 10 % |

The number of sites is `n_files // 100` by default (e.g. 30 sites for 3,000 files, 290 sites for 29,000 files).
The content of each file is random text built from a fixed 32-word vocabulary (Hadoop / HDFS / graph terms), one line per record, until the target size is reached. Each file is generated with its own seed (`seed + file index`).

## Installation

Python ≥ 3.9 is required.

```bash
git clone https://github.com/<user>/HLS.git
cd HLS
pip install -r requirements.txt
```

## Usage

Edit the parameters at the top of `generate_dataset.py`, then run:

```bash
python generate_dataset.py
```

| Parameter | Default | Description |
|---|---|---|
| `SEED` | `42` | random seed |
| `N_FILES` | `3000` | number of small files |
| `N_SITES` | `N_FILES // 100` | number of sites |
| `ZIPF_S` | `1.2` | Zipf exponent |
| `DIRICHLET_ALPHA` | `0.5` | Dirichlet concentration parameter |
| `OUTPUT_DIR` | `"dataset"` | output directory |

To reproduce the datasets of the article (1,000 to 30,000 files), change `N_FILES` (and `OUTPUT_DIR`) and run the script once per size.

> **Disk space:** the text files of the largest dataset (30,000 files) take about 16 GB (see Table 2 of the article).

## Output

```
<output-dir>/
├── small_files/        # small_0000.txt, small_0001.txt, ...
└── dataset_index.csv   # file_id, size_bytes, total_access, S1 ... Sm
```

`dataset_index.csv` has one row per file, with its actual size in bytes, its total number of accesses and its number of accesses from each site.

At the end of the run, the script prints the size distribution obtained against the target distribution.

## Reproducibility

All random draws are controlled by `--seed` (default `42`). With the same parameters and the same NumPy version, the generated tables are identical from one run to another.

## Citation

If you use this code, please cite the article above.

## License

Released under the MIT License (see [`LICENSE`](LICENSE)).
