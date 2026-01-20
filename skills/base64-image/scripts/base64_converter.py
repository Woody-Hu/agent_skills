#!/usr/bin/env python3
"""
Base64 Image Converter

Convert between Base64 strings and image files using Python standard library.
"""

import base64
import argparse
import sys
from pathlib import Path
import mimetypes


class Base64Converter:
    """
    Convert between Base64 strings and image files.
    """
    
    def image_to_base64(self, image_path, format='plain'):
        """
        Convert an image file to Base64 string.
        
        Args:
            image_path (str): Path to the input image file
            format (str): Output format ('plain' or 'data_url')
            
        Returns:
            str: Base64 encoded string
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Encode to Base64
        base64_str = base64.b64encode(image_data).decode('utf-8')
        
        if format == 'data_url':
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Format as data URL
            return f"data:{mime_type};base64,{base64_str}"
        
        return base64_str
    
    def base64_to_image(self, base64_string, output_path):
        """
        Convert a Base64 string to an image file.
        
        Args:
            base64_string (str): Base64 encoded string
            output_path (str): Path to save the output image
        """
        output_path = Path(output_path)
        
        # Check if string is a data URL
        if base64_string.startswith('data:'):
            # Extract Base64 part from data URL
            base64_str = base64_string.split(',')[1]
        else:
            base64_str = base64_string
        
        # Decode Base64 to binary data
        try:
            image_data = base64.b64decode(base64_str)
        except Exception as e:
            raise ValueError(f"Invalid Base64 string: {e}")
        
        # Write to output file
        with open(output_path, 'wb') as f:
            f.write(image_data)


def main():
    """
    Command line interface.
    """
    parser = argparse.ArgumentParser(
        description='Convert between Base64 strings and image files.'
    )
    
    # Create subparsers for encode and decode commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode image file to Base64 string')
    encode_parser.add_argument('input_file', help='Path to input image file')
    encode_parser.add_argument('-o', '--output', help='Output file path (default: stdout)')
    encode_parser.add_argument('-f', '--format', choices=['plain', 'data_url'], 
                             default='plain', help='Output format (default: plain)')
    
    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode Base64 string to image file')
    decode_parser.add_argument('input', help='Base64 string or input file containing Base64 string')
    decode_parser.add_argument('-o', '--output', required=True, help='Output image file path')
    
    args = parser.parse_args()
    
    converter = Base64Converter()
    
    if args.command == 'encode':
        # Encode image to Base64
        base64_str = converter.image_to_base64(args.input_file, args.format)
        
        if args.output:
            # Write to file
            with open(args.output, 'w') as f:
                f.write(base64_str)
        else:
            # Print to stdout
            print(base64_str)
    
    elif args.command == 'decode':
        # Check if input is a file
        input_path = Path(args.input)
        if input_path.exists():
            # Read Base64 string from file
            with open(input_path, 'r') as f:
                base64_string = f.read().strip()
        else:
            # Treat as Base64 string
            base64_string = args.input
        
        # Decode Base64 to image
        converter.base64_to_image(base64_string, args.output)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()