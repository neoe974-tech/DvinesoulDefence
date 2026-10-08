import tempfile
import unittest
from pathlib import Path

from app.main import DEFAULT_PATHS, load_words, make_password, strength, valid_url


class CoreTests(unittest.TestCase):
    def test_valid_url_normalizes_trailing_slash(self):
        self.assertEqual(valid_url(" https://example.com/app "), "https://example.com/app/")

    def test_valid_url_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            valid_url("ftp://example.com")

    def test_strength_empty_password(self):
        self.assertEqual(strength("")[0], 0)

    def test_generated_password_length_and_character_classes(self):
        password = make_password(20)
        self.assertEqual(len(password), 20)
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(not c.isalnum() for c in password))

    def test_generated_password_rejects_short_length(self):
        with self.assertRaises(ValueError):
            make_password(8)

    def test_default_wordlist_is_preserved(self):
        self.assertIs(load_words("", DEFAULT_PATHS), DEFAULT_PATHS)

    def test_loads_custom_wordlist(self):
        with tempfile.TemporaryDirectory() as directory:
            wordlist = Path(directory) / "words.txt"
            wordlist.write_text("# comment\nadmin\n\nlogin\n", encoding="utf-8")
            self.assertEqual(load_words(str(wordlist), DEFAULT_PATHS), ["admin", "login"])


if __name__ == "__main__":
    unittest.main()
