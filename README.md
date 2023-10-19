# STSSL-MTS
An implementation of STSSL backbone on METRLA and PEMSBAY datasets.

# Preparation
For both datasets, please run the following code to get train/val/test data.
``` python
python generate_training_data.py --dataset=DATA
# DATA = {METRLA, PEMSBAY}
```

# Running
``` python
cd model
```
``` python
python traintest_GCRN.py --dataset=DATA GPU_DEVICE_ID
```
