import sys

_AR_WARNED = False


def fix_ar(text: str) -> str:
    """Reshape + reorder Arabic text for matplotlib / consoles without bidi support."""
    global _AR_WARNED
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except ImportError:
        if not _AR_WARNED:
            print("[!] pip install arabic-reshaper python-bidi   "
                  "(needed for correct Arabic shaping)  /  "
                  "لعرض العربية بشكل صحيح ثبّت الحزمتين أعلاه", file=sys.stderr)
            _AR_WARNED = True
        return text


def print_header(title: str, lang: str = 'ar'):
    """Prints a formatted section header based on the selected language."""
    fixed_title = fix_ar(title) if lang == 'ar' else title
    line = "=" * (len(title) + 8)
    print(f"\n{line}\n    {fixed_title}\n{line}\n")