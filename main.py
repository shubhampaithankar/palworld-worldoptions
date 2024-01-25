#!/usr/bin/env python3

from typing import Dict
import argparse
import json
import os
from lib.rawdata import encode_group_data, decode_group_data
from lib.noindent import CustomEncoder
from lib.palsav import convert_to_save, convert_to_json
from lib.palworldsettings import create_palworldsettings


def convert_single_to_sav(uesave_path: str, save_path: str) -> None:
    print(f"Loading JSON from {save_path}")
    with open(save_path, "rb") as f:
        data = json.load(f)
    if "worldSaveData" in data["root"]["properties"]:
        print(f"Encoding GroupSaveDataMap")
        encode_group_data(data)
    print(f"Converting JSON")
    convert_to_save(uesave_path, save_path, data)


def convert_single_to_json(uesave_path: str, save_path: str) -> None:
    print(f"Converting {save_path} to JSON (using {uesave_path})")
    json_blob = convert_to_json(uesave_path, save_path)
    if "worldSaveData" in json_blob["root"]["properties"]:
        print("Decoding GroupSaveDataMap")
        decode_group_data(json_blob)
    output_path = save_path + ".json"
    print(f"Writing JSON to {output_path}")
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(json_blob, f, indent=2, cls=CustomEncoder, ensure_ascii=False)


def game_files_exist(path: str) -> bool:
    return os.path.exists(os.path.join(path, "LevelMeta.sav")) \
           and os.path.exists(os.path.join(path, "PalWorldSettings.ini"))


def uesave_exists(path: str) -> bool:
    return os.path.exists(path)


def load_levelmeta(path: str) -> Dict:
    with open(os.path.join(path, "LevelMeta.sav.json"), encoding="utf-8") as f:
        data = json.load(f)
    data["root"]["properties"].pop("SaveData")
    return data


def save_worldoptions(path: str, data: Dict) -> None:
    with open(os.path.join(path, "WorldOption.sav.json"), mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, cls=CustomEncoder, ensure_ascii=False)


def convert_to_worldoptions(uesave_path: str, save_path: str) -> None:
    # Make sure files exist
    if game_files_exist(save_path):
        print("Found game files")
    else:
        print(f"Could not find LevelMeta.sav and PalWorldSettings.ini in {save_path}")
    if uesave_exists(save_path):
        print("Found uesave")
    else:
        print(f"uesave does not exist at {uesave_path}")
    convert_single_to_json(uesave_path, os.path.join(save_path, "LevelMeta.sav"))
    levelmetadata = load_levelmeta(save_path)
    optionworlddata = create_palworldsettings(save_path)
    levelmetadata["root"]["properties"]["OptionWorldData"] = optionworlddata
    levelmetadata["root"]["save_game_type"] = "/Script/Pal.PalWorldOptionSaveGame"
    save_worldoptions(save_path, levelmetadata)
    convert_single_to_sav(uesave_path, os.path.join(save_path, "WorldOption.sav.json"))
    print("Cleaning up")
    os.remove(os.path.join(save_path, "LevelMeta.sav.json"))
    os.remove(os.path.join(save_path, "WorldOption.sav.json"))
    print("Complete!")
    print("Restart your palworld server to apply the changes")


def main() -> None:
    parser = argparse.ArgumentParser(prog='palworld-worldoptions',
                                     description='Creates a worldoptions.sav file for dedicated servers')
    parser.add_argument('--uesave', help='specify uesave location',
                        default=f"{os.path.realpath(os.path.dirname(__file__))}\\uesave\\uesave.exe")
    parser.add_argument('save_path', help='location of the saved game data folder')
    args = parser.parse_args()
    convert_to_worldoptions(args.uesave, args.save_path)


if __name__ == '__main__':
    main()
