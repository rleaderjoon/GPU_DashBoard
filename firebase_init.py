import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import csv
import time

# Firebase Admin SDK 비공개 키 파일 경로 설정
cred = credentials.Certificate('gpu-dashboard-d0c06-firebase-adminsdk-iv3bm-f0e5f41465.json')

# Firebase 프로젝트 초기화
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 초기화
db = firestore.client()

# Firestore에 1초마다 CSV의 마지막행을 읽어서 업로드
target = db.collection("GPU_LOG").document()
target.set({
    "name": "John Doe",
})

# CSV 파일에서 마지막 행 읽기
def read_gpu_data_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        data = list(csv_reader)
        gpu_data = data[-1]
    return gpu_data

# Firestore에 데이터 저장
def save_to_firestore(gpu_data):
    # GPU_LOG 컬렉션에 저장할 문서 ID 지정
    document_id = "gpu_data"
    doc_ref = db.collection("GPU_LOG").document(document_id)
    doc_ref.set({
        "GPU_CLOCK": gpu_data[0],  # 적절한 데이터 인덱스로 수정
        "MEMORY_CLOCK": gpu_data[1],
        "GPU_TEMP": gpu_data[2],
    })

def main():
    csv_file = "gpu_data.csv"
    while True:
        last_row = read_gpu_data_from_csv(csv_file)
        save_to_firestore(last_row)
        print("Data saved to Firestore:", last_row)
        time.sleep(1)  # 1초 대기 후 다음 반복

if __name__ == "__main__":
    main()