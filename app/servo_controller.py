import serial
import time

ser = None

def int16_to_sb_feetech_int16(x):
    if x < 0 :
        return ((0x8000 | -x) & 0xFFFF).to_bytes(2, byteorder='little', signed=False) 
    else :
        return x.to_bytes(2, byteorder='little', signed=True)


def set_pos(pos):
    global ser
    if(not ser):
        try:
            ser=serial.Serial("/dev/ttyTHS1",115200,timeout=0)
            # ser=serial.Serial("/dev/ttyUSB0",115200,timeout=0)
        except Exception as e:
            print("串口初始化出错 ",e)


    pkt = bytearray([0xFF, 0xFF, 0xFE, 13, 0x83, 0x2A, 2, 1, 0, 0, 2, 0, 0, 3, 0, 0])

    pkt[8:10] = int16_to_sb_feetech_int16(pos)
    pkt[11:13] = int16_to_sb_feetech_int16(pos)
    pkt[14:16] = int16_to_sb_feetech_int16(pos)

    cs = 0
    for i in range(2, pkt[3] + 3):
        cs += pkt[i]
    pkt.append(~cs & 0xFF)  # Append checksum

    try:
        ser.write(pkt)
    except Exception as e:
        print("发送失败 ",e)
        

def open_door():
    set_pos(2240)
    time.sleep(7)
    set_pos(3200)


if __name__ == "__main__":
    open_door()
