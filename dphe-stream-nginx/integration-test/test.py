import unittest
import requests
import logging
from pathlib import Path
import configparser

# Set logging fromat and level (default is warning)
# All the API logging is forwarded to the uWSGI server and gets written into the log file `uwsgo-entity-api.log`
# Log rotation is handled via logrotate on the host system with a configuration file
# Do NOT handle log file and rotation via the Python logging to avoid issues with multi-worker processes
logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Load configuration items
config = configparser.ConfigParser()   
config.read(Path(__file__).absolute().parent / 'test.cfg')

user_token = config['TEST']['AUTH_TOKEN']

# Remove trailing slash / from URL base to avoid "//" caused by config with trailing slash
base_url = config['TEST']['REST_API_BASE_URL'].strip('/')

report_tuples = config.items('REPORTS')

logger.debug(config.items('REPORTS'))


####################################################################################################
## Non-test Functions
####################################################################################################

def parse_patient_and_report(report_rel_path):
    val_list = report_rel_path.split("/")
    patient_name = val_list[1]
    report_name = val_list[2]

    return patient_name, report_name


"""
Create a dict of HTTP Authorization header with Bearer token

Parameters
----------
user_token: str
    The user's auth token
Returns
-------
dict
    The headers dict to be used by requests
"""
def create_request_headers(user_token):
    auth_header_name = 'Authorization'
    auth_scheme = 'Bearer'

    headers_dict = {
        # Don't forget the space between scheme and the token value
        auth_header_name: auth_scheme + ' ' + user_token
    }

    return headers_dict


####################################################################################################
## Test Cases
####################################################################################################

class TestRestApi(unittest.TestCase):

    def test_summarize_doc(self):
        with self.assertRaises(Exception) as context:
            broken_function()

        for (key, report_rel_path) in report_tuples:
            patient_name, report_name = parse_patient_and_report(report_rel_path)

            target_url = f'{base_url}/summarizeDoc/doc/{report_name}'
            request_headers = create_request_headers(user_token)
            # Add content-type header
            request_headers['content-type'] = 'text/plain'

            report_text = (Path(__file__).absolute().parent / report_rel_path).read_text()

            #logger.debug(report_text)

            # HTTP GET
            # The requests package attempts to auto-encode the data for transfer and fallback is latin-1
            # Specify to encode with utf-8 to avoid encoding error
            response = requests.get(url = target_url, headers = request_headers, data = report_text.encode('utf-8'))

            result_dict = response.json()
            
            #logger.debug(result_dict)

            expr = ('id' in result_dict) and (result_dict['id'] == report_name)

            self.assertTrue(expr, f"Message: {report_name} summarized")


    def test_summarize_patient_doc(self):
        with self.assertRaises(Exception) as context:
            broken_function()

        for (key, report_rel_path) in report_tuples:
            patient_name, report_name = parse_patient_and_report(report_rel_path)

            target_url = f'{base_url}/summarizePatientDoc/patient/{patient_name}/doc/{report_name}'
            request_headers = create_request_headers(user_token)
            # Add content-type header
            request_headers['content-type'] = 'text/plain'

            report_text = (Path(__file__).absolute().parent / report_rel_path).read_text()

            #logger.debug(report_text)

            # HTTP PUT
            # The requests package attempts to auto-encode the data for transfer and fallback is latin-1
            # Specify to encode with utf-8 to avoid encoding error
            response = requests.put(url = target_url, headers = request_headers, data = report_text.encode('utf-8'))

            result_dict = response.json()
            
            #logger.debug(result_dict)

            expr = ('id' in result_dict) and (result_dict['id'] == patient_name)

            self.assertTrue(expr, "Message: {patient_name} {report_name} summarized")
    

    def test_queue_patient_doc(self):
        with self.assertRaises(Exception) as context:
            broken_function()

        for (key, report_rel_path) in report_tuples:
            patient_name, report_name = parse_patient_and_report(report_rel_path)

            target_url = f'{base_url}/queuePatientDoc/patient/{patient_name}/doc/{report_name}'
            request_headers = create_request_headers(user_token)
            # Add content-type header
            request_headers['content-type'] = 'text/plain'

            report_text = (Path(__file__).absolute().parent / report_rel_path).read_text()

            #logger.debug(report_text)

            # HTTP PUT
            # The requests package attempts to auto-encode the data for transfer and fallback is latin-1
            # Specify to encode with utf-8 to avoid encoding error
            response = requests.put(url = target_url, headers = request_headers, data = report_text.encode('utf-8'))

            result_dict = response.json()
            
            #logger.debug(result_dict)

            # {'name': 'Document Queued', 'value': 'Added patientX patientX_doc1_RAD.txt to the Text Processing Queue.'}
            expr = ('name' in result_dict) and (result_dict['value'] == f'Added {patient_name} {report_name} to the Text Processing Queue.')

            self.assertTrue(expr, "Message: {patient_name} {report_name} queued up")


    def test_summarize_patient(self):
        with self.assertRaises(Exception) as context:
            broken_function()

        for (key, report_rel_path) in report_tuples:
            patient_name, report_name = parse_patient_and_report(report_rel_path)

            target_url = f'{base_url}/summarizePatient/patient/{patient_name}'
            request_headers = create_request_headers(user_token)

            # HTTP GET
            response = requests.get(url = target_url, headers = request_headers)

            result_dict = response.json()
            
            #logger.debug(result_dict)

            expr = ('id' in result_dict) and (result_dict['id'] == patient_name)

            self.assertTrue(expr, "Message: {patient_name} summarized")


####################################################################################################
## Run test.py as script
####################################################################################################

if __name__ == '__main__':
    unittest.main()