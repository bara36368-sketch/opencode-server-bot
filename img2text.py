"""Image to text (OCR) - extract text from screenshots."""
import sys
import subprocess

def ensure_deps():
    try:
        import pytesseract
        from PIL import Image
        return True
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract", "Pillow"])
        return True

def extract_text(image_path):
    import pytesseract
    from PIL import Image
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python img2text.py <image_path>")
        print("Example: python img2text.py screenshot.jpg")
        sys.exit(1)
    
    ensure_deps()
    path = sys.argv[1]
    text = extract_text(path)
    print("=" * 50)
    print("EXTRACTED TEXT:")
    print("=" * 50)
    print(text)
