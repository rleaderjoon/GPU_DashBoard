import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
import pandas as pd
import schedule

csv_file = "gpu_data.csv"
cred = credentials.Certificate('gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_to_firestore(collection_name):
    #컬렉션 -> 문서 순서
    data = pd.read_csv(csv_file)

    for index, row in data.iterrows():
        data = {
            'Count': row['Count'],
            'Date': row['Date'],
            'GPU Clock [MHz]': row['GPU Clock [MHz]'],
            'Memory Clock [MHz]': row['Memory Clock [MHz]'],
            'GPU Temperature [C]': row['GPU Temperature [C]'],
            'GPU Load [%]': row['GPU Load [%]'],
            'GPU Power [W]': row['GPU Power [W]']
        }
        doc_ref = db.collection(collection_name).document(str(row['Count']))
        doc_ref.set(data)

def main():
    while True:
        save_to_firestore("csvLog")
        print("Data saved to Firestore:")
        # 단위가 초?
        time.sleep(60)

if __name__ == "__main__":
    main()