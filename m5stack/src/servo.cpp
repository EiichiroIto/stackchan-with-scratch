#include <M5Unified.h>
#include "servo.h"

#ifndef sign
#define sign(x) (((x)==0)?0:((x)>0?1:-1))
#endif
#ifndef min
#define min(x,y) ((x)<(y)?(x):(y))
#endif
#ifndef max
#define max(x,y) ((x)>(y)?(x):(y))
#endif

const uint8_t extio_address = 0x45;

const uint8_t SETMODE = 0x00;
const uint8_t SERVO_ANGLE_8B_REG = 0x50;

const uint8_t DIGITAL_INPUT_MODE = 0;
const uint8_t DIGITAL_OUTPUT_MODE = 1;
const uint8_t ADC_INPUT_MODE = 2;
const uint8_t SERVO_CTL_MODE = 3;
const uint8_t RGB_LED_MODE = 4;

const int Num_servos = 2;
bool init_ok[Num_servos] = {false, false};
int current_pos[Num_servos];

#define I2C M5.In_I2C

void
servo_attach(int ch)
{
  int _ch = ch - 1;
  if (ch < 1 || ch > Num_servos || init_ok[_ch]) {
    return;
  }
  uint8_t mode = SERVO_CTL_MODE;
  if (!I2C.writeRegister(extio_address, SETMODE + _ch, &mode, 1, 400000)) {
    return;
  }
  init_ok[_ch] = true;
}

void
servo_detach(int ch)
{
  int _ch = ch - 1;
  if (ch < 1 || ch > Num_servos || !init_ok[_ch]) {
    return;
  }
  uint8_t mode = DIGITAL_INPUT_MODE;
  if (!I2C.writeRegister(extio_address, SETMODE + _ch, &mode, 1, 400000)) {
    return;
  }
  init_ok[_ch] = false;
}

void
init_servo()
{
  for (int ch = 1; ch <= Num_servos; ch ++) {
    init_ok[ch - 1] = false;
    servo_attach(ch);
    servo_set_force(ch, 90);
    delay(100);
    servo_detach(ch);
  }
}

void
servo_set_force(int ch, int degrees)
{
  int _ch = ch - 1;
  if (ch < 1 || ch > Num_servos || !init_ok[_ch]) {
    return;
  }
  uint8_t deg = (uint8_t) degrees;
  I2C.writeRegister(extio_address, SERVO_ANGLE_8B_REG + _ch, &deg, 1, 400000);
  current_pos[_ch] = degrees;
}

void
servo_set(int ch, int degrees)
{
  servo_attach(ch);
  int _ch = ch - 1;
  if (ch < 1 || ch > Num_servos || !init_ok[_ch]) {
    return;
  }
  degrees = max(min(degrees,180),0);
  int pos = current_pos[_ch];
  int step = sign(degrees - pos);
	for (; pos != degrees; pos += step) {
    uint8_t deg = (uint8_t) pos;
    I2C.writeRegister(extio_address, SERVO_ANGLE_8B_REG + _ch, &deg, 1, 400000);
		delay(moving_delay);
	}
  current_pos[_ch] = degrees;
  servo_detach(ch);
}
