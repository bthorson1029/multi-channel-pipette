Software for multi-channel-pipette

Load "Main.ino" file onto arduino, it will automatically include the "MotorDrivers.ino" script if it is in the same folder.  

MotorLift sketch (arduino/MotorLift): for the motorized-lift layout (fixed head, lead-screw bed lift,
one belt-synced plunger motor). Open MotorLift.ino; settings are in Config.h.
- Wiring: plunger motor in the X slot, lift motor in the Y slot (Z and A unused).
  Plunger switch(es) on X- (D9), and optionally Z- (D11) / CoolEn (A3); any one closing homes it.
  Lift home switch on Y- (D10), pressed by the platform at the bottom of travel.
- Set each driver's microstep jumpers to match PLUNGER_MICROSTEPS / LIFT_MICROSTEPS (default 1/8).
- If an axis runs backwards, flip PLUNGER_DISPENSE_LEVEL or LIFT_UP_LEVEL.
- On power-up it homes the lift (down), then the plunger. The lift re-zeroes on its switch every
  time it lowers, so lost steps do not accumulate.
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
