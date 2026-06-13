'use strict';
const zlib = require('zlib');
const fs   = require('fs');

// ── CRC32 (required for PNG chunk integrity) ──────────────────────────────
const CRC_TABLE = new Uint32Array(256);
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
  CRC_TABLE[n] = c;
}
function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function pngChunk(type, data) {
  const len = Buffer.allocUnsafe(4); len.writeUInt32BE(data.length);
  const t   = Buffer.from(type);
  const crc = Buffer.allocUnsafe(4); crc.writeUInt32BE(crc32(Buffer.concat([t, data])));
  return Buffer.concat([len, t, data, crc]);
}

// ── Minimal PNG builder (RGBA, no interlace) ──────────────────────────────
function buildPNG(size, getPixel) {
  const SIG = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const hdr = Buffer.alloc(13);
  hdr.writeUInt32BE(size, 0); hdr.writeUInt32BE(size, 4);
  hdr[8] = 8; hdr[9] = 6; // 8-bit RGBA

  const stride = 1 + size * 4;
  const raw = Buffer.alloc(size * stride);
  for (let y = 0; y < size; y++) {
    raw[y * stride] = 0; // filter: None
    for (let x = 0; x < size; x++) {
      const [r, g, b, a] = getPixel(x, y, size);
      const o = y * stride + 1 + x * 4;
      raw[o] = r; raw[o+1] = g; raw[o+2] = b; raw[o+3] = a;
    }
  }

  return Buffer.concat([
    SIG,
    pngChunk('IHDR', hdr),
    pngChunk('IDAT', zlib.deflateSync(raw)),
    pngChunk('IEND', Buffer.alloc(0)),
  ]);
}

// ── App palette ───────────────────────────────────────────────────────────
const GOLD = [232, 197, 71, 255]; // #e8c547
const DARK = [17,  17,  17, 255]; // #111
const NONE = [0,   0,   0,  0  ];

// ── Is this pixel part of the "G" letterform? ────────────────────────────
function inG(px, py, cx, cy, sz) {
  const s  = sz / 256;
  const W  = 80  * s;
  const H  = 100 * s;
  const TH = Math.max(2, Math.round(14 * s)); // stroke thickness

  const L   = cx - W / 2;
  const R   = cx + W / 2;
  const Top = cy - H / 2;
  const Bot = cy + H / 2;
  const MID = cy - 2 * s;

  // Sample pixel center
  const x = px + 0.5, y = py + 0.5;
  if (x < L || x > R || y < Top || y > Bot) return false;

  if (y < Top + TH) return true;              // top bar
  if (y > Bot - TH) return true;              // bottom bar
  if (x < L + TH)   return true;              // left column (full height)
  if (x > R - TH && y >= MID) return true;   // right column (lower half only)
  if (y >= MID && y < MID + TH && x >= cx) return true; // mid crossbar

  return false;
}

// ── Per-pixel color function ──────────────────────────────────────────────
function pixel(x, y, sz) {
  const cx = sz / 2, cy = sz / 2;
  const dx = x + 0.5 - cx, dy = y + 0.5 - cy;
  const d  = Math.sqrt(dx * dx + dy * dy);

  // Ring width: at least 3px, scales with size
  const ringW = Math.max(3, Math.round(sz * 0.047));
  const OR = sz * 0.448; // outer radius
  const IR = OR - ringW; // inner radius

  // Soft outer edge (1px anti-alias)
  if (d > OR + 0.5) return NONE;
  if (d > OR - 0.5) {
    const a = Math.round(255 * (OR + 0.5 - d));
    return [GOLD[0], GOLD[1], GOLD[2], a];
  }

  if (d > IR) return GOLD;                  // gold ring
  if (inG(x, y, cx, cy, sz)) return GOLD;  // gold letter
  return DARK;                              // dark interior
}

// ── Generate files ────────────────────────────────────────────────────────
fs.writeFileSync('icon.png',      buildPNG(256, pixel));
console.log('icon.png      created (256×256)');

fs.writeFileSync('tray-icon.png', buildPNG(32, pixel));
console.log('tray-icon.png created (32×32)');
