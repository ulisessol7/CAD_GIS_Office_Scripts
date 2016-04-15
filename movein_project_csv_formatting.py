# -*- coding: utf-8 -*-
"""
movein_project_csv_formatting.py:
--------------------------------------------------------------------------------
This scripts translates the traffic volume counts, collected by CUPD & Parking
and Transportation Services, from excel files into feature classes. The
resulting feature classes will be stored in the provided PARK_MI.gdb
--------------------------------------------------------------------------------
"""
from __future__ import print_function
import os
import glob
import pandas as pd
import re
from num2words import num2words
import arcpy
from arcpy import env
env.overwriteOutput = True
env.qualifiedFieldNames = "UNQUALIFIED"

__author__ = 'Ulises  Guzman'
__date__ = '02/25/2016'
__credits__ = 'CAD/GIS Office at CU Boulder'

"""this dictionary was created manually due to data constraints.The name of
the keys have to exactly matched the excel volume data filename,
i.e 'j-100-15 Colorado - Folsom VOL.xls'. The spatial reference system is our
standard projection: NAD_1983_HARN_StatePlane_Colorado_North_FIPS_0501_Feet
"""
SENSORS_COORDINATES = {'j-100-15 Colorado - Folsom VOL.xls':
                       (3066000.14, 1245908.47),
                       'j-200-15 Regent - CU Event Center VOL.xls':
                       (3066631.619, 1244733.818),
                       'j-400-15 Euclid - Broadway VOL.xls':
                       (3064135.525, 1245083.861),
                       'j-500-15 18th St - Broadway VOL.xls':
                       (3064554.362, 1244679.781)}
"""'j-100-15 Colorado - Folsom VOL.xls',
 'j-200-15 Regent - CU Event Center VOL.xls',
 'j-400-15 Euclid - Broadway VOL.xls', 'j-500-15 18th St - Broadway VOL.xls'"""


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


def movein_dataparser():
    """
    This function iterates over a folder collecting only the files with
    extension xls that contains the keyword 'VOL'. The logic follows the
    naming conventions that are already in place for the CUPD sensor excel
    files.
    Args:

    Returns:
    Creates 4 feature classes , one per each sensor file.

    Examples:
    >>> movein_dataparser()
    Hello, I will parse the data for you
    Regards,
    J.
    Please enter a valid path for PARK_MI_XLSX:
    """
    # setting up the workspaces
    XLS_PATH = path_retriever('PARK_MI_XLSX')
    # this gdb was created in advance at the start of the project
    GDB_PATH = path_retriever('PARK_MI.gdb')
    os.chdir(XLS_PATH)
    env.workspace = GDB_PATH
    xls_list = glob.glob('*.xls')
    # print(xls_list)
    # getting the excel files for volume data
    volume_data_files = [xls for xls in xls_list if 'VOL' in xls]
    print("""
      Processing the following files:
      %s
      """ % volume_data_files)
    # reading the data in the excel files (xls, note the version of the
    # files)
    for vol_data in volume_data_files:
        xl = pd.ExcelFile(vol_data)
        # first sheet
        sheet = xl.sheet_names[0]
        df = xl.parse(sheet, skiprows=11)
        df.insert(5, 'DATE', 'x')
        # iterating over the rows in the current dataframe
        for index, row in df.iterrows():
            # arcgis online format m/d/yyyy h:mm
            # i.e. 8/16/2016  11:30:00 PM
            day = row['Unnamed: 1']
            hour = row['Unnamed: 2']
            # using a bit of regex to parse the data
            hour_pattern = '\w\w\s'
            hour_repla = hour[3:5] + ':00' + ' '
            parsed_hour_data = re.sub(hour_pattern, hour_repla, hour)
            # setting DATE to the new hour values
            df.loc[index, 'DATE'] = day + ' ' + parsed_hour_data
            # print(day, hour, parsed_hour_data)
        # preparing dataframe for arcmap by adding headers to the date
        df.rename(
            columns={'Unnamed: 0': 'OBJECTID', 'Unnamed: 1': 'DAY',
                     'Unnamed: 2': 'HOUR', 'Unnamed: 3': 'VOL_LEFTLANE',
                     'Unnamed: 4': 'VOL_RIGHTLANE'}, inplace=True)
        # highly dependent on naming convention:
        # 'j-100-15 Colorado - Folsom VOL.xls'
        fc_name = vol_data[9:-4].replace(' ', '').replace('-', '_')
        # transforming digits into words to follow arcmap feature classes
        # naming rules
        if fc_name[0].isdigit():
            pattern = re.search('\d\d|\d', fc_name)
            num = int(pattern.group(0))
            numword = num2words(num)
            fc_name = re.sub(str(num), numword, fc_name)
        # creating feature classes from data
        # harcoding our standard spatial reference
        # NAD_1983_HARN_StatePlane_Colorado_North_FIPS_0501_Feet
        # ESRI code: 2876
        sr = arcpy.SpatialReference(2876)
        # create point object from dictionay elements
        for k, v in SENSORS_COORDINATES.iteritems():
            if vol_data in k:
                # creating point geomtry object
                pt = arcpy.PointGeometry(arcpy.Point(
                    SENSORS_COORDINATES[k][0], SENSORS_COORDINATES[k][1]), sr)
        # creating empty feature class
        arcpy.CreateFeatureclass_management(env.workspace, fc_name,
                                            'POINT', '', '',
                                            '', sr)
        # adding necessary fields
        field_names = list(df.columns.values)
        field_names.remove('OBJECTID')
        field_names.insert(0, 'SHAPE@')
        # ['SHAPE@', 'DAY', 'HOUR', 'VOL_LEFTLANE', 'VOL_RIGHTLANE', 'DATE']
        '''change this part to make it explicit'''
        arcpy.AddField_management(fc_name, 'VOL_LEFTLANE', 'DOUBLE')
        arcpy.AddField_management(fc_name, 'VOL_RIGHTLANE', 'DOUBLE')
        arcpy.AddField_management(fc_name, 'DAY', 'TEXT')
        arcpy.AddField_management(fc_name, 'HOUR', 'TEXT')
        arcpy.AddField_management(fc_name, 'DATE', 'DATE')
        for pd_index, pd_row in df.iterrows():
            with arcpy.da.InsertCursor(fc_name, field_names) as cursor:
                # directly inserting geometry using the "SHAPE@" token
                cursor.insertRow((pt, pd_row[1], pd_row[2], pd_row[3],
                                  pd_row[4], pd_row[5]))
        print('%s feature class was successfully created' % fc_name)


def main():
    print("""Hello, I will parse the data for you
Regards,
J.""")
    movein_dataparser()

if __name__ == "__main__":
    main()
