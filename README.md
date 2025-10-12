# Flipper SubGhz RAW to ESP32 C Array Converter

A Python script that converts Flipper Zero SubGhz RAW files (`.sub`) into C arrays, suitable for use in ESP32 projects for RF signal transmission.

## What it Does

This script reads the `RAW_Data` from Flipper `.sub` files and formats it into C-style `int16_t` arrays. It generates a header file (`signal_arrays.h`) containing the arrays, which can be easily integrated into an Arduino or ESP-IDF project.

The script specifically looks for two files:
- `on.sub`: The signal to be transmitted for the "ON" command.
- `off.sub`: The signal to be transmitted for the "OFF" command.

## How to Use

1.  **Place your files:** Put your `on.sub` and `off.sub` files in the same directory as the `sub_to_cpp_converter.py` script.
2.  **Run the script:**
    ```bash
    python3 sub_to_cpp_converter.py
    ```
3.  **Check the output:** The script will create a new file named `signal_arrays.h`.
4.  **Integrate into your project:**
    - Open `signal_arrays.h`.
    - Copy the generated C arrays (`signalOn` and `signalOff`).
    - Paste them into your ESP32 sketch, replacing any existing signal arrays.
    - Upload the updated sketch to your ESP32.

## Input Files

The script requires the following files to be present in the same directory:

- `on.sub`: A Flipper SubGhz RAW file containing the "ON" signal data.
- `off.sub`: A Flipper SubGhz RAW file containing the "OFF" signal data.

## Output

The script generates a single file:

- `signal_arrays.h`: A C header file containing the `signalOn` and `signalOff` arrays, along with their lengths.

### Example Output (`signal_arrays.h`)

```c
// Generated RF signal arrays for ESP32
// Copy these into your Arduino sketch

const int16_t signalOff[] = {
  -1000, 2000, -3000, 4000, -5000, 6000, -7000, 8000, -9000, 10000,
  -11000, 12000, -13000, 14000, -15000, 16000, -17000, 18000, -19000, 20000
};
const int signalOffLength = 20;

const int16_t signalOn[] = {
  1000, -2000, 3000, -4000, 5000, -6000, 7000, -8000, 9000, -10000,
  11000, -12000, 13000, -14000, 15000, -16000, 17000, -18000, 19000, -20000
};
const int signalOnLength = 20;
```
*Note: The values in the example are for illustration purposes only. The actual values will be derived from your `.sub` files.*