import os.path
import click
import subprocess
import yolo_setup
import dataset_functions
import train_test
import edge_detection

DEFAULT_TRAIN_PERCENTAGE = 70

@click.group()
def cli():
    pass

@cli.command()
@click.option('--gpu/--cpu', default=True, help='Flag to build YOLO to either use the GPU or CPU, GPU if not specified')
@click.option('--cuda-path', default=False, help='Specify the path to CUDA, default is /usr/local/cuda-9.0/')
@click.option('--omit-weight-file', is_flag=True, default=False, help='Flag to omit downloading the pretrained convolutional weight file')
def setup(gpu, cuda_path, omit_weight_file):
    '''Automatically download, configure, and build YOLO to the yolo/ directory.'''

    yolo_setup.download()

    if cuda_path:
        yolo_setup.configure(enable_gpu=gpu, cuda_path=cuda_path)
    else:
        yolo_setup.configure(enable_gpu=gpu)

    yolo_setup.install()

    if not omit_weight_file:
        yolo_setup.downloadConvolutionalWeights()

    print('YOLO has been setup successfully')

@cli.command()
def datasets():
    '''List the properly setup datasets within the datasets/ directory.'''

    if not dataset_functions.datasetDirExists():
        print('The datasets/ directory does not exist')
        return
    else:
        datasets = dataset_functions.getDatasets()

        if not datasets:
            print('There are no datasets within the datasets/ directory')
            return
        else:
            for dataset in datasets:
                print(dataset)

@cli.command()
@click.argument('dataset')
def dataset(dataset):
    '''View information about a specific dataset.'''

    dataset_obj = dataset_functions.getDataset(dataset)

    if not dataset_obj:
        print("Dataset '" + dataset + "' does not exist or is not configured properly")
        return
    else:
        for class_folder in dataset_obj:
            print("Object class folder '" + class_folder[0] + "' contains " + str(class_folder[1]) + " images and " + str(class_folder[2]) + " bounds files.")

@cli.command()
@click.argument('dataset')
@click.option('--train-percentage', type=int, default=DEFAULT_TRAIN_PERCENTAGE, help='Specify the percentage of dataset to use for training, default first 70% of each (automatically) sorted classification group. Remaining percentage should be used for testing.')
@click.option('--config-file', default=False, help='Specify path of custom YOLO configuration file (relative to yolo/ directory) to override the automatically generated file')
@click.option('--max-iterations', default=False, help='Specify max number of iterations to train to, default 2000 per number of classes')
def train(dataset, train_percentage, config_file, max_iterations):
    '''Train an image classifier with the given image dataset.'''

    dataset_obj = dataset_functions.getDataset(dataset)

    if not dataset_obj:
        print("Dataset '" + dataset + "' does not exist or is not configured properly")
        return
    elif not yolo_setup.yoloSetup():
        print("YOLO has not been setup correctly yet, run the setup command to do so")
        return
    elif not yolo_setup.convolutionalWeightFileDownloaded():
        print("Pretrained convolutional weight file is missing, rerun the setup subcommand to download")
    else:
        data_file_location = train_test.generateDataFile(dataset, train_percentage)

        if not config_file:
            if max_iterations:
                config_file = train_test.generateConfigFile(dataset, True, max_iterations)
            else:
                config_file = train_test.generateConfigFile(dataset, True)

        p = subprocess.Popen(['./darknet', 'detector', 'train', data_file_location, config_file, 'darknet53.conv.74'], cwd='yolo')
        p.wait()

@cli.command()
@click.argument('image-classifier')
@click.argument('dataset')
@click.option('--test-percentage', type=int, default=100-DEFAULT_TRAIN_PERCENTAGE, help='Specify the percentage of dataset to use for testing, default last 30% of each (automatically) sorted classification group.')
@click.option('--config-file', default=False, help='Specify path of custom YOLO configuration file (relative to yolo/ directory) to override the automatically generated file')
def test(image_classifier, dataset, test_percentage, config_file):
    '''Test an image classifier on the given image dataset.'''

    dataset_obj = dataset_functions.getDataset(dataset)

    if not dataset_obj:
        print("Dataset '" + dataset + "' does not exist or is not configured properly")
        return
    elif not yolo_setup.yoloSetup():
        print("YOLO has not been setup correctly yet, run the setup command to do so")
        return
    elif not os.path.isfile('yolo/' + image_classifier) :
        print("Could not find image classifier. Ensure file path is relative to the yolo/ directory.")
    else:
        data_file_location = train_test.generateDataFile(dataset, 100 - test_percentage)

        if not config_file:
            config_file = train_test.generateConfigFile(dataset, False)

        p = subprocess.Popen(['./darknet', 'detector', 'recall', data_file_location, config_file, image_classifier], cwd='yolo')
        p.wait()

@cli.command()
@click.argument('dataset')
@click.argument('feature-extraction-method')
def apply_feature_extraction(dataset, feature_extraction_method):
    """Apply a method of feature extraction to the given image dataset, possible values are 'edw' & 'edb'."""
    
    dataset_obj = dataset_functions.getDataset(dataset)

    if not dataset_obj:
        print("Dataset '" + dataset + "' does not exist or is not configured properly")
        return
    elif feature_extraction_method.lower() not in ['edw', 'edb']:
        print("Unknown method of feature extraction. Possible values are 'edw' & 'edb'.")
        return
    else:
        if feature_extraction_method.lower() == 'edw':
            edge_detection.edgeDetection(dataset, 'white')
            print("Edge detection (white border) applied to new dataset '" + dataset + "-edw' successfully")
        elif feature_extraction_method.lower() == 'edb':
            edge_detection.edgeDetection(dataset, 'black')
            print("Edge detection (black border) applied to new dataset '" + dataset + "-edb' successfully")