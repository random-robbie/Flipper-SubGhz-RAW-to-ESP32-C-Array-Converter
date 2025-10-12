#!/usr/bin/env python3
"""
Flipper SubGhz RAW to ESP32 C Array Converter
Converts .sub files to C arrays for ESP32 RF transmission
"""

def parse_sub_file(filename):
    """Parse a Flipper .sub file and extract RAW timing data"""
    timings = []
    
    with open(filename, 'r') as f:
        in_raw_data = False
        for line in f:
            line = line.strip()
            
            # Check if we're in a RAW_Data line
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

def main():
    print("Flipper SubGhz RAW to ESP32 Converter")
    print("=" * 50)
    
    # Process OFF signal
    print("\nProcessing 'off.sub'...")
    try:
        off_timings = parse_sub_file('off.sub')
        print(f"Found {len(off_timings)} timing values")
        off_array = format_c_array(off_timings, "signalOff")
    except FileNotFoundError:
        print("Error: 'off.sub' file not found!")
        off_array = "// Error: off.sub not found\n"
    
    # Process ON signal
    print("\nProcessing 'on.sub'...")
    try:
        on_timings = parse_sub_file('on.sub')
        print(f"Found {len(on_timings)} timing values")
        on_array = format_c_array(on_timings, "signalOn")
    except FileNotFoundError:
        print("Error: 'on.sub' file not found!")
        on_array = "// Error: on.sub not found\n"
    
    # Write output to file
    output_filename = "signal_arrays.h"
    with open(output_filename, 'w') as f:
        f.write("// Generated RF signal arrays for ESP32\n")
        f.write("// Copy these into your Arduino sketch\n\n")
        f.write(off_array)
        f.write("\n")
        f.write(on_array)
    
    print(f"\n✓ Conversion complete!")
    print(f"✓ Output written to: {output_filename}")
    print("\nInstructions:")
    print("1. Open 'signal_arrays.h'")
    print("2. Copy the array definitions")
    print("3. Replace the existing signalOff and signalOn arrays in your ESP32 sketch")
    print("4. Upload to your ESP32")
    
    # Also print to console for quick copy-paste
    print("\n" + "=" * 50)
    print("COPY THE FOLLOWING INTO YOUR SKETCH:")
    print("=" * 50)
    print(off_array)
    print(on_array)

if __name__ == "__main__":
    main()
