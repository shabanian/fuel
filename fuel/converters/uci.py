 
import gzip
import os
import struct
 
import h5py
import numpy as np
import tables
from fuel.converters.base import fill_hdf5_file, check_exists
from fuel.datasets.hdf5 import H5PYDataset
 
import argparse 
from fuel.downloaders.base import default_downloader
import io as mlio
 
 
Datasets = [ 'adult',
             'connect4',
             'dna',
             'mushrooms',
             'nips',
             'ocr_letters',
             'rcv1',
             'web']
             
FILENAME = [ 'a5a_{}.libsvm',
             'connect-4_{}.libsvm',
             'dna_scale_{}.libsvm',
             'mushrooms_{}.libsvm',
             'nips-0-12_all_shuffled_bidon_target_{}.amat',
             'ocr_letters_{}.txt',
             'rcv1_all_subset.binary_{}_voc_150.amat',
             'w6a_{}.libsvm']
             
FILEDirect = [ 'adult/',
             'connect-4/',
             'dna/',
             'mushrooms/',
             'nips-0-12/',
             '',
             'rcv1/',
             'web/']
             
FILESIZE = [(5000, 1414 ,26147,123), #train, valid,test, dim
	    (16000, 4000, 47557, 126), 
	    (1400, 600 ,1186,180),
	    (2000, 500, 5624, 112), 
	    (400,  100, 1240,500), 
	    (32152,10000, 10000,128), 
	    (40000, 10000, 150000, 150), 
	    (14000, 3188 ,32561, 300)]
	    
	    
def convert_uci ( directory, dataset ,    **kwargs):
 
    if dataset not in Datasets:
        raise ValueError("data_name must be one of " + Datasets)
    for i, data_name in enumerate(Datasets):
	if  dataset == Datasets[i]:
	    File_Name = FILENAME[i]
	    File_Directory = FILEDirect[i] + File_Name
	    File_Size = FILESIZE[i]
    
    sets = ['train', 'valid', 'test']
    for s in sets:
      	 
	check_exists(required_files= [File_Name.format(s)]) 

	
    File_PathS= [os.path.join(directory,  File_Name.format(s))   for s in sets]
 
 
 
 
    targets = set([0,1])
    target_mapping = {'-1':0,'+1':1}
    def convert_target(target):
        return target_mapping[target]

    def load_line(line):
        return mlio.libsvm_load_line(line,convert_target=convert_target,sparse=False,input_size=File_Size[3])
 
 
    train_load = mlio.load_from_file(File_PathS[0],load_line)
    valid_load = mlio.load_from_file(File_PathS[1],load_line)
    test_load = mlio.load_from_file(File_PathS[2],load_line)
 
    train_set = mlio.MemoryDataset(train_load,[(File_Size[3],),(1,)],['uint8',int],File_Size[0]).mem_data [0] 
    valid_set = mlio.MemoryDataset(valid_load,[(File_Size[3],),(1,)],['uint8',int],File_Size[1]).mem_data [0]  
    test_set = mlio.MemoryDataset(test_load,[(File_Size[3],),(1,)],['uint8',int],File_Size[2]).mem_data [0]
 
 
 
  
    data = (('train', 'features', train_set),
	    ('valid', 'features', valid_set),
	    ('test', 'features', test_set))
    h5file = h5py.File( os.path.join(directory, dataset) + ".hdf5", mode='w')
    fill_hdf5_file(h5file, data)
    for i, label in enumerate(('batch',  'length')):
	h5file['features'].dims[i].label = label

    h5file.flush()
    h5file.close()
 


def fill_subparser(subparser):
    """Sets up a subparser to download the UCI dataset files.
    The following UCI dataset files can be downloaded
    from http://www.cs.toronto.edu/~larocheh/public/datasets/
    Parameters
    ----------
    subparser : :class:`argparse.ArgumentParser`
        Subparser handling the `uci` command.
    """
    subparser.add_argument(
        "dataset", type = str, choices = Datasets,
        help="Name of dataset")
  
    subparser.set_defaults( func= convert_uci  )

 