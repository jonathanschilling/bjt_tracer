# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BJT curve tracer: measures and plots I_c vs. V_ce characteristics of bipolar junction transistors for varying base currents (I_b). The system uses two hardware peripherals controlled from Python:

1. **DAC4813** (`dac4813.py`) — 4-channel 12-bit DAC on an Arduino, accessed via serial (pyserial). CH1 drives collector voltage (via LT1010 buffer + 10Ω shunt), CH2 drives base current (via V-to-I converter, 10mA/10V).
2. **SERUSB** (`serusb.py`) — Python replacement for a legacy Delphi DLL. Communicates with a Cypress AN2131 EZ-USB device hosting a MAX186 8-channel 12-bit ADC, accessed via pyusb. Uploads 8051 firmware on init, then reads ADC values via USB vendor requests.

## Dependencies

- `pyserial` — for DAC4813 serial communication
- `pyusb` — for SERUSB USB communication

## Hardware Details

- DAC value range: 0x000 (-10V) to 0xFFF (+10V), 0x800 = 0V
- ADC (MAX186): 12-bit, 0–4095 counts. Input 1 reads collector current (after 10× diff amp on 10Ω shunt). ADC saturates around 9.3V (4095 counts); response is nonlinear above ~6V.
- Base current sweep: 50µA–500µA in 50µA steps (DAC CH2 outputs 50mV–500mV)
- Collector voltage: swept 0V to configurable V_c,max (default 5V), fast sweep to prevent BJT overheating

## Running

Both modules have `__main__` self-tests:
```
python serusb.py    # uploads firmware, reads all 8 ADC channels
python dac4813.py   # (no self-test block currently)
```

Linux udev rule may be needed for SERUSB:
```
SUBSYSTEM=="usb", ATTR{idVendor}=="0547", ATTR{idProduct}=="2131", MODE="0666"
```
