const int Expression_Neutral = 0;
const int Expression_Angry = 1;
const int Expression_Sleepy = 2;
const int Expression_Happy = 3;
const int Expression_Sad = 4;
const int Expression_Doubt = 5;

extern void init_avatar();
extern void avatar_say(const char *text);
extern void avatar_expression(int number);
extern void avatar_clear();
