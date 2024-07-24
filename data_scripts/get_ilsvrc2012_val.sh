$WORKSPACE="/home/vijay/Documents/devmk6/TinierCLIP/cc_manipulation/tars"
cd $WORKSPACE

wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar --no-check-certificate
tar -xf ILSVRC2012_img_val.tar
cd ILSVRC2012_img_val
wget https://raw.githubusercontent.com/soumith/imagenetloader.torch/master/valprep.sh
bash valprep.sh