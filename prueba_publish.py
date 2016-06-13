from __future__ import print_function
import arcpy
import os
import xml.dom.minidom as DOM


def mxd_properties(mxd_loc, out_loc='IN MEMORY'):
    """
    ...
    """
    service_name = os.path.basename(mxd_loc)[:-4] + '.sddraft'
    map_document = arcpy.mapping.MapDocument(mxd_loc)
    out_sddraft = out_loc + '/' + service_name
    sd = arcpy.CreateMapSDDraft(map_document, )
    print(out_sddraft)
    print(sd)
    return

mxd_loc = 'E:/Users/ulgu3559/Desktop/GIS_projects/CU_ED_MXD/' \
    'sustainable_transportation_webmap.mxd'
mxd_properties(mxd_loc)