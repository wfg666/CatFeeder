# CatFeeder

#### If you'd like to make a feeder yourself, please open an issue and I'll be more than happy to write instructions.

## 效果图

## Jetson nano配置
刷(镜像)[https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image]
sudo apt install python3-opencv
sudo usermod -a -G tty jetson
sudo systemctl stop nvgetty
sudo systemctl disable nvgetty
udevadm trigger


## 致谢
感谢weixiong提供的丹和亿航提供的丹炉。
感谢Qengineering提供的(镜像)[https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image]