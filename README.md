# Spiral Route Cipher + Dual-Lane Vowel-Consonant Hash

**Course:** Cryptography  
**Assignment:** CIA - Classical Cipher & Hashing Implementation (ROUTE CIPHER)
**Language:** Python 3 (no external libraries, no cryptography imports) 

---

## Repository Structure

```
├── cipher_and_hash.py   # Spiral Route Cipher + Dual-Lane Vowel-Consonant Hash
├── test_roundtrip.py    # Full encrypt → hash → decrypt round-trip test
└── README.md
```

---

## How to Run

```bash
# Clone the repo
git clone <your-repo-url>
cd <repo-folder>

# Run the test script (pure Python 3, nothing to install)
python test_roundtrip.py
```

---

## Part 1 — Spiral Route Cipher

### Route Cipher?

A Route Cipher is a **transposition cipher** — characters are rearranged according to a geometric route through a grid rather than substituted. It is one of the oldest cipher families, used historically for military communication because the key is a single integer and the operation is easy to do by hand.

### Why Spiral?

A standard route cipher reads columns or rows - linear patterns that are predictable and easy to reverse without the key. We use a **clockwise spiral** as the route instead. This makes the transposition non-linear: characters that were adjacent in the plaintext end up far apart in the ciphertext. The result is better diffusion (spreading of plaintext patterns) with the same simple key.

### How Encryption Works

**Key:** a single integer — the number of columns in the grid. Both sender and receiver must agree on this.

**Steps:**

1. Uppercase the plaintext and remove spaces
2. Write it into a grid of `num_cols` columns, left to right, top to bottom
3. If the last row is not full, pad with `X` (classical dummy character for transposition ciphers — filling the row makes the grid a complete rectangle, which is required for the spiral to work correctly)
4. Read the grid back out in a **clockwise spiral** starting from the top-left corner
5. That reading order is the ciphertext

**Decryption** is the exact inverse:
- Write the ciphertext back into a grid following the same spiral route
- Read the grid row by row → plaintext recovered

This works because:
```
Encryption: write row-by-row  →  read spiral
Decryption: write spiral      →  read row-by-row
```
The two operations are exact inverses of each other.

### Variables

| Variable | Description |
|---|---|
| `num_cols` | Key — width of the grid |
| `num_rows` | Derived: `ceil(len(plaintext) / num_cols)` |
| `PAD` | `'X'` — dummy character to complete the last row |
| `grid` | 2D list of characters, filled row by row |
| `top, bottom, left, right` | Boundary variables that shrink inward each spiral pass |

### Example 1 - Short Message

```
Plaintext   :  HELLOWORLD
Key (cols)  :  4

Grid layout (written row by row):
  H  E  L  L
  O  W  O  R
  L  D  X  X   ← XX is padding

Clockwise spiral read:
  Top row    →   H  E  L  L
  Right col  ↓   R  X
  Bottom row ←   X  D  L
  Left col   ↑   O
  Inner      →   W  O

Ciphertext  :  HELLRXXDLOWO
Decrypted   :  HELLOWORLDXX   (strip trailing X padding to recover original)
Hash digest :  ADCCD92C5860AD3C
```

### Example 2 - Longer Message

```
Plaintext   :  THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG
Key (cols)  :  6
Ciphertext  :  THEQUIWUEAXGODYZRMNCKBROJVLEHTPFOXOS
Decrypted   :  THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGX
Hash digest :  3C9B82DADA72A465
```

---

## Part 2 - Dual-Lane Vowel-Consonant Hash

### Why This Hash?

Vowels and consonants play structurally different roles in English. Vowels carry the rhythm and stress of a word; consonants carry its shape. A naive hash treats all characters identically — patterns in the input tend to produce patterns in the output.

This hash separates them into **two independent accumulators** (lanes) that run in parallel and only combine at the very end via XOR:

- The **vowel lane** accumulates only on vowel characters
- The **consonant lane** accumulates only on consonant characters
- A change to any vowel propagates through the vowel lane and flips the final digest
- A change to any consonant propagates through the consonant lane and flips the final digest
- Because the merge is XOR, either change scrambles the whole output

**Bit rotation** after each character gives the avalanche property: a change at position `i` cascades through every state from `i+1` onward, not just the current one. This is what makes ~50% of output bits flip from a single character change.

### Constants

| Constant | Value | Purpose |
|---|---|---|
| `MASK` | `0xFFFFFFFFFFFFFFFF` | 64-bit mask. Python integers grow unboundedly — AND-ing with this after every operation keeps all values within 64 bits |
| `V_PRIME` | `1000000007` | Large prime for the vowel lane multiplier. Primes spread values uniformly — a composite multiplier causes periodic patterns in the accumulator |
| `C_PRIME` | `998244353` | Large prime for the consonant lane. Deliberately different from `V_PRIME` so the two lanes mix at different rates, reducing the chance they cancel each other at the XOR step |
| `ROT_V` | `13` | Bit rotation amount for the vowel lane |
| `ROT_C` | `17` | Bit rotation amount for the consonant lane — asymmetric to `ROT_V` so the two lanes' bit patterns don't align and interfere |
| `VOWELS` | `{A, E, I, O, U}` | The five English vowels used to route each character to its lane |

### Variables

| Variable | Description |
|---|---|
| `i` | Index of the current character (0-based) |
| `ch` | Current character (uppercased) |
| `weight` | `(i + 1) * ord(ch)` — position-weighted ASCII value. The `+1` ensures index-0 characters contribute a non-zero weight. `ord(ch)` ties the contribution to which character it is, not just where |
| `v_acc` | Vowel lane accumulator — 64-bit, updated only when `ch` is a vowel |
| `c_acc` | Consonant lane accumulator — 64-bit, updated only when `ch` is a consonant |
| `combined` | Final merged value before output |

### Algorithm — Step by Step

For each character `ch` at index `i` (letters only, spaces and symbols skipped):

```
weight = (i + 1) × ord(ch)
```

If `ch` is a vowel:
```
v_acc = rotate_left_64(v_acc, 13)
v_acc = (v_acc + weight × V_PRIME) & MASK
```

If `ch` is a consonant:
```
c_acc = rotate_left_64(c_acc, 17)
c_acc = (c_acc + weight × C_PRIME) & MASK
```

**What rotate_left_64 does:**  
A normal left shift discards the high bits that fall off the top. Rotation wraps them back to the low end — no information is lost, and every bit of the current state influences all future states.

```
8-bit example:
  rotate_left(0b11000001, 2) → 0b00000111
  The two high 1-bits wrap around to the bottom.
```

**Final merge:**
```
combined = (v_acc XOR c_acc) & MASK
combined = (combined × V_PRIME + c_acc) & MASK
```

XOR merges both lanes. The extra multiply-and-add step prevents the digest from being zero in the edge case where `v_acc == c_acc`.

**Output:** 16-character uppercase hex string (64-bit digest)  
Possible values: 2⁶⁴ ≈ 18.4 quintillion

### Avalanche Test Results

A one-character change flips approximately half the output bits - the same property targeted by SHA-family hashes:
(To evaluate strength of algorithm)

| Input A | Input B | Bits flipped (out of 64) |
|---|---|---|
| `ATTACK` | `ATTACC` | 29 |
| `HELLO` | `HELLA` | 28 |
| `THEQUICKBROWNFOX` | `THEQUICKBROWNFOY` | 30 |
| `CRYPTOGRAPHY` | `CRYPTOGRAPHX` | 25 |

---

## Part 3 — Round-Trip Test Output

```
Example 1 — Short message
  Plaintext   : HELLOWORLD
  Key (cols)  : 4
  Ciphertext  : HELLRXXDLOWO
  Hash digest : ADCCD92C5860AD3C
  Decrypted   : HELLOWORLDXX
  Integrity   : PASS 
  Tamper test : DETECTED 
    original  : ADCCD92C5860AD3C
    tampered  : A5BEFF58A6EDEED4

Example 2 — Longer message
  Plaintext   : THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG
  Key (cols)  : 6
  Ciphertext  : THEQUIWUEAXGODYZRMNCKBROJVLEHTPFOXOS
  Hash digest : 3C9B82DADA72A465
  Decrypted   : THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGX
  Integrity   : PASS 
  Tamper test : DETECTED 
    original  : 3C9B82DADA72A465
    tampered  : 266043E9222FB17A
```

The hash is applied to the **ciphertext**, not the plaintext. This means it acts as an integrity check on what is actually transmitted. The sender computes `vowel_consonant_hash(ciphertext)` and sends the digest alongside. The receiver recomputes it on arrival — if the digests match, the ciphertext was not altered in transit. The tamper test above demonstrates this: flipping a single character in the ciphertext produces a completely different digest.

---

## Limitations 

- Both lanes start at zero. If the input contains no vowels (e.g. `BCDF`), the vowel lane stays at zero and the digest is effectively single-lane. For normal English text this does not occur. A non-zero starting seed for each lane would fix this edge case — it was intentionally left out to keep the design transparent and easy to follow.

The Spiral Route Cipher is not secure by modern standards. It is a pure transposition cipher and is vulnerable to frequency analysis and known-plaintext attacks. This implementation is for educational purposes only. The Dual-Lane Vowel-Consonant Hash has not been formally analysed or peer-reviewed and should not replace SHA-256 or similar in any real application.
