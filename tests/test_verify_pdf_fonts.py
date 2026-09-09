"""Regression checks for Chinese vs Japanese Hiragino PDF font resources."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "verify_pdf_fonts",
    Path(__file__).parents[1] / ".github/scripts/verify_pdf_fonts.py",
)
fonts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fonts)


def row(name, embedded="yes"):
    return f"{name} CID TrueType Identity-H {embedded} yes yes 42 0\n"


class FontChecks(unittest.TestCase):
    def run_check(self, table):
        result = subprocess.CompletedProcess([], 0, stdout=table)
        with patch.object(fonts.subprocess, "run", return_value=result), \
             patch.object(fonts.sys, "argv", ["verify_pdf_fonts.py", "book.pdf"]):
            return fonts.main()

    def test_chinese_hiragino_does_not_trigger_japanese_limit(self):
        table = row("ABCDEF+PingFangSC-Regular")
        table += row("ABCDEF+HiraginoSansGB-W3") * 48
        self.assertEqual(self.run_check(table), 0)

    def test_japanese_fallback_still_fails(self):
        table = row("ABCDEF+PingFangSC-Regular")
        table += row("ABCDEF+HiraginoSans-W3") * 21
        self.assertEqual(self.run_check(table), 1)

    def test_nonembedded_pingfang_does_not_pass(self):
        self.assertEqual(self.run_check(row("PingFangSC-Regular", "no")), 1)

    def test_mixed_hiragino_variants_are_separate(self):
        table = row("ABCDEF+PingFangSC-Regular")
        table += row("ABCDEF+HiraginoSansGB-W3") * 48
        table += row("ABCDEF+HiraginoSans-W3") * 20
        self.assertEqual(self.run_check(table), 0)
        self.assertEqual(fonts.font_group("ABCDEF+HiraginoSansCNS-W3"),
                         "HiraginoTraditionalChinese")


if __name__ == "__main__":
    unittest.main()
