import subprocess
import csv
import time

# GPU-Z Sensor Log.txt 파일 경로
log_file_path = "GPU-Z Sensor Log.txt"

# CSV 파일 경로
csv_file_path = "gpu_data.csv"

# 필요한 열의 인덱스
required_columns = [1, 2, 3, 4]  # GPU Clock, Memory Clock, GPU Temperature, GPU Load

# CSV 파일 열 제목
csv_header = ["GPU Clock [MHz]", "Memory Clock [MHz]", "GPU Temperature [C]", "GPU Load [%]"]

# 최대 행 수
max_rows = 100

def read_gpu_z_log():
    """
    GPU-Z Sensor Log.txt 파일을 읽어서 필요한 정보를 추출하는 함수
    """
    gpu_data = []
    with open(log_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:  # 첫 번째 줄은 헤더이므로 제외
            data = line.strip().split(',')
            gpu_info = [data[i].strip() for i in required_columns]
            gpu_data.append(gpu_info)
    return gpu_data

def write_to_csv(data):
    """
    추출한 GPU 정보를 CSV 파일에 쓰는 함수
    """
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        for row in data:
            writer.writerow(row)

# 메인 루프
while True:
    gpu_data = read_gpu_z_log()
    write_to_csv(gpu_data[:max_rows])  # 최대 행 수 제한
    time.sleep(1)  # 1초마다 업데이트
