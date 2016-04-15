# -*- coding: utf-8 -*-
"""
dwg_floorplans_cleaner.py:
--------------------------------------------------------------------------------
This script was developed to automate part of the CAD/GIS Office at CU Boulder
CAD standardization process. The office's current CAD standards can be found at
http://www.colorado.edu/fm/planning-design-construction/cad-document-management
--------------------------------------------------------------------------------
"""
from __future__ import print_function
import os
import glob
from win32com import client

__author__ = 'Ulises  Guzman'
__date__ = '04/08/2016'
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


def dwgs_cleaner(folderpath):
    """
    This function was developed as an alternative to Hurricane for AutoCAD
    because some lisp routines do not work well in Hurricane. The function
    removes all layer filters, runs an AREA graphic report, set up the layers'
    visibility according to our current CAD standards, turns on ANNOALLVISIBLE
    for the whole drawing (including layouts) and finally save the drawing with
    appropiate extents. In some cases when the function is completed an
    Autodesk error appears on screen, if this happens, just ignore it.
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
        # this lisp routine removes the layers' filters programatically,
        # when used in Hurricane for AutoCAD, the "Model" tab in the drawings
        # gets hidden.
        doc.SendCommand('''(LOAD "Z:/ACAD/Lisp/dlf.lsp")\n''')
        doc.SendCommand("DLF\n")
        # this line runs the area graphic report.
        doc.SendCommand("-SREPORT AREA\n")
        # this lisp routine frezzes and thaws the drawing's layers to leave it
        # at the desired state.
        doc.SendCommand(
            '''(LOAD "Z:/ACAD/Lisp/LAYERS-BLDG-FINAL-ULISES.lsp")\n''')
        # this lisp routine frezzes and thaws the drawing layers to leave it
        # a the desired state.
        doc.SendCommand(
            '''(LOAD "Z:/ACAD/Lisp/TRUEANNOALLVISIBLE.lsp")\n''')
        doc.SendCommand("TRUEANNOALLVISIBLE\n")
        # the following lines make sure that the drawing gets save with
        # the appropiate extents.
        doc.SendCommand('(command "-LAYOUT" "S" "11x17")\n')
        doc.SendCommand("PSPACE\n")
        doc.SendCommand("ZOOM EXTENTS\n")
        doc.SendCommand("QSAVE\n")
    doc.SendCommand("QUIT\n")
    print('All drawings have been standardized!')
    return


def main():
    print("""Relax while I take care of the boring stuff
Regards,
J.""")
    folder = simple_path_retriever(
        'Please tell me where can I find your dwgs <path>?: ')
    dwgs_cleaner(folder)

if __name__ == "__main__":
    main()
