# README

## Introduction

The `common-api-validation` package aims to provide a convenient utility for validating input CSV files against the [Common API](https://github.com/federated-data-sharing/common-api) metadata standard:

- File encoding should be UTF-8
- The file must be parsable as a CSV
- Reporting the size of the file by raw file size and the number records and fields (rows and columns)
- If provided with a local JSON file, report whether expected fields were found or unexpected fields were founds

> Terminology note: To simplify the documentation we may refer to CSV columns as "fields" and CSV rows as "records" interchangeably. 

## Scope

We expect to improve this file in response to user feedback and the evovling standard. This may include checking and validating content  URIs for linking tables, fields and controlled vocabularies (factors) to ontologies and terminologies.

## Pre-requsiites and Dependencies

> This version was developed and tested on Ubuntu Linux 18.04 and should run on most Linux environments and could be adapted to run on Windows.

This utility uses features of Python and the [pandas](https://pandas.pydata.org/) data science package. We recommend using the [Anaconda](https://www.anaconda.com/) python distribution for convenience but the dependencies could be installed individually. 

To install via Anaconda 
```sh
conda create -f < environment.yml  
```

See the file [`environment.yml`](./environment.yml) for details of what packages and versions are in use. Key packages used:

- pandas 1.2.1
- numpy 1.19.2
- chardet 4.0.0

## Usage

The package provides a single python script [`validation.py`](./validation.py) that is executued on the command line. It works on two inputs:

1. a CSV file
2. (optionally) a JSON file with metadata describing the CSV file in one of its dictionary sections.
3. (optionally) the name of a dictionary in the JSON file to test 

> If no dictionary_to_test parameter is foud, the script will default to either the dictionary that matches the CSV base name or the first dictionary in the JSON file.  

To find usage information, run the script with no parameters:
```sh
python validation.py
```
To check enconding and CSV features of a sample file `example.csv`:
```sh
python validation.py example.csv
```
To check enconding and CSV features of a sample file `example.csv` and also report on conformance to a dataset definition in JSON `metadata.json`:
```sh 
python validation.py example.csv metadata.json
```

## Examples

A number of examples are provided in the [`test` folder](./test).

Check a file that is not UTF-8:
```sh
python validation.py ./test/UTF-8-test.txt
```
Check a file that matches its metadata:
```sh 
python validation.py ./test/all_types_ok.csv ./test/all_types.json
```
Check a file that has additional columns:
```sh 
python validation.py ./test/all_types_extra.csv ./test/all_types.json
```
Check a file that has a missing columns (`classification`):
```sh 
python validation.py ./test/all_types_missing.csv ./test/all_types.json
```

## Known limitations

- Reporting is to a log - maybe we should report to HTML?
- checking CSV structure deeper - expecting or not expecting headers
- checking field values match dictionary types
- field and column names are matched in case insensitive mode. This could be made stricter

## Acknowledgements

Thanks to the following people who provided material for the test data:

- UTF-8 stress test example via https://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt (CC-BY)
- the Periodic data of elements are adapted from https://gist.github.com/GoodmanSciences/c2dd862cd38f21b0ad36b8f96b4bf1ee