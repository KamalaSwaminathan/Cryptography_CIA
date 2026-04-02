import math


# ══════════════════════════════════════════════════════════════
#  PART 1 — SPIRAL ROUTE CIPHER
# ══════════════════════════════════════════════════════════════

def _build_grid(text, num_cols):
    """
    Lay the text into a 2D grid row by row and pad if needed.
   'X' is the classical dummy for transposition ciphers.
    """
    PAD      = 'X'
    num_rows = math.ceil(len(text) / num_cols)
    total    = num_rows * num_cols
    text     = text + PAD * (total - len(text))

    grid = []
    for r in range(num_rows):
        grid.append(list(text[r * num_cols : (r + 1) * num_cols]))

    return grid, num_rows


def _spiral_read(grid, num_rows, num_cols):
    """
    Read the grid in clockwise spiral order, starting top-left.

    Direction cycle: right → down → left → up → repeat inward.
    Four boundary variables (top, bottom, left, right) shrink after
    each pass so we never re-visit a cell.
    """
    result = []
    top, bottom = 0, num_rows - 1
    left, right = 0, num_cols - 1

    while top <= bottom and left <= right:

        for c in range(left, right + 1):         # → right along top
            result.append(grid[top][c])
        top += 1

        for r in range(top, bottom + 1):         # ↓ down right side
            result.append(grid[r][right])
        right -= 1

        if top <= bottom:                         # ← left along bottom
            for c in range(right, left - 1, -1):
                result.append(grid[bottom][c])
            bottom -= 1

        if left <= right:                         # ↑ up left side
            for r in range(bottom, top - 1, -1):
                result.append(grid[r][left])
            left += 1

    return result


def _spiral_write(chars, num_rows, num_cols):
    """
    Place characters into an empty grid following the same spiral route.

    Why this works:
      Encryption = write row-by-row, read spiral
      Decryption = write spiral,     read row-by-row
      The two are exact inverses.
    """
    grid = [['' for _ in range(num_cols)] for _ in range(num_rows)]
    idx  = 0

    top, bottom = 0, num_rows - 1
    left, right = 0, num_cols - 1

    while top <= bottom and left <= right:

        for c in range(left, right + 1):
            grid[top][c] = chars[idx]; idx += 1
        top += 1

        for r in range(top, bottom + 1):
            grid[r][right] = chars[idx]; idx += 1
        right -= 1

        if top <= bottom:
            for c in range(right, left - 1, -1):
                grid[bottom][c] = chars[idx]; idx += 1
            bottom -= 1

        if left <= right:
            for r in range(bottom, top - 1, -1):
                grid[r][left] = chars[idx]; idx += 1
            left += 1

    return grid


def encrypt(plaintext, num_cols):
    
  # Encrypt plaintext using the spiral route cipher.

    plaintext      = plaintext.upper().replace(" ", "")
    grid, num_rows = _build_grid(plaintext, num_cols)
    spiral         = _spiral_read(grid, num_rows, num_cols)
    return ''.join(spiral)


def decrypt(ciphertext, num_cols):
    
# Decrypt a spiral route ciphertext.
    
    num_rows  = math.ceil(len(ciphertext) / num_cols)
    grid      = _spiral_write(list(ciphertext), num_rows, num_cols)
    plaintext = ''.join(''.join(row) for row in grid)
    return plaintext


# ══════════════════════════════════════════════════════════════
#  PART 2 — DUAL-LANE VOWEL-CONSONANT HASH  (custom, from scratch)
# ══════════════════════════════════════════════════════════════

MASK    = 0xFFFFFFFFFFFFFFFF
V_PRIME = 1000000007
C_PRIME = 998244353
ROT_V   = 13
ROT_C   = 17
VOWELS  = set("AEIOU")


def _rotate_left_64(val, shift):
    """
    Rotate a 64-bit integer left by `shift` bits.

    Unlike a plain left shift (which discards high bits), rotation
    wraps the displaced bits back to the low end. No information is
    lost - every bit of the current state influences all future states.

    """
    shift = shift % 64
    return ((val << shift) | (val >> (64 - shift))) & MASK


def vowel_consonant_hash(text):

   # Compute the dual-lane vowel-consonant hash of a string.

    text  = text.upper()
    v_acc = 0     # vowel lane starts at zero
    c_acc = 0     # consonant lane starts at zero

    for i, ch in enumerate(text):
        if not ch.isalpha():
            continue                        # skip spaces, digits, punctuation

        weight = (i + 1) * ord(ch)         # position-weighted contribution

        if ch in VOWELS:
            # rotate first (avalanche), then fold in the weighted value
            v_acc = _rotate_left_64(v_acc, ROT_V)
            v_acc = (v_acc + weight * V_PRIME) & MASK
        else:
            c_acc = _rotate_left_64(c_acc, ROT_C)
            c_acc = (c_acc + weight * C_PRIME) & MASK

    # merge: XOR combines both lanes; the extra multiply-and-add
    # prevents the digest being zero when v_acc == c_acc
    combined = (v_acc ^ c_acc) & MASK
    combined = (combined * V_PRIME + c_acc) & MASK

    return format(combined, '016X')
