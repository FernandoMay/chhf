"""CLI for chhf: compress/decompress text files with Huffman + optional chaotic cipher.

Usage:
    python -m chhf compress input.txt output.chhf
    python -m chhf decompress input.chhf output.txt
    python -m chhf demo
"""
import argparse
import sys
from pathlib import Path

from chhf import ChaoticKeystreamGenerator, HuffmanCompression, process_data


def compress_file(src: Path, dst: Path, key=None) -> None:
    text = src.read_text(encoding="utf-8")
    h = HuffmanCompression()
    data = bytearray(h.compress(text))

    if key is not None:
        x0, r = key
        gen = ChaoticKeystreamGenerator(x0, r)
        data = bytearray(b ^ gen.next_byte() for b in data)

    dst.write_bytes(bytes(data))
    ratio = len(text.encode("utf-8")) / max(len(data), 1)
    print(f"compressed: {src} ({len(text.encode('utf-8'))} B) -> {dst} ({len(data)} B) [{ratio:.2f}:1]")


def decompress_file(src: Path, dst: Path, key=None) -> None:
    data = bytearray(src.read_bytes())

    if key is not None:
        x0, r = key
        gen = ChaoticKeystreamGenerator(x0, r)
        data = bytearray(b ^ gen.next_byte() for b in data)

    h = HuffmanCompression()
    text = h.decompress(data)
    dst.write_text(text, encoding="utf-8")
    print(f"decompressed: {src} -> {dst} ({len(text.encode('utf-8'))} B)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="chhf",
        description="Huffman compression with optional chaotic (logistic-map) stream cipher.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_enc = sub.add_parser("compress", help="compress a UTF-8 text file")
    p_enc.add_argument("src", type=Path)
    p_enc.add_argument("dst", type=Path)

    p_dec = sub.add_parser("decompress", help="decompress a .chhf file")
    p_dec.add_argument("src", type=Path)
    p_dec.add_argument("dst", type=Path)

    sub.add_parser("demo", help="run the end-to-end demo")

    args = parser.parse_args(argv)

    if args.command == "demo":
        process_data(
            "La seguridad, la seguridad, la seguridad. Sin seguridad no hay nada. " * 30
        )
        return 0

    if not args.src.exists():
        print(f"error: {args.src} does not exist", file=sys.stderr)
        return 1

    if args.command == "compress":
        compress_file(args.src, args.dst)
    else:
        decompress_file(args.src, args.dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
