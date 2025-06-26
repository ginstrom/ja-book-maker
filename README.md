# Japanese Book Maker

## Synopsis

Project for creating the files necessary for publishing Japanese-language books. Currently includes functionality for generating print-ready PDF book covers with proper spine calculations and Japanese text support.

## How to Install

### Requirements
- Python 3.10+
- Virtual environment (recommended)

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

1. **Ensure your virtual environment is activated:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Prepare your cover image:**
   - Place your front cover image (PNG/JPG) in the project directory
   - Update the `cover_image_path` in the script

3. **Run the cover generator:**
   ```bash
   python src/cover.py
   ```

4. **Customize your book details:**
   Edit the parameters in `src/cover.py` to match your book:
   - `paper_width_mm` / `paper_height_mm` - Book dimensions
   - `page_count` - Total pages for spine width calculation
   - `title` / `author` - Japanese text for spine
   - `cover_image_path` - Path to your cover image
   - `output_path` - Output PDF filename

The script will generate a print-ready PDF with your cover image and Japanese spine text. 