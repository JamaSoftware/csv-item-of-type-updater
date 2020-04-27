import os
import sys
import csv
import logging
import datetime
import configparser

from py_jama_rest_client.client import JamaClient
from py_jama_rest_client.client import APIException

logger = logging.getLogger(__name__)

unique_item_id_map = {}


def update_item_of_types(config: configparser.ConfigParser):
    # Get Script settings from config
    csv_file_path = None
    destination_item_of_type_field = None
    csv_source_header = None
    csv_destination_header = None
    using_api_id = None
    source_field_name = None
    destination_field_name = None

    try:
        csv_file_path = config.get('SCRIPT_SETTINGS', 'csv_file_path')
        destination_item_of_type_field = config.get('SCRIPT_SETTINGS', 'destination_item_of_type_field')
        csv_source_header = config.get('SCRIPT_SETTINGS', 'csv_source_header')
        csv_destination_header = config.get('SCRIPT_SETTINGS', 'csv_destination_header')
        using_api_id = config.getboolean('SCRIPT_SETTINGS', 'using_api_id')
        source_field_name = config.get('SCRIPT_SETTINGS', 'source_field_name')
        destination_field_name = config.get('SCRIPT_SETTINGS', 'destination_field_name')

    except configparser.Error as config_error:
        logger.error("Unable to parse SCRIPT_SETTINGS because: {} Please check settings and try again."
                     .format(str(config_error)))
        exit(1)

    # parse out the csv rows here
    csv_content = process_csv_content(csv_file_path, csv_source_header, csv_destination_header)

    # build out all the patch payloads and push them up
    patch_payloads = []
    for row in csv_content:
        # if we are using the api id then no additional api calls are needed
        if using_api_id:
            source = row.get('source')
            destination = row.get('destination')
        # otherwise we are going to need to resolve this identifier to the API ID
        else:
            source = get_api_id(source_field_name, row.get('source'))
            destination = get_api_id(destination_field_name, row.get('destination'))

        payload = {
            'op': 'add',
            'path': '/fields/' + str(destination_item_of_type_field),
            'value': str(source)
        }
        patch_payloads.append({
            'id': str(destination),
            'payload': payload
        })

    if len(patch_payloads) > 0:
        try:
            for patch in patch_payloads:
                logger.info("Patching item: {}".format(str(patch.get('id'))))
                jama_client.patch_item(patch.get('id'), patch.get('payload'))
        except APIException as error:
            logger.error("Unable to patch item: {} because: {}".format(str(patch.get('id')), str(error)))


def get_api_id(field_name, field_value):
    if field_value in unique_item_id_map:
        return unique_item_id_map[field_value]
    lucene_search = field_name + ":\"" + field_value + "\""
    results = jama_client.get_abstract_items(contains=lucene_search)
    if len(results) == 1:
        unique_item_id_map[field_value] = results[0].get('id')
        return results[0].get('id')
    else:
        return None


def process_csv_content(csv_file, source_item_column, destination_item_column):
    csv_content = []
    csv_lines_read = 0

    # Open the CSV file for reading, use the utf-8-sig encoding to deal with excel file type outputs.
    with open(str(csv_file), encoding='utf-8-sig') as open_csv_file:
        # We need to get a dict reader, if the CSV file has headers, we dont need to supply them
        csv_dict_reader = csv.DictReader(open_csv_file)

        # Begin processing the data in the CSV file.
        for row_number, row_data in enumerate(csv_dict_reader):
            # For each row in the CSV file we will append an object to a list for later processing.
            # First get source and target data. These are mandatory, a missing data point here is an error.
            csv_lines_read += 1
            current_row_rel_data = {
                'row': row_number,
                'source': row_data[source_item_column],
                'destination': row_data[destination_item_column],
            }
            csv_content.append(current_row_rel_data)

    logger.info('Successfully processed ' + str(csv_lines_read) + ' CSV rows.')
    return csv_content


def init_logging():
    try:
        os.makedirs('logs')
    except FileExistsError:
        pass
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    log_file = 'logs/harm-severity-updater_' + str(current_date_time) + '.log'
    logging.basicConfig(filename=log_file, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def parse_config():
    if (len(sys.argv) == 1):
        current_dir = os.path.dirname(__file__)
        path_to_config = 'config.ini'
        if not os.path.isabs(path_to_config):
            path_to_config = os.path.join(current_dir, path_to_config)

    if len(sys.argv) == 2:
        current_dir = os.path.dirname(__file__)
        path_to_config = sys.argv[1]
        if not os.path.isabs(path_to_config):
            path_to_config = os.path.join(current_dir, path_to_config)

    # Parse config file.
    configuration = configparser.ConfigParser()
    configuration.read_file(open(path_to_config))
    return configuration


def create_jama_client(config: configparser.ConfigParser):
    url = None
    user_id = None
    user_secret = None
    oauth = None
    try:
        url = config.get('CLIENT_SETTINGS', 'jama_connect_url').strip()
        # Clean up URL field
        while url.endswith('/') and url != 'https://' and url != 'http://':
            url = url[0:len(url) - 1]
        # If http or https method not specified in the url then add it now.
        if not (url.startswith('https://') or url.startswith('http://')):
            url = 'https://' + url
        oauth = config.getboolean('CLIENT_SETTINGS', 'oauth')
        user_id = config.get('CLIENT_SETTINGS', 'user_id').strip()
        user_secret = config.get('CLIENT_SETTINGS', 'user_secret').strip()
    except configparser.Error as config_error:
        logger.error("Unable to parse CLIENT_SETTINGS from config file because: {}, "
                     "Please check config file for errors and try again."
                     .format(str(config_error)))
        exit(1)

    return JamaClient(url, (user_id, user_secret), oauth=oauth)


# Execute this as a script.
if __name__ == "__main__":
    # Setup logging
    init_logging()

    # Get Config File Path
    conf = parse_config()

    # Create Jama Client
    jama_client = create_jama_client(conf)

    # Begin business logic
    update_item_of_types(conf)

    logger.info("Done.")
