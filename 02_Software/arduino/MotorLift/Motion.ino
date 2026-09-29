// Stepper motion for the lift (Y) and the belt-synced plunger (X).
// Positions are tracked in steps from each axis's home switch.

long liftPos = 0;          // steps above home
long plungerPos = 0;       // steps above the switches ("second stop"); see plungerWorkZero()
int8_t plungerLastDir = 0; // +1 up, -1 down, 0 unknown (for backlash compensation)
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

// Rise to `mm` (fast, then the last LIFT_SEAT_ZONE_MM at approachMmS), or descend at downMmS.
bool moveLiftTo(float mm, float approachMmS, float downMmS) {
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
    long moved = liftDown(liftPos - target, downMmS, true);
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
// Positions are steps above the switches. The working zero ("first stop") is BLOWOUT_UL above
// them; "held" is liquid (and, in reverse mode, excess) drawn above the working zero.
const long PLUNGER_BACKLASH_STEPS = lround(BACKLASH_UL * PLUNGER_STEPS_PER_UL);
const float PLUNGER_ACCEL_STEPS_S2 = PLUNGER_ACCEL_UL_S2 * PLUNGER_STEPS_PER_UL;

long plungerWorkZero() { return lround(BLOWOUT_UL * PLUNGER_STEPS_PER_UL); }

float heldUl() {
  long h = plungerPos - plungerWorkZero();
  return h > 0 ? h / PLUNGER_STEPS_PER_UL : 0;
}

long plungerUp(long steps, float ulPerS) {
  return stepAxis(PLUNGER_STEP_PIN, PLUNGER_DIR_PIN, !PLUNGER_DISPENSE_LEVEL, steps,
                  ulPerS * PLUNGER_STEPS_PER_UL, PLUNGER_ACCEL_STEPS_S2, nullptr);
}

long plungerDown(long steps, float ulPerS) {
  return stepAxis(PLUNGER_STEP_PIN, PLUNGER_DIR_PIN, PLUNGER_DISPENSE_LEVEL, steps,
                  ulPerS * PLUNGER_STEPS_PER_UL, PLUNGER_ACCEL_STEPS_S2, plungerSwitch);
}

// Move to an absolute position. On a direction change, first take up BACKLASH_UL (not counted).
// Downward moves always stop on the switches; hitting them early re-zeroes and returns false.
bool plungerMoveTo(long target, float ulPerS) {
  long delta = target - plungerPos;
  if (delta == 0) return true;
  int8_t dir = delta > 0 ? 1 : -1;
  long lash = (plungerLastDir != 0 && dir != plungerLastDir) ? PLUNGER_BACKLASH_STEPS : 0;
  plungerLastDir = dir;
  if (dir > 0) {
    plungerUp(lash, ulPerS);
    plungerPos += plungerUp(delta, ulPerS);
    return true;
  }
  if (lash) plungerDown(lash, ulPerS);
  long moved = plungerDown(-delta, ulPerS);
  plungerPos -= moved;
  if (plungerSwitch()) {                         // at the switches: that is position 0
    bool expected = (target <= 0);
    plungerPos = 0;
    return expected;
  }
  return true;
}

// Same pattern as the lift, then up to the working zero. Only call with the bed lowered:
// homing dispenses whatever is held.
bool homePlunger() {
  plungerHomed = false;
  const long backoff = lround(PLUNGER_BACKOFF_UL * PLUNGER_STEPS_PER_UL);
  if (plungerSwitch()) plungerUp(backoff, PLUNGER_HOME_FAST_UL_S);
  plungerDown(PLUNGER_HOME_MAX_UL * PLUNGER_STEPS_PER_UL, PLUNGER_HOME_FAST_UL_S);
  if (!plungerSwitch()) return false;
  plungerUp(backoff, PLUNGER_HOME_FAST_UL_S);
  if (plungerSwitch()) return false;
  plungerDown(2 * backoff, PLUNGER_HOME_SLOW_UL_S);
  if (!plungerSwitch()) return false;
  plungerPos = 0;
  plungerLastDir = -1;
  plungerHomed = true;
  return plungerReset();
}

// Move so that `ul` is held above the working zero.
bool plungerToHeld(float ul, float ulPerS) {
  if (!plungerHomed) return false;
  if (ul < 0) ul = 0;
  if (ul > TIP_CAPACITY_UL) ul = TIP_CAPACITY_UL;
  bool ok = plungerMoveTo(plungerWorkZero() + lround(ul * PLUNGER_STEPS_PER_UL), ulPerS);
  if (!ok) plungerHomed = false;                 // reached the switches unexpectedly
  return ok;
}

// Push out the last drop: from wherever it is down to the switches ("second stop").
bool plungerBlowout() {
  if (!plungerHomed) return false;
  plungerLastDir = -1;
  plungerDown(plungerPos + lround(PLUNGER_BACKOFF_UL * PLUNGER_STEPS_PER_UL), BLOWOUT_UL_S);
  if (!plungerSwitch()) { plungerHomed = false; return false; }
  plungerPos = 0;
  return true;
}

// Back up to the working zero (draws air: tips must be out of the liquid).
bool plungerReset() {
  return plungerMoveTo(plungerWorkZero(), DISPENSE_UL_S);
}
