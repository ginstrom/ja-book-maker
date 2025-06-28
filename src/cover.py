import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image
import os

def mm_to_points(mm_value):
    return mm_value * mm

def calculate_spine_width(page_count):
    """
    KDP standard for cream paper: 0.0635 mm per page
    """
    return page_count * 0.0635

def get_japanese_fonts():
    """
    Find all Japanese-capable fonts on the system using fc-list.
    Returns a dict mapping family -> {'regular': path, 'bold': path, 'italic': path}
    """
    import subprocess
    fonts = {}
    try:
        print("Running fc-list to find Japanese fonts...")
        result = subprocess.run(
            ["fc-list", ":lang=ja"], capture_output=True, text=True, check=False
        )
        if result.returncode != 0 or not result.stdout.strip():
            print("fc-list failed or returned no output")
            return {}

        for line in result.stdout.splitlines():
            parts = [p.strip() for p in line.split(":")]
            if len(parts) < 2:
                continue

            font_path = parts[0]
            # first colon-field is the font file, second is comma-sep families
            families = parts[1].split(",")
            family = families[0]

            # find style=… in any of the remaining fields
            style = "regular"
            for seg in parts[2:]:
                seg_low = seg.lower()
                if seg_low.startswith("style="):
                    style = seg_low.split("=", 1)[1]
                    break

            style = style if style in ("regular", "bold", "italic", "oblique") else "regular"
            if style == "oblique":
                style = "italic"

            if family not in fonts:
                fonts[family] = {"regular": None, "bold": None, "italic": None}
            fonts[family][style] = font_path

        # keep only families that have a regular face
        filtered = {fam: s for fam, s in fonts.items() if s["regular"]}
        print(f"Found {len(filtered)} Japanese font families with Regular variants")
        return filtered

    except Exception as e:
        print(f"Error finding Japanese fonts: {e}")
        return {}


def get_japanese_font():
    """
    Get a font that supports Japanese characters.
    Returns the font name to use.
    """
    # Try to find Japanese fonts using fc-list
    japanese_fonts = get_japanese_fonts()
    
    if japanese_fonts:
        # Use the first available Japanese font family
        for family_name, styles in japanese_fonts.items():
            if styles["regular"]:
                try:
                    font_path = styles["regular"]
                    pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                    print(f"Using Japanese font: {family_name} ({font_path})")
                    return 'JapaneseFont'
                except Exception as e:
                    print(f"Failed to register font {family_name} ({font_path}): {e}")
                    continue
    
    # Fallback to Helvetica if no Japanese font found
    print("Warning: No Japanese-compatible font found, using Helvetica (Japanese text may not display correctly)")
    return 'Helvetica'


def draw_spine_text(c, title, author, spine_x_center, spine_top, spine_bottom):
    """
    Draws vertical spine text: title at top, author at bottom.
    Text flows vertically (top-to-bottom) with proper padding.
    """
    c.setFillColorRGB(1, 1, 1)
    font_size = 14
    padding = 20 * mm  # Padding from top and bottom edges
    
    # Get a font that supports Japanese characters
    font_name = get_japanese_font()
    c.setFont(font_name, font_size)
    
    # Calculate available space for text
    available_height = spine_top - spine_bottom - (2 * padding)
    
    # Draw title vertically (top-to-bottom) near top of spine
    title_start_y = spine_top - padding
    draw_vertical_text(c, title, spine_x_center, title_start_y, font_size, -1)
    
    # Draw author vertically (top-to-bottom) near bottom of spine
    author_height = len(author) * font_size * 1.2  # Estimate author text height
    author_start_y = spine_bottom + padding + author_height
    draw_vertical_text(c, author, spine_x_center, author_start_y, font_size, -1)


def draw_vertical_text(c, text, x, start_y, font_size, direction=-1):
    """
    Draw text vertically (character by character).
    
    Args:
        c: Canvas object
        text: Text to draw
        x: X position (center)
        start_y: Starting Y position
        font_size: Font size
        direction: -1 for top-to-bottom, 1 for bottom-to-top
    """
    line_height = font_size * 1.2  # Space between characters
    current_y = start_y
    
    for char in text:
        c.drawCentredString(x, current_y, char)
        current_y += direction * line_height

def generate_cover_pdf(paper_width_mm, paper_height_mm, page_count, cover_image_path,
                       title, author, output_path):
    # Calculate dimensions
    spine_width_mm = calculate_spine_width(page_count)
    total_width_mm = paper_width_mm * 2 + spine_width_mm
    total_height_mm = paper_height_mm

    # Convert to points
    total_width_pts = mm_to_points(total_width_mm)
    total_height_pts = mm_to_points(total_height_mm)
    paper_width_pts = mm_to_points(paper_width_mm)
    spine_width_pts = mm_to_points(spine_width_mm)

    # Create canvas
    c = canvas.Canvas(output_path, pagesize=(total_width_pts, total_height_pts))

    # Fill background with black
    c.setFillColorRGB(0, 0, 0)
    c.rect(0, 0, total_width_pts, total_height_pts, fill=1, stroke=0)

    # Place cover image on right (front cover)
    try:
        img = Image.open(cover_image_path)
        img_width, img_height = img.size
        img_aspect = img_width / img_height
        target_aspect = paper_width_mm / paper_height_mm

        # Scale to cover entire front cover area (may crop at spine boundary)
        # Calculate scale factors needed to fill each dimension
        width_scale = paper_width_mm / (img_width * 25.4 / 72)  # Convert pixels to mm
        height_scale = paper_height_mm / (img_height * 25.4 / 72)  # Convert pixels to mm
        
        # Use the larger scale factor to ensure complete coverage
        scale_factor = max(width_scale, height_scale)
        
        # Calculate final dimensions in mm, then convert to points
        new_width_mm = (img_width * 25.4 / 72) * scale_factor
        new_height_mm = (img_height * 25.4 / 72) * scale_factor
        
        new_width_pts = mm_to_points(new_width_mm)
        new_height_pts = mm_to_points(new_height_mm)

        # Position the image to cover the front cover (left side for Japanese books)
        # If image is wider than needed, align to left edge (crop at spine/right)
        # If image is taller than needed, center vertically
        x = min(0, paper_width_pts - new_width_pts)
        y = (total_height_pts - new_height_pts) / 2

        c.drawImage(cover_image_path, x, y, new_width_pts, new_height_pts, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Draw spine text
    spine_x_center = paper_width_pts + spine_width_pts / 2
    draw_spine_text(c, title, author, spine_x_center, total_height_pts, 0)

    # Save PDF
    c.showPage()
    c.save()
    print(f"PDF cover saved to: {output_path}")

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the cover generator.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate print-ready PDF book covers with Japanese text support"
    )
    
    parser.add_argument(
        "-w", "--paper-width", 
        type=float, 
        default=140.0,
        help="Paper width in mm (default: 140.0 for 5.5 inches)"
    )
    parser.add_argument(
        "-H", "--paper-height", 
        type=float, 
        default=216.0,
        help="Paper height in mm (default: 226.0 for 8.5 inches)"
    )
    parser.add_argument(
        "-p", "--page-count", 
        type=int, 
        default=381,
        help="Total number of pages for spine width calculation (default: 381)"
    )
    parser.add_argument(
        "-c", "--cover-image", 
        type=str, 
        default="cover.png",
        help="Path to front cover image file (default: cover.png)"
    )
    parser.add_argument(
        "-t", "--title", 
        type=str, 
        default="聖騎士の目覚め",
        help="Title text for spine (default: 聖騎士の目覚め)"
    )
    parser.add_argument(
        "-a", "--author", 
        type=str, 
        default="ライアン・ジンストロム",
        help="Author text for spine (default: ライアン・ジンストロム)"
    )
    parser.add_argument(
        "-o", "--output", 
        type=str, 
        default="japanese_book_cover.pdf",
        help="Output PDF filename (default: japanese_book_cover.pdf)"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main function to parse arguments and generate cover PDF.
    """
    args = parse_args()
    
    generate_cover_pdf(
        paper_width_mm=args.paper_width,
        paper_height_mm=args.paper_height,
        page_count=args.page_count,
        cover_image_path=args.cover_image,
        title=args.title,
        author=args.author,
        output_path=args.output
    )


if __name__ == "__main__":
    main()
