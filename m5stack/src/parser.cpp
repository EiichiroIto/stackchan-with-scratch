#include <M5Unified.h>
#include "config.h"
#include "parser.h"

const int max_number = 100;
int numbers[max_number];
int numcount = 0;

void add_number(int v)
{
  if (numcount >= max_number) {
    return;
  }
  numbers[numcount++] = v;
}

void skip_eol(HardwareSerial &serial)
{
  while (serial.available()) {
    serial.read();
  }
}

void parse(HardwareSerial &serial)
{
  bool flag = false;
  int v = 0;
  int c = 0;
  numcount = 0;
  c = serial.read();
  if (c != '*') {
    serial.printf("invalid start char=%d\r\n", c);
    skip_eol(serial);
    return;
  }
  while (serial.available()) {
    int c = serial.read();
    if (c >= '0' && c <= '9') {
      flag = true;
      v = v * 10 + c - '0';
    } else if (c == ',') {
      if (flag) {
        add_number(v);
        v = 0;
        flag = false;
      }
    }
  }
  if (flag) {
    add_number(v);
  }
}
