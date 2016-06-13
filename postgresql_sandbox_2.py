# -*- coding: utf-8 -*-
"""
Name:       TBD
Author:     Ulises  Guzman
Created:    05/04/2016
Copyright:   (c)
ArcGIS Version:   10.3.1
Python Version:   2.7.8
PostgreSQL Version: 9.4
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
"""
from __future__ import print_function
import os
from subprocess import call
import glob
import re
import inspect
import StringIO
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import arcpy


def path_retriever(ws):
    """ This helper function prompts the user for a folder or a gdb name,
    the string will then be use to construct a valid path string.

    Args:
    ws (string) = The name of the folder or the gdb that contains the data

    Returns:
    path (string) = A string representation of the folder,or geodb,
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


def employees_to_postgresql(db, user, password, workspace=os.getcwd()):
    """
    ...
    """
    original_workspace = os.getcwd()
    os.chdir(workspace)
    # grabbing the latest excel file in directory, in certain os max
    # must be changed to min
    excel_file = max(glob.glob('*.xlsx'), key=os.path.getctime)
    xl = pd.ExcelFile(excel_file)
    sheet = xl.sheet_names[0]
    # this is done because the source file contains an extra row
    df = xl.parse(sheet, skiprows=1)
    # print(df)
    # formatting column names to make them compatible with ArcMap
    df.rename(columns=lambda x: x.lower(), inplace=True)
    df.rename(columns=lambda x: x.replace('/', '_'), inplace=True)
    df.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)
    df.insert(12, 'normalize_addr', 'x')
    for index, row in df.iterrows():
        try:
            street = str(df.loc[index, 'address_1']).decode('UTF-8')
            city = str(df.loc[index, 'city']).decode('UTF-8')
            state = str(df.loc[index, 'state']).decode('UTF-8')
            zipcode = str(df.loc[index, 'postal']).decode('UTF-8')
            # print (type(street), type(city), type(state), type(zipcode))
            normalize_addr = '{}, {} {} {}'.format(
                street, city, state, zipcode)
            df.loc[index, 'normalize_addr'] = normalize_addr
        except Exception as e:
            print(street, city, state, zipcode)
            print(e)
            """authenticating to the PostgreSQL db by using a URI
    (Uniform Resource Identifier). This is done to avoid the password
    prompt in the cmd window.
    """
    target_db = 'postgresql://{}:{}@localhost/{}'.format(
        user, password, db)
    engine = create_engine(target_db)
    # removing file extension
    table_name = excel_file[:-5]
    # writing pandas dataframe to PostgreSQL table
    df.to_sql(name=table_name, con=engine, if_exists='replace')
    os.chdir(original_workspace)
    return


def load_shps_to_postgresql(db, user, password,
                            host='localhost', schema='public',
                            postg_vers='9.4', srid='26913',
                            shp_loc=os.getcwd()):
    """
    ...
    """
    # getting the name of the function programatically.
    print('Executing {}... '.format(inspect.currentframe().f_code.co_name))
    os.chdir(shp_loc)
    shp_list = glob.glob('*.shp')
    shp2pgsql = "C:\Program Files\PostgreSQL\{0}\\bin\shp2pgsql.exe".format(
        postg_vers)
    psql = "C:\Program Files\PostgreSQL\{0}\\bin\psql.exe".format(
        postg_vers)
    """authenticating to the PostgreSQL db by using a URI
    (Uniform Resource Identifier).
    """
    postgresql_uri = "postgresql://{0}:{1}@{2}/{3}".format(user, password,
                                                           host, db)
    for shp in shp_list:
        """this line works even though the psql and PostgreSQL windows
        enviromental variables are not set.
        """
        shp_full_path = '{0}\{1}'.format(shp_loc, shp)
        """ the cmd postgis syntax for importing shps to PostgreSQL is as
        follows:
        shp2pgsql -s 4326 -d neighborhoods public.neighborhoods |
        psql -h myserver -d mydb -U myuser
        """
        # the call to executables inside the cmd should be double quoted
        command = '''"{0}" -s {1} -d {2} {3}.{4} | "{5}" "{6}"'''.format(
            shp2pgsql, srid, shp_full_path, schema, shp[:-4], psql,
            postgresql_uri)
        # this part sends the command to the windows command prompt (cmd)
        call(command, shell=True)
    return


def run_sql_on_db(db, user, password, sql_script_loc=os.getcwd()):
    """
    ...
    """
    """authenticating to the PostgreSQL db by using a URI
    (Uniform Resource Identifier).
    """
    # getting the name of the function programatically.
    print('Executing {}... '.format(inspect.currentframe().f_code.co_name))
    target_db = 'postgresql://{}:{}@localhost/{}'.format(
        user, password, db)
    engine = create_engine(target_db)
    sql_script = StringIO.StringIO()
    # removing comments from SQL code ('--')
    with open(sql_script_loc, 'r') as sql:
        for line in sql:
            if not line.startswith('-'):
                sql_script.write(line)
    sql_commands = sql_script.getvalue()
    # all SQL commands (split on ';')
    sql_commands = sql_commands.split(';')
    with engine.connect() as con:
        for command in sql_commands:
            if command not in ('', '\n', '\n\n'):
                try:
                    con.execute(text(command))
                    print('{} was successfully executed'.format(command))
                except Exception as e:
                    print(e)
    return


def rename_layers_in_mxd(mxd_loc, pattern, ind_result=-1):
    """
    ...
    """
    # getting the name of the function programatically.
    print('Executing {}... '.format(inspect.currentframe().f_code.co_name))
    mxd = arcpy.mapping.MapDocument(mxd_loc)
    lyrs = arcpy.mapping.ListLayers(mxd)
    for lyr in lyrs:
        lyr.name = re.split(pattern, lyr.name)[ind_result]
        print(lyr.name)
    mxd.save()
    return


def apply_symbology_to_lyr(mxd_loc, lyrs_loc):
    """
    ...
    """
    # getting the name of the function programatically.
    print('Executing {}... '.format(inspect.currentframe().f_code.co_name))
    original_workspace = os.getcwd()
    os.chdir(lyrs_loc)
    lyrs_symb = glob.glob('*.lyr')
    # print(lyrs_symb)
    os.chdir(original_workspace)
    mxd = arcpy.mapping.MapDocument(mxd_loc)
    lyrs = arcpy.mapping.ListLayers(mxd)
    for lyr in lyrs:
        if lyr.name + '.lyr' in lyrs_symb:
            try:
                arcpy.ApplySymbologyFromLayer_management(
                    lyr, lyrs_loc + '/' + lyr.name + '.lyr')
            except Exception as e:
                print(e)
    mxd.save()
    return


if __name__ == '__main__':
    # ws = path_retriever('cu_employees_data')
    # user = raw_input()
    # password = raw_input()
    db = 'postgis_22_sample'
    user = 'postgres'
    password = 'CAD123456'
    ws = 'E:/Users/ulgu3559/Desktop/cu_employees_data'
    employees_to_postgresql(db, user, password, ws)
    shp_loc = 'E:\Users\ulgu3559\Desktop\GIS_projects\CU_ED_SHP'
    load_shps_to_postgresql(db, user, password, shp_loc=shp_loc)
    ed_format = 'E:\Users\ulgu3559\Desktop\GIS_projects\CU_ED_SQL' \
        '\cu_employees_data_formatting.sql'
    # running tiger geocoder
    run_sql_on_db(db, user, password, sql_script_loc=ed_format)
    ed_map_lyr = 'E:\Users\ulgu3559\Desktop\GIS_projects\CU_ED_SQL' \
        '\cu_ed_map_layers.sql'
    # running buffers
    run_sql_on_db(db, user, password, sql_script_loc=ed_map_lyr)
    mxd_loc = 'E:/Users/ulgu3559/Desktop/GIS_projects/CU_ED_MXD/' \
        'sustainable_transportation_webmap.mxd'
    # rename_layers_in_mxd(mxd_loc, '\.')
    # lyrs_loc = 'E:/Users/ulgu3559/Desktop/GIS_projects/CU_ED_LYR'
    # apply_symbology_to_lyr(mxd_loc, lyrs_loc)
