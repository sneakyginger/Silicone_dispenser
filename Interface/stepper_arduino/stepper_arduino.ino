const int PIN = 13;
const float FREQ = 40.0;  // Frequency in Hz

void setup() {
  pinMode(PIN, OUTPUT);
}

void loop() {
  int halfPeriod = (1000 / FREQ) / 2;  // Half period in ms
  //int halfPeriod = 1/FREQ/2
  digitalWrite(PIN, HIGH);
  //delayMicroseconds()
  delay(halfPeriod);
  digitalWrite(PIN, LOW);
  //delayMicroseconds()
  delay(halfPeriod);
}