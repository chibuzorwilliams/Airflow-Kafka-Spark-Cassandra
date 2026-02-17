from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import uuid  

default_args = {
    'owner': 'chibuzorw',
    'start_date': datetime(2026, 1, 30, 4, 0)
}

def get_data():
    import requests

    print("Starting API call...") 
    url = "https://randomuser.me/api/"

    response = requests.get(url)
    response = response.json()
    response = response['results'][0]

    return response

def format_data(response):
    data = {}
    location = response['location']
    data['id'] = str(uuid.uuid4())  
    data['first_name'] = response['name']['first']
    data['last_name'] = response['name']['last']
    data['gender'] = response['gender']
    data['address'] = (f"{str(location['street']['number'])} {location['street']['name']}, "
                      f"{location['city']}, {location['state']} {location['postcode']}, {location['country']}")
    data['post_code'] = str(location['postcode']) 
    data['email'] = response['email']
    data['username'] = response['login']['username']
    data['dob'] = response['dob']['date']
    data['registered_date'] = response['registered']['date']
    data['phone'] = response['phone']
    data['picture'] = response['picture']['medium']

    return data

def stream_data():
    import json
    from kafka import KafkaProducer
    import time
    import logging

    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    curr_time = time.time()

    while True:
        if time.time() > curr_time + 60:  # Run for 1 minute
            break
        try:
            response = get_data()
            response = format_data(response)

            producer.send('users_created', json.dumps(response).encode('utf-8'))
            print(f"Sent user: {response['first_name']} {response['last_name']} (ID: {response['id']})")

        except Exception as e:
            logging.error(f'An error occurred: {e}')
            continue

with DAG('user_automation',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False) as dag:

    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )