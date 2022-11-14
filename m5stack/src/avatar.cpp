#include <M5Unified.h>
#include <Avatar.h>
#include "config.h"
#include "avatar.h"
//#include <faces/DogFace.h>

using namespace m5avatar;

const Expression expressions[] = {
  Expression::Neutral,
  Expression::Angry,
  Expression::Sleepy,
  Expression::Happy,
  Expression::Sad,
  Expression::Doubt,
};
const int expressionsSize = sizeof(expressions) / sizeof(Expression);

Avatar avatar;

void init_avatar()
{
  avatar.init();
}

void avatar_say(const char *text)
{
  avatar.setSpeechText(text);
  for (int i = 0; i < strlen(text); i ++) {
    avatar.setMouthOpenRatio(random(1, 10) * 0.1);
    delay(500);
  }
  avatar.setMouthOpenRatio(0);
  avatar.setSpeechText("");
}

void avatar_expression(int number)
{
  number = number < 0 ? 0 : number;
  number = number >= expressionsSize ? random(1, expressionsSize) : number;
  avatar.setExpression(expressions[number]);
}

void avatar_clear()
{
  avatar.setMouthOpenRatio(0);
  avatar.setExpression(expressions[0]);
}
