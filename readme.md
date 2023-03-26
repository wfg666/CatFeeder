# CatFeeder

#### If you'd like to make a feeder yourself, please open an issue and I'll be more than happy to write instructions.

## 效果图
![demo](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/demo.gif "demo") 
![cloud](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/cloud.png "cloud") 

## Jetson nano配置
刷[镜像](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image)，然后
```
sudo apt install python3-opencv
sudo python3 -m pip install paho.mqtt
sudo usermod -a -G tty jetson
sudo systemctl stop nvgetty
sudo systemctl disable nvgetty
udevadm trigger
```

## 致谢
感谢weixiong的丹和亿航的丹炉。
感谢Qengineering提供的[镜像](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image)。