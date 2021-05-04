#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import json
import redis
import sys


class JohnyServer(object):
    """Class for processing connections between elements of Johny's avatar system"""

    def __init__(self, host='localhost', port=6379, password='', status_sending_interval=5):
        """Connects to local Redis server, subscribes to 'command' topic and starts
        sending system status to 'status' topic

        Args:
            host: redis server address
            port: redis server port
            password: redis server password
            status_sending_interval: interval in seconds to send system status to topic
        """
        self.redis_connection = redis.Redis(host=host, port=port, db=0, password=password)
        self.status_sending_interval = status_sending_interval

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
                        self.system_status[command["command"]] = command["data"]
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
