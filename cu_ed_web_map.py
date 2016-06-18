# -*- coding: utf-8 -*-
"""
Name:       cu_ed_web_map.py
Author:     Ulises  Guzman
Created:    06/18/2016
Copyright:   (c)
ArcGIS Version:   10.4
Python Version:   2.7.8
PostgreSQL Version: 9.4
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
"""
from __future__ import print_function
import os
from subprocess import call
import glob
import ast
import inspect
import StringIO
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import arcpy


def employees_to_postgresql(db, user, password, workspace=os.getcwd()):
    """
    ...
    """
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
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
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
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
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
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


def sdd_drafter(mxd_loc, out_loc, portal='MY_HOSTED_SERVICES'):
    """
    ...
    """
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    map_document = arcpy.mapping.MapDocument(mxd_loc)
    service_name = os.path.basename(mxd_loc)[:-4]
    sddraft = '{}/{}.sddraft'.format(out_loc, service_name)
    try:
        sd_obj = arcpy.mapping.CreateMapSDDraft(
            map_document, sddraft, service_name, portal)
        print('{} completed successfully'. format(func_name))
    except Exception as e:
        print(e.args[0])
        print(arcpy.GetMessages())
    return sd_obj


def agol_publisher(sdd, out_name, groups, sd_out_loc=os.getcwd(),
                   portal='MY_HOSTED_SERVICES'):
    """
    """
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    try:
        sd = '{}/{}.sd'.format(out_name, sd_out_loc)
        arcpy.StageService_server(sdd, sd)
        arcpy.UploadServiceDefinition_server(sd, portal)
        print('{} completed successfully'. format(func_name))
    except Exception as e:
        print(e.args[0])
        print(arcpy.GetMessages())
    return

if __name__ == '__main__':
    credentials = 'C:/Users/ulisesdario/Desktop/GIS_projects/credentials.txt'
    with open(credentials, 'r') as c:
        for line in c:
            # print(line)
            login_dict = ast.literal_eval(line)
            print(type(login_dict), login_dict)
    db_name = login_dict['dbname']
    db_user = login_dict['dbuser']
    db_password = login_dict['dbpassword']
    ws = 'E:/Users/ulgu3559/Desktop/cu_employees_data'
    employees_to_postgresql(db_name, db_user, db_password, ws)
    shp_loc = 'E:\Users\ulgu3559\Desktop\GIS_projects\CU_ED_SHP'
    load_shps_to_postgresql(db_name, db_user, db_password, shp_loc=shp_loc)
    # path to the sql script that prepares the database
    ed_format = 'E:\Users\ulgu3559\Desktop\GIS_projects\CU_ED_SQL' \
        '\cu_employees_data_formatting.sql'
    # running tiger geocoder
    run_sql_on_db(db_name, db_user, db_password, sql_script_loc=ed_format)
    # path to the sql script that creates the analysis
    ed_map_lyr = 'E:\Users\ulgu3559\Desktop\GIS_projects\CU_ED_SQL' \
        '\cu_ed_map_layers.sql'
    # running buffers
    run_sql_on_db(db_name, db_user, db_password, sql_script_loc=ed_map_lyr)
    # path to the mxd file that serves as
    mxd_loc = 'E:/Users/ulgu3559/Desktop/GIS_projects/CU_ED_MXD/' \
        'sustainable_transportation_webmap.mxd'
    # location for the sdd (draft) file
    sdd_outloc = ''
    sd_out_loc = ''
    # this function defaults to 'MY_HOSTED_SERVICES'
    sdd = sdd_drafter(mxd_loc, sdd_outloc)
    agol_user = login_dict['agoluser']
    agol_password = login_dict['agolpassword']
    # this function defaults to 'MY_HOSTED_SERVICES'
    agol_publisher(sdd, 'test', 'group', sd_out_loc)
