OrganicMapsDownload
A simple Python script to download Organic Maps map files (`.mwm`) from omaps.webfreak.org to your computer, so you can then transfer them to your phone via USB — useful when you have a slow or limited mobile connection.
---
Why?
Organic Maps lets you download maps directly in the app, but if your phone connection is slow or you want to grab many regions at once, it's much faster to download them on your computer and copy them over USB.
---
Requirements
Python 3.8 or newer
No third-party packages — uses only the Python standard library
---
Installation
```bash
git clone https://github.com/Olibesnier/OrganicMapsDownload.git
cd OrganicMapsDownload
```
Usage
Download a specific country or region
```bash
python download_maps.py --filter France
```
```bash
python download_maps.py --filter Netherlands
```
```bash
python download_maps.py --filter "United States"
```
The `--filter` flag is case-insensitive and matches any part of the filename, so `--filter Spain` will match `Spain_North.mwm`, `Spain_South.mwm`, etc.
Download everything (warning: hundreds of GB)
```bash
python download_maps.py
```
Custom output directory
```bash
python download_maps.py --filter Germany --output-dir ~/Downloads/maps
```
Faster downloads with more parallel threads
```bash
python download_maps.py --filter Italy --workers 5
```
---
All options
Flag	Default	Description
`--filter TEXT`	(none)	Only download files whose name contains TEXT
`--output-dir PATH`	`./maps`	Directory to save `.mwm` files
`--workers N`	`3`	Number of parallel download threads
---
Transferring maps to your Android phone
Once downloaded, copy the `.mwm` files to your phone via USB:
Connect your phone via USB and enable File Transfer mode
Navigate to:
```
   /Android/data/app.organicmaps/files/260310/
   ```
> If installed from F-Droid, the path may use `app.organicmaps.fdroid` instead of `app.organicmaps`
Copy your `.mwm` files into that folder
Open Organic Maps — the maps will be detected automatically
> **Note:** The version folder (`260310`) must match the map data version your installed app expects. You can check this in the app under **Menu → About**.
---
Notes
Resume-safe: Already downloaded files are skipped automatically, so you can stop and restart freely
Retry logic: Failed downloads are retried up to 3 times with exponential back-off
Safe temp files: Downloads are written to `.part` files and only renamed on success, so you'll never end up with a corrupted `.mwm`
iOS: Manual map transfer on iOS is not straightforward — it's generally easier to download maps directly in the app
---
Disclaimer
This script downloads map data from a third-party mirror (omaps.webfreak.org). Map data is © OpenStreetMap contributors, licensed under ODbL. This project is not affiliated with the Organic Maps team.
---
License
MIT
