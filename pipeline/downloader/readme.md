# Pipeline Downloader

## Overview
This Unix tool is built to consume a CSV containing a list of URLs. It will download each URL, extract the raw text from the downloaded file (downloaded PDF, PPTX and HTML files are currently supported) and dump it into a text file. The raw files are automatically cleaned up.

## Usage
Here is a sample command to run off the shelf, from the root `AAN2021` directory:
`python -m pipeline.downloader.main -csv aanotator/sample_links.csv -dp pipeline/download_data/ -col 2 -j 8`

- csv: Path to CSV containing the links
- dp: the data path (the path to the directory where the raw text `.txt` files will be output to
- col: the column number of the CSV which contains all of the links (0-indexed)
- j: Number of downloader threads to run
