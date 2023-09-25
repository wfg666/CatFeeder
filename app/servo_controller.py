import serial
import time

ser = None

def open_serial():
    global ser
    if(not ser):
        try:
            ser=serial.Serial("/dev/ttyTHS1",115200,timeout=0)
        except Exception as e:
            print("串口初始化出错 ",e)

def feed():
    global ser
    if(not ser):
        open_serial()
    
    try:
        ser.write(bytearray([0xFF,]))
        time.sleep(0.8)
        ser.write(bytearray([0x50,]))

    except Exception as e:
        print("发送失败 ",e)

def open_door():
    global ser
    if(not ser):
        open_serial()
    
    for i in range(0x55,0xFD,1):
        ser.write(bytearray([i,]))
        time.sleep(0.01)

    time.sleep(6)
    for i in range(0xfD,0x55,-1):
        ser.write(bytearray([i,]))
        time.sleep(0.01)

    # try:
    #     ser.write(bytearray([0x6F,]))
    #     time.sleep(0.1)
    #     ser.write(bytearray([0x8F,]))
    #     time.sleep(0.1)
    #     ser.write(bytearray([0xAF,]))
    #     time.sleep(0.1)
    #     ser.write(bytearray([0xCF,]))
    #     time.sleep(0.1)
    #     ser.write(bytearray([0xEF,]))
    #     time.sleep(0.1)
    #     ser.write(bytearray([0xFF,]))
    #     time.sleep(6)
    #     ser.write(bytearray([0x85,]))
    #     time.sleep(0.2)
    #     ser.write(bytearray([0x55,]))

    # except Exception as e:
    #     print("发送失败 ",e)

if __name__ == "__main__":
    open_door()
