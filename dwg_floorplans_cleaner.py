# -*- coding: utf-8 -*-
"""
Jarvis drawing cleaner:
--------------------------------------------------------------------------------
This script...
--------------------------------------------------------------------------------
"""
from __future__ import print_function
import os
import glob
from win32com import client

__author__ = 'Ulises  Guzman'
__date__ = '04/08/2016'
__credits__ = 'CAD/GIS Office at CU Boulder'


def path_retriever(ws):
    """ This helper function prompts the user for a folder or a gdb name,
    the string will then be use to construct a valid path string.

    Args:
    ws (string) = The name of the folder or the gdb that contains the data

    Returns:
    path (string) = A string representation of the folder,or geodatabase,
    location.

    Examples:
    >>> path_retriever('Guzman_lab3')
    Please enter a valid path for Guzman_lab3:
    """
    path = raw_input('Please enter a valid path for'
                     ' %s : ' % ws)
    # checking if the information provided by the user is a valid path
    while not (os.path.exists(path) and path.endswith('%s' % ws)):
        path = raw_input('Please enter a valid path for the %s: ' % ws)
    return path


def dwgs_cleaner(folderpath):
    """
    """
    os.chdir(folderpath)
    dwg_list = glob.glob('*.dwg')
    folderpath = folderpath.replace('\\', '/')
    acad = client.Dispatch("AutoCAD.Application")
    acad.Visible = True
    doc = acad.ActiveDocument
    for dwg in dwg_list:
        floor_plan = folderpath + '/' + "%s" % dwg
        doc.SendCommand('(command "_.OPEN" "%s")\n' % floor_plan)
        # this lisp routine removes the layers' filters programatically
        # when used in hurricane, the "Model" tab in the drawings
        # gets hidden.
        doc.SendCommand('''(LOAD "Z:/ACAD/Lisp/dlf.lsp")\n''')
        doc.SendCommand("DLF\n")
        # this line runs the area graphic report.
        doc.SendCommand("-SREPORT AREA\n")
        # this lisp routine frezzes and thaws the drawing layers to leave it
        # a the desired state.
        doc.SendCommand(
            '''(LOAD "Z:/ACAD/Lisp/LAYERS-BLDG-FINAL-ULISES.lsp")\n''')
        # this lisp routine frezzes and thaws the drawing layers to leave it
        # a the desired state.
        doc.SendCommand(
            '''(LOAD "Z:/ACAD/Lisp/TRUEANNOALLVISIBLE.lsp")\n''')
        doc.SendCommand("TRUEANNOALLVISIBLE\n")
        doc.SendCommand('(command "-LAYOUT" "S" "11x17")\n')
        doc.SendCommand("PSPACE\n")
        doc.SendCommand("ZOOM EXTENTS\n")
        doc.SendCommand("QSAVE\n")
    doc.SendCommand("QUIT\n")
    print('The drawings are ready sir\n'
          'J.')
    return


def main():
    folder = raw_input('Please enter the folder name: ')
    dwgs_cleaner(path_retriever(folder))


if __name__ == "__main__":
    main()
