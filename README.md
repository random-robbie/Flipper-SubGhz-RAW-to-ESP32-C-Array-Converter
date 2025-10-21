# Flipper SubGhz RAW to ESP32 C Array Converter

A Python script that converts Flipper Zero SubGhz RAW files (`.sub`) into C arrays, suitable for use in ESP32 projects for RF signal transmission.

## What it Does

This script reads the `RAW_Data` from any Flipper `.sub` file and formats it into a C-style `int16_t` array. It generates a header file (`signal_arrays.h`) containing the arrays, which can be easily integrated into an Arduino or ESP-IDF project.

The script generates a C array for each `.sub` file processed. The name of the array is derived from the filename of the `.sub` file. For example, `my_signal.sub` will be converted into a C array named `my_signal`.

## How to Use

1.  **Place your `.sub` files:** Put your `.sub` files in the same directory as the `sub_to_cpp_converter.py` script.
2.  **Run the script:**

    To process all `.sub` files in the directory:
    ```bash
    python3 sub_to_cpp_converter.py
    ```

    To process specific files:
    ```bash
    python3 sub_to_cpp_converter.py file1.sub file2.sub
    ```
3.  **Check the output:** The script will create a new file named `signal_arrays.h`.
4.  **Integrate into your project:**
    - Open `signal_arrays.h`.
    - Copy the generated C arrays.
    - Paste them into your ESP32 sketch.
    - Upload the updated sketch to your ESP32.

## Input Files

The script can process any `.sub` file. You can either provide the filenames as arguments or let the script discover all `.sub` files in the current directory.

## Output

The script generates a single file:

- `signal_arrays.h`: A C header file containing the C arrays for all processed `.sub` files.

### Example Output (`signal_arrays.h`)

If you have `on.sub` and `off.sub` in your directory, the output will look like this:

```c
// Generated RF signal arrays for ESP32
// Copy these into your Arduino sketch

const int16_t off[] = {
  -1000, 2000, -3000, 4000, -5000, 6000, -7000, 8000, -9000, 10000,
  -11000, 12000, -13000, 14000, -15000, 16000, -17000, 18000, -19000, 20000
};
const int offLength = 20;

const int16_t on[] = {
  1000, -2000, 3000, -4000, 5000, -6000, 7000, -8000, 9000, -10000,
  11000, -12000, 13000, -14000, 15000, -16000, 17000, -18000, 19000, -20000
};
const int onLength = 20;
```
*Note: The values in the example are for illustration purposes only. The actual values will be derived from your `.sub` files.*