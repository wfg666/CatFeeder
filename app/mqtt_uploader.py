import time
import mqtt_config
from paho.mqtt import client as mqtt_client


class mqtt_uploader:
    def __init__(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        def topic_one_callback(client, userdata, message):
            print(message.topic + " " + str(message.payload))

        self.client = mqtt_client.Client(f'CF{int(time.time())}')
        self.client.on_connect = on_connect
        self.client.message_callback_add("attributes/response", topic_one_callback)
        self.client.username_pw_set(mqtt_config.user, mqtt_config.passwd)
        try:
            self.client.loop_start()
            self.client.connect(mqtt_config.host, mqtt_config.port)
        except Exception as e:
            print("MQTT连接失败", e)

    def publish(self, attribute, value):
        if not self.client.is_connected():
            print("MQTT客户端断开")
            try:
                self.client.disconnect()
                self.client.loop_stop()
                time.sleep(0.01)
                self.client.reconnect()
                self.client.loop_start()
            except Exception as e:
                print("MQTT重连失败", e)

        msg = '{"' + attribute + '" : ' + str(value) + '}'
        result = self.client.publish(mqtt_config.topic, msg)
        status = result[0]
        if status != 0:
            print(f"Failed to send MQTT message {msg}")


if __name__ == '__main__':
    m = mqtt_uploader()
    while True:
        time.sleep(5)
        t = time.time()
        print(f"publishing {t}")
        m.publish('aaa', time.time())
        print(f"published {t}")
