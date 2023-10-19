# STSSL-MTS
An implementation of STSSL backbone on METRLA and PEMSBAY datasets.

## Preparation
For both datasets, please run python generate_training_data.py --dataset=DATA to get train/val/test data.

## Running
### cd model
### python traintest_GCRN.py --dataset=DATA GPU_DEVICE_ID
### DATA = {METRLA, PEMSBAY}
