# Japanese Book Maker

## Synopsis

Project for creating the files necessary for publishing Japanese-language books. Currently includes functionality for generating print-ready PDF book covers with proper spine calculations, Japanese text support, and automatic font detection.

## Features

- **Japanese Font Support**: Automatically detects and uses Japanese-capable fonts on your system
- **Command-Line Interface**: Easy-to-use CLI with customizable options
- **Proper Vertical Text**: Renders Japanese text vertically on the spine (top-to-bottom)
- **Smart Image Scaling**: Optimized cover image positioning and scaling
- **Print-Ready Output**: Generates PDFs suitable for print-on-demand services

## How to Install

### Requirements
- Python 3.10+
- Virtual environment (recommended)
- FontConfig (for Japanese font detection on Linux/macOS)

### Installation Steps

1. **Clone the repository and navigate to the project directory**

2. **Create and activate a virtual environment:**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## How to Run

### Basic Usage

1. **Ensure your virtual environment is activated:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run with default settings:**
   ```bash
   python src/cover.py
   ```
   This will use the default Japanese book settings and look for `cover.png` in the current directory.

### Command-Line Options

The cover generator supports the following command-line arguments:

```bash
python src/cover.py [OPTIONS]
```

**Available Options:**

- `-w, --paper-width`: Paper width in mm (default: 140.0 for 5.5 inches)
- `-H, --paper-height`: Paper height in mm (default: 216.0 for 8.5 inches)  
- `-p, --page-count`: Total number of pages for spine width calculation (default: 381)
- `-c, --cover-image`: Path to front cover image file (default: cover.png)
- `-t, --title`: Title text for spine (default: 聖騎士の目覚め)
- `-a, --author`: Author text for spine (default: ライアン・ジンストロム)
- `-o, --output`: Output PDF filename (default: japanese_book_cover.pdf)

### Examples

**Basic usage with custom image:**
```bash
python src/cover.py -c my_cover.jpg
```

**Custom book dimensions and page count:**
```bash
python src/cover.py -w 150 -H 220 -p 250 -c cover.png
```

**Full customization:**
```bash
python src/cover.py \
  --paper-width 140 \
  --paper-height 216 \
  --page-count 381 \
  --cover-image "my_book_cover.png" \
  --title "私の本のタイトル" \
  --author "著者名" \
  --output "my_book_cover.pdf"
```

**Get help:**
```bash
python src/cover.py --help
```

## Japanese Font Support

The script automatically detects Japanese-capable fonts on your system using FontConfig. It will:

1. Scan for fonts that support Japanese characters
2. Register the first available Japanese font with ReportLab
3. Fall back to Helvetica if no Japanese fonts are found (with a warning)

On macOS and Linux, ensure FontConfig is installed for automatic font detection.

## Output

The script generates a print-ready PDF that includes:
- Front cover with your provided image
- Spine with Japanese text (title at top, author at bottom)
- Back cover (blank)
- Proper spine width calculation based on page count

The generated PDF is suitable for upload to print-on-demand services. 