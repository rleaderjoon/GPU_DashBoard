import pandas as pd
import time
import subprocess
import psutil

log_file = 'GPU-Z Sensor Log.txt'
csv_file = 'gpu_data.csv'
count = 0

def clear_text_file(filename):
    """텍스트 파일의 내용을 지웁니다."""
    with open(filename, 'w') as file:
        file.write("GPU Clock [MHz], Memory Clock [MHz], GPU Temperature [C], GPU Load [%]\n")

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
        
def clear_file():
    with open(log_file, "w") as file:
        pass
    with open(csv_file, 'w') as file:
        pass
    init_csv(csv_file)
    
def init_csv(filename):
    global count
    header = ['GPU Clock [MHz]', 'Memory Clock [MHz]', 'GPU Temperature [C]', 'GPU Load [%]']
    dummy_data = []
    for i in range(61):
        dummy_data.append([0.0,0.0,0.0,0.0])
    dummy_data.append([count, count, count, count])
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
            data = last_line.split(',')[1:5] 
            for i in range(3):
                data[i] = data[i].strip()

            data = [float(x) for x in data]

            to_csv = {"GPU Clock [MHz]":data[0], "Memory Clock [MHz]" : data[1], "GPU Temperature [C]" : data[2], "GPU Load [%]" : data[3]}
            checkTime = {"GPU Clock [MHz]":count, "Memory Clock [MHz]" : count, "GPU Temperature [C]" : count, "GPU Load [%]" : count}
            df = pd.read_csv(csv_file)
            df.iloc[count] = to_csv
            df.iloc[61] = checkTime
            print(df.iloc[61,0])
            df.to_csv(csv_file, index=False)
            print(f"Appended {count} row(s) to {csv_file}")
            count += 1


            if count > 60:
                count = 0
                with open(log_file, "w") as file:
                    file.write("        Date        , GPU Clock [MHz] , Memory Clock [MHz] , GPU Temperature [캜] , GPU Load [%] , Memory Used (Dedicated) [MB] , GPU Power [W] , GPU Voltage [V] , CPU Temperature [캜] , System Memory Used [MB] ,")
        else:
            print("No data available in the log file.")
        time.sleep(1)

if __name__ == "__main__":
    main()
