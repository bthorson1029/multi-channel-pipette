// Multi-channel pipette firmware for the motorized-lift layout (fixed head, lead-screw bed
// lift, belt-synced plunger). Pins, mechanics, speeds, calibration and labware are in Config.h.
//
// Menu (turn to move, press to select; a '*' marks a value being edited):
//   Volume      press, turn to set (1 uL steps below 20, 5 below 100, then 10), press to confirm
//   Aspirate    raise bed -> draw -> settle -> withdraw slowly -> lower bed
//   Dispense    Forward: dispense everything, blow out, withdraw, then reset the plunger
//               Reverse: dispense Volume (repeatable), keeping the excess in the tip
//   Mode        Forward (single transfers) / Reverse (repeat dispenses); only while empty
//   Labware     press to cycle presets (bed must be down)
//   Height      press, turn to trim the preset's working height by 0.1 mm (the bed follows
//               live if it is up), press to save to EEPROM
//   Raise/Lower bed (a manually raised bed stays up for Aspirate and reverse Dispense)
//   Empty tips  dispense everything held + blow out into the current labware (e.g. waste)
//   Eject tips  push the tips off onto whatever is on the bed (a waste tray, or the rack to return
//               them): plunger past home drives the ejector plate. Only with the bed down and the
//               tips empty; re-homes the plunger afterwards.
//   Cartridge   press to cycle the syringe cartridge fitted (tip capacity, calibration and tip
//               height come from its entry in CARTRIDGES); only with the tips empty and the bed
//               down; kept in EEPROM
//   Home all    re-home lift, then plunger. Shows "Homed, level 0.04" (spread of the plunger
//               switches in mm), or "Level: pin 11 late" if one switch closed more than
//               PLUNGER_TILT_MAX_MM after the first (plate tilted, e.g. a skipped belt tooth, or a
//               dead switch); the plunger then stays un-homed until Home all succeeds.
#include <Wire.h>
#include <EEPROM.h>
#include <LiquidCrystal_I2C.h>
#include "Config.h"

LiquidCrystal_I2C lcd(LCD_ADDR, 20, 4);

enum Item { ITEM_VOLUME, ITEM_ASPIRATE, ITEM_DISPENSE, ITEM_MODE, ITEM_LABWARE, ITEM_HEIGHT,
            ITEM_RAISE, ITEM_EMPTY, ITEM_EJECT, ITEM_CART, ITEM_HOME, ITEM_COUNT };

long volumeUl = 50;
bool reverseMode = false;
uint8_t labwareIdx = 0;
float heightTrim[LABWARE_COUNT];     // mm, per preset
uint8_t cartIdx = 0;                 // CARTRIDGES entry fitted
bool bedUp = false;

int8_t menuIdx = 0, menuTop = 0;
int8_t editItem = -1;                // item being edited with the knob, -1 = none
char statusMsg[19] = "";             // replaces the selected row's text until the next input
bool dirty = true;

const uint8_t EEPROM_MAGIC = 0xA8;   // bump if the stored layout changes

// ---------------------------------------------------------------- setup / loop
void setup() {
  lcd.init();
  lcd.backlight();
  pinMode(ENCODER_A_PIN, INPUT_PULLUP);
  pinMode(ENCODER_B_PIN, INPUT_PULLUP);
  pinMode(ENCODER_SW_PIN, INPUT_PULLUP);
  initMotors();
  loadTrims();
  homeAll();
}

void loop() {
  int8_t turn = 0;
  if (rotaryEncoder(turn)) onClick();
  if (turn) onTurn(turn);
  render();
}

// ---------------------------------------------------------------- calibration
// Commanded volume that delivers `wantUl`, by inverting a commanded->measured table
// (linear between points, extrapolated from the last segment).
float calCommand(const CalPoint *t, uint8_t n, float wantUl) {
  uint8_t i = 1;
  while (i < n - 1 && wantUl > t[i].measuredUl) i++;
  float m0 = t[i - 1].measuredUl, m1 = t[i].measuredUl;
  float c0 = t[i - 1].commandedUl, c1 = t[i].commandedUl;
  if (m1 == m0) return c0;
  return c0 + (wantUl - m0) * (c1 - c0) / (m1 - m0);
}

float commandFor(float wantUl) {
  const Cartridge &c = CARTRIDGES[cartIdx];
  if (reverseMode) return calCommand(c.calReverse, c.nReverse, wantUl);
  return calCommand(c.calForward, c.nForward, wantUl);
}

long tipCapacityUl() { return CARTRIDGES[cartIdx].capacityUl; }
float reverseExcessUl() { return CARTRIDGES[cartIdx].reverseExcessUl; }
float reversePreloadUl() { return CARTRIDGES[cartIdx].reversePreloadUl; }

// ---------------------------------------------------------------- bed
float engageMm() {
  float h = LABWARE[labwareIdx].engageMm + CARTRIDGES[cartIdx].tipOffsetMm + heightTrim[labwareIdx];
  return constrain(h, 0.0, LIFT_TRAVEL_MM);
}

bool raiseBed() {
  showStatus("Raising...");
  if (!moveLiftTo(engageMm(), LABWARE[labwareIdx].approachMmS, LIFT_FAST_MM_S)) {
    showStatus("Lift error: home");
    return false;
  }
  bedUp = true;
  return true;
}

// Leave the liquid slowly for the first WITHDRAW_MM, then drop to home (re-zeroing on it).
bool lowerBed() {
  showStatus("Lowering...");
  bool ok = moveLiftTo(liftMm() - WITHDRAW_MM, LIFT_FAST_MM_S, WITHDRAW_MM_S) && lowerLiftToHome();
  bedUp = false;
  if (!ok) showStatus("Lift error: home");
  return ok;
}

// ---------------------------------------------------------------- sequences
// Pin label for a plunger switch, as wired on the CNC shield (for status messages).
const char *swName(int8_t k) {
  static char buf[4];
  uint8_t pin = PLUNGER_SW_PINS[k];
  if (pin >= A0) snprintf(buf, sizeof(buf), "A%d", pin - A0);
  else snprintf(buf, sizeof(buf), "%d", pin);
  return buf;
}

void homeAll() {
  bedUp = false;
  showStatus("Homing lift...");
  if (!homeLift()) { showStatus("Lift home FAIL"); return; }
  showStatus("Homing plunger...");
  bool ok = homePlunger();
  char msg[19];
  if (plungerTiltMm < 0 && plungerLateSw >= 0) {     // a switch lagged the first by too much
    snprintf(msg, sizeof(msg), "Level: pin %s late", swName(plungerLateSw));
  } else if (!ok) {
    strcpy(msg, "Plunger home FAIL");
  } else {
    char mm[6];
    dtostrf(plungerTiltMm, 4, 2, mm);
    snprintf(msg, sizeof(msg), "Homed, level %s", mm);
  }
  showStatus(msg);
}

bool ready() {
  if (liftHomed && plungerHomed) return true;
  showStatus("Home all first");
  return false;
}

bool plungerFail() {
  showStatus("Plunger: home all");
  return false;
}

void runAspirate() {
  if (!ready()) return;
  float held = heldUl();
  // Draw the calibrated command (the same one the dispense uses). Reverse: plus the preload
  // (pushed back below), plus the excess if the tips are empty.
  float draw = commandFor(volumeUl);
  if (reverseMode) draw += reversePreloadUl() + (held < 0.5 ? reverseExcessUl() : 0);
  if (held + draw > tipCapacityUl()) { showStatus("Over tip capacity"); return; }
  bool stayUp = bedUp;
  if (!bedUp && !raiseBed()) return;
  for (uint8_t n = PREWET_CYCLES; n--;) {
    showStatus("Pre-wetting...");
    if (!plungerToHeld(held + draw, ASPIRATE_UL_S)) { plungerFail(); return; }
    delay(ASPIRATE_DELAY_MS);
    if (!plungerToHeld(held, DISPENSE_UL_S)) { plungerFail(); return; }
    delay(DISPENSE_DELAY_MS);
  }
  showStatus("Aspirating...");
  if (!plungerToHeld(held + draw, ASPIRATE_UL_S)) { plungerFail(); return; }
  delay(ASPIRATE_DELAY_MS);
  if (reverseMode) {                   // take up the slack in the dispense direction
    if (!plungerToHeld(held + draw - reversePreloadUl(), DISPENSE_UL_S)) { plungerFail(); return; }
    delay(DISPENSE_DELAY_MS);
  }
  if (!stayUp && !lowerBed()) return;
  showStatus("Aspirate DONE");
}

// Everything out at the current labware: dispense to the working zero, blow out, withdraw,
// and only then return the plunger (it draws air on the way back up).
bool dispenseAll(const char *doneMsg) {
  if (!bedUp && !raiseBed()) return false;
  showStatus("Dispensing...");
  if (!plungerToHeld(0, DISPENSE_UL_S)) return plungerFail();
  delay(DISPENSE_DELAY_MS);
  showStatus("Blowing out...");
  if (!plungerBlowout()) return plungerFail();
  delay(BLOWOUT_DELAY_MS);
  if (!lowerBed()) return false;
  if (!plungerReset()) return plungerFail();
  showStatus(doneMsg);
  return true;
}

void runDispense() {
  if (!ready()) return;
  float held = heldUl();
  if (held < 0.5) { showStatus("Nothing held"); return; }
  if (!reverseMode) { dispenseAll("Dispense DONE"); return; }
  float cmd = commandFor(volumeUl);
  if (held - cmd < reverseExcessUl() - 0.05) { showStatus("Low: Empty tips"); return; }
  bool stayUp = bedUp;
  if (!bedUp && !raiseBed()) return;
  showStatus("Dispensing...");
  if (!plungerToHeld(held - cmd, DISPENSE_UL_S)) { plungerFail(); return; }
  delay(DISPENSE_DELAY_MS);
  if (!stayUp && !lowerBed()) return;
  showStatus("Dispense DONE");
}

void runEject() {
  if (!ready()) return;
  if (bedUp) { showStatus("Lower bed first"); return; }
  if (heldUl() >= 0.5) { showStatus("Empty tips first"); return; }
  showStatus("Ejecting tips...");
  if (!plungerEject()) { showStatus("Eject: home FAIL"); return; }
  showStatus("Tips ejected");
}

void runEmpty() {
  if (!ready()) return;
  if (heldUl() < 0.5) { showStatus("Tips are empty"); return; }
  dispenseAll("Tips emptied");
}

// ---------------------------------------------------------------- input
long volumeStep(long v) { return v < 20 ? 1 : (v < 100 ? 5 : 10); }

void onClick() {
  statusMsg[0] = '\0';
  switch (menuIdx) {
    case ITEM_VOLUME:
      editItem = (editItem == ITEM_VOLUME) ? -1 : ITEM_VOLUME;
      break;
    case ITEM_HEIGHT:
      if (editItem == ITEM_HEIGHT) { editItem = -1; saveTrims(); showStatus("Height saved"); }
      else editItem = ITEM_HEIGHT;
      break;
    case ITEM_MODE:
      if (heldUl() >= 0.5) showStatus("Empty tips first");
      else reverseMode = !reverseMode;
      break;
    case ITEM_LABWARE:
      if (bedUp) showStatus("Lower bed first");
      else labwareIdx = (labwareIdx + 1) % LABWARE_COUNT;
      break;
    case ITEM_ASPIRATE: runAspirate(); break;
    case ITEM_DISPENSE: runDispense(); break;
    case ITEM_RAISE:
      if (!ready()) break;
      if (bedUp) { if (lowerBed()) showStatus("Bed down"); }
      else if (raiseBed()) showStatus("Bed up");
      break;
    case ITEM_EMPTY: runEmpty(); break;
    case ITEM_EJECT: runEject(); break;
    case ITEM_CART:
      if (heldUl() >= 0.5) showStatus("Empty tips first");
      else if (bedUp) showStatus("Lower bed first");
      else {
        cartIdx = (cartIdx + 1) % CARTRIDGE_COUNT;
        volumeUl = constrain(volumeUl, VOLUME_MIN_UL, tipCapacityUl());
        saveTrims();
      }
      break;
    case ITEM_HOME: homeAll(); break;
  }
  dirty = true;
}

void onTurn(int8_t d) {
  statusMsg[0] = '\0';
  if (editItem == ITEM_VOLUME) {
    long v = volumeUl + (d > 0 ? volumeStep(volumeUl) : -volumeStep(volumeUl - 1));
    volumeUl = constrain(v, VOLUME_MIN_UL, tipCapacityUl());
  } else if (editItem == ITEM_HEIGHT) {
    float base = LABWARE[labwareIdx].engageMm;
    float t = heightTrim[labwareIdx] + d * HEIGHT_STEP_MM;
    heightTrim[labwareIdx] = constrain(base + t, 0.0, LIFT_TRAVEL_MM) - base;
    if (bedUp) moveLiftTo(engageMm(), LABWARE[labwareIdx].approachMmS, LIFT_FAST_MM_S);   // follow live
  } else {
    menuIdx = (menuIdx + d + ITEM_COUNT) % ITEM_COUNT;
    if (menuIdx < menuTop) menuTop = menuIdx;
    if (menuIdx > menuTop + 3) menuTop = menuIdx - 3;
  }
  dirty = true;
}

// ---------------------------------------------------------------- display
void showStatus(const char *msg) {
  strncpy(statusMsg, msg, sizeof(statusMsg) - 1);
  statusMsg[sizeof(statusMsg) - 1] = '\0';
  dirty = true;
  render();                         // visible during blocking moves
}

void rowText(int8_t item, char *buf) {
  char sel = ' ';
  if (item == menuIdx) sel = (editItem == item) ? '*' : '>';
  char num[8];
  if (item == menuIdx && statusMsg[0]) {
    snprintf(buf, 21, "%c %s", sel, statusMsg);
  } else switch (item) {
    case ITEM_VOLUME:   snprintf(buf, 21, "%c Volume    %4ld uL", sel, volumeUl); break;
    case ITEM_ASPIRATE: snprintf(buf, 21, "%c Aspirate", sel); break;
    case ITEM_DISPENSE: snprintf(buf, 21, "%c Dispense  held %3ld", sel, lround(heldUl())); break;
    case ITEM_MODE:     snprintf(buf, 21, "%c Mode: %s", sel, reverseMode ? "Reverse" : "Forward"); break;
    case ITEM_LABWARE:  snprintf(buf, 21, "%c %s", sel, LABWARE[labwareIdx].name); break;
    case ITEM_HEIGHT:
      dtostrf(engageMm(), 5, 1, num);
      snprintf(buf, 21, "%c Height   %s mm", sel, num);
      break;
    case ITEM_RAISE:    snprintf(buf, 21, "%c %s", sel, bedUp ? "Lower bed" : "Raise bed"); break;
    case ITEM_EMPTY:    snprintf(buf, 21, "%c Empty tips", sel); break;
    case ITEM_EJECT:    snprintf(buf, 21, "%c Eject tips", sel); break;
    case ITEM_CART:     snprintf(buf, 21, "%c Cart %s", sel, CARTRIDGES[cartIdx].name); break;
    case ITEM_HOME:     snprintf(buf, 21, "%c Home all", sel); break;
    default:            buf[0] = '\0';
  }
  size_t n = strlen(buf);                      // pad so old characters are overwritten
  while (n < 20) buf[n++] = ' ';
  buf[20] = '\0';
}

void render() {
  if (!dirty) return;
  char buf[21];
  for (uint8_t r = 0; r < 4; r++) {
    rowText(menuTop + r, buf);
    lcd.setCursor(0, r);
    lcd.print(buf);
  }
  dirty = false;
}

// ---------------------------------------------------------------- EEPROM (height trims, cartridge)
const int EEPROM_CART_ADDR = 1 + LABWARE_COUNT * sizeof(float);

void loadTrims() {
  if (EEPROM.read(0) != EEPROM_MAGIC) {
    for (uint8_t i = 0; i < LABWARE_COUNT; i++) heightTrim[i] = 0;
    cartIdx = 0;
    return;
  }
  for (uint8_t i = 0; i < LABWARE_COUNT; i++) {
    EEPROM.get(1 + i * sizeof(float), heightTrim[i]);
    if (isnan(heightTrim[i]) || fabs(heightTrim[i]) > LIFT_TRAVEL_MM) heightTrim[i] = 0;
  }
  cartIdx = EEPROM.read(EEPROM_CART_ADDR);
  if (cartIdx >= CARTRIDGE_COUNT) cartIdx = 0;
}

void saveTrims() {
  EEPROM.update(0, EEPROM_MAGIC);
  for (uint8_t i = 0; i < LABWARE_COUNT; i++) EEPROM.put(1 + i * sizeof(float), heightTrim[i]);
  EEPROM.update(EEPROM_CART_ADDR, cartIdx);
}

// ---------------------------------------------------------------- encoder (from the original)
bool rotaryEncoder(int8_t &delta) {
  delta = 0;
  enum {STATE_LOCKED, STATE_TURN_RIGHT_START, STATE_TURN_RIGHT_MIDDLE, STATE_TURN_RIGHT_END,
        STATE_TURN_LEFT_START, STATE_TURN_LEFT_MIDDLE, STATE_TURN_LEFT_END, STATE_UNDECIDED};
  static uint8_t encoderState = STATE_LOCKED;

  bool a = !digitalRead(ENCODER_A_PIN);
  bool b = !digitalRead(ENCODER_B_PIN);
  bool s = !digitalRead(ENCODER_SW_PIN);

  static bool switchState = s;

  switch (encoderState) {
    case STATE_LOCKED:
      if (a && b) encoderState = STATE_UNDECIDED;
      else if (!a && b) encoderState = STATE_TURN_LEFT_START;
      else if (a && !b) encoderState = STATE_TURN_RIGHT_START;
      else encoderState = STATE_LOCKED;
      break;

    case STATE_TURN_RIGHT_START:
      if (a && b) encoderState = STATE_TURN_RIGHT_MIDDLE;
      else if (!a && b) encoderState = STATE_TURN_RIGHT_END;
      else if (a && !b) encoderState = STATE_TURN_RIGHT_START;
      else { encoderState = STATE_LOCKED; }
      break;

    case STATE_TURN_RIGHT_MIDDLE:
    case STATE_TURN_RIGHT_END:
      if (a && b) encoderState = STATE_TURN_RIGHT_MIDDLE;
      else if (!a && b) encoderState = STATE_TURN_RIGHT_END;
      else if (a && !b) encoderState = STATE_TURN_RIGHT_START;
      else { encoderState = STATE_LOCKED; delta = -1; }
      break;

    case STATE_TURN_LEFT_START:
      if (a && b) encoderState = STATE_TURN_LEFT_MIDDLE;
      else if (!a && b) encoderState = STATE_TURN_LEFT_START;
      else if (a && !b) encoderState = STATE_TURN_LEFT_END;
      else { encoderState = STATE_LOCKED; }
      break;

    case STATE_TURN_LEFT_MIDDLE:
    case STATE_TURN_LEFT_END:
      if (a && b) encoderState = STATE_TURN_LEFT_MIDDLE;
      else if (!a && b) encoderState = STATE_TURN_LEFT_START;
      else if (a && !b) encoderState = STATE_TURN_LEFT_END;
      else { encoderState = STATE_LOCKED; delta = 1; }
      break;

    case STATE_UNDECIDED:
      if (a && b) encoderState = STATE_UNDECIDED;
      else if (!a && b) encoderState = STATE_TURN_RIGHT_END;
      else if (a && !b) encoderState = STATE_TURN_LEFT_END;
      else encoderState = STATE_LOCKED;
      break;
  }

  // simple debounce for switch
  uint32_t current_time = millis();
  static uint32_t switch_time = 0;
  const uint32_t bounce_time = 30;
  bool back = false;
  if (current_time - switch_time >= bounce_time) {
    if (switchState != s) {
      switch_time = current_time;
      back = s;
      switchState = s;
    }
  }
  return back;
}
