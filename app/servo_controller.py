import serial
import time

ser = None

def feed():
    global ser
    if(not ser):
        try:
            ser=serial.Serial("/dev/ttyTHS1",115200,timeout=0)
        except Exception as e:
            print("串口初始化出错 ",e)
    
    try:
        ser.write(bytearray([0xE0,]))
        time.sleep(0.35)
        ser.write(bytearray([0x50,]))
    except Exception as e:
        print("发送失败 ",e)

if __name__ == "__main__":
    feed()