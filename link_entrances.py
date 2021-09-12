import os
from typing import List

from zdspy.helpers import ZDS_PH_MAP, ZDS_PH_AREA
from zdspy import zmb as zds


def link_entrances(entrance1, entrance2, workdir, outdir):
    entrance1_values = entrance1.split("-")
    entrance2_values = entrance2.split("-")

    print(entrance1_values)

    dirs = []
    # r=root, d=directories, f = files
    for root, directories, _ in os.walk(workdir):
        for name in directories:
            dirs.append(os.path.join(root, name))

    loaded_maps_list: List[ZDS_PH_MAP] = []

    print("Loading maps...")

    for directory in dirs:
        loaded_maps_list.append(ZDS_PH_MAP(directory, debug_print=False))

    phantom_map: ZDS_PH_MAP
    for phantom_map in loaded_maps_list:
        if phantom_map.getName() != entrance1_values[0] and phantom_map.getName() != entrance2_values[0]:
            continue

        map_area: ZDS_PH_AREA
        for map_area in phantom_map.children:
            if map_area.getID() != entrance1_values[1] and map_area.getID() != entrance2_values[1]:
                continue

            filename = "zmb/" + phantom_map.getName() + "_" + map_area.getID() + ".zmb"
            print(filename)
            try:
                zmb = zds.ZMB(map_area.getArchive().getFileByName(filename))
                warph = zmb.get_child("WARP")
                if not (warph is None):
                    warp: zds.ZMB_WARP_CE
                    for i, warp in enumerate(warph.children):
                        if warp.UID != int(entrance1_values[2]) and warp.UID != int(entrance2_values[2]):
                            continue

                        if phantom_map.getName() == entrance1_values[0] and map_area.getID() == entrance1_values[1] \
                                and warp.UID == int(entrance1_values[2]):
                            warp.map_id = int(entrance2_values[1])
                            warp.destination_warp_id = int(entrance2_values[2])
                            warp.destination = entrance2_values[0]
                            print("New: " + warp.destination)
                        else:
                            warp.map_id = int(entrance1_values[1])
                            warp.destination_warp_id = int(entrance1_values[2])
                            warp.destination = entrance1_values[0]

                    map_area.getArchive().setFileByName(filename, zmb.save())
            except Exception as err:
                print(err)

        phantom_map.saveToFolder(outdir)
