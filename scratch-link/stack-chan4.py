from websocket_server import WebsocketServer
import json
import base64
import time
import sys
from threading import Timer
from serial import Serial, SerialException
from serial.tools import list_ports

class StackChan:
    def __init__(self):
        self.uart = None
        self.port_name = None
    def is_connected(self):
        return self.uart != None
    def open(self):
        print("Opening %s" % self.port_name)
        self.uart = None
        try:
            self.uart = Serial(self.port_name, 115200)
        except SerialException:
            print("can't open %s" % self.port_name)
        return self.is_connected()
    def _send(self, text):
        print(text)
        self.uart.write(text.encode('utf-8'))
    def clear(self):
        if not self.uart:
            return
        self._send('*0')
    def servo(self, ch, degrees):
        if not self.uart:
            return
        if not (ch == 1 or ch == 2):
            return
        self._send('*%d,%d' % (ch, degrees))
    def say(self, message):
        if not self.uart:
            return
        self._send('*3,'+','.join(list(map(str,message))))
    def expression(self, kind):
        if not self.uart:
            return
        self._send('*4,%d' % kind)
    def receive(self):
        if not self.uart:
            return None
        try:
            r = self.uart.read_until(b'\n').strip()
        except Exception as e:
            print(e)
            return None
        if not (len(r)>0 and r[0] == 43):
            return None
        try:
            s = list(map(int,r[1:].decode('utf-8').split(',')))
        except Exception as e:
            print(e)
            return None
        tiltX = 0
        tiltY = 0
        if len(s) and s[0] == 1:
            print(s)
            tiltX = int(s[1]) * 10
            tiltY = int(s[2]) * 10
        buf = bytearray(10)
        buf[0] = tiltX // 256
        buf[1] = tiltX % 256
        buf[2] = tiltY // 256
        buf[3] = tiltY % 256
        buf[4] = 1 if int(s[3]) > 50 else 0
        return buf

class ScratchLink:
    def __init__(self):
        self.close()
    def open(self):
        self.connected = True
    def close(self):
        self.connected = False
    def is_connected(self):
        return self.connected
    def characteristicDidChange(self, server, client, buf):
        response = '{"jsonrpc":"2.0","method":"characteristicDidChange","params":{"serviceId":61445,"characteristicId":"5261da01-fa7e-42ab-850b-7c80220097cc","encoding":"base64","message":"%s"}}' % (base64.b64encode(bytes(buf)).decode('utf-8'),)
        server.send_message(client, response)
    def result(self, server, client, id, ok):
        if ok:
            response = '{"jsonrpc":"2.0","id":%d,"result":null}' % id
        else:
            response = '{"jsonrpc":"2.0","id":%d,"error":{}}' % id
        server.send_message(client, response)
    def didDiscoverPeripheral(self, server, client, name, rssi, peripheralId):
        response = '{"jsonrpc":"2.0","method":"didDiscoverPeripheral","params":{"name":"%s","rssi":%d,"peripheralId":%d}}' % (name, rssi, peripheralId)
        server.send_message(client, response)

without_sensor = False
stackchan = StackChan()
scratchlink = ScratchLink()

def update(client, server):
    time.sleep(2)
    scratchlink.characteristicDidChange(server, client, bytes(10))
    time.sleep(2)
    scratchlink.characteristicDidChange(server, client, bytes(10))
    while scratchlink.is_connected():
        if stackchan.is_connected() and not without_sensor:
            buf = stackchan.receive()
            if buf:
                scratchlink.characteristicDidChange(server, client, buf)
        else:
            scratchlink.characteristicDidChange(server, client, bytes(10))
            time.sleep(1)
    print("Update exited")

def new_client(client, server):
    print("New client connected: %d" % client['id'])

def client_left(client, server):
    print("Client disconnected: %d" % client['id'])
    scratchlink.close()

def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'
    print("Client(%d) said: %s" % (client['id'], message))
    dict = json.loads(message)
    if dict['method'] == 'discover':
        id = dict['id']
        scratchlink.result(server, client, id, True)
        scratchlink.didDiscoverPeripheral(server, client, "python", -70, 65536)
    if dict['method'] == 'connect':
        id = dict['id']
        ret = stackchan.open()
        scratchlink.result(server, client, id, ret)
        if ret:
            scratchlink.open()
    if dict['method'] == 'read':
        timer = Timer(1, update, (client, server))
        timer.start()
    if dict['method'] == 'write':
        message = base64.b64decode(dict['params']['message'])
        if message[0] == 0x81:
            stackchan.say(message[1:])
        elif message[0] == 0x82:
            for x in list(message[1:]):
                print(format(x,"05b")[::-1])
            if message[1] == 1 or message[1] == 2:
                stackchan.servo(message[1], message[2]*32 + message[3])
            elif message[1] == 4:
                stackchan.expression(message[2])
            else:
                stackchan.clear()
        id = dict['id']
        scratchlink.result(server, client, id, True)

def auto_select_port_name(port_name):
    if port_name:
        return port_name
    port_names = [port.device for port in list_ports.comports()]
    port_names.sort()
    if len(port_names) == 0:
        return None
    elif len(port_names) == 1:
        return port_names[0]
    print("Available ports:")
    for i in range(len(port_names)):
        print(" %d --> %s" % (i,port_names[i]))
    print("enter number >> ", end="")
    num = int(input())
    return port_names[num]

if __name__ == "__main__":
    port_name = auto_select_port_name(sys.argv[1] if len(sys.argv) >= 2 else None)
    if not port_name:
        print("No serial ports found")
        exit()
    stackchan.port_name = port_name
    PORT=20111
    server = WebsocketServer(port = PORT)
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()
