#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import json
import redis
import sys
import socket


class JohnyServer(object):
    """Class for processing connections between elements of Johny's avatar system"""

    def __init__(self, redis_host='localhost', redis_port=6379, redis_password='',
                 status_sending_interval=5, johny_ip='192.168.118.125', johny_port=9009):
        """Connects to local Redis server, subscribes to 'command' topic and starts
        sending system status to 'status' topic

        Args:
            host: redis server address
            port: redis server port
            password: redis server password
            status_sending_interval: interval in seconds to send system status to topic
        """
        self.redis_connection = redis.Redis(host=redis_host, port=redis_port, db=0,
                                            password=redis_password)
        self.status_sending_interval = status_sending_interval

        self.johny_ip = johny_ip
        self.johny_port = johny_port
        self.johny_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.allowed_commands_and_fields = {
            "ARM": {"arm", "x", "y", "z", "r", "p", "yw", "fingers"},
            "HEAD": {"r", "p", "y"},
            "WHEELS": {"x", "y"},
            "OPTION": {"assistanceOn"}
        }

        self.pubsub = self.redis_connection.pubsub()

        self.system_status = {}
        self.status_lock = threading.Lock()

        # Start sending system status
        self.publish_status_periodically()

        # Receiving commands in separate thread
        self.pubsub.psubscribe(**{'command': self.command_callback})
        self.pubsub.run_in_thread(sleep_time=.01)

    def send_wheels_command(self, data):
        package["x"] = -round(data['x'], 3)
        package["y"] = -round(data['y'], 3)
        self.send_to_udp(package)

    def send_head_command(self, data):
        head_package["yaw"] = round(data['y'], 3)
        head_package["pitch"] = round(data['p'], 3)
        head_package["roll"] = -round(data['r'], 3)
        self.send_to_udp(head_package)

    def send_to_udp(self, udp_package):
        self.johny_udp_socket.sendto(
            json.dumps(udp_package, ensure_ascii=False).encode("utf8"),
            (self.johny_ip, self.johny_port)
        )

    def command_callback(self, msg):
        """Callback for 'command' topic

        Args:
            msg: message received from topic
        """
        print('Command received: ', msg)
        with self.status_lock:
            try:
                command = json.loads(msg["data"])
                if command["command"] in self.allowed_commands_and_fields:
                    print(command["data"].keys())
                    print(self.allowed_commands_and_fields[command["command"]])
                    if command["data"].keys() == self.allowed_commands_and_fields[
                       command["command"]]:
                        # Echo command's data to 'status' topic
                        self.system_status[command["command"]] = command["data"]
                        # Sending commands to Johny through UDP socket
                        if command["command"] == "WHEELS":
                            self.send_wheels_command(command["data"])
                        if command["command"] == "HEAD":
                            self.send_head_command(command["data"])
                    else:
                        print("Command error: wrong fields in data!")
                else:
                    print("Error: unknown command!")
            except:
                e = sys.exc_info()[0]
                print('Error: ' + str(e))

    def publish_system_status(self):
        """Publishes status to 'status' topic"""
        with self.status_lock:
            self.redis_connection.publish('status', json.dumps(self.system_status))

    def publish_status_periodically(self):
        """Restarts timer each status_sending_interval seconds to send status to topic"""
        t = threading.Timer(self.status_sending_interval, self.publish_status_periodically)
        t.daemon = True
        t.start()
        self.publish_system_status()


if __name__ == '__main__':
    JohnyServer()
