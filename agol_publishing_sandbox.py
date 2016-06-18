from __future__ import print_function
import arcpy
import inspect
import os
import xml.dom.minidom as DOM


def agol_login(user, password, portal=''):
    """
    ...
    """
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    try:
        arcpy.SignInToPortal_server(user, password, portal)
        print('{} completed successfully'.format(func_name))
    except Exception as e:
        print(e)
        print(arcpy.GetMessages())
    return


def mxd_properties_collector(mxd_loc, prop='title'):
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    mxd = arcpy.mapping.MapDocument(mxd_loc)
    # checking for __iter__ works on sequence types
    # it would fail on e.g. strings
    try:
        mxd_prop = {}
        if hasattr(prop, '__iter__'):
            for i in prop:
                # getting map attributes dynamically
                mxd_prop[i] = getattr(mxd, i)
        else:
            mxd_prop[prop] = getattr(mxd, prop)
        print(mxd_prop)
        print('{} completed successfully'. format(func_name))
    except Exception as e:
        print(e.args[0])
    return mxd_prop


def mxd_properties_writer(mxd_loc, prop='title'):
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    mxd = arcpy.mapping.MapDocument(mxd_loc)
    # checking for __iter__ works on sequence types
    # it would fail on e.g. strings
    try:
        mxd_prop = {}
        if hasattr(prop, '__iter__'):
            for i in prop:
                # getting map attributes dynamically
                mxd_prop[i] = getattr(mxd, i)
        else:
            mxd_prop[prop] = getattr(mxd, prop)
        print(mxd_prop)
        print('{} completed successfully'. format(func_name))
    except Exception as e:
        print(e.args[0])
    return mxd_prop


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


def sdd_modifier(sdd_loc):
    """
    ...
    """
    # getting the name of the function programatically.
    func_name = inspect.currentframe().f_code.co_name
    print('Executing {}... '.format(func_name))
    try:
        doc = DOM.parse(sdd_loc)
        x = doc.getElementsByTagName('TypeName')
        for i in x:
            print(i)
    except Exception as e:
        print(e.args[0])
        print(arcpy.GetMessages())
    return


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


if __name__ == "__main__":
    # mxd_loc = 'E:/Users/ulgu3559/Desktop/GIS_projects/CU_ED_MXD/' \
    #     'sustainable_transportation_webmap.mxd'
    mxd_loc = 'C:/Users/ulisesdario/Desktop/Sustainable_Transportation/' \
        'SUSTRA_MXD/Sustainable_transportation.mxd'
    out_loc = 'C:/Users/ulisesdario/Desktop/Sustainable_Transportation'
    sdd_loc = 'C:/Users/ulisesdario/Desktop/Sustainable_Transportation/' \
        'Sustainable_transportation.sddraft'
    agol_login('Ulisessol7', 'katie2387')
    # mxd_properties_collector(mxd_loc, ('title', 'tags'))
    # sdd_drafter(mxd_loc, out_loc)
    # sdd_modifier(sdd_loc)
