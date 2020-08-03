#!/usr/bin/env python                                            
#
# subj2label ds ChRIS plugin app
#
# (c) 2016-2019 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#


import os
import sys
import shutil
from tqdm import tqdm
sys.path.append(os.path.dirname(__file__))

# import the Chris app superclass
from chrisapp.base import ChrisApp


Gstr_title = """

           _     _  _____  _       _          _ 
          | |   (_)/ __  \| |     | |        | |
 ___ _   _| |__  _ `' / /'| | __ _| |__   ___| |
/ __| | | | '_ \| |  / /  | |/ _` | '_ \ / _ \ |
\__ \ |_| | |_) | |./ /___| | (_| | |_) |  __/ |
|___/\__,_|_.__/| |\_____/|_|\__,_|_.__/ \___|_|
               _/ |                             
              |__/                              

"""

Gstr_synopsis = """

(Edit this in-line help for app specifics. At a minimum, the 
flags below are supported -- in the case of DS apps, both
positional arguments <inputDir> and <outputDir>; for FS apps
only <outputDir> -- and similarly for <in> <out> directories
where necessary.)

    NAME

       subj2label.py 

    SYNOPSIS

        python subj2label.py                                         \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir> 

    BRIEF EXAMPLE

        * Bare bones execution

            mkdir in out && chmod 777 out
            python subj2label.py   \\
                                in    out

    DESCRIPTION

        `subj2label.py` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.
        
        [--version]
        If specified, print version number and exit. 

"""


class Subj2label(ChrisApp):
    """
    An app to combine all image slices related to a particular label from different subjects under one directory.
    """
    AUTHORS                 = 'Sandip Samal (sandip.samal@childrens.harvard.edu)'
    SELFPATH                = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC                = os.path.basename(__file__)
    EXECSHELL               = 'python3'
    TITLE                   = 'A ChRIS plugin app'
    CATEGORY                = ''
    TYPE                    = 'ds'
    DESCRIPTION             = 'An app to combine all image slices related to a particular label from different subjects under one directory'
    DOCUMENTATION           = 'http://wiki'
    VERSION                 = '0.1'
    ICON                    = '' # url of an icon image
    LICENSE                 = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT           = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        
        self.add_argument('--refIn', dest='refIn', type=str,
                          optional=False, help='name of the folder containing raw image slices within the inputDir', default = "")
                          
        self.add_argument('--refOut', dest='refOut', type=str,
                          optional=True, help='name of the directory that will contain the raw data slices for a subject', default = "reference")
                          
        self.add_argument( '--featPref', dest='featPref', type=str,
                          optional=True, help='Prefix of the directory that contains the segmented data slices for a subject', default = "")  
        self.add_argument( '--featOut', dest='featOut', type=str,
                          optional=True, help='Name of the directory that will contain the segmented data slices for a subject', default = "features")                     

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        
        # All user input paths
        if options.refIn == "":
            print ("*** ERROR ***\n\n--refIn <Directory containing reference data slices> must be specified")
            exit()
        raw_data = options.refOut
        seg_data = options.featOut
        
        warnings = ""
        
        # Define the output path
        output_path = options.outputdir
        
        # Get a list of subjects present in inputdir
        subjects = os.listdir(options.inputdir)
        
        subj_count = len(subjects)
        
        
        # Get a list of labels available
        labels = os.listdir(options.inputdir + "/" + subjects[0])
        
        ## Remove folder containing raw data slices from labels
        if os.path.exists(options.inputdir + "/" + subjects[0] + "/"+options.refIn):
            labels.remove(options.refIn)
        
        label_count = len(labels)
        
        # Delete any existing data
        output_count = len(os.listdir(options.outputdir))
        if output_count!=0:
            print ("\n*** Deleting existing files ***")
            for folder in tqdm(os.listdir(options.outputdir)):
                shutil.rmtree(output_path+"/"+folder,ignore_errors=True)
                
        copy_count = 0
        # Create label wise folder containing label wise info from all subjects
        for label in labels:
            label_path = options.outputdir + "/" + label
            if not os.path.isdir(label_path):
                print ("\n\n\n### Creating %s ... ###" %label_path)
                os.mkdir(label_path)
            for subject in subjects:
                # path of a subject inside a label
                subject_in_label_path = label_path + "/" + subject
                if not os.path.isdir(subject_in_label_path):
                    print ("### Creating %s ... ###" %subject_in_label_path)
                    os.mkdir(subject_in_label_path)
                    os.mkdir(subject_in_label_path +"/%s" %raw_data)
                    os.mkdir(subject_in_label_path +"/%s" %seg_data)
                    
                # Now copy contents from src to destination
               
                target_path = options.inputdir + "/"+ subject+"/" + options.refIn
                if not os.path.exists(target_path):
                    print ("\n\n*** ERROR ***\n%s does not exist" %target_path)
                    exit()
                # Copy raw data slices from the target path to raw data dir
                shutil.copytree(target_path, subject_in_label_path+"/%s" %raw_data,dirs_exist_ok=True)
                src = options.inputdir + "/" + subject + "/" + label + "/"
                
                try:
                    shutil.copytree(src, subject_in_label_path+"/%s"%seg_data,dirs_exist_ok=True)
                    copy_count += 1
                    print ("### Copying files from %s to %s ... ###" %(src,subject_in_label_path+"/%s"%seg_data))
                except:
                    warnings = warnings + "\n Folder not found for %s in %s" %(label,subject)
                    shutil.rmtree(subject_in_label_path)
                
        print ("\n\n\n###################### SUMMARY #############################")
        print ("\n\n*** Total labels found : %s ***" %label_count)        
        print ("\n\n*** Total subjects found : %s ***" %subj_count ) 
        print ("\n\n*** Total folders copied : %s ***" %copy_count )
        print ("\n\n*** Feature slices are stored in %s directory of a subject ***" %seg_data)
        print ("\n\n*** Reference slices are stored in %s directory of a subject ***" %raw_data)
        if copy_count == label_count * subj_count:        
            print ("\n\n*** All files copied and sorted successfully ***")
        else:
            print("\n\n************ Warnings ***********")
            print (warnings)
        

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)


# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Subj2label()
    chris_app.launch()
