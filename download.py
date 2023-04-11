#!/usr/bin/python3

from zoom import ZoomClient
from logger import get_logger
import os
import json
import requests

import avdal.env
import avdal.config

logger = get_logger(".log")

appname = "R2D2"
environ = avdal.env.Environment(os.environ, prefix=appname).union(avdal.env.DotEnv(".env", prefix=appname))


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


auth = readj("auth.json")


client = ZoomClient(".config",
                    auth["account_id"],
                    auth["client_id"],
                    auth["client_secret"])

rec = client.meeting_recordings("86078512479")
for file in rec["recording_files"]:
    url = file["download_url"]
    ext = file["file_extension"].lower().strip()
    typ = file["recording_type"]

    if ext not in Config.download_extensions:
        continue

    client.download(url, f"{typ}.{ext}")
