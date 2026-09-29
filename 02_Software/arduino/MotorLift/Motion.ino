// Stepper motion for the lift (Y) and the belt-synced plunger (X).
// Positions are tracked in steps from each axis's home switch.

long liftPos = 0;          // steps above home
long plungerPos = 0;       // steps above home (home = fully dispensed, plate on its switches)
bool liftHomed = false;
bool plungerHomed = false;

void initMotors() {
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);
  pinMode(PLUNGER_STEP_PIN, OUTPUT);
  pinMode(PLUNGER_DIR_PIN, OUTPUT);
  pinMode(LIFT_STEP_PIN, OUTPUT);
  pinMode(LIFT_DIR_PIN, OUTPUT);
  for (uint8_t i = 0; i < PLUNGER_SW_COUNT; i++) pinMode(PLUNGER_SW_PINS[i], INPUT_PULLUP);
  pinMode(LIFT_SW_PIN, INPUT_PULLUP);
}

bool liftSwitch() {
  return digitalRead(LIFT_SW_PIN) == LOW;
}

bool plungerSwitch() {
  for (uint8_t i = 0; i < PLUNGER_SW_COUNT; i++)
    if (digitalRead(PLUNGER_SW_PINS[i]) == LOW) return true;
  return false;
}

// (No `static` on these helpers: the Arduino IDE's prototype generator mishandles it.)

// Step one axis `steps` times with a trapezoidal speed profile (David Austin's step-interval
// recurrence, no per-step sqrt). If stopCheck is given, stop once it has read true on three
// consecutive steps. Returns the number of steps taken.
long stepAxis(uint8_t stepPin, uint8_t dirPin, uint8_t dirLevel, long steps,
              float vmax, float accel, bool (*stopCheck)()) {
  if (steps <= 0) return 0;
  digitalWrite(dirPin, dirLevel);
  delayMicroseconds(5);                         // DIR setup time

  const float cMin = 1e6 / vmax;                // us per step at full speed
  float c = 0.676 * sqrt(2.0 / accel) * 1e6;    // first interval
  if (c < cMin) c = cMin;
  long n = 0;                                   // steps spent accelerating
  uint8_t hits = 0;
  uint32_t next = micros();

  for (long i = 0; i < steps; i++) {
    while ((long)(micros() - next) < 0) {}
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(3);
    digitalWrite(stepPin, LOW);

    if (stopCheck) {
      hits = stopCheck() ? hits + 1 : 0;
      if (hits >= 3) return i + 1;
    }

    long remaining = steps - i - 1;
    if (remaining <= n) {                       // decelerate symmetrically
      if (remaining > 0) c = c + 2.0 * c / (4.0 * remaining - 1.0);
    } else if (c > cMin) {                      // accelerate
      n++;
      c = c - 2.0 * c / (4.0 * n + 1.0);
      if (c < cMin) c = cMin;
    }
    next += (uint32_t)c;
  }
  while ((long)(micros() - next) < 0) {}        // hold the last interval so back-to-back moves don't jerk
  return steps;
}

// ---------------------------------------------------------------- lift
float liftMm() { return liftPos / LIFT_STEPS_PER_MM; }

long liftUp(long steps, float mmS) {
  return stepAxis(LIFT_STEP_PIN, LIFT_DIR_PIN, LIFT_UP_LEVEL, steps,
                  mmS * LIFT_STEPS_PER_MM, LIFT_ACCEL_MM_S2 * LIFT_STEPS_PER_MM, nullptr);
}

long liftDown(long steps, float mmS, bool stopAtSwitch) {
  return stepAxis(LIFT_STEP_PIN, LIFT_DIR_PIN, !LIFT_UP_LEVEL, steps,
                  mmS * LIFT_STEPS_PER_MM, LIFT_ACCEL_MM_S2 * LIFT_STEPS_PER_MM,
                  stopAtSwitch ? liftSwitch : nullptr);
}

// Down to the switch fast, back off, re-approach slowly; home is where the switch closes.
bool homeLift() {
  liftHomed = false;
  const long backoff = LIFT_BACKOFF_MM * LIFT_STEPS_PER_MM;
  if (liftSwitch()) liftUp(backoff, LIFT_HOME_FAST_MM_S);
  const long maxSteps = (LIFT_TRAVEL_MM + 5) * LIFT_STEPS_PER_MM;
  liftDown(maxSteps, LIFT_HOME_FAST_MM_S, true);
  if (!liftSwitch()) return false;
  liftUp(backoff, LIFT_HOME_FAST_MM_S);
  if (liftSwitch()) return false;               // switch stuck closed
  liftDown(2 * backoff, LIFT_HOME_SLOW_MM_S, true);
  if (!liftSwitch()) return false;
  liftPos = 0;
  liftHomed = true;
  return true;
}

// Rise to `mm` (fast, then the last LIFT_SEAT_ZONE_MM at approachMmS), or descend to it.
bool moveLiftTo(float mm, float approachMmS) {
  if (!liftHomed) return false;
  if (mm < 0) mm = 0;
  if (mm > LIFT_TRAVEL_MM) mm = LIFT_TRAVEL_MM;
  long target = lround(mm * LIFT_STEPS_PER_MM);
  if (target <= 0) return lowerLiftToHome();
  if (target > liftPos) {
    long seatStart = target - (long)(LIFT_SEAT_ZONE_MM * LIFT_STEPS_PER_MM);
    if (seatStart > liftPos) liftPos += liftUp(seatStart - liftPos, LIFT_FAST_MM_S);
    liftPos += liftUp(target - liftPos, approachMmS);
  } else if (target < liftPos) {
    long moved = liftDown(liftPos - target, LIFT_FAST_MM_S, true);
    liftPos -= moved;
    if (liftSwitch()) {                          // hit home early: steps were lost going up
      liftPos = 0;
      return false;
    }
  }
  return true;
}

// Lower to home and re-zero on the switch every time, so lost steps never accumulate.
bool lowerLiftToHome() {
  if (!liftHomed) return false;
  if (liftPos > 0) liftDown(liftPos, LIFT_FAST_MM_S, true);
  if (!liftSwitch()) {                           // not there yet: creep down up to 3 mm
    liftDown(3 * LIFT_STEPS_PER_MM, LIFT_HOME_SLOW_MM_S, true);
    if (!liftSwitch()) { liftHomed = false; return false; }
  }
  liftPos = 0;
  return true;
}

// ---------------------------------------------------------------- plunger
float heldUl() { return plungerPos / PLUNGER_STEPS_PER_UL; }

long plungerUp(long steps, float v) {
  return stepAxis(PLUNGER_STEP_PIN, PLUNGER_DIR_PIN, !PLUNGER_DISPENSE_LEVEL, steps,
                  v, PLUNGER_ACCEL_STEPS_S2, nullptr);
}

long plungerDown(long steps, float v) {
  return stepAxis(PLUNGER_STEP_PIN, PLUNGER_DIR_PIN, PLUNGER_DISPENSE_LEVEL, steps,
                  v, PLUNGER_ACCEL_STEPS_S2, plungerSwitch);
}

// Same pattern as the lift. Only call with the bed lowered: homing dispenses whatever is held.
bool homePlunger() {
  plungerHomed = false;
  if (plungerSwitch()) plungerUp(PLUNGER_BACKOFF_STEPS, PLUNGER_HOME_FAST_STEPS_S);
  plungerDown(PLUNGER_HOME_MAX_UL * PLUNGER_STEPS_PER_UL, PLUNGER_HOME_FAST_STEPS_S);
  if (!plungerSwitch()) return false;
  plungerUp(PLUNGER_BACKOFF_STEPS, PLUNGER_HOME_FAST_STEPS_S);
  if (plungerSwitch()) return false;
  plungerDown(2 * PLUNGER_BACKOFF_STEPS, PLUNGER_HOME_SLOW_STEPS_S);
  if (!plungerSwitch()) return false;
  plungerPos = 0;
  plungerHomed = true;
  return true;
}

// Returns the volume actually moved (uL).
long aspirateUl(long ul) {
  if (!plungerHomed || ul <= 0) return 0;
  long room = VOLUME_MAX_UL - lround(heldUl());
  if (ul > room) ul = room;
  long steps = lround(ul * PLUNGER_STEPS_PER_UL);
  plungerPos += plungerUp(steps, PLUNGER_MAX_STEPS_S);
  return ul;
}

long dispenseUl(long ul) {
  if (!plungerHomed || ul <= 0) return 0;
  long steps = lround(ul * PLUNGER_STEPS_PER_UL);
  if (steps >= plungerPos) {                     // everything: run down to the switches
    long held = lround(heldUl());
    plungerDown(plungerPos + PLUNGER_BACKOFF_STEPS, PLUNGER_MAX_STEPS_S);
    plungerPos = 0;
    if (!plungerSwitch()) { plungerHomed = false; return 0; }   // never reached home: re-home
    return held;
  }
  long moved = plungerDown(steps, PLUNGER_MAX_STEPS_S);
  plungerPos -= moved;
  if (plungerSwitch()) plungerPos = 0;           // reached home early: re-zero
  return lround(moved / PLUNGER_STEPS_PER_UL);
}
