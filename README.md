# BJT-Tracer

Trace the I_c vs. V_ce characteristic of BJTs for varying I_b.

## Circuit

A DAC4813 connected to an Arduino is used to output two voltages.
CH1 is connected via a 1x buffer (LT1010) through a shunt resistor of 10 Ohms to the collector of the BJT.
CH2 is connected via a voltage-controlled current source (10mA out for 10V in) to the basis of the BJT.

The collector current I_c is measured as the voltage drop over the shunt resistor of 10 Ohms via a 10x amplifying difference amplifier.
The resulting voltage (I_c * 10 Ohms * 10) is measured using the SERAI-8-12 USB ADC with MAX186 at its input 1.
The characteristic of this ADC input is as follows:

| input voltage | ADC count |
|---------------|-----------|
| 0 | 0 |
| 1.0 | 501 |
| 2.0 | 1003 |
| 3.0 | 1506 |
| 4.0 | 2009 |
| 5.0 | 2507 |
| 6.0 | 2991 |
| 7.0 | 3427 |
| 8.0 | 3777 |
| 9.0 | 4033 |
| 9.3 | 4095 |

The voltage at the collector is therefore given as the output voltage from the DAC at channel 1 minus the voltage drop over the shunt resistor.

## Usage

The basis current is varied between 50uA and 500uA in steps of 50uA.
This corresponds to a voltage output from the DAC CH2 between 50mV and 500mV.

Then, for a constant basis current, the collector voltage is sweps once from 0V to V_c,max (configurable, default 5V) as fast as possible and then immediately set back to 0V.
Along the collector voltage sweep, the collector current is measured using the ADC.
This fast sweep prevents the BJT from overheating.

## Plotting

The main plot shows the collector current I_c over collector-emitter voltage V_ce, for different basis currents (different traces in the plot, identified via legend).

