from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image

def mm_to_points(mm_value):
    return mm_value * mm

def calculate_spine_width(page_count):
    """
    KDP standard for cream paper: 0.0635 mm per page
    """
    return page_count * 0.0635

def draw_spine_text(c, title, author, spine_x_center, spine_top, spine_bottom):
    """
    Draws vertical spine text: title at top, author at bottom.
    Text is rotated and centered on the spine.
    """
    c.setFillColorRGB(1, 1, 1)
    font_size = 12
    c.setFont("Helvetica", font_size)

    # Title near top of spine
    c.saveState()
    c.translate(spine_x_center, spine_top - 10 * mm)
    c.rotate(90)
    c.drawCentredString(0, 0, title)
    c.restoreState()

    # Author near bottom of spine
    c.saveState()
    c.translate(spine_x_center, spine_bottom + 10 * mm)
    c.rotate(90)
    c.drawCentredString(0, 0, author)
    c.restoreState()

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

        # Scale while preserving aspect ratio
        if img_aspect > target_aspect:
            new_width_mm = paper_width_mm
            new_height_mm = paper_width_mm / img_aspect
        else:
            new_height_mm = paper_height_mm
            new_width_mm = paper_height_mm * img_aspect

        new_width_pts = mm_to_points(new_width_mm)
        new_height_pts = mm_to_points(new_height_mm)

        x = paper_width_pts + spine_width_pts + (paper_width_pts - new_width_pts) / 2
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

# === Example Usage ===
if __name__ == "__main__":
    generate_cover_pdf(
        paper_width_mm=140,                # 5.5" width
        paper_height_mm=226,               # 8.5" height
        page_count=381,                    # Total number of pages
        cover_image_path="cover.png",      # Path to your front cover image
        title="聖騎士の目覚め",              # Title text for spine
        author="ライアン・ジンストロム",                  # Author text for spine
        output_path="japanese_book_cover.pdf"
    )
