# yolo-fe
Command line tool for interfacing with the YOLO system and applying different methods of feature extraction to image datasets. This tool is made specifically to be ran on a computer running Ubuntu 16.04 with a CUDA enabled GPU (with appropriate drivers + CUDA installed).

## Installation
This tool requires Python3 and the Python `setuptools` module which can be found [here](https://pypi.org/project/setuptools/).
1. Run `git clone https://github.com/pricheal/yolo-fe.git`
2. Inside repository, run `pip install --editable .`
3. If you plan to utilize the GPU, use the `ubuntu_cuda_gpu_driver_install.sh` file to download and and install the proper drivers for the GPU and CUDA. After that is complete, ensure that CUDA is in the system path. This can be done temporarily for the current terminal session with `export PATH="/usr/local/cuda-9.0/bin/:$PATH"` (change PATH value if needed).
4. Run `yolo-fe` to use command line tool

## Usage
The command line tool is accessed with `yolo-fe`. Running `yolo-fe --help` will display the various subcommands that can be ran. Running `yolo-fe subcommand --help` will display more information for that particular subcommand.

### 1. Initial setup
Before any other commands that utilize YOLO can be ran, YOLO must be downloaded, installed, and built. To do this, run `yolo-fe setup`. By default, this will build YOLO to use the computers GPU. If you want to build YOLO to use the computers CPU, run `yolo-fe setup --cpu` instead. The tool assumes the CUDA path is `/usr/local/cuda-9.0/` but this can also be overwritten with the `--cuda-path` option. Running the setup command will also automatically download the pretrained convolutional weight file, but this can be ommited with the `--omit-weight-file` flag.

### 2. Loading a dataset
The next step that needs to be done is to load a dataset into the datasets/ directory. The structure of a dataset is described below but can also be seen by looking at the `test-dataset` that already exists within the datasets/ directory.

#### What is a dataset
A dataset is simply a folder that sits within the datasets/ directory. The name of the dataset is the name of the folder. A dataset folder should contain a .names file that is named the same as the dataset (so if the dataset is named dataset1, the .names file should be dataset1.names), and a folder for each object class within the dataset (so if the dataset contained images of cats and dogs, the .names file should contain one line with the string dog and another with the string cat, and there should be a dog folder and a cat folder within the dataset folder). The point of separating the images of different object classes into folders is so the tool can select an even distribution of images from each object class when training and testing.

#### What should be in the folder for each object class
Within each folder for the object classes (cats, dogs) should be all of the image files with a corresponding bounds text file that is named the same as the image. Each bounds file should have a line with the following format for each boundary within the image.
```
<class number> <center x> <center y> <width> <height>
```
Class number is `line number - 1` (line number is the line number of where that object appears in the .names file, so the first line in the .names file would have a class number of 0), and center x, center y, width, and height are all a decimal number 0 to 1 that is relative to the image's width and height.

#### Checking to see if it was loaded correctly
Once the dataset is loaded, you can run the command `yolo-fe datasets` to see the loaded datasets. If the dataset is not loaded correctly (e.g. the .names file is missing), the dataset will not be listed. If the dataset does appear, then the command `yolo-fe dataset DATASET` can be ran to view more information about that specific dataset.

### 3. Training an image classifier
Now that YOLO is setup correctly and a dataset has been loaded into the correct location, an image classifier can be trained. To do so, run `yolo-fe train DATASET` where DATASET is the name of the dataset you wish to train off of. This will automatically train the image classifier with an even percentage of images from each class folder within the dataset. The default percentage is 70%, but this can be overridden with the `--train-percentage` option which accepts a number 1-100. For training, all of the images in each folder are sorted and then the first X percentage is taken for training. This is to ensure that separate images are used for training and testing, as the test subcommand uses the last X percentage.

A configuration file for YOLO is automatically generated and used for training, which is based off of a default training file that has some slight modifications based off of the number of classes that are being trained. To see these exact changes, you can look at the `train_test.py` file in the `generateConfigFile()` method.

By default, the training will stop after `2000 * <# of classes>` iterations, but this can be overridden with the `--max-iterations` option.

### 4. Applying feature extraction to a dataset
Now that an image classifier has been trained on an unmodified dataset, you will likely want to train another image classifier on a modified image dataset. To do so, feature extraction has to be applied to a copy of an entire dataset. To do this, use the `apply-feature-extraction` subcommand. The first argument for this subcommand is the dataset to create a copy of, and the second argument is the feature extraction method to use. The current supported methods of feature extraction are 'edw' (edge detection white border) and 'edb' (edge detection black border). So to apply white border edge detection to the test dataset, the command would be `yolo-fe apply-feature-extraction test-dataset edw`. This would create a copy of the test dataset named `test-dataset-edw` that has white border edge detection applied to each image.

### 5. Testing an image classifier
Now that datasets can have feature extraction applied, multiple image classifiers can be trained on those different datasets. To compare the accuracy of each of those image classifiers, run `yolo-fe test IMAGE_CLASSIFIER DATASET` where IMAGE_CLASSIFIER is the file path of the desired .weights file to test (relative to the yolo/ directory) and DATASET is the name of the dataset to test on (should be the same as the dataset you trained the image classifier on). This will automatically test the image classifier using the testing portion of the image dataset, which by default is the last 30% of each sorted image class's files. To override that amount, use the `--test-percentage` option, but ensure that the value is the remainder of whatever percentage was used for training.

## Cloud instance used for testing

This tool was tested using a Google Cloud instance with the following specifications.
* Region: us-east4
* Machine type: 1vCPU, 3.75 GB memory
* GPU: 1 NVIDIA Tesla P4
* Boot disk: 20GB standard persistent, Ubuntu 16.04 LTS

## Image datasets

The image datasets that we put together can be downloaded [here](https://drive.google.com/open?id=1McvTglcqOl33WleuzrR6c4vz4t3YOwCi).

### Downloading image datasets onto Ubuntu
* Download the google drive file with this python script: https://stackoverflow.com/a/39225039
* Install the unzip tool and unzip the downloaded zip file

### Useful links
* [YOLO](https://pjreddie.com/darknet/yolo/)
* [darknet](https://github.com/pjreddie/darknet)
* [How to train to detect custom objects](https://github.com/AlexeyAB/darknet#how-to-train-to-detect-your-custom-objects)
