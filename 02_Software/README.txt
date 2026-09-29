Software for multi-channel-pipette

Load "Main.ino" file onto arduino, it will automatically include the "MotorDrivers.ino" script if it is in the same folder.  

MotorLift sketch (arduino/MotorLift): for the motorized-lift layout (fixed head, lead-screw bed lift,
one belt-synced plunger motor). Open MotorLift.ino; settings are in Config.h.
- Wiring: plunger motor in the X slot, lift motor in the Y slot (Z and A unused).
  Plunger home sensors on X- (D9), Z- (D11) and CoolEn (A3): slotted optical endstops, one on
  each sensor post, with flags on the plunger plate; all three are needed (see the level check
  below). Set PLUNGER_SW_ACTIVE to the level your boards give when the beam is blocked (HIGH for
  most 3D-printer endstop boards, which then also fail safe when unplugged).
  Lift home switch on Y- (D10), pressed by the platform at the bottom of travel.
- Set each driver's microstep jumpers to match PLUNGER_MICROSTEPS / LIFT_MICROSTEPS (default 1/8).
- If an axis runs backwards, flip PLUNGER_DISPENSE_LEVEL or LIFT_UP_LEVEL.
- On power-up it homes the lift (down), then the plunger. The lift re-zeroes on its switch every
  time it lowers, so lost steps do not accumulate.
- Eject tips (menu): with the bed down and the tips empty, the plunger goes EJECT_MM (11.5 mm)
  past home, pushing the ejector plate down so the tips drop onto whatever is on the bed (a
  waste tray, or the rack), then comes back up and re-homes.
- Plunger level check: homing sets zero where the first plunger switch closes, then presses on
  until the other two close and shows their spread ("Homed, level 0.04"). If one closes more
  than PLUNGER_TILT_MAX_MM after the first, the plate is tilted (e.g. the belt skipped a tooth on
  one screw) or that switch is dead: it shows "Level: pin 11 late" and the plunger stays
  un-homed until Home all succeeds. PLUNGER_TILT_MAX_MM (0.10 mm) is a placeholder: home about
  ten times on the built machine, note the readings, and set it just above the largest.
- Plunger screws are T8x2 (2 mm lead) with anti-backlash nuts: 48 steps/uL, scaled from the
  original 12 steps/uL on T8x8. Volumes are capped at the tip capacity (200 uL).
- Two modes: Forward (single transfer: dispense everything, then blow out past the working zero)
  and Reverse (repeat dispenses: draws a little extra and pushes some back first, so the nut's
  slack is already taken up in the dispense direction). "Empty tips" discards what is left.
- Calibrate with CAL_FORWARD / CAL_REVERSE in Config.h: weigh water dispensed at several volumes
  (1 uL = 1 mg) and enter commanded -> measured pairs; a 0.1 mg balance is the minimum for this.
- Set the "Tip loading" / "Reservoir" heights in Config.h for your labware (placeholders).
  Heights can be trimmed on the device in 0.1 mm steps; trims are saved to EEPROM.

NOTE: The rotary encoder uses digital pins D0 and D1, which are typically reserved for serial. This may interfere with subsequent uploads. 
If so, either (1) scroll the rotary encoder 1-3 ticks and try again OR (2) Disconnect encoder during upload OR (3) adjust code to use A0 and A2 insteald of D0 and D1
