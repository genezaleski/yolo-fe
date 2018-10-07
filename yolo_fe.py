import click
from configure_gpu import configure_gpu

@click.group()
def cli():
    pass

@cli.command()
def setup():
    '''Automatically downloads and sets up YOLO in the current directory'''

    # Run script to automatically download and setup YOLO

    configure_gpu()

    print('YOLO has been setup successfully')