const int Servo_ch1 = 1;
const int Servo_ch2 = 2;

const int moving_delay = 10;

extern void init_servo();
extern void servo_set_force(int ch, int degrees);
extern void servo_set(int ch, int degrees);
