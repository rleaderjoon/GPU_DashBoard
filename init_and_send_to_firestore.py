import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import csv
import time
import pandas

csv_file = "gpu_data.csv"
cred = credentials.Certificate('gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def read_gpu_data_from_csv(csv_file, count):
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        data = list(csv_reader)
        print(data)
        gpu_data = data[int(count)]
    return gpu_data

def save_to_firestore(gpu_data, count):
    #컬렉션 -> 문서 순서
    document_id = "gpu_data_" + str(int(count))
    doc_ref = db.collection("GPU_LOG").document(document_id)
    doc_ref.set({
        "GPU_CLOCK": gpu_data[0],
        "MEMORY_CLOCK": gpu_data[1],
        "GPU_TEMP": gpu_data[2],
        "GPU_LOAD": gpu_data[3],
    })

    #현재 count가 어디까지 진행됐는지 확인할 수 있게 저장
    document_id = "count"
    doc_ref = db.collection("COUNT").document(document_id)
    doc_ref.set({
        "TIME" : int(count),
    })

'''
1. create_csv에서 저장된 csv파일을 읽어 들입니다.
2. count를 통해 어디까지 진행됐는지 알 수 있어야 하기 때문에 62행을 고정적으로 읽어들입니다.
3. csv의 [count]행을 읽어들입니다.
4. 읽어들인 리스트를 Firestore에 저장합니다.
5. 1초마다 갱신할 것이기 떄문에 1초씩 정지합니다.

add. 62행을 읽는 이유는 1분마다 순환을 시킬것이기 떄문에 62행을 고정적으로 count를 저장하기 위해 할당했습니다.
add. 파이썬은 헤더를 인식하여 읽지 않기 때문에 csv보다 1행 적게 읽습니다.
'''

def main():
    while True:
        df = pandas.read_csv(csv_file)
        count = df.iloc[61,0]
        gpu_data = read_gpu_data_from_csv(csv_file, count)
        save_to_firestore(gpu_data, count)
        print("Data saved to Firestore:", gpu_data)
        time.sleep(1)

if __name__ == "__main__":
    main()