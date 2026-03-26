const int PIN = 13;
const float FREQ = 10.0;  // Frequency in Hz

void setup() {
  pinMode(PIN, OUTPUT);
}

void loop() {
  int halfPeriod = (1000 / FREQ) / 2;  // Half period in ms
  digitalWrite(PIN, HIGH);
  delay(halfPeriod);
  digitalWrite(PIN, LOW);
  delay(halfPeriod);
}