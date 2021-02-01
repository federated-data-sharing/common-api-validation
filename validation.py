import chardet
import glob
import json
import os
import os.path
import sys
import codecs
import pandas as pd
import numpy as np
import pathlib
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M')

def check_file_is_readable(path_to_file, label):
    """
    Check if a file is readable. This checks the path is to a file (not a directory) 
    and the current user can read the file
    """
    if not os.path.isfile(path_to_file):
        logging.error(f"{label} invalid or missing: {path_to_file}")
        return False
    if not os.access(path_to_file, os.R_OK):
        logging.error(f"{label} can't be read: {path_to_file}")
        return False
    return True

def check_encoding(path_to_csv_file):
    """
    Assumes the file exists and can be read.
    Checks the file is encoded as a UTF-8 (or ASCII) file using two different methods 
    provided by the `chardet` an `codecs` libraries.
    """
    logging.info("Checking encoding 1 of 2: chardet")
    codecs_pass = False
    try:
        with codecs.open(path_to_csv_file, encoding='utf-8', errors='strict') as f:
            for line in f:
                pass
        logging.info('File is UTF-8 encoded (codecs)')
        codecs_pass = True
    except UnicodeDecodeError:
        logging.error('File is NOT UTF-8 encoded (codecs)')

    logging.info("Checking encoding 2 of 2: codecs")
    chardet_pass = False
    with open(path_to_csv_file, 'rb') as f:
        data = f.read()
        e = chardet.detect(data)
        if e['encoding'] not in ['ascii', 'utf-8']:
            logging.error(f"Error: Encoding does not match requirement: {e['encoding']} ({e['confidence'] * 100}%)")
        else:
            logging.info(f"Supported encoding: {e['encoding']} ({e['confidence'] * 100}%)")
            chardet_pass = True

    # TODO - improve the logic here; currently we accept a pass on either
    return codecs_pass or chardet_pass

def file_is_parsable_csv(path_to_csv_file):
    """
    Check if the file is parseable as CSV by the pandas library. 
    This will try to load the file as CSV into a pandas dataframe and discard the output
    """
    try:
        df = pd.read_csv(path_to_csv_file, error_bad_lines=True)
        logging.info(f"Readable as a CSV file: {path_to_csv_file}")
    except:
        logging.error(f"Failed to read as CSV file: {path_to_csv_file}")

def get_csv_properties(path_to_csv_file):
    """
    Assumes the file is readable and parseable as CSV
    """
    df = pd.read_csv(path_to_csv_file, error_bad_lines=True)
    rows, cols = df.shape
    logging.info(f"CSV shape: {rows} rows x {cols} columms")
    columns = df.columns
    logging.info(f"Columns: {columns.values}")



def standardise(field_name):
    """
    Standardise a field name to lower case for case insensitive matching
    """
    if not field_name or not isinstance(field_name, str):
        return None
    else:
        return field_name.lower().strip()

def check_metadata(path_to_csv_file, path_to_metadata_json, dictionary_to_test=None):
    """
    Assumes CSV and JSON files are valid and readable
    """
    logging.info("Checking metadata")

    df = pd.read_csv(path_to_csv_file, error_bad_lines=True)
    with open(path_to_metadata_json, 'r') as mdf:
        try:
            md = json.load(mdf)
            if 'dictionaries' not in md:
                print("Missing 'dictionaries' section in metadata file")
                exit(1)
        except:
            logging.error(f"Unexpected error with Metadata JSON file: {metadata_json_file}")
            exit(1)

        # If no table is provided try to infer the dictionary to use:
        dictionaries = { standardise(d['code']):d for d in md['dictionaries']}
        if dictionary_to_test is not None:
            if standardise(dictionary_to_test) in dictionaries:
                dictionary = dictionaries[dictionary_to_test]
            else:
                # Error 
                logging.error(f"Dictionary not found: {dictionary_to_test}")
                # TODO - can't exit here to be library friendly?
                return
        else:
            # default to the first
            dictionary = md['dictionaries'][0]
        
        expected_table = dictionary['code']

        p = pathlib.Path(path_to_csv_file)
        found_table = p.stem
        logging.info(f"Expected table name '{expected_table}' Found '{found_table}'")

        # Check the columns and fields against what's expected
        # Using Python set operations https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
        expected_fields = set([standardise(f['name']) for f in dictionary['fields']])
        found_columns = set([standardise(c) for c in df.columns])
        intersection = expected_fields.intersection(found_columns)
        missing_fields = expected_fields - found_columns
        unexpected_fields = found_columns - expected_fields

        # print a summary
        logging.info(f"Expecting: {len(expected_fields)}, Found: {len(found_columns)}, Intersection: {len(intersection)}")
        logging.info(f"CSV file has {len(missing_fields)} missing field(s)")
        
        # Do we find the fields we're expecting
        logging.info("Expected fields:")
        for f in expected_fields:
            if f in found_columns:
                logging.info(f"Expected field '{f}' - Found")
            else:
                logging.info(f"Expected field '{f}' - Missing")

        # Now report on fields found that we didn't expect
        if len(unexpected_fields) > 0: 
            logging.info(F"Found {len(unexpected_fields)} fields that were not expected:")
            for c in (found_columns - expected_fields):
                logging.info(f"Found column '{c}' - Unexpected")
        else:
            logging.info("No unexpected fields found")

if __name__ == '__main__':
    # if no parameters, output usage
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <csv_file> [<metadata_json_file>] [<dictionary_to_test>]")
        exit(1)

    # Step 1: Check input files exist and can be read. Exit if not
    csv_file = sys.argv[1]
    logging.info(f"Input CSV file: {csv_file}")
    if not check_file_is_readable(csv_file, 'CSV file'):
        exit(1)

    metadata_json_file = None
    if len(sys.argv) > 2:
        metadata_json_file = sys.argv[2]
        logging.info(f"Input Metadata JSON file: {metadata_json_file}")
        if not check_file_is_readable(metadata_json_file, 'Metadata JSON file'):
            exit(1)

    dictionary_to_test = None
    if len(sys.argv) > 3:
        dictionary_to_test = sys.argv[3]

    # Step 2: Check encoding is UTF-8 or ASCII
    encoding_pass = check_encoding(csv_file)

    if encoding_pass:
        # Step 3: Check file can be parsed as CSV
        file_is_parsable_csv(csv_file)

        # Step 4: Check basic CSV features
        get_csv_properties(csv_file)

        # Step 5: (Optional) Check alignment to metadata file
        if metadata_json_file is not None:
            if dictionary_to_test is not None:
                logging.info(f"Checking metadata - for specific dictionary_to_test {dictionary_to_test}")
                check_metadata(csv_file, metadata_json_file, dictionary_to_test)
            else:
                check_metadata(csv_file, metadata_json_file)
