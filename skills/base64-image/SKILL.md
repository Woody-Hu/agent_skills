---
name: base64-image
description: Convert between Base64 strings and image files. Supports various image formats (JPEG, PNG, GIF, BMP, TIFF) and provides both command-line interface and Python API for encoding images to Base64 and decoding Base64 strings back to images.
---

# Base64-Image Conversion

## Overview

Convert images to Base64 strings and vice versa using this skill. Ideal for embedding images in HTML, CSS, JSON, or any text-based format where binary data needs to be represented as text.

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Quick Start

### Image to Base64

**Command Line:**
```bash
python scripts/base64_converter.py encode input.jpg -o output.txt
```

**Python API:**
```python
from base64_converter import Base64Converter

converter = Base64Converter()
base64_string = converter.image_to_base64('input.jpg')
print(base64_string)
```

### Base64 to Image

**Command Line:**
```bash
python scripts/base64_converter.py decode input.txt -o output.png
```

**Python API:**
```python
from base64_converter import Base64Converter

converter = Base64Converter()
converter.base64_to_image('base64_string_here', 'output.png')
```

## Command Line Interface

### Installation

No external dependencies required - uses only Python standard library.

### Usage

```
Usage: base64_converter.py [OPTIONS] COMMAND [ARGS]...

  Convert between Base64 strings and image files.

Options:
  --help  Show this message and exit.

Commands:
  decode  Decode Base64 string to image file
  encode  Encode image file to Base64 string
```

### Encode Command

```
Usage: base64_converter.py encode [OPTIONS] INPUT_FILE

  Encode image file to Base64 string

Options:
  -o, --output TEXT  Output file path (default: stdout)
  -f, --format TEXT  Output format: plain, data_url (default: plain)
  --help             Show this message and exit.
```

### Decode Command

```
Usage: base64_converter.py decode [OPTIONS] INPUT

  Decode Base64 string to image file

Options:
  -o, --output TEXT  Output image file path (required)
  --help             Show this message and exit.
```

## Python API

### Base64Converter Class

**Constructor:**
```python
Base64Converter()
```

**Methods:**

#### image_to_base64(image_path, format='plain')
Convert an image file to Base64 string.

- `image_path`: Path to the input image file
- `format`: Output format ('plain' or 'data_url'), default: 'plain'
- Returns: Base64 encoded string

#### base64_to_image(base64_string, output_path)
Convert a Base64 string to an image file.

- `base64_string`: Base64 encoded string
- `output_path`: Path to save the output image
- Returns: None

## Examples

### Example 1: Encode Image to Base64

**Command Line:**
```bash
python scripts/base64_converter.py encode cat.jpg -o cat_base64.txt
```