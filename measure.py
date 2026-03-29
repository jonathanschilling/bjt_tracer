"""
BJT curve tracer measurement script.

Sweeps base current (I_b) and collector voltage (V_ce) to measure
the I_c vs V_ce output characteristics of a BJT.

Usage:
    python measure.py --port /dev/ttyACM0 --vc-max 5.0
"""

import argparse
import json
import time

import numpy as np
import matplotlib.pyplot as plt

import serusb
from dac4813 import DAC4813

# ADC calibration table from README (SERAI-8-12 with MAX186, input 1)
ADC_CAL_COUNTS = np.array([0, 501, 1003, 1506, 2009, 2507, 2991, 3427, 3777, 4033, 4095])
ADC_CAL_VOLTAGE = np.array([0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 9.3])

SHUNT_RESISTANCE = 10.0  # Ohms
DIFF_AMP_GAIN = 10.0     # 10x difference amplifier
IB_TO_VOLTAGE = 1000.0   # V-to-I source: 10 mA / 10 V = 1 mA/V → I_b(A) * 1000 = V


def adc_count_to_voltage(count):
    """Convert ADC count (0–4095) to voltage using calibration table."""
    return np.interp(count, ADC_CAL_COUNTS, ADC_CAL_VOLTAGE)


def voltage_to_dac(voltage):
    """Convert voltage (-10 V to +10 V) to 12-bit DAC value."""
    value = int((voltage + 10.0) * 0xFFF / 20.0)
    return max(0, min(0xFFF, value))


def measure_sweep(dac, vc_max, n_steps):
    """Sweep collector voltage from 0 to vc_max and measure I_c.

    Returns (v_ce_list, ic_ma_list) where I_c is in milliamps.
    Sets DAC CH1 back to 0 V immediately after the sweep.
    """
    v_ce_list = []
    ic_ma_list = []

    for i in range(n_steps + 1):
        v_dac = vc_max * i / n_steps
        dac.set(1, voltage_to_dac(v_dac))

        adc_count = serusb.AD(1)
        v_adc = adc_count_to_voltage(adc_count)
        ic = v_adc / (SHUNT_RESISTANCE * DIFF_AMP_GAIN)  # Amps
        v_ce = v_dac - ic * SHUNT_RESISTANCE               # Volts

        v_ce_list.append(v_ce)
        ic_ma_list.append(ic * 1000.0)

    # Immediately return to 0 V to prevent BJT overheating
    dac.set(1, voltage_to_dac(0.0))

    return v_ce_list, ic_ma_list


def main():
    parser = argparse.ArgumentParser(description="BJT Curve Tracer")
    parser.add_argument("--port", default="/dev/ttyACM0",
                        help="DAC4813 serial port (default: /dev/ttyACM0)")
    parser.add_argument("--vc-max", type=float, default=5.0,
                        help="Maximum collector voltage in V (default: 5.0)")
    parser.add_argument("--steps", type=int, default=100,
                        help="Number of DAC steps per sweep (default: 100)")
    parser.add_argument("--output", default=None,
                        help="Save plot to file (e.g. plot.png)")
    parser.add_argument("--save-data", default=None,
                        help="Save measurement data to JSON file")
    args = parser.parse_args()

    # Initialize hardware
    print("Initializing ADC (SERUSB)...")
    serusb.INIT()

    print(f"Opening DAC on {args.port}...")
    with DAC4813(args.port) as dac:
        print(f"DAC: {dac.identify()}")
        dac.reset()

        results = {}

        for ib_ua in range(50, 550, 50):
            ib = ib_ua * 1e-6
            ib_voltage = ib * IB_TO_VOLTAGE

            dac.set(2, voltage_to_dac(ib_voltage))
            time.sleep(0.05)  # let base current settle

            v_ce, ic_ma = measure_sweep(dac, args.vc_max, args.steps)
            results[ib_ua] = (v_ce, ic_ma)

            print(f"  I_b = {ib_ua} µA done")

        dac.reset()

    # Save data
    if args.save_data:
        data = {
            "vc_max_V": args.vc_max,
            "steps": args.steps,
            "traces": [
                {
                    "ib_uA": ib_ua,
                    "v_ce_V": results[ib_ua][0],
                    "ic_mA": results[ib_ua][1],
                }
                for ib_ua in sorted(results)
            ],
        }
        with open(args.save_data, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {args.save_data}")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 7))
    for ib_ua in sorted(results):
        v_ce, ic_ma = results[ib_ua]
        ax.plot(v_ce, ic_ma, label=f"$I_b$ = {ib_ua} µA")

    ax.set_xlabel("$V_{CE}$ (V)")
    ax.set_ylabel("$I_C$ (mA)")
    ax.set_title("BJT Output Characteristics")
    ax.legend()
    ax.grid(True)

    if args.output:
        fig.savefig(args.output, dpi=150)
        print(f"Plot saved to {args.output}")

    plt.show()


if __name__ == "__main__":
    main()
