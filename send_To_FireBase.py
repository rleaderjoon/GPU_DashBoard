import time
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Firebase 관리자 SDK 초기화
cred = credentials.Certificate("gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://https://gpu-dashboard-d0c06.firebaseio.com/'
})

# CSV 파일에서 데이터를 읽는 함수
def read_csv(filename):
    data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

# Firebase에 데이터를 업데이트하는 함수
def update_firebase(data):
    ref = db.reference('/path/to/your/data/in/firebase')
    ref.set(data)

# CSV 파일의 경로
csv_filename = 'gpu_data.csv'

# 1초마다 데이터를 업데이트
while True:
    csv_data = read_csv(csv_filename)
    update_firebase(csv_data)
    time.sleep(1)
