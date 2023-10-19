# STSSL-MTS
An implementation of STSSL backbone on METRLA and PEMSBAY datasets.
DATA = {METRLA, PEMSBAY}

# Preparation
For both datasets, please run python generate_training_data.py --dataset=DATA to get train/val/test data.

# Running
``` python
cd model
```
``` python
python traintest_GCRN.py --dataset=DATA GPU_DEVICE_ID
```
