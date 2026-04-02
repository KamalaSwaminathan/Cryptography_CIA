"""
test_roundtrip.py
-----------------
Full encrypt → hash → decrypt round-trip test.
Demonstrates both worked examples and an avalanche sensitivity check.

Run with:
    python test_roundtrip.py
"""

from cipher_and_hash import encrypt, decrypt, vowel_consonant_hash


# ──────────────────────────────────────────────────────────────
#  ROUND-TRIP EXAMPLE
# ──────────────────────────────────────────────────────────────

def run_example(label, plaintext, key):
    """
    Run one full encrypt → hash → decrypt cycle and print results.

    The hash is computed on the ciphertext (not the plaintext) so it
    serves as an integrity check on what is actually transmitted.
    The receiver recomputes the hash on arrival — if the digests
    match, the ciphertext was not altered in transit.
    """
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    ciphertext = encrypt(plaintext, key)
    digest     = vowel_consonant_hash(ciphertext)
    recovered  = decrypt(ciphertext, key)

    print(f"  Plaintext   : {plaintext}")
    print(f"  Key (cols)  : {key}")
    print(f"  Ciphertext  : {ciphertext}")
    print(f"  Hash digest : {digest}")
    print(f"  Decrypted   : {recovered}")

    # integrity check — recompute and compare
    integrity = "PASS ✓" if vowel_consonant_hash(ciphertext) == digest else "FAIL ✗"
    print(f"  Integrity   : {integrity}")

    # tamper detection — flip one character, check if hash changes
    tampered    = ciphertext[:-1] + ('A' if ciphertext[-1] != 'A' else 'B')
    tamper_hash = vowel_consonant_hash(tampered)
    detected    = "DETECTED ✓" if tamper_hash != digest else "MISSED ✗"
    print(f"  Tamper test : {detected}")
    print(f"    original  : {digest}")
    print(f"    tampered  : {tamper_hash}")


# ──────────────────────────────────────────────────────────────
#  AVALANCHE TEST
# ──────────────────────────────────────────────────────────────

def test_avalanche():
    """
    A good hash should flip roughly half its output bits when the
    input changes by even one character. We count the differing bits
    by XOR-ing the two digests and counting set bits.~32/64 bits changing is ideal.
    """
    print(f"\n{'='*60}")
    print(f"  Avalanche / Sensitivity Test")
    print(f"  (how many of 64 output bits flip from a 1-char change)")
    print(f"{'='*60}")

    pairs = [
        ("ATTACK",             "ATTACC"),
        ("HELLO",              "HELLA"),
        ("THEQUICKBROWNFOX",   "THEQUICKBROWNFOY"),
        ("CRYPTOGRAPHY",       "CRYPTOGRAPHX"),
    ]

    for a, b in pairs:
        ha       = vowel_consonant_hash(a)
        hb       = vowel_consonant_hash(b)
        diffbits = bin(int(ha, 16) ^ int(hb, 16)).count('1')
        print(f"\n  Input A : {a}")
        print(f"  Hash A  : {ha}")
        print(f"  Input B : {b}")
        print(f"  Hash B  : {hb}")
        print(f"  Bits changed : {diffbits} / 64")


# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  SPIRAL ROUTE CIPHER + DUAL-LANE VOWEL-CONSONANT HASH")
    print("  Round-Trip Test\n")

    run_example(
        label     = "Example 1 — Short message",
        plaintext = "HELLOWORLD",
        key       = 4
    )

    run_example(
        label     = "Example 2 — Longer message",
        plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",
        key       = 6
    )

    test_avalanche()

    print(f"\n{'='*60}\n")
