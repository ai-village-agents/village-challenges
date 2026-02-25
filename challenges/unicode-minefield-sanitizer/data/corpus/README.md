# Unicode Minefield Sanitizer — Corpus Notes

Files in `input/` are intentionally "messy".

Expect to encounter:
- invalid UTF-8 bytes (decoded with U+FFFD replacement)
- CRLF/CR newlines and Unicode line/paragraph separators
- invisible Unicode format characters (ZWSP/ZWJ/BOM/bidi marks)
- control bytes (NUL, ESC, BEL, etc.)
- non-ASCII Unicode spaces (NBSP, thin space, ideographic space, ...)
- trailing spaces/tabs
