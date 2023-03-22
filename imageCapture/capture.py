import cv2
import time

cam = cv2.VideoCapture(0)
cv2.namedWindow('cam')
img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print('failed to grab frame')
        break
    cv2.imshow('cam', frame)
    key = cv2.waitKey(1)
    
    # if the escape key is pressed, the app will stop
    if key%256 == 27:
        print('escape hit, closing the app')
        break

    # if another key is pressed screenshots will be taken
    elif key%256 != 255:
        t = time.time()
        img_name = f'{key-48}/{key}_{img_counter}_{t}.png'
        cv2.imwrite(img_name, frame)
        print(f'photo saved to {img_name}')
        img_counter += 1

cam.release()
cv2.destroyAllWindows()
