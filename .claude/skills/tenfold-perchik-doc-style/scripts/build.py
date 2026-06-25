#!/usr/bin/env python3
"""Render a Tenfold/Perchik HTML document to a styled A4 PDF.

Usage:
    python build.py input.html output.pdf

Renderer priority:
    1. WeasyPrint  -> matches the original toolchain (Archivo + IBM Plex Mono,
       DejaVu fallback, @page footers). Install: pip install weasyprint
    2. Playwright/Chromium -> faithful web-font rendering as a fallback.
       Install: pip install playwright && playwright install chromium

The HTML must <link> style.css (sit it next to the HTML, or pass an absolute
href). Fonts load from Google Fonts over the network; for offline builds,
download Archivo + IBM Plex Mono .ttf and repoint the @font-face/@import URLs
in style.css to local files.
"""
import sys
import os


def render_weasyprint(html_path, pdf_path):
    from weasyprint import HTML
    HTML(filename=html_path).write_pdf(pdf_path)


def render_playwright(html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    url = "file://" + os.path.abspath(html_path).replace("\\", "/")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.pdf(path=pdf_path, format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    html_path, pdf_path = sys.argv[1], sys.argv[2]
    if not os.path.exists(html_path):
        sys.exit(f"input not found: {html_path}")

    try:
        render_weasyprint(html_path, pdf_path)
        print(f"[weasyprint] wrote {pdf_path}")
        return
    except ImportError:
        print("[info] weasyprint not available, trying playwright/chromium...")
    except Exception as e:  # weasyprint present but failed (e.g. missing libs)
        print(f"[warn] weasyprint failed ({e}); trying playwright/chromium...")

    try:
        render_playwright(html_path, pdf_path)
        print(f"[playwright] wrote {pdf_path}")
    except ImportError:
        sys.exit("No renderer available. Install weasyprint OR "
                 "playwright (+ `playwright install chromium`).")


if __name__ == "__main__":
    main()
