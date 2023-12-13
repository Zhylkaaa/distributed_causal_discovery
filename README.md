# Distributed causal discovery

## Requirements

This repository was run and tested with python 3.8 and 3.9, in case of any issues please open contact us by opening the issue on github.
To install dependencies run:
```bash
python -m pip install -r requirements.txt
```

## Data processing

To obtain data please first run:
```bash
bash scripts/download_data.sh
```

this should take a few seconds. After that you can run:
```bash
python preprcessing/preprocess_pems_data.py
```
Look into the source code to find how you can customize parameters of processing.
By default, script produces subsampled version of dataset with `20` nodes and applies non-overlapping sliding window of size `2` 

## Run experiments

To establish baseline results run:
```bash
time python run_baseline.py
```

In order to start distributed experiment on slurm cluster use:
```bash
sbatch launch_ray_job.sh data/gt_pems_graph_2_20.pkl <cpus for weak actor> <cpus for strong actor>
```
or locally with:
```bash
time PYTHONPATH=.:$PYTHONPATH python -u methods/constraint_based/pc.py data/gt_pems_graph_2_20.pkl <cpus for weak actor> <cpus for strong actor>
```
