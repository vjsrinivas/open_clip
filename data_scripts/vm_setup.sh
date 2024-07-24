#!/bin/bash
DATA_ROOT="/data/"
TRAIN_ROOT="/"

# hyperparameters
BATCH_SIZE=64
NUM_WORKERS=16
TRAIN_SAMPLES=2800000
EPOCHS=30

# Download ILSVRC2012 and reformat
mkdir $DATA_ROOT
cd $DATA_ROOT
wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar --no-check-certificate
tar -xf ILSVRC2012_img_val.tar
cd ILSVRC2012_img_val
wget https://raw.githubusercontent.com/soumith/imagenetloader.torch/master/valprep.sh
bash valprep.sh

# Setup project:
cd ${TRAIN_ROOT}
git clone https://github.com/vjsrinivas/open_clip.git
cd ${TRAIN_ROOT}open_clip

# Setup and download AWS credentials:
cd ${TRAIN_ROOT}open_clip/data_scripts
python3 grab_aws_data.py --cred_file aws_credentials.json --output ${DATA_ROOT}images

# Start training:
cd ${TRAIN_ROOT}open_clip/src
python ${TRAIN_ROOT}open_clip_train/main.py \
    --train-data "${DATA_ROOT}images/tars/{00000..00001}.tar" \
    --dataset-type webdataset \
    --train-num-samples $TRAIN_SAMPLES \
    --batch-size $BATCH_SIZE \
    --precision amp \
    --workers $NUM_WORKERS \
    --imagenet-val $DATASET_ROOT/ILSVRC2012_img_val \
    --zeroshot-frequency 2 \
    --val-frequency 2 \
    --model "RN50" \
    --epochs $EPOCHS \
    --hdf5-path "N/A" \
    --hdf5-meta-path "N/A" \
    --syn-text-file "N/A"
