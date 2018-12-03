"""Find possible Sentinel-2 scenes which could see Landsat-8 satellite."""

import sys
import json
import datetime
from random import shuffle

import click

import pandas as pd
import geopandas as gpd
from shapely.geometry import box, mapping

# LANDSAT_METADATA_URL = 'http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz'
# SENTINEL2_METADATA_URL = 'http://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz'
s2_path = "sentinel.csv"
l8_path = "landsat.csv"
crs = {"init": "epsg:4326"}


def create_feature(s2, l8):
    return {
        "type": "Feature",
        "properties": {
            "S2_PRODUCT_ID": s2.PRODUCT_ID,
            "S2_SENSING_TIME": s2.SENSING_TIME.isoformat(),
            "L8_SCENE_ID": list(l8.SCENE_ID),
            "L8_PRODUCT_ID": list(l8.PRODUCT_ID),
            "L8_SENSING_TIME": [x.isoformat() for x in l8.SENSING_TIME],
        },
        "geometry": mapping(s2.geometry),
    }


def main():
    click.echo("Reading Landsat index...", err=True)
    l8_meta = pd.read_csv(l8_path)
    l8_meta.drop(
        columns=[
            "SENSOR_ID",
            "COLLECTION_NUMBER",
            "COLLECTION_CATEGORY",
            "DATA_TYPE",
            "TOTAL_SIZE",
        ],
        inplace=True,
    )
    l8_meta = l8_meta.loc[l8_meta.SPACECRAFT_ID == "LANDSAT_8"]
    l8_meta["SENSING_TIME"] = pd.to_datetime(l8_meta["SENSING_TIME"])
    l8_meta = l8_meta.loc[l8_meta.SENSING_TIME > datetime.datetime(2015, 6, 23)]
    click.echo("Creating Landsat catalog...", err=True)
    geometry = [
        box(*bbox)
        for bbox in zip(
            l8_meta.WEST_LON, l8_meta.SOUTH_LAT, l8_meta.EAST_LON, l8_meta.NORTH_LAT
        )
    ]
    l8_catalog = gpd.GeoDataFrame(l8_meta, crs=crs, geometry=geometry)
    del geometry, l8_meta

    click.echo("Reading Sentinel index...", err=True)
    s2_meta = pd.read_csv(s2_path)
    s2_meta.drop(
        columns=[
            "DATATAKE_IDENTIFIER",
            "TOTAL_SIZE",
            "GEOMETRIC_QUALITY_FLAG",
            "GENERATION_TIME",
        ],
        inplace=True,
    )
    s2_meta["SENSING_TIME"] = pd.to_datetime(s2_meta["SENSING_TIME"])
    click.echo("Creating Sentinel catalog...", err=True)
    geometry = [
        box(*bbox)
        for bbox in zip(
            s2_meta.WEST_LON, s2_meta.SOUTH_LAT, s2_meta.EAST_LON, s2_meta.NORTH_LAT
        )
    ]
    s2_catalog = gpd.GeoDataFrame(s2_meta, crs=crs, geometry=geometry)
    del geometry, s2_meta

    padding = 5
    min_lon = -180
    max_lon = 180
    min_lat = -90
    max_lat = 90
    ll = [
        (lon, lat, lon + padding, lat + padding)
        for lat in range(min_lat, max_lat, padding)
        for lon in range(min_lon, max_lon, padding)
    ]
    shuffle(ll)

    click.echo(f"Processing {len(ll)} boxes...", err=True)
    with click.progressbar(
        ll, length=len(ll), file=sys.stderr, show_percent=True, show_pos=True
    ) as boxes:
        for bbox in boxes:
            # Cheap Polygon intersect
            query = [
                f"(NORTH_LAT > {bbox[1]} and NORTH_LAT <= {bbox[3]}) and (WEST_LON > {bbox[0]} and WEST_LON <= {bbox[2]})",  # ul
                f"(NORTH_LAT > {bbox[1]} and NORTH_LAT <= {bbox[3]}) and (EAST_LON > {bbox[0]} and EAST_LON <= {bbox[2]})",  # ur
                f"(SOUTH_LAT > {bbox[1]} and SOUTH_LAT <= {bbox[3]}) and (EAST_LON > {bbox[0]} and EAST_LON <= {bbox[2]})",  # lr
                f"(SOUTH_LAT > {bbox[1]} and SOUTH_LAT <= {bbox[3]}) and (WEST_LON > {bbox[0]} and WEST_LON <= {bbox[2]})",  # ll
            ]
            query = " or ".join(query)

            s2_sub = s2_catalog.query(query)
            if not len(s2_sub):
                continue

            l8_sub = l8_catalog.query(query)
            if not len(l8_sub):
                continue

            s2_grid = s2_sub.groupby(["MGRS_TILE"])
            for name, group in s2_grid:
                geom = box(
                    group.WEST_LON.mean(),
                    group.SOUTH_LAT.mean(),
                    group.EAST_LON.mean(),
                    group.NORTH_LAT.mean(),
                )
                # Cheap and fast filtering
                l8_inter = l8_sub[l8_sub.intersects(geom)]
                for ind, item in group.iterrows():
                    selection = l8_inter[
                        (l8_inter["SENSING_TIME"] - item["SENSING_TIME"]).abs()
                        < pd.Timedelta("5 seconds")
                    ]
                    if len(selection):
                        r = create_feature(item, selection)
                        print(json.dumps(r))


if __name__ == "__main__":
    main()
