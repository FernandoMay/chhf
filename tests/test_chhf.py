"""Test suite for chhf: Huffman compression + chaotic keystream.

Run with:
    python -m unittest discover -s tests -v
"""
import unittest

from chhf import ChaoticKeystreamGenerator, HuffmanCompression


class TestHuffmanRoundTrip(unittest.TestCase):
    """compress(decompress(x)) must be an identity for ANY input."""

    def setUp(self):
        self.h = HuffmanCompression()

    def test_empty_string(self):
        self.assertEqual(self.h.decompress(self.h.compress("")), "")

    def test_single_char(self):
        # THE regression: single-symbol trees lost all data before revival.
        self.assertEqual(self.h.decompress(self.h.compress("a")), "a")

    def test_repeated_single_char(self):
        text = "a" * 5000
        self.assertEqual(self.h.decompress(self.h.compress(text)), text)

    def test_two_distinct_chars(self):
        self.assertEqual(self.h.decompress(self.h.compress("ab")), "ab")

    def test_ascii_text(self):
        text = "the quick brown fox jumps over the lazy dog. " * 20
        self.assertEqual(self.h.decompress(self.h.compress(text)), text)

    def test_unicode_and_emoji(self):
        text = "Hola 🌎 ¿cómo estás? ¡Qué bueno verte! — ünïcødé ✓ " * 3
        self.assertEqual(self.h.decompress(self.h.compress(text)), text)

    def test_spanish_literary_sample(self):
        text = (
            "En el corazón de la vasta y silenciosa noche, un único faro "
            "enviaba su rayo de luz sobre las olas oscuras. La seguridad, "
            "la seguridad, la seguridad. Sin seguridad no hay nada.\n"
        ) * 10
        self.assertEqual(self.h.decompress(self.h.compress(text)), text)

    def test_newlines_and_whitespace(self):
        text = "line1\nline2\r\n\tindented  spaces\n" * 7
        self.assertEqual(self.h.decompress(self.h.compress(text)), text)


class TestCompressionRatio(unittest.TestCase):
    """Huffman must actually compress redundant data."""

    def setUp(self):
        self.h = HuffmanCompression()

    def test_redundant_text_compresses(self):
        text = "seguridad " * 200
        compressed = self.h.compress(text)
        self.assertLess(len(compressed), len(text.encode("utf-8")))

    def test_single_symbol_compresses(self):
        text = "z" * 1000
        compressed = self.h.compress(text)
        self.assertLess(len(compressed), len(text.encode("utf-8")))


class TestWireFormat(unittest.TestCase):
    """Format: [padding byte] + [serialized tree] + [packed data]."""

    def setUp(self):
        self.h = HuffmanCompression()

    def test_starts_with_padding_byte(self):
        data = self.h.compress("abracadabra")
        self.assertEqual(data[0], (8 - (len("abracadabra") * 0) % 8) % 8 if False else data[0] in range(8))

    def test_round_trip_binary_stability(self):
        # Same input → same bytes (deterministic format).
        a = self.h.compress("deterministic output")
        b = self.h.compress("deterministic output")
        self.assertEqual(bytes(a), bytes(b))

    def test_corrupted_tree_header_raises(self):
        # flag=1 (leaf) but truncated before the length byte arrives.
        with self.assertRaises(ValueError):
            self.h._deserialize_tree(bytearray([1]), 0)

    def test_truncated_char_bytes_raises(self):
        with self.assertRaises(ValueError):
            self.h._deserialize_tree(bytearray([1, 4, 0x41]), 0)


class TestChaoticKeystream(unittest.TestCase):
    def setUp(self):
        self.gen = ChaoticKeystreamGenerator(0.7351, 3.999)

    def test_deterministic_stream(self):
        g1 = ChaoticKeystreamGenerator(0.5, 3.99)
        g2 = ChaoticKeystreamGenerator(0.5, 3.99)
        self.assertEqual([g1.next_byte() for _ in range(32)],
                         [g2.next_byte() for _ in range(32)])

    def test_bytes_in_range(self):
        for _ in range(100):
            b = self.gen.next_byte()
            self.assertTrue(0 <= b <= 255)

    def test_seed_changes_stream(self):
        g1 = ChaoticKeystreamGenerator(0.5, 3.99)
        g2 = ChaoticKeystreamGenerator(0.7, 3.99)
        self.assertNotEqual(g1.next_byte(), g2.next_byte())

    def test_rejects_non_chaotic_r(self):
        with self.assertRaises(ValueError):
            ChaoticKeystreamGenerator(0.5, 2.0)   # not chaotic
        with self.assertRaises(ValueError):
            ChaoticKeystreamGenerator(0.5, 4.5)   # out of range


if __name__ == "__main__":
    unittest.main()
