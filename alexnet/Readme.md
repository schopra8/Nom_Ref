# alexnet

We leverage a pretrained version of alexnet from (http://www.cs.toronto.edu/~guerzhoy/tf_alexnet/). In order to run Alexnet, you mustfirst download the trained alexnet weights via:
```
curl http://www.cs.toronto.edu/~guerzhoy/tf_alexnet/bvlc_alexnet.npy# --output bvlc_alexnet.npy

```

Once the weights are downloaded, initialize your sherlock environment by running the following commands to load the appropriate dependencies:
```
ml load python/2.7.5
module load tensorflow
module load py-scipy/0.17.0
```

### alexnet_output
This is a directoy of the output produced by alexnet, including top 10 labels, predicted labels, and embeddings for specified objects.

### default_imgs
This is a directory of the images that came with the pretrained Alexnet model. 

### analysis
This is a directory that contains analysis of the Alexnet classification of images from the Nominal Reference data.

### img_preprocess.py
Takes the images from nom_ref_iamges and resizes them appropriately for Alexnet.

### myalexnet_forward.py
Runs alexnet on the resized images from the Nominal Reference Game data. It outputs embeddings for the object and two csv files detailing the top 10 labels for each object.

### object_table.csv
Information about the objects used in the Nominal Reference Game data.


