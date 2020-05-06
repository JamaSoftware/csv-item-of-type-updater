# CSV Item Of Type Updater
The purpose of this script is to read in a csv file and process each row to update the corresponding item of type fields.

It parses a CSV file with a source and destination column. This script will then update each item specified in the CSV with the corresponding item of type value. 


# Source CSV Content
The source csv content must have a header row with two columns to represent a source ID and a destination ID. There can
be extra data in this CSV because the config file will require you to specify this source and destination CSV header names.
The content of the cells must me a unique Jama identifier (e.g. API ID, documentKey, globalId, a custom field). Using 
the API ID is the most ideal for script efficiency. 

# Installation
This section contains information on how to install the required dependencies for this script.

## Pre-Requisites
* [Python 3.7+](https://www.python.org/downloads/release/python-377/) If using pipenv you must use a python 3.7.X 
version.  If installing requirements manually you may use any python version including 3.8+ however testing has only
been done against python 3.7

* [py-jama-rest-client](https://pypi.org/project/py-jama-rest-client/)

* Enable the REST API on your Jama Connect instance

## Pipenv installation (Recommended)
If you do not already have Pipenv installed on your machine you can learn how to install it here: 
[https://pypi.org/project/pipenv/](https://pypi.org/project/pipenv/)

The required dependencies for this project are managed with Pipenv and can be installed by opening a terminal
to the project directory and entering the following command:
```bash
    pipenv install
```

## Manual installation
If you do not wish to use Pipenv you may manually install the required dependencies with pip.
```bash
pip install --user py-jama-rest-client
```

# Usage
This section contains information on configuration and execution the script.

## Configuration
Before you can execute the script you must configure the script via a config file.  The config file is
structured in a standard .ini file format. there is an example config.ini file included with this repo that you
may modify with your settings.  I recommend that you create a copy of the template config file and rename it to
something that is meaningful for your execution.

#### Client Settings:
This section contains settings related to connecting to your Jama Connect REST API.

* jama_connect_url: this is the URL to your Jama Connect instance

* oauth: setting this value to 'false' will instruct the client to authenticate via basic authentication.  Setting this 
value to 'true' instructs the client to use OAuth authentication protocols

* user_id: This should be either your username or clientID if using OAuth

* user_secret: This should be either your password or client_secret if using OAuth

#### Script Settings:
This section contains settings for configuration of the scripts functionality.

* csv_file_path: The path the csv file to be uploaded.

* destination_item_of_type_field: API field name of the item of type field on the destination item being updated.

* csv_source_header: CSV header name for the source column to map to. 

* csv_destination_header: CSV header name for the destination column to map to. 

* using_api_id: boolean (e.g. true, false) if using a different identifier field, please ensure that the selected field
is unique across your Jama instance.

* source_field_name: This field is required if you are not using the API ID, specify the source field name.

* destination_field_name: This field is required if you are not using the API ID, specify the destination field name.

## Running the script

1) Open a terminal to the project directory.
2) If using pipenv enter the following(otherwise skip to step 3):
   ```bash
   pipenv shell 
   ``` 
3) Enter the following command into your terminal (Note that the script accepts one parameter and that is the path to
the config file created above):  
   ```bash 
   python csv_item_of_type_updater.py config.ini
   ```

## Output
Execution logs will be output to the terminal as well as output to a log file in the logs/ folder located next to the 
script.
