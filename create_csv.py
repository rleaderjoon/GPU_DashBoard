import pandas as pd
import time
import subprocess
import psutil

log_file = 'GPU-Z Sensor Log.txt'
csv_file = 'gpu_data.csv'
count = 0

# 텍스트 파일의 내용을 초기화하는 함수
def clear_text_file(filename):
    with open(filename, 'w') as file:
        file.write("        Date        , GPU Clock [MHz] , Memory Clock [MHz] , GPU Temperature [캜] , GPU Load [%] , Memory Used (Dedicated) [MB] , GPU Power [W] , GPU Voltage [V] , CPU Temperature [캜] , System Memory Used [MB] ,")

# 파일의 마지막 줄 만을 읽고 반환하는 함수
def read_last_line():
    with open(log_file, 'r') as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-1]
            return last_line
        else:
            print("파일이 비어있습니다.")
            time.sleep(2)
            return read_last_line()
    
# txt와 csv를 초기화 하는 함수
def clear_file():
    with open(log_file, "w") as file:
        pass
    with open(csv_file, 'w') as file:
        pass
    init_csv(csv_file)
    
def init_csv(filename):
    global count

    #열 제목을 나타낼 리스트
    header = ['Count','Date', 'GPU Clock [MHz]', 'Memory Clock [MHz]', 'GPU Temperature [C]', 'GPU Load [%]', 'GPU Power [W]']
    dummy_data = []
    for i in range(60):
        dummy_data.append([0,"2024-01-01 00:00:00",0.0,0.0,0.0,0.0,0.0])
    df = pd.DataFrame(dummy_data, columns = header)
    df.to_csv(filename, index = False)

def main():
    global count
    process = subprocess.Popen("GPU-Z.exe")
    while not any(proc.name() == "GPU-Z.exe" for proc in psutil.process_iter()):
        time.sleep(1)
    clear_file()

    #gpu-z.exe의 실행을 기다립니다.
    time.sleep(2)
    '''
    1. 마지막 줄 만을 읽어들입니다.
    2. 마지막 줄의 공백을 제거합니다.
    3. string을 float으로 변환합니다.
    4. csv를 읽어들입니다.
    5. count에 맞추어 csv를 갱신합니다.
    6. 갱신을 저장합니다.

    add. 만약 60회의 기록을 끝냈다면 log는 초기화 시키고 csv는 다시 처음부터 갱신합니다.
    '''
    while True:
        last_line = read_last_line()
        if "GPU Clock [MHz]" not in last_line:
            data = last_line.split(',')[0:7] 
            for i in range(0,7):
                data[i] = data[i].strip()
            for index in range(1,7):
                data[index] = float(data[index])
            to_csv = {"Count":count, "Date" : data[0], "GPU Clock [MHz]":data[1], "Memory Clock [MHz]" : data[2], "GPU Temperature [C]" : data[3], "GPU Load [%]" : data[4], "GPU Power [W]" : data[6]}
            df = pd.read_csv(csv_file)
            df.iloc[count] = to_csv
            df.to_csv(csv_file, index=False)
            print(f"Appended {count} row(s) to {csv_file}")
            count += 1

            if count > 59:
                count = 0
                with open(log_file, "w") as file:
                    file.write("        Date        , GPU Clock [MHz] , Memory Clock [MHz] , GPU Temperature [캜] , GPU Load [%] , Memory Used (Dedicated) [MB] , GPU Power [W] , GPU Voltage [V] , CPU Temperature [캜] , System Memory Used [MB] ,")
        else:
            print("No data available in the log file.")
        time.sleep(1)

if __name__ == "__main__":
    main()
