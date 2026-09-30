# Firmware

`arduino/MotorLift` runs the pipette on an Arduino Uno with a CNC Shield V3: the plunger motor
in the shield's X slot, the lift motor in the Y slot (Z and A unused). Open `MotorLift.ino` in the
Arduino IDE; every setting is in `Config.h`. It needs the LiquidCrystal I2C library for the LCD.

## Wiring

| Part | Shield connection | Uno pin | `Config.h` |
|---|---|---|---|
| Plunger motor | X driver | D2 step, D5 dir | `PLUNGER_STEP_PIN`, `PLUNGER_DIR_PIN` |
| Lift motor | Y driver | D3 step, D6 dir | `LIFT_STEP_PIN`, `LIFT_DIR_PIN` |
| Driver enable | (shared) | D8 | `EN_PIN` |
| Plunger home sensors (3 slotted optical endstops) | X-, Z-, CoolEn | D9, D11, A3 | `PLUNGER_SW_PINS` |
| Lift home switch (micro switch) | Y- | D10 | `LIFT_SW_PIN` |
| Rotary encoder A / B | serial header | D0 / D1 | `ENCODER_A_PIN`, `ENCODER_B_PIN` |
| Rotary encoder push switch | Hold | A1 | `ENCODER_SW_PIN` |
| 20 x 4 LCD, I2C backpack at 0x27 | SDA / SCL | A4 / A5 | `LCD_ADDR` |

All three plunger sensors are needed (see the level check below). Set `PLUNGER_SW_ACTIVE` to the
level your boards give when the beam is blocked: `HIGH` for most 3D-printer endstop boards, which
then also fail safe when unplugged. Set each driver's microstep jumpers to match
`PLUNGER_MICROSTEPS` / `LIFT_MICROSTEPS` (default 1/8). If an axis runs backwards, flip
`PLUNGER_DISPENSE_LEVEL` or `LIFT_UP_LEVEL`.

The encoder uses D0 and D1, which are also the serial pins, so an upload can fail with it
connected. If it does, turn the encoder 1-3 clicks and try again, unplug it during the upload, or
move it to A0 and A2 in `Config.h`.

## What it does

- **Homing:** on power-up it homes the lift (down), then the plunger. The lift re-zeroes on its
  switch every time it lowers, so lost steps don't accumulate.
- **Plunger level check:** homing sets zero where the first plunger sensor trips, then presses
  on until the other two trip and shows their spread ("Homed, level 0.04"). If one trips more
  than `PLUNGER_TILT_MAX_MM` after the first, the plate is tilted (for example, the belt skipped a
  tooth on one screw) or that sensor is dead: it shows "Level: pin 11 late" and the plunger stays
  un-homed until *Home all* succeeds. `PLUNGER_TILT_MAX_MM` (0.10 mm) is a placeholder: home about
  ten times on the built machine, note the readings, and set it just above the largest.
- **Volumes:** the plunger screws are T8x2 (2 mm lead) with anti-backlash nuts: 48 steps/uL.
  Volumes are capped at the fitted cartridge's tip capacity (200 uL).
- **Two modes:** *Forward* (single transfer: dispense everything, then blow out past the working
  zero) and *Reverse* (repeat dispenses: it draws a little extra and pushes some back first, so
  the nut's slack is already taken up in the dispense direction). *Empty tips* discards what's
  left.
- **Labware heights:** each labware entry (`LABWARE` in `Config.h`) is the bed height where the
  tips are at working depth. The 96-well plate's is set from the model; *Tip loading* and
  *Reservoir* are placeholders to set for your rack and reservoir. Trim them on the device in
  0.1 mm steps; trims are saved to EEPROM. The lift's soft limit is `LIFT_TRAVEL_MM` (66 mm).
- **Cartridge** (menu): pick the syringe cartridge fitted. Each entry in `CARTRIDGES` has its tip
  capacity, its own calibration tables and a tip height offset added to every labware height (keep
  it 0 until measured; the 10 uL entry is a placeholder). Only allowed with the tips empty and the
  bed down; kept in EEPROM.
- **Eject tips** (menu): with the bed down and the tips empty, the plunger goes `EJECT_MM`
  (11.5 mm) past home, pushing the ejector plate down so the tips drop onto whatever is on the bed
  (a waste tray), then comes back up and re-homes.

## Calibration

Each cartridge has its own tables (`CAL_200_FORWARD`, `CAL_200_REVERSE`, and so on in
`Config.h`). Weigh water dispensed at several volumes (1 uL = 1 mg at room temperature; ISO 8655
describes the method) and enter commanded -> measured pairs. A 0.1 mg analytical balance is the
minimum for this; dye and a plate reader are an alternative.
