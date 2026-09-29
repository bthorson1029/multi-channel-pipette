// Configuration for the motorized-lift layout: fixed pipette head, lead-screw bed lift,
// belt-synced plunger (one motor drives all four plunger screws).
//
// Hardware: Arduino Uno + CNC Shield V3, 20x4 I2C LCD, rotary encoder with push switch.
//   X slot -> plunger motor      Y slot -> lift motor      Z and A slots -> unused
// Set each driver's microstepping jumpers to match *_MICROSTEPS below.
#pragma once
#include <Arduino.h>

// ---------------------------------------------------------------- pins (CNC Shield V3)
const uint8_t EN_PIN           = 8;    // shared driver enable, LOW = enabled
const uint8_t PLUNGER_STEP_PIN = 2;    // X
const uint8_t PLUNGER_DIR_PIN  = 5;
const uint8_t LIFT_STEP_PIN    = 3;    // Y
const uint8_t LIFT_DIR_PIN     = 6;

// Limit switches: normally-open to GND, read with INPUT_PULLUP (LOW = pressed).
// The plunger keeps three of the original corner switches (X-, Z-, CoolEn); any one of them
// homes it, since the belt keeps the plate level. The fourth original switch moves to the
// lift's home position on Y-.
const uint8_t PLUNGER_SW_PINS[] = {9, 11, A3};
const uint8_t PLUNGER_SW_COUNT  = sizeof(PLUNGER_SW_PINS) / sizeof(PLUNGER_SW_PINS[0]);
const uint8_t LIFT_SW_PIN       = 10;

// UI (unchanged from the original build). D0/D1 are the serial pins: if an upload fails,
// turn the encoder a few clicks or unplug it during the upload.
const uint8_t ENCODER_A_PIN = 0;
const uint8_t ENCODER_B_PIN = 1;
const uint8_t ENCODER_SW_PIN = A1;
const uint8_t LCD_ADDR = 0x27;

// ---------------------------------------------------------------- directions
// Flip these if an axis moves the wrong way (depends on motor wiring and mounting).
const uint8_t PLUNGER_DISPENSE_LEVEL = HIGH;   // DIR level that moves the plunger plate down
const uint8_t LIFT_UP_LEVEL          = HIGH;   // DIR level that raises the bed

// ---------------------------------------------------------------- mechanics
const uint16_t MOTOR_STEPS        = 200;   // 1.8 deg steppers
const uint8_t  PLUNGER_MICROSTEPS = 8;     // X-slot jumpers
const uint8_t  LIFT_MICROSTEPS    = 8;     // Y-slot jumpers
const float    LIFT_LEAD_MM       = 2.0;   // T8x2 lead screws on the lift

// Carried over from the original firmware (T8x8 screws, same microstepping; the 20T:20T belt
// is 1:1). Calibrate by weighing dispensed water: 1 uL = 1 mg.
const float PLUNGER_STEPS_PER_UL = 12.0;
const float LIFT_STEPS_PER_MM    = MOTOR_STEPS * (float)LIFT_MICROSTEPS / LIFT_LEAD_MM;

const float LIFT_TRAVEL_MM = 46.0;         // soft limit above home (Blender model: 45.9 mm)
const long  VOLUME_MIN_UL  = 10;
const long  VOLUME_MAX_UL  = 990;          // most the syringes will hold in total
const long  VOLUME_STEP_UL = 10;

// ---------------------------------------------------------------- speeds (all trapezoidal)
const float LIFT_FAST_MM_S       = 6.0;    // travel moves
const float LIFT_ACCEL_MM_S2     = 30.0;
const float LIFT_SEAT_ZONE_MM    = 4.0;    // final approach at the labware's slow speed
const float LIFT_HOME_FAST_MM_S  = 4.0;
const float LIFT_HOME_SLOW_MM_S  = 0.5;
const float LIFT_BACKOFF_MM      = 2.0;

const float PLUNGER_MAX_STEPS_S   = 900.0;  // about the original 1.1 ms/step
const float PLUNGER_ACCEL_STEPS_S2 = 4000.0;
const float PLUNGER_HOME_FAST_STEPS_S = 600.0;
const float PLUNGER_HOME_SLOW_STEPS_S = 150.0;
const long  PLUNGER_BACKOFF_STEPS = 120;    // 10 uL
const float PLUNGER_HOME_MAX_UL   = 1100;   // give up homing after this much travel

const unsigned int SETTLE_MS = 400;        // let liquid follow the plunger before moving the bed

// ---------------------------------------------------------------- labware
// engageMm = bed height above home where the tips are at working depth.
// approachMmS = speed for the last LIFT_SEAT_ZONE_MM of the rise.
// Heights can be trimmed on the device ("Height" item); trims are kept in EEPROM.
struct Labware {
  const char *name;     // <= 18 characters
  float engageMm;
  float approachMmS;
};
const Labware LABWARE[] = {
  {"96-well plate", 45.9, 2.0},   // 15 mm tray + SBS plate: tips 9 mm into the wells
  {"Tip loading",   40.0, 0.8},   // PLACEHOLDER: set where the tips finish seating on your rack
  {"Reservoir",     40.0, 2.0},   // PLACEHOLDER: set for your reservoir
};
const uint8_t LABWARE_COUNT = sizeof(LABWARE) / sizeof(LABWARE[0]);
const float   HEIGHT_STEP_MM = 0.1;

// ---------------------------------------------------------------- shared declarations
// Motion.ino
void initMotors();
bool liftSwitch();
bool plungerSwitch();
long stepAxis(uint8_t stepPin, uint8_t dirPin, uint8_t dirLevel, long steps,
              float vmax, float accel, bool (*stopCheck)());
bool homeLift();
bool homePlunger();
bool moveLiftTo(float mm, float approachMmS);
bool lowerLiftToHome();
long aspirateUl(long ul);
long dispenseUl(long ul);
float liftMm();
float heldUl();
extern bool liftHomed, plungerHomed;
// MotorLift.ino
void showStatus(const char *msg);
