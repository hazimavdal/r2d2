#!/usr/bin/python3

# this is a test change

from zoom import ZoomClient
from logger import get_logger
from lib import parse_datetime, make_parents

import os
import csv
import json
import argparse
import requests

import avdal.env
import avdal.config

logger = get_logger(".log")

appname = "R2D2"

env = avdal.env.DotEnv(".env", prefix=appname)
print(env)
environ = avdal.env.Environment(os.environ, prefix=appname).union(env)


def ext_mapper(raw: str) -> list:
    result = [e.lower().strip() for e in raw.split(",")]
    assert len(result) > 0, "R2D2_DOWNLOAD_EXTENSIONS: Must specify at least one extension to download"
    return result


class Config(avdal.config.Base):
    class Meta:
        environ = environ

    account_id: str = avdal.config.Field()
    r2d2_path: str = avdal.config.Field(cast=avdal.env.path_mapper)
    download_extensions: str = avdal.config.Field(cast=ext_mapper)
    zoom_client_id: str = avdal.config.Field()
    zoom_client_secret: str = avdal.config.Field()
    noop: bool = avdal.config.Field(cast=bool, default=False)

client = ZoomClient(os.path.join(Config.r2d2_path, ".config"),
                    Config.account_id,
                    Config.zoom_client_id,
                    Config.zoom_client_secret)


def download_meeting(dest, meeting_id):
    meeting = client.meeting_recordings(meeting_id)
    manifest = {
        "meeting_id": meeting_id,
        "topic": meeting["topic"],
        "start_time": meeting["start_time"]
    }
    logger.info(f"Downloading '{meeting['topic']}'")
    for file in meeting["recording_files"]:
        url = file["download_url"]
        ext = file["file_extension"].lower().strip()
        typ = file["recording_type"]
        start = file["recording_start"]

        if ext not in Config.download_extensions:
            continue

        timestamp = parse_datetime(start).strftime("%Y-%m-%d")
        out_file = os.path.join(dest, timestamp, f"{typ}.{ext}")
        make_parents(out_file)

        if not Config.noop:
            client.download(url, out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file")

    args = parser.parse_args()

    with open(args.config_file) as f:
        rows = csv.DictReader(f)
        for row in rows:
            code = row["Class Code"].strip().replace(" ", "").lower()
            meeting_id = row["Meeting ID"].strip().replace(" ", "")
            if len(code) == 0 or len(meeting_id) == 0:
                continue

            class_dir = os.path.join(Config.r2d2_path, code)
            download_meeting(class_dir, meeting_id)
