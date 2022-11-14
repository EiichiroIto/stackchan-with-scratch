import lcd
import image
import time
import uos
import sys
from Maix import GPIO
from fpioa_manager import *
from machine import UART
import pmu
from machine import UART

print("!Press A button for 3 seconds to stop the execution")

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP)

fm.register(board_info.LED_R, fm.fpioa.GPIO4)
led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
led_r.value(0)

fm.register(board_info.LED_G, fm.fpioa.GPIO5)
led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
led_g.value(1)

fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1)

time.sleep(2)

if but_a.value() == 0:
    led_r.value(1)
    sys.exit() 

lcd.init()
lcd.rotation(2)

lcd.draw_string(0, 0, "Initializing sensor", lcd.WHITE, lcd.RED)

led_r.value(1)
led_b.value(0)

import sensor
import KPU as kpu

err_counter = 0

while True:
    try:
        sensor.reset()
        break
    except:
        err_counter = err_counter + 1
        if err_counter == 20:
            lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)
        time.sleep(0.1)
        continue

sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

led_b.value(1)
led_g.value(0)

lcd.draw_string(0, 10, "Initializing kpu", lcd.WHITE, lcd.RED)

task = kpu.load(0x300000)
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)

lcd.draw_string(0, 20, "Initializing UART", lcd.WHITE, lcd.RED)

uart = UART(UART.UARTHS, 115200)

fm.register(35, fm.fpioa.UART1_TX, force=True)
fm.register(34, fm.fpioa.UART1_RX, force=True)
uart2 = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)

indicator = 1

led_r.value(1)
led_g.value(1)
led_b.value(1)

_ = uart.write(b"Start recognition\r\n")

lcd.clear()
axp192 = pmu.axp192()
axp192.__writeReg(0x91, 0x80)

try:
    while(True):
        time.sleep(0.1)
        if uart.any():
            while uart.any():
               a=uart.read()
            uart.write('!')
            uart.write(a)
            uart2.write(a)
        img = sensor.snapshot()
        bbox = kpu.run_yolo2(task, img) # Run the detection routine
        v = 0
        if bbox:
            b = bbox[0]
            _=img.draw_rectangle(b.rect())
            x = b.x() + (b.w() // 2)
            y = b.y() + (b.h() // 2)
            v = int(b.value() * 100.0)
            _ = uart.write('+1,{},{},{}\r\n'.format(x, y, v))
        else:
            _ = uart.write('+0,0,0,0\r\n')
        if not indicator:
            _ = lcd.display(img)
        if but_a.value() == 0:
            while but_a.value() == 0:
                pass
            indicator = 1 - indicator
            if indicator:
                axp192.__writeReg(0x91, 0x80)
                lcd.clear()
            else:
                axp192.__writeReg(0x91, 0xF0)
        if indicator == 1 and v > 75:
            led_b.value(0)
        else:
            led_b.value(1)

except KeyboardInterrupt:
    _ = kpu.deinit(task)
    uart.deinit()
    del uart
    uart2.deinit()
    del uart2
    sys.exit()
