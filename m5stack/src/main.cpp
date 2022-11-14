#include <M5Unified.h>
#include "config.h"
#include "servo.h"
#include "parser.h"
#include "avatar.h"

void setup()
{
  M5.begin();
  UART.begin(115200);
  UART2.begin(115200, SERIAL_8N1, serial2RxPin, serial2TxPin );
  UART.println("Initializing ...");

  init_servo();
  init_avatar();

  UART.println("Starting ...");
}

void dispatch()
{
  if (numcount == 1) {
    if (numbers[0] == 0) {
      // *0
      avatar_clear();
    }
  } else if (numcount >= 2) {
    if (numbers[0] == 1 || numbers[0] == 2) {
      // *1,0
      // *1,25
      // *1,50
      // *1,60
      // *1,70
      // *1,120
      // *1,180
      // *2,50
      // *2,90
      // *2,110
      int ch = numbers[0];
      int degrees = numbers[1];
      servo_set(ch, degrees);
      UART.printf("Servo %d to %d\n", ch, degrees);
    } else if (numbers[0] == 3) {
      // *3,72,101,108,108,111
      String text;
      for (int i = 1; i < numcount; i ++) {
        text += (char) numbers[i];
      }
      text += '\0';
      avatar_say(text.c_str());
    } else if (numbers[0] == 4) {
      // *4,1
      // *4,5
      avatar_expression(numbers[1]);
    }
  }
}

void loop()
{
  if (UART.available()) {
    parse(UART);
    dispatch();
  }
  if (UART2.available()) {
    parse(UART2);
    dispatch();
  }
  delay(100);
}
