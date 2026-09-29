// Multi-channel pipette firmware for the motorized-lift layout (fixed head, lead-screw bed
// lift, belt-synced plunger). Pins, mechanics, speeds and labware heights are in Config.h.
//
// Menu (turn to move, press to select; a '*' marks a value being edited):
//   Volume      press, turn to set (10 uL steps), press to confirm
//   Aspirate    raise bed -> draw Volume -> settle -> lower bed
//   Dispense    raise bed -> push Volume (or everything held) -> settle -> lower bed
//   Labware     press to cycle presets (bed must be down)
//   Height      press, turn to trim the preset's working height by 0.1 mm (the bed follows
//               live if it is up), press to save to EEPROM
//   Raise/Lower bed (Aspirate/Dispense leave a manually raised bed up)
//   Home all    re-home lift, then plunger
#include <Wire.h>
#include <EEPROM.h>
#include <LiquidCrystal_I2C.h>
#include "Config.h"

LiquidCrystal_I2C lcd(LCD_ADDR, 20, 4);

enum Item { ITEM_VOLUME, ITEM_ASPIRATE, ITEM_DISPENSE, ITEM_LABWARE, ITEM_HEIGHT, ITEM_RAISE,
            ITEM_HOME, ITEM_COUNT };

long volumeUl = 100;
uint8_t labwareIdx = 0;
float heightTrim[LABWARE_COUNT];     // mm, per preset
bool bedUp = false;

int8_t menuIdx = 0, menuTop = 0;
int8_t editItem = -1;                // item being edited with the knob, -1 = none
char statusMsg[19] = "";             // replaces the selected row's text until the next input
bool dirty = true;

const uint8_t EEPROM_MAGIC = 0xA7;   // bump if the stored layout changes

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

// ---------------------------------------------------------------- actions
float engageMm() {
  float h = LABWARE[labwareIdx].engageMm + heightTrim[labwareIdx];
  return constrain(h, 0.0, LIFT_TRAVEL_MM);
}

bool raiseBed() {
  showStatus("Raising...");
  if (!moveLiftTo(engageMm(), LABWARE[labwareIdx].approachMmS)) {
    showStatus("Lift error: home");
    return false;
  }
  bedUp = true;
  return true;
}

bool lowerBed() {
  showStatus("Lowering...");
  bool ok = lowerLiftToHome();
  bedUp = false;
  if (!ok) showStatus("Lift error: home");
  return ok;
}

void homeAll() {
  bedUp = false;
  showStatus("Homing lift...");
  if (!homeLift()) { showStatus("Lift home FAIL"); return; }
  showStatus("Homing plunger...");
  if (!homePlunger()) { showStatus("Plunger home FAIL"); return; }
  showStatus("Homed");
}

bool ready() {
  if (liftHomed && plungerHomed) return true;
  showStatus("Home all first");
  return false;
}

void runAspirate() {
  if (!ready()) return;
  if (lround(heldUl()) + volumeUl > VOLUME_MAX_UL) { showStatus("Over capacity"); return; }
  bool stayUp = bedUp;
  if (!bedUp && !raiseBed()) return;
  showStatus("Aspirating...");
  aspirateUl(volumeUl);
  delay(SETTLE_MS);
  if (!stayUp && !lowerBed()) return;
  showStatus("Aspirate DONE");
}

void runDispense() {
  if (!ready()) return;
  if (lround(heldUl()) <= 0) { showStatus("Nothing held"); return; }
  bool stayUp = bedUp;
  if (!bedUp && !raiseBed()) return;
  showStatus("Dispensing...");
  dispenseUl(volumeUl);
  delay(SETTLE_MS);
  if (!plungerHomed) { showStatus("Plunger: home all"); return; }
  if (!stayUp && !lowerBed()) return;
  showStatus("Dispense DONE");
}

// ---------------------------------------------------------------- input
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
    case ITEM_HOME: homeAll(); break;
  }
  dirty = true;
}

void onTurn(int8_t d) {
  statusMsg[0] = '\0';
  if (editItem == ITEM_VOLUME) {
    volumeUl = constrain(volumeUl + d * VOLUME_STEP_UL, VOLUME_MIN_UL, VOLUME_MAX_UL);
  } else if (editItem == ITEM_HEIGHT) {
    float base = LABWARE[labwareIdx].engageMm;
    float t = heightTrim[labwareIdx] + d * HEIGHT_STEP_MM;
    heightTrim[labwareIdx] = constrain(base + t, 0.0, LIFT_TRAVEL_MM) - base;
    if (bedUp) moveLiftTo(engageMm(), LABWARE[labwareIdx].approachMmS);   // follow live
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
    case ITEM_LABWARE:  snprintf(buf, 21, "%c %s", sel, LABWARE[labwareIdx].name); break;
    case ITEM_HEIGHT:
      dtostrf(engageMm(), 5, 1, num);
      snprintf(buf, 21, "%c Height   %s mm", sel, num);
      break;
    case ITEM_RAISE:    snprintf(buf, 21, "%c %s", sel, bedUp ? "Lower bed" : "Raise bed"); break;
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

// ---------------------------------------------------------------- EEPROM (height trims)
void loadTrims() {
  if (EEPROM.read(0) != EEPROM_MAGIC) {
    for (uint8_t i = 0; i < LABWARE_COUNT; i++) heightTrim[i] = 0;
    return;
  }
  for (uint8_t i = 0; i < LABWARE_COUNT; i++) {
    EEPROM.get(1 + i * sizeof(float), heightTrim[i]);
    if (isnan(heightTrim[i]) || fabs(heightTrim[i]) > LIFT_TRAVEL_MM) heightTrim[i] = 0;
  }
}

void saveTrims() {
  EEPROM.update(0, EEPROM_MAGIC);
  for (uint8_t i = 0; i < LABWARE_COUNT; i++) EEPROM.put(1 + i * sizeof(float), heightTrim[i]);
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
