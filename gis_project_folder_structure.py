# -*- coding: utf-8 -*-
"""
gis_project_folder_structure.py:
--------------------------------------------------------------------------------
This script creates the standard folder structure for the CAD/GIS Office at
CU Boulder GIS projects, it creates 10 empty folders and 1 logbook text file.
The folder_structure python list can be expanded to accomodate more file
extensions. The script only requires a standard python installation, no special
dependencies are required.
--------------------------------------------------------------------------------
"""
from __future__ import print_function
import os
import time


__author__ = 'Ulises  Guzman'
__date__ = '03/28/2016'
__credits__ = 'CAD/GIS Office at CU Boulder'


def simple_path_retriever(vpath):
    """ This helper function prompts the user for a path while checking if the
    string is valid.
    Args:
    vpath (string) = The raw_input function message.
    Returns:
    path (string) = A string representation of the folder,or geodatabase,
    location.
    Examples:
    >>> simple_path_retriever(
    'Please tell me where can I find your dwgs <path>?: ')
    Please tell me where can I find your dwgs <path>?:
    """
    path = raw_input('%s' % vpath)
    # checking if the information provided by the user is a valid path
    while not (os.path.exists(path)):
        path = raw_input('%s' % vpath)
    return path


def gis_folder_structure(folderpath):
    """
    This function creates the folder structure we use for our GIS projects,
    this is an ongoing effort to standardize our processes.
    Args:
    folderpath (string) = A string representation of the folder location.
    Returns:
    10 folders and 1 text file.
    Examples:
    >>> gis_folder_structure(folder)
    Hello, this will not take long
    Regards,
    J.
    Where would you like me to create your GIS project structure<path>?:
    """
    os.chdir(folderpath)
    folder_structure = ['_DOC', '_IMG', '_GDB', '_LYR', '_MXD',
                        '_PDF', '_SHP', '_XLSX', '_SCRIPTS', '_CAD']
    project_name = raw_input('Please enter the project name: ')
    p_author = raw_input('Please enter your initials: ').upper()
    project_name = project_name.upper()
    # making sure the project name starts with a string and not with a digit
    while not project_name[0].isalpha():
        project_name = raw_input('Please enter the project name: ')
    print(project_name)
    for ext in folder_structure:
        if not os.path.exists(project_name + ext):
            os.makedirs(project_name + ext)
    logbook = open(project_name + '_logbook.txt', 'w')
    # getting current time in 12 hour format
    current_time = time.strftime("%d/%m/%Y")
    logbook.write('Project name: %s\n' % project_name)
    logbook.write('Deliverables: \n')
    logbook.write('Date: %s\n' % current_time)
    logbook.write('Request by: \n')
    logbook.write('Assigned to: %s\n' % p_author)
    logbook.write(
        '***********************************************************\n')
    logbook.write('Comments: \n')
    print('The folder structure for you GIS project is ready!')


def main():
    print("""Hello, this will not take long
Regards,
J.""")
    folder = simple_path_retriever('Where would you like me to create'
                                   ' your GIS project structure<path>?: ')
    gis_folder_structure(folder)


if __name__ == "__main__":
    main()
