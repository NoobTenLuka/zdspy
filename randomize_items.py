import collections
import os
import random
from typing import List

from zdspy.helpers import ZDS_PH_MAP, ZDS_PH_AREA
from zdspy import zmb as zds
from zdspy import dataio as d


def randomize_items(seed, workdir, outdir, rando_type="nl"):
    random.seed(seed)

    error_log = []

    dirs = []
    # r=root, d=directories, f = files
    for root, directories, _ in os.walk(workdir):
        for name in directories:
            dirs.append(os.path.join(root, name))

    loaded_maps_list: List[ZDS_PH_MAP] = []

    print("Loading maps...")

    for directory in dirs:
        print("[Reading] " + directory)
        loaded_maps_list.append(ZDS_PH_MAP(directory, debug_print=False))

    zmb_cache = {}

    # key = filename (zmb/dngn_main_00.zmb) + item child number
    item_list = {}

    phantom_map: ZDS_PH_MAP
    for phantom_map in loaded_maps_list:
        print(phantom_map.getName())

        map_area: ZDS_PH_AREA
        for map_area in phantom_map.children:
            filename = "zmb/" + phantom_map.getName() + "_" + map_area.getID() + ".zmb"
            print(filename)
            try:
                zmb = zds.ZMB(map_area.getArchive().getFileByName(filename))
                zmb_cache[filename] = zmb
                mpobh = zmb.get_child("MPOB")
                if not (mpobh is None):
                    mpob: zds.ZMB_MPOB_CE
                    for i, mpob in enumerate(mpobh.children):
                        if mpob.mapobjectid == 10 or mpob.mapobjectid == 90 or mpob.mapobjectid == 92 or mpob.mapobjectid == 12 or mpob.mapobjectid == 11 or mpob.mapobjectid == 91:
                            if not (filename + str(i) in item_list):
                                item_list[filename + str(i)] = d.UInt8(mpob.data, 8)
                            else:
                                raise Exception("Duplicate filename: \"" + filename + str(i) + "\".")
            except Exception as err:
                error_log.append(repr(err) + " | " + filename)

    if rando_type == "nl":
        new_item_list = no_logic(item_list)
    else:
        raise ValueError("Error. " + rando_type + " not found!")

    print("#######################################################################")
    print("#######################################################################")
    print("#######################################################################")
    print("Writing changes ...")
    print(zmb_cache)

    # Write new items to maplist
    phantom_map: ZDS_PH_MAP
    for phantom_map in loaded_maps_list:
        print(phantom_map.getName() + " ...")

        map_area: ZDS_PH_AREA
        for map_area in phantom_map.children:
            filename = "zmb/" + phantom_map.getName() + "_" + map_area.getID() + ".zmb"
            print(filename)
            try:
                zmb = zmb_cache[filename]
                mpobh = zmb.get_child("MPOB")
                if not (mpobh is None):
                    for i, mpob in enumerate(mpobh.children):
                        if mpob.mapobjectid == 10 or mpob.mapobjectid == 90 or mpob.mapobjectid == 92 or mpob.mapobjectid == 12 or mpob.mapobjectid == 11 or mpob.mapobjectid == 91:
                            print("YES!")
                            mpob.data = d.w_UInt8(mpob.data, 8, new_item_list[filename + str(i)])

                    map_area.getArchive().setFileByName(filename, zmb.save())
            except Exception as err:
                error_log.append(repr(err) + " | " + filename)

        phantom_map.saveToFolder(outdir)
        # input("Neat Break Point :)")

    error_path = os.path.join(outdir, "../", "RANDOMIZER_ERROR_LOG.txt")
    print("Writing Errors to file ... (" + error_path + ")")
    err_string = ""
    for err in error_log:
        err_string += err + "\n"

    with open(error_path, 'wt', encoding='utf-8') as f:
        f.write(err_string[:-1])


def no_logic(item_list):
    new_item_list = {}

    prev_filename, prev_item = random.choice(list(item_list.items()))
    first = (prev_filename, prev_item)
    del item_list[prev_filename]
    for i in range(len(item_list)):
        filename, item = random.choice(list(item_list.items()))
        del item_list[filename]

        print(str(filename) + " is now " + str(prev_item))
        new_item_list[filename] = prev_item
        prev_filename = filename
        prev_item = item
    # Insert first item
    filename, item = first
    new_item_list[filename] = prev_item
    return new_item_list


