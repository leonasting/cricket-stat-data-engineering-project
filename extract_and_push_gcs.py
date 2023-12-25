import requests
import csv
from google.cloud import storage
import sys
import json
# Fetch keys from file - Follow sample_keys.json to create your own keys.json file
with open('keys.json') as f:
    keys = json.load(f)
url = 'https://cricbuzz-cricket.p.rapidapi.com/stats/v1/rankings/batsmen'
headers = {
    #'X-RapidAPI-Key': '1bd0a14833mshc18ed4be5953504p1236e8jsn709d3a0bc623',
    'X-RapidAPI-Key': str(keys["rapid_key"]),
    'X-RapidAPI-Host': 'cricbuzz-cricket.p.rapidapi.com'
}
params = {
    'formatType': 'odi'
}
# storage key file provided by GCP used to authenticate the user to access the GCS bucket
storage_client = storage.Client.from_service_account_json(keys["gcp_key_file"])


def upload_to_gcs(csv_filename,bucket_name = 'bkt-ranking-data'):
    # Upload the CSV file to GCS
    #bucket_name = 'bkt-ranking-data'
    #storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    destination_blob_name = f'{csv_filename}'  # The path to store in GCS

    blob = bucket.blob(destination_blob_name)# blob object to store the file in GCS
    blob.upload_from_filename(csv_filename)

    print(f"File {csv_filename} uploaded to GCS bucket {bucket_name} as {destination_blob_name}")


def fetch_data_from_api():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get('rank', [])  # Extracting the 'rank' data
        csv_filename = 'batsmen_rankings.csv'

        if data:
            field_names = ['rank', 'name', 'country']  # Specify required field names

            # Write data to CSV file with only specified field names
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                # writer.writeheader()
                for entry in data:
                    writer.writerow({field: entry.get(field) for field in field_names})

            print(f"Data fetched successfully and written to '{csv_filename}'")
            upload_to_gcs(csv_filename)
        else:
            print("No data available from the API.")
    else:
        print("Failed to fetch data:", response.status_code)



    return response
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Please provide the path to the model of the file as an argument.\n 1 - Fetching new data and pushing to GCS\
              \n 2 - Fetching data local file and pushing to gcs\n ")
        sys.exit(1)
    
    file_mode = sys.argv[1]
    if file_mode == '1':
        response = requests.get(url, headers=headers, params=params)
    elif file_mode == '2':
        csv_filename = 'batsmen_rankings.csv'
        upload_to_gcs(csv_filename)
        
    