# -*- coding: utf-8 -*-
"""
Name:       cu_ed_web_map.py
Author:     Ulises  Guzman
Created:    06/20/2016
Copyright:   (c) CU Boulder GIS Office
ArcGIS Version:   10.4
Python Version:   2.7.8
PostgreSQL Version: 9.4
--------------------------------------------------------------------------------
This script  creates and publishes  a web map for the Sustainable
Transportation Group to CU's ArcGIS Online Organization account. It manipulates
data from excel and  creates query layers by utilizing PosgreSQL & PostGIS.This
approach allow us to update the feature service programmatically.
The goal of this resource is to aid the outreach efforts of the Sustainable
TRansportation Group.
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


def employees_to_postgresql(db, user, password, host='localhost',
                            schema='public', cu_ed_loc=os.getcwd()):
    """ This function grabs the employee data provided by the sustainable
    transportation group (excel file) and import it into a PostgreSQL
    database. The format of the excel file was previously agreed on.

    Args:
    db (string) = A string that represents the name of the target PostgreSQL
    database.
    user (string) = A string that represents the user name of the target
    PostgreSQL database.
    password (string) = A string that represents the corresponding user
    password.
    host (string) (default = 'localhost') = A string that represents this
    represents the port where
    PosgreSQL service was instantiated.
    schema (string) (default = 'public') = A string that represents the name of
     the target PostgreSQL
    schema.
    cu_ed_loc (string) = The path for the folder that contains the cu employees
    data information (excel files).

    Examples:
    >>> employees_to_postgresql(db_name, db_user, db_password, cu_ed_loc)
    Executing employees_to_postgresql...
    employees_to_postgresql was successfully executed
    """
    # getting the name of the function programmatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    original_workspace = os.getcwd()
    os.chdir(cu_ed_loc)
    # grabbing the latest excel file in directory, in certain os, max
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
    print('{} was successfully executed'.format(func_name))
    return


def load_shps_to_postgresql(db, user, password,
                            host='localhost', schema='public',
                            postg_vers='9.4', srid='26913',
                            shp_loc=os.getcwd()):
    """ This function reads the shapefiles in a folder and programmatically
    import them into a spatially enabled database . A PostGIS PostgreSQL
    database is required for the function to properly work.

    Args:
    db (string) = A string that represents the name of the target
    PostgreSQL database.
    user (string) = A string that represents the user name of the target
    PostgreSQL database.
    password (string) = A string that represents the corresponding user
    password.
    host (string) (default = 'localhost') = A string that represents this
    represents the port where
    PosgreSQL service was instantiated.
    schema (string) (default = 'public') = A string that represents the name of
     the target PostgreSQL
    schema.
    postg_vers (string) (default = '9.4') = A string that represents the
    PosgreSQL flavor (version).
    This argument defaults to 9.4 because this is the one that is supported by
    the latest ArcGIS version (10.4).
    srid (string) (default = '26913') = A string that represents the Spatial
    Reference System Identifier
    (SRID) number. 26913 is the number for NAD83 / UTM zone 13N.
    shp_loc (string) (default = os.getcwd()) = A string that represents the
    path for the folder that contains the shapefiles that are going to be
    imported into the PostgreSQL database. It defaults to the current python
    directory.

    Examples:
    >>> load_shps_to_postgresql(db_name, db_user, db_password, cu_ed_loc)
    Executing load_shps_to_postgresql...
    load_shps_to_postgresql was successfully executed
    """
    # getting the name of the function programmatically.
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
    print('{} was successfully executed'.format(func_name))
    return


def run_sql_on_db(db, user, password, sql_script_loc, host='localhost',
                  schema='public'):
    """ This function executes SQL scripts against a  PostgreSQL database, the
    function can handle comments of the type '--' and multiline SQL statements.

    Args:
    db (string) = A string that represents the name of the target PostgreSQL
    database.
    user (string) = A string that represents the user name for the target
    PostgreSQL database.
    password (string) = A string that represents the corresponding user
    password.
    sql_script_loc (string) = A string that represents path and file name for
    the SQL script that is going to be executed.
    host (string) (default = 'localhost') = A string that represents the port
    where the PosgreSQL service was instantiated.
    schema (string) (default = 'public') = A string that represents the name of
    the target PostgreSQL schema.

    Examples:
    >>> run_sql_on_db(db_name, db_user, db_password,ed_format)
    Executing run_sql_on_db...
    SET SEARCH PATH public, tiger, tiger.data was successfully executed
    SELECT * FROM cu_employees_data WHERE state='CO'
    run_sql_on_db was successfully executed
    """
    """authenticating to the PostgreSQL db by using a URI
    (Uniform Resource Identifier).
    """
    # getting the name of the function programmatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    target_db = 'postgresql://{}:{}@{}/{}?currentSchema={}'.format(
        user, password, host, db, schema)
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


def sdd_drafter(mxd_loc, sdd_out_loc, portal='MY_HOSTED_SERVICES'):
    """ This function executes SQL scripts against a  PostgreSQL database, the
    function can handle comments of the type '--' and multiline SQL statements.

    Args:
    mxd_loc (string) = A string that represents the path and file name for the
    mxd document.
    sdd_out_loc (string) = A string that represents the path and file name for
    the output Service Definition Draft (.sddraft) file.
    portal (string) (default = 'MY_HOSTED_SERVICES') = A string representing
    the server type. The string 'MY_HOSTED_SERVICES' represents
    My Hosted Services server type for ArcGIS Online or Portal for ArcGIS.

    Returns:
    A sdd object, draft service definition File, (i.e. mymap.sd).

    Examples:
    >>> sdd_drafter(mxd_loc, sdd_outloc)
    Executing sdd_drafter...
    sdd_drafter was successfully executed
    """
    # getting the name of the function programmatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    map_document = arcpy.mapping.MapDocument(mxd_loc)
    service_name = os.path.basename(mxd_loc)[:-4]
    sddraft = '{}/{}.sddraft'.format(sd_out_loc, service_name)
    try:
        sdd_obj = arcpy.mapping.CreateMapSDDraft(
            map_document, sddraft, service_name, portal)
        print('{} was successfully executed'. format(func_name))
    except Exception as e:
        print(e.args[0])
        print(arcpy.GetMessages())
    return sdd_obj


def agol_publisher(sdd, out_name, groups, sd_out_loc=os.getcwd(),
                   portal='MY_HOSTED_SERVICES'):
    """ This function executes SQL scripts against a  PostgreSQL database, the
    function can handle comments of the type '--' and multiline SQL statements.

    Args:
    sdd (string) = A string that represents the path and file name for the
    mxd document.
    out_name (string) = A string that represents the name for the output  sd
    file, Service Definition File.
    groups (list) = A list of group names with which to share the service.
    sd_out_loc (string) =   A string that represents the path for
    the output Service Definition (.sd) file.
    portal (string) (default = 'MY_HOSTED_SERVICES') = A string representing
    the server type. The string 'MY_HOSTED_SERVICES' represents
    My Hosted Services server type for ArcGIS Online or Portal for ArcGIS.

    Examples:
    >>> agol_publisher(sdd, 'test', 'group', sd_out_loc)
    Executing agol_publisher...
    agol_publisher was successfully executed
    """
    # getting the name of the function programmatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    try:
        sd = '{}/{}.sd'.format(sd_out_loc, out_name)
        arcpy.StageService_server(sdd, sd)
        arcpy.UploadServiceDefinition_server(sd, portal, groups)
        print('{} was successfully executed'. format(func_name))
    except Exception as e:
        print(e.args[0])
        print(arcpy.GetMessages())
    return

if __name__ == '__main__':
    # reading credentials from text
    credentials = ''
    with open(credentials, 'r') as c:
        for line in c:
            login_dict = ast.literal_eval(line)
    db_name = login_dict['dbname']
    db_user = login_dict['dbuser']
    db_password = login_dict['dbpassword']
    # employees data folder location
    cu_ed_loc = '/cu_employees_data'
    employees_to_postgresql(db_name, db_user, db_password, cu_ed_loc)
    # shapes folder location
    shp_loc = '\CU_ED_SHP'
    load_shps_to_postgresql(db_name, db_user, db_password, shp_loc=shp_loc)
    # path to the sql script that prepares the database
    ed_format = '\CU_ED_SQL' \
        '\cu_employees_data_formatting.sql'
    # running tiger geocoder
    run_sql_on_db(db_name, db_user, db_password, ed_format)
    # path to the sql script that creates the analysis
    ed_map_lyr = '\CU_ED_SQL' \
        '\cu_ed_map_layers.sql'
    # running buffers
    run_sql_on_db(db_name, db_user, db_password, ed_map_lyr)
    # path to the mxd file that serves as
    mxd_loc = '/CU_ED_MXD/' \
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
