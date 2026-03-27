const int PIN = 13;
//zet hier u RPM
const float RPM = 5;
float steps = RPM*200/60;
//schrijf hier hoeveel microsteps aanstaan
int microsteps = 16;
float halfPeriod;
float state;
float FREQ;
void setup() {
  pinMode(PIN, OUTPUT);
  FREQ = steps*microsteps;
  halfPeriod = (1000 / FREQ) / 2;  // Half period in ms
  state = 0;
  if(halfPeriod <1){
    halfPeriod = 1000000/FREQ/2;
    state = 1;
  }
}

void loop() {
  
  if(state == 0){
    digitalWrite(PIN, HIGH);
    delay(halfPeriod);
    digitalWrite(PIN, LOW);
    delay(halfPeriod);
  }else if(state == 1){
    digitalWrite(PIN, HIGH);
    delayMicroseconds(halfPeriod);
    digitalWrite(PIN, LOW);
    delayMicroseconds(halfPeriod);
  }
  
}