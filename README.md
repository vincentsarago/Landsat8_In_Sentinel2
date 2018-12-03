# Find Landsat-8 in Sentinel-2 - Work In Progress

This repo is a response to this (:point_down:) blog post to see if it was possible to find a Sentinel-2 scene where we can spot Landsat 8 satellite.

<blockquote class="twitter-tweet" data-partner="tweetdeck"><p lang="en" dir="ltr">I am prepared to be wrong on this new blogpost &quot;When <a href="https://twitter.com/hashtag/Landsat8?src=hash&amp;ref_src=twsrc%5Etfw">#Landsat8</a> (almost) meets <a href="https://twitter.com/hashtag/Sentinel2?src=hash&amp;ref_src=twsrc%5Etfw">#Sentinel2</a>&quot;. <a href="https://t.co/5RXzAerKCu">https://t.co/5RXzAerKCu</a> <a href="https://twitter.com/USGSLandsat?ref_src=twsrc%5Etfw">@USGSLandsat</a> <a href="https://twitter.com/CopernicusData?ref_src=twsrc%5Etfw">@CopernicusData</a> <a href="https://twitter.com/hashtag/earthengine?src=hash&amp;ref_src=twsrc%5Etfw">#earthengine</a> <a href="https://twitter.com/hashtag/EarthObservation?src=hash&amp;ref_src=twsrc%5Etfw">#EarthObservation</a> <a href="https://twitter.com/hashtag/remotesensing?src=hash&amp;ref_src=twsrc%5Etfw">#remotesensing</a> <a href="https://twitter.com/hashtag/freedata?src=hash&amp;ref_src=twsrc%5Etfw">#freedata</a> <a href="https://t.co/VjUCVCH92e">pic.twitter.com/VjUCVCH92e</a></p>&mdash; Philipp Gärtner (@gartn001) <a href="https://twitter.com/gartn001/status/1015302356102205447?ref_src=twsrc%5Etfw">July 6, 2018</a></blockquote>


### Prerequisites

1. Install Python modules

`pip install pandas geopandas shapely`

*Note:* if :point_up: fails for pyproj, try: `pip install git+https://github.com/jswhit/pyproj.git#egg=pyproj`

2. Download Landsat and Sentinel indexes

	- Landsat: `wget http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz && gunzip index.csv.gz > landsat.csv`
	- Sentinel: `wget http://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz && gunzip index.csv.gz > sentinel.csv`

```
$ cat landsat.csv | wc -l
13 749 024

$ cat sentinel.csv | wc -l
6 741 652
```

### Run

1. Find overlapping Sentinel-2 and Landsat-8 scenes
```
python find_landsat_in_sentinel.py > l8_overlap_s2.json
```
Come back in ~5 hours

![](https://user-images.githubusercontent.com/10407788/49354986-83672300-f693-11e8-850e-f87142fe86c4.jpg)

The script should find ~5800 Sentinel-2 scenes which have at least one overlapping Landsat-8 scene acquired within 5 seconds.

Each output should be like:
```json
{
  "type": "Feature",
  "properties": {
	// Sentinel-2 scene ID
    "S2_PRODUCT_ID": "S2A_MSIL1C_20170915T112701_N0205_R080_T35XNJ_20170915T112704",
	// Sentinel-2 acquisition date
    "S2_SENSING_TIME": "2017-09-15T11:27:04.460000",
	// List of overlapping Landsat-8 ID
    "L8_SCENE_ID": [ "LC82080022017258LGN00" ],
    "L8_PRODUCT_ID": [ "LC08_L1GT_208002_20170915_20170928_01_T2" ],
	// List of overlapping Landsat-8 acquisition date
    "L8_SENSING_TIME": [ "2017-09-15T11:27:01.014935" ]
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [ 32.737655971799995, 79.1376077611 ],
        [ 32.737655971799995, 80.132118355 ],
        [ 26.9985522679, 80.132118355 ],
        [ 26.9985522679, 79.1376077611 ],
        [ 32.737655971799995, 79.1376077611 ]
      ]
    ]
  }
}
```


[TODO]
2. Validate Scenes (S2/L8) geometries by reading scenes metadata
3. Check Landsat orbit parameters to confirm Sentinel-2 could see it
