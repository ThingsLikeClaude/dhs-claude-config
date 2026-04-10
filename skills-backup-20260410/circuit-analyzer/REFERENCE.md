# Circuit Analyzer Reference

> Altium .schdoc format details and record type registry.

## File Format

Altium `.schdoc` files are OLE Compound File Binary (CFB) containers. The schematic data lives in the `FileHeader` stream as pipe-delimited ASCII records.

### Binary Structure

```
[2-byte LE length][1 zero byte][1 type byte][payload]
```

- Length: Little-endian uint16, payload size
- Payload: `|KEY=VALUE|KEY=VALUE|...` format, null-terminated
- Encoding: Latin-1 base, with `%UTF8%` prefix for Unicode fields

### Field Naming

Two conventions exist across Altium versions:

| Older Files | Newer Files | Parser Key |
|-------------|-------------|------------|
| `LIBREFERENCE` | `LibReference` | `libreference` |
| `RECORD` | `Record` | `record` |
| `OWNERINDEX` | `OwnerIndex` | `ownerindex` |

The parser lowercases all keys, so access is uniform.

### UTF-8 Handling

Korean/Unicode text appears as dual fields:
```
|%UTF8%Text=한글텍스트|Text=raw_bytes|
```

The parser prefers `%UTF8%` values when present.

## Record Type Registry

Based on verification against real .schdoc files:

| Record | Type | Key Fields | Purpose |
|--------|------|------------|---------|
| 1 | Component | `libreference`, `indexinsheet`, `location.x/y` | Component instance |
| 2 | Pin | `designator`, `name`, `electrical`, `ownerindex` | Component pin |
| 4 | Label | `text`, `location.x/y` | Text label |
| 6 | Polyline | `locationcount`, `color` | Drawing polyline |
| 7 | Polygon | `locationcount`, `color` | Drawing polygon |
| 12 | Arc | `radius`, `startangle`, `endangle` | Drawing arc |
| 13 | Line | `location.x/y`, `corner.x/y` | Drawing line |
| 14 | Rectangle | `location.x/y`, `corner.x/y`, `color` | Drawing rectangle |
| 17 | Power Port | `text`, `style`, `location.x/y` | Power/GND symbol |
| 25 | Net Label | `text`, `location.x/y` | Signal net name |
| 27 | Wire | `location.x/y`, `corner.x/y` | Electrical wire |
| 28 | Bus | `location.x/y`, `corner.x/y` | Bus line |
| 29 | Junction | `location.x/y` | Wire junction |
| 31 | Sheet Symbol | `sheetname`, `filename` | Hierarchical sheet |
| 34 | Designator | `text`, `name=Designator`, `ownerindex` | Ref designator (R1, U1) |
| 41 | Parameter | `name`, `text`, `ownerindex` | Component parameter (Value) |

### Pin Electrical Types

| Code | Type | Description |
|------|------|-------------|
| 0 | Input | Signal input |
| 1 | IO | Bidirectional |
| 2 | Output | Signal output |
| 3 | OpenCollector | Open collector output |
| 4 | Passive | Passive element (R, C, L) |
| 5 | HiZ | High impedance |
| 6 | OpenEmitter | Open emitter output |
| 7 | Power | Power pin (VCC, GND) |

### Power Port Styles

| Style | Symbol |
|-------|--------|
| 0 | Circle (generic) |
| 1 | Arrow (power rail) |
| 2 | Bar (ground) |
| 3 | Wave (earth ground) |
| 4 | Power ground |
| 5 | Signal ground |
| 6 | Earth |
| 7 | GND power |

## OwnerIndex Resolution

Two mapping schemes exist:

### Scheme A (Older files)
```
Component.IndexInSheet == Child.OwnerIndex
```
Example: Component has `IndexInSheet=5` → Children have `OwnerIndex=5`

### Scheme B (Newer files)
```
Component._seq - 1 == Child.OwnerIndex
```
Example: Component is 10th record (seq=10) → Children have `OwnerIndex=9`

The parser tests both schemes against the first 10 components and uses whichever matches more designators.

## Coordinate System

- Units: 1/100 inch (centimils)
- Origin: Bottom-left of sheet
- Y-axis: Increases upward
- Typical sheet: 29700 x 21000 (A4 landscape in centimils)

## Output JSON Schema

```json
{
  "file": "string — source file path",
  "header": "string — file header info",
  "owner_scheme": "A | B",
  "total_records": "number",
  "bom": [
    {
      "ref": "string — R1, U1, CON1",
      "lib_ref": "string — library component name",
      "value": "string — component value",
      "pin_count": "number",
      "pins": [
        {
          "number": "string — pin number",
          "name": "string — pin function name",
          "electrical": "Input | IO | Output | Passive | Power | ..."
        }
      ],
      "location": { "x": "number", "y": "number" }
    }
  ],
  "component_summary": {
    "Resistors": "number",
    "Capacitors": "number",
    "Logic ICs (74xx)": "number",
    "FPGA/CPLD": "number"
  },
  "nets": {
    "labels": ["string — unique net names"],
    "label_count": "number"
  },
  "power": {
    "rails": ["string — VCC, GND, etc."],
    "signals_via_power_port": ["string — signals using power port symbols"],
    "detail": { "net_name": "instance_count" }
  },
  "connectors": [
    {
      "ref": "string",
      "lib_ref": "string",
      "pin_count": "number",
      "pins": ["pin objects"]
    }
  ],
  "wiring": {
    "wires": "number",
    "junctions": "number",
    "buses": "number"
  },
  "stats": {
    "components": "number",
    "pins_total": "number",
    "net_labels_unique": "number",
    "power_port_instances": "number",
    "wires": "number",
    "junctions": "number"
  }
}
```

## Known Limitations

1. **Multi-part component pin duplication (~11%)** — Components like 74LS08 (4 gates in one IC) appear across multiple sheets with shared power pins. These power pins appear in multiple nets (~11% of all pins). This is cosmetic — the named signal nets are correct.
2. **Pin hotspot accuracy (~74%)** — The `pinconglomerate` rotation-based hotspot calculation matches wire endpoints for ~74% of pins. Remaining mismatches are likely from mirrored or custom-rotated components.
3. **Hierarchical sheets** — Sheet symbols (Record 31) are parsed but hierarchical port/entry connectivity is not traced. Cross-sheet connectivity relies on same-name net labels.
4. **Constraint file pin prefix** — UCF/XDC use prefixed pins (P100, B5) while schematics use numeric-only (100, 5). Strip the letter prefix before cross-referencing.
5. **No rendering** — SVG/PNG rendering of the schematic from parsed data is not implemented.

## Validation Results

Tested against HVPG_RA00 board (6 sheets, 506 components, XC3S250E FPGA):

| Metric | Result |
|--------|--------|
| UCF pin cross-reference | 96% (128/134) |
| Pin deduplication | 88.6% clean |
| Named nets | 322 |
| Cross-sheet nets | 196 |
| FPGA I/O coverage | 83% (172/208) |
