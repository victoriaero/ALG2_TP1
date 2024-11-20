import random
import string
import json
import csv
import os

OUTPUT_PATH = "samples/txt/"
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

BMP_OUTPUT_PATH = "samples/bmp/"
if not os.path.exists(BMP_OUTPUT_PATH):
    os.makedirs(BMP_OUTPUT_PATH)

CSV_OUTPUT_PATH = "samples/csv/"
if not os.path.exists(CSV_OUTPUT_PATH):
    os.makedirs(CSV_OUTPUT_PATH)

JSON_OUTPUT_PATH = "samples/json/"
if not os.path.exists(JSON_OUTPUT_PATH):
    os.makedirs(JSON_OUTPUT_PATH)

def generate_random_text(size, pattern=None):
    if pattern:
        return (pattern * (size // len(pattern) + 1))[:size]
    else:
        return ''.join(random.choices(string.ascii_letters + string.digits + " ", k=size))

def generate_txt_files(num_files=10, file_size=16384, pattern=None):
    for i in range(1, num_files + 1):
        filename = os.path.join(OUTPUT_PATH, f"generated_txt_sample{i}.txt")
        with open(filename, "w") as f:
            text = generate_random_text(file_size*i, pattern)
            f.write(text)

def generate_bmp(width, height, filename):
    file_size = 14 + 40 + (width * height * 3)
    header = bytearray([
        0x42, 0x4D,
        *file_size.to_bytes(4, byteorder="little"),
        0x00, 0x00,
        0x00, 0x00,
        0x36, 0x00, 0x00, 0x00
    ])

    dib_header = bytearray([
        0x28, 0x00, 0x00, 0x00,
        *width.to_bytes(4, byteorder="little"),
        *height.to_bytes(4, byteorder="little"),
        0x01, 0x00,
        0x18, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x13, 0x0B, 0x00, 0x00,
        0x13, 0x0B, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00
    ])

    pixel_data = bytearray()
    for _ in range(height):
        for _ in range(width):
            pixel_data.extend([
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ])
        padding = (4 - (width * 3) % 4) % 4
        pixel_data.extend([0] * padding)

    with open(filename, "wb") as f:
        f.write(header)
        f.write(dib_header)
        f.write(pixel_data)

def generate_bmp_files(num_files=10, width=100, height=100):
    for i in range(1, num_files + 1):
        filename = os.path.join(BMP_OUTPUT_PATH, f"generated_bmp_sample{i}.bmp")
        generate_bmp(width, height, filename)

def generate_json_files(num_files=10, num_entries=100):
    for i in range(1, num_files + 1):
        filename = os.path.join(JSON_OUTPUT_PATH, f"generated_json_sample{i}.json")
        data = []
        for _ in range(num_entries*i):
            entry = {
                "id": random.randint(1, 1000),
                "name": ''.join(random.choices(string.ascii_letters, k=10)),
                "value": random.uniform(0, 100),
                "is_active": random.choice([True, False])
            }
            data.append(entry)
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

def generate_csv_files(num_files=10, num_rows=100, num_columns=10):
    for i in range(1, num_files + 1):
        filename = os.path.join(CSV_OUTPUT_PATH, f"generated_csv_sample{i}.csv")
        with open(filename, "w", newline='') as f:
            writer = csv.writer(f)
            header = [f"Column_{j+1}" for j in range(num_columns)]
            writer.writerow(header)
            for _ in range(num_rows*i):
                row = [random.randint(0, 1000) for _ in range(num_columns)]
                writer.writerow(row)

if __name__ == "__main__":
    
    generate_bmp_files(num_files=3, width=100, height=100)
    # generate_csv_files(num_files=10, num_rows=100, num_columns=10)
    # generate_json_files(num_files=10, num_entries=100)
    # generate_txt_files(num_files=10, file_size=16384, pattern=None)