#!/usr/bin/env python3
"""
Flipper SubGhz RAW to ESP32 C Array Converter
Converts .sub files to C arrays for ESP32 RF transmission
"""

import argparse
import os
from pathlib import Path

def parse_sub_file(filename):
    """Parse a Flipper .sub file and extract RAW timing data"""
    timings = []
    protocol = None
    te = None
    bit_count = None

    with open(filename, 'r') as f:
        in_raw_data = False
        in_data_raw = False
        data_raw_hex = []

        for line in f:
            line = line.strip()

            # Check protocol type
            if line.startswith('Protocol:'):
                protocol = line.split(':', 1)[1].strip()

            # Get bit count for BinRAW
            if line.startswith('Bit:'):
                bit_count = int(line.split(':', 1)[1].strip())

            # Get Time Element for BinRAW
            if line.startswith('TE:'):
                te = int(line.split(':', 1)[1].strip())

            # Check if we're in a RAW_Data line (Protocol: RAW)
            if line.startswith('RAW_Data:'):
                in_raw_data = True
                # Extract numbers after "RAW_Data: "
                data_part = line.split('RAW_Data:', 1)[1].strip()
                numbers = data_part.split()

                for num in numbers:
                    try:
                        timings.append(int(num))
                    except ValueError:
                        pass  # Skip non-numeric values
            elif in_raw_data and line and not line.startswith('Filetype'):
                # Continue reading if line doesn't start a new field
                numbers = line.split()
                for num in numbers:
                    try:
                        timings.append(int(num))
                    except ValueError:
                        in_raw_data = False  # End of RAW data
                        break

            # Check if we're in Data_RAW line (Protocol: BinRAW)
            elif line.startswith('Data_RAW:'):
                in_data_raw = True
                # Extract hex data after "Data_RAW: "
                data_part = line.split('Data_RAW:', 1)[1].strip()
                hex_values = data_part.split()
                data_raw_hex.extend(hex_values)
            elif in_data_raw and line and not any(line.startswith(prefix) for prefix in ['Filetype', 'Version', 'Frequency', 'Preset', 'Protocol', 'Bit', 'TE', 'Bit_RAW']):
                # Continue reading hex data
                hex_values = line.split()
                if all(len(val) == 2 and all(c in '0123456789ABCDEFabcdef' for c in val) for val in hex_values):
                    data_raw_hex.extend(hex_values)
                else:
                    in_data_raw = False

        # Convert BinRAW hex data to timings
        if protocol == 'BinRAW' and data_raw_hex and te:
            timings = convert_binraw_to_timings(data_raw_hex, te, bit_count)

    return timings

def convert_binraw_to_timings(hex_data, te, bit_count=None):
    """Convert BinRAW hex data to timing array using Time Element"""
    # Convert hex strings to binary
    binary_str = ''
    for hex_byte in hex_data:
        binary_str += format(int(hex_byte, 16), '08b')

    # Use only the specified number of bits if bit_count is provided
    if bit_count and bit_count < len(binary_str):
        binary_str = binary_str[:bit_count]

    # Convert binary to timings
    # Each bit represents a period of TE microseconds
    # Positive values = signal high, negative = signal low
    timings = []
    if not binary_str:
        return timings

    current_state = int(binary_str[0])
    count = 1

    for i in range(1, len(binary_str)):
        bit = int(binary_str[i])
        if bit == current_state:
            count += 1
        else:
            # Add timing for accumulated bits
            timing_value = count * te
            if current_state == 0:
                timing_value = -timing_value
            timings.append(timing_value)

            # Reset for new state
            current_state = bit
            count = 1

    # Add final timing
    timing_value = count * te
    if current_state == 0:
        timing_value = -timing_value
    timings.append(timing_value)

    return timings

def format_c_array(timings, array_name, values_per_line=20):
    """Format timing data as a C array"""
    output = f"const int16_t {array_name}[] = {{\n  "
    
    for i, timing in enumerate(timings):
        output += str(timing)
        
        if i < len(timings) - 1:
            output += ", "
            
            # Add newline every N values for readability
            if (i + 1) % values_per_line == 0:
                output += "\n  "
    
    output += "\n};\n"
    output += f"const int {array_name}Length = {len(timings)};\n"
    
    return output

def sanitize_name(filename):
    """Convert filename to valid C variable name"""
    name = Path(filename).stem
    # Replace invalid characters with underscore
    name = ''.join(c if c.isalnum() else '_' for c in name)
    # Ensure it doesn't start with a digit
    if name and name[0].isdigit():
        name = 'signal_' + name
    return name

def main():
    parser = argparse.ArgumentParser(
        description='Convert Flipper SubGhz RAW files to ESP32 C arrays',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                    # Process all .sub files in current directory
  %(prog)s file1.sub          # Process specific file
  %(prog)s file1.sub file2.sub  # Process multiple files
        '''
    )
    parser.add_argument('files', nargs='*', help='.sub files to convert (default: all .sub files in current directory)')
    args = parser.parse_args()

    print("Flipper SubGhz RAW to ESP32 Converter")
    print("=" * 50)

    # Determine which files to process
    if args.files:
        sub_files = args.files
    else:
        # Find all .sub files in current directory
        sub_files = sorted(Path('.').glob('*.sub'))
        if not sub_files:
            print("Error: No .sub files found in current directory!")
            return
        print(f"\nFound {len(sub_files)} .sub file(s)")

    # Process each file
    all_arrays = []
    for sub_file in sub_files:
        filename = str(sub_file)
        print(f"\nProcessing '{filename}'...")
        try:
            timings = parse_sub_file(filename)
            print(f"  Found {len(timings)} timing values")

            # Generate array name from filename
            array_name = sanitize_name(filename)
            array_code = format_c_array(timings, array_name)
            all_arrays.append(array_code)

        except FileNotFoundError:
            print(f"  Error: '{filename}' not found!")
            all_arrays.append(f"// Error: {filename} not found\n")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            all_arrays.append(f"// Error processing {filename}: {e}\n")

    # Write output to file
    output_filename = "signal_arrays.h"
    with open(output_filename, 'w') as f:
        f.write("// Generated RF signal arrays for ESP32\n")
        f.write("// Copy these into your Arduino sketch\n\n")
        for array in all_arrays:
            f.write(array)
            f.write("\n")

    print(f"\n✓ Conversion complete!")
    print(f"✓ Output written to: {output_filename}")
    print("\nInstructions:")
    print("1. Open 'signal_arrays.h'")
    print("2. Copy the array definitions")
    print("3. Use the arrays in your ESP32 sketch")
    print("4. Upload to your ESP32")

    # Also print to console for quick copy-paste
    print("\n" + "=" * 50)
    print("COPY THE FOLLOWING INTO YOUR SKETCH:")
    print("=" * 50)
    for array in all_arrays:
        print(array)

if __name__ == "__main__":
    main()
