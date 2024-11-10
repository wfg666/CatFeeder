# CatFeeder 猫粮自动喂食器

- [CatFeeder 猫粮自动喂食器](#catfeeder-猫粮自动喂食器)
  - [故事](#故事)
  - [搭建指南](#搭建指南)
    - [前言](#前言)
    - [硬件设备](#硬件设备)
    - [配置](#配置)
      - [舵机配置](#舵机配置)
      - [Jetson nano配置](#jetson-nano配置)
      - [软件调试](#软件调试)
      - [自启动](#自启动)
      - [为你的猫猫重新炼丹](#为你的猫猫重新炼丹)
  - [致谢](#致谢)
  
## 故事
![cats](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/cats.jpg "cats") 

左边的蓝猫叫小怪兽，一只从小娇生惯养，食欲一般的瘦猫，喜欢少吃多餐，每次吃两口就不吃了。

右边的花猫是小怪兽的老婆216，去年2月16号晚上在路边捡的小流浪。216流浪的时候挨的饿可能给她留下了毕生的阴影，在跟我爬了十层楼回家之后，她仍不敢相信自己的后半生将会荣华富贵。她会尽自己所能炫光视野里的一切食物，1个月从3.5kg吃到5.5kg，并在我出差一周之后把小怪兽饿到住院。

于是我需要一个东西来让小怪兽随时有饭吃、让216减肥。第一版的设计长这样：

![demo](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/demo.gif "demo") 

上面的摄像头拍摄猫猫的图像，可以为每只猫设定喂食策略，该喂的猫过去了就控制舵机按一下出粮。我还接入了一个[云平台](https://console.thingscloud.xyz/region/gz-3/view/amap15vaqj/sk242hobqy)可以看喂食情况。
![cloud](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/cloud.png "cloud") 

一开始效果还可以，后来小怪兽习惯了张口饭来的生活，又开始每次只吃一点。经过几次改进，小怪兽拥有了自己的猫猫别墅，别墅门口有猫脸识别门禁，别墅里有自助猫粮。216只能炫光别墅外的食物。

![house](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/house.jpg "house") 

![enter](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/enter.gif "enter") 

![leave](https://raw.githubusercontent.com/wfg666/CatFeeder/master/images/leave.gif "leave") 

## 搭建指南

### 前言

显然本项目的作者是一个水平有限的懒鬼，否则也不会拖到现在才写这些东西。本项目无法像那些优秀的开源项目一样，为各种各样的用户考虑周到并提供手把手的教程。当您决定参考本项目搭建您自己的猫食盆时，请做好心理准备，本项目中的代码杂乱、bug无数，作者完全不懂什么叫做软件工程，也没有足够的精力为您解答开发过程中的所有问题。

尽管如此，作者还是真心地希望这个项目能够帮助到您。当您在使用过程遇到问题时，欢迎在issue页面提出，作者也许会不定时地为您解答。除了做好自己解决技术问题的心理准备，作者还建议您在开始之前，能够具备一点点linux和python基础、了解深度学习的基础概念、掌握基本的电子知识并具有基本的安全意识。

### 硬件设备
以下是经验证的，作者当前使用的硬件：
* [Jetson nano开发板](https://detail.tmall.com/item.htm?id=633051843000)及其[电源](https://item.taobao.com/item.htm?id=535670251053)
* [串口舵机](https://item.taobao.com/item.htm?id=606232429568)及其[电源](https://item.taobao.com/item.htm?id=729931222716) 推荐这个舵机，在很多别的项目上用过，可以直接用开发板上的串口驱动。但很不幸，他不能和开发板共用电源。
* [摄像头](https://detail.tmall.com/item.htm?&id=721445044093) 随便什么摄像头都行，这个的好处是自带灯，坏处是灯要触摸控制，我拆开改成常亮了。
* [木质隧道](https://item.taobao.com/item.htm?id=681584104458) 建议自己另找，这款是密度板的，放屋里出甲醛。推荐使用[博世万用宝](https://item.taobao.com/item.htm?id=835470720440)开槽。
* [猫门](https://item.taobao.com/item.htm?id=643884200791)
* [塑料收纳箱](https://detail.tmall.com/item.htm?id=662803907898) 
  
以前的配件：
* [老版本中的猫食盆](https://item.taobao.com/item.htm?id=847140069636) 那个脚踩出粮的
* [STM32开发板](https://item.taobao.com/item.htm?id=620064088112) 用来驱动PWM舵机

### 配置

#### 舵机配置

如果您使用作者同款的串口舵机，请把它配置为115200波特率，然后把舵机DATA引脚插到开发板的UART TX上，共地。默认参数转得有点快，可以限制扭矩来让它温和一点。

我们用同步写指令控制舵机，所以不用担心舵机回数据烧TX，实在不放心的话可以加个二极管。

如果您坚持使用PWM舵机，建议您尝试使用nano输出PWM。但是 ~~英伟达有毒~~ ~~作者的板子坏了~~ 作者太菜了，调不通。如果您和作者一样菜，可以用单片机做一个简单的串口转PWM，[这里](https://github.com/wfg666/CatFeeder/tree/master/mcu_uart2pwm)有STM32固件源码供参考。


#### Jetson nano配置
刷[这个镜像](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image)，然后开机

#### 软件调试

```
# 串口权限问题
sudo usermod -a -G tty jetson
sudo systemctl stop nvgetty
sudo systemctl disable nvgetty
udevadm trigger

# 克隆代码
git clone git@github.com:wfg666/CatFeeder.git

# 安装依赖
cd CatFeeder
pip3 install -r requirements.txt
sudo apt install python3-opencv
```

app文件夹里的代码是运行在nano上的，你可以手动运行`python3 app/servo_controller.py`来测试你的舵机，并修改次文件让舵机可以以你喜欢的动作开门。

运行`app/app.py`来运行主程序，几秒钟后你应该能在屏幕上看到摄像头画面和一些命令行输出。这时你可以用一团黑色T恤代替猫猫来触发开门。


#### 自启动
建议使用gnome-autostart + gnome-terminal来实现自启动，这样你插上显示器可以看到摄像头画面和终端输出。可以直接在创建~/.config/autostart/gnome-terminal.desktop文件并写入以下内容：

```
[Desktop Entry]
Type=Application
Exec=gnome-terminal -- /home/jetson/CatFeeder/
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=CatFeeder
Name=CatFeeder
Comment[en_US]=Wangzong's CatFeeder
Comment=Wangzong's CatFeeder
```

#### 为你的猫猫重新炼丹

建议使用支持CUDA的独显PC进行，本项目使用resnet18作为基础模型微调，实测破卡也不会很慢。训练、测试、推理的代码和模型都在elixir文件夹里。

master版本的代码只支持单猫识别，[以前有个版本](https://github.com/wfg666/CatFeeder/commit/8416b3f140d3b62b4803fbf778c1789ce6d14f1f)支持两只猫，可以参考，你需要根据自己的需要修改代码。

imageCapture里有一些脚本（主要是GPT写的）可以帮你采集数据，采集的数据在data文件夹里。采集前记得把我的删了，也可以把我的图片当作没猫的数据用。

在elixir文件夹运行`./train.py`训练，运行`./test.py`测试。根据我的经验训练三四百轮左右的模型效果可能比较好。去output文件夹里找你选定的模型并且用它替换elixir/pretrain/maomaonet-359.pth。

初期可能会有比较多的误识别，你可以去运行app.py的路径/output里找识别出来猫猫的照片，把错题加到训练数据里再炼一炼。


## 致谢
感谢weixiong的丹和亿航的丹炉。
感谢Qengineering提供的[镜像](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image)。