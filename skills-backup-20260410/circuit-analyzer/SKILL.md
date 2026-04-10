# Circuit Analyzer Skill

> Parse Altium .schdoc files and circuit PDFs to understand board designs for FPGA development.

## Trigger Conditions

Activate this skill when:
- User provides a `.schdoc` or `.SchDoc` file path for analysis
- User provides a circuit schematic PDF for analysis
- User asks to analyze a circuit board design
- User wants to write FPGA/VHDL code based on a schematic
- User mentions Altium Designer files, pin maps, or board connectors

## Core Workflow

The primary use case: user provides a NEW schematic → parse it → understand the board → help write FPGA VHDL code with correct pin mappings and signal names.

### Step 1: Detect File Type

```
Input file extension:
├── .schdoc / .SchDoc  → Step 2a (Binary parse)
├── .pdf               → Step 2b (Vision parse)
└── Both provided      → Run both, cross-reference
```

### Step 2a: Parse Single .schdoc File

For single-sheet schematics:

```bash
python ~/.claude/skills/circuit-analyzer/scripts/parse_schdoc.py "{path}" -f json
```

Available output formats:
- `-f json` — Full structured data (default)
- `-f summary` — Human-readable overview
- `-f bom` — BOM table only
- `-f nets` — Net labels and power nets only
- `-f pins` — Pin map for FPGA port mapping

### Step 2a-multi: Parse Multi-Sheet Board (v2)

For boards with multiple schematic sheets (most real boards have 2-70+ sheets):

```bash
python ~/.claude/skills/circuit-analyzer/scripts/parse_board.py "{directory}" -f summary
```

This provides everything parse_schdoc.py does, PLUS:
- **Multi-sheet batch parsing** — All .schdoc files in directory parsed together
- **Unified BOM** — Deduplicated across sheets (multi-part components merged)
- **Cross-sheet net unification** — Same net name on different sheets = same net
- **Wire-based netlist** — Union-Find traces pin→wire→net label connections
- **Pin hotspot calculation** — Correct connection point using pinconglomerate rotation

Available output formats:
- `-f json` — Full structured data with netlist (default)
- `-f summary` — Board overview with cross-sheet net details
- `-f netlist` — Named nets with all connected pins

### Step 2b: Parse Circuit PDF

Convert PDF pages to images for Claude Vision analysis:

```bash
python ~/.claude/skills/circuit-analyzer/scripts/pdf_to_images.py "{path}" -d 200 -o /tmp/circuit_pages
```

Then read each generated PNG with the Read tool for visual analysis.

Options:
- `-d DPI` — Resolution (default 200, use 300 for fine details)
- `-o DIR` — Output directory
- `--pages 1-3` — Specific page range (e.g., `1-3` or `1,3,5`)

### Step 3: Analyze and Report

After parsing, provide:

1. **Board Overview** — What this board does, its functional blocks
2. **FPGA Interface Map** — Which connector pins map to which signals
3. **Power Architecture** — Power rails, voltage domains, filtering
4. **Signal Grouping** — Categorize signals (data bus, control, analog, etc.)
5. **Design Notes** — Any unusual patterns, potential issues, or recommendations

### Step 3b: Cross-Reference with FPGA Constraints (when available)

When both schematic AND FPGA constraint files (UCF/XDC/QSF) exist:

1. Parse schematic netlist → get FPGA component pin-to-net mapping
2. Parse constraint file → get signal-to-LOC mapping
3. Cross-reference via **pin number as bridge**:
   - UCF `LOC=P100` → strip prefix → pin `100`
   - Schematic FPGA pin `100` → net name from netlist
   - Result: UCF signal name ↔ schematic net name mapping

**Pin number format differences:**
- UCF/XDC: `P100`, `B5`, `AB12` (with letter prefix)
- Schematic: `100`, `5`, `12` (numeric only)
- Always strip letter prefix from constraint file before matching

This validates both the parser accuracy AND reveals the naming convention between
schematic-level signals and FPGA-level signals.

**Validated accuracy: 96%** (128/134 pins matched on HVPG board)

### Step 4: FPGA Code Generation (when requested)

When the user wants VHDL code for this board:

1. Reference the parsed pin map from Step 2a
2. Cross-reference with existing constraint files (Step 3b) if available
3. Check existing FPGA knowledge base in the current project:
   - `docs/reports/` — Previous board analysis reports
   - `docs/inventory/` — Technology matrix, group classifications
   - `FPGA/` directories — Existing VHDL source code
   - `docs/quality/` — Common issues and improvement patterns
4. Generate VHDL with:
   - Correct pin names matching the schematic net labels
   - Proper signal directions (input/output/bidirectional) from pin electrical types
   - Power-aware design (correct voltage domain handling)
   - Patterns consistent with existing codebase conventions

## Important Notes

### Vision Limitations
- Claude Vision is ~85% accurate for component identification
- Claude Vision is <19% accurate for net connectivity tracing
- **Always use text extraction (parse_schdoc.py) as the primary data source**
- Use Vision only for visual verification and layout understanding

### OwnerIndex Schemes
The parser auto-detects two Altium file versions:
- **Scheme A**: `OwnerIndex == Component.IndexInSheet` (older files)
- **Scheme B**: `OwnerIndex == Component._seq - 1` (newer files)

No manual intervention needed — detection is automatic.

### Dependencies

Install with: `pip install -r ~/.claude/skills/circuit-analyzer/scripts/requirements.txt`

- `olefile` — OLE Compound File parsing for .schdoc
- `PyMuPDF` (fitz) — PDF to PNG conversion

## Script Locations

```
~/.claude/skills/circuit-analyzer/
├── SKILL.md              ← This file
├── REFERENCE.md          ← Altium record type details
└── scripts/
    ├── parse_schdoc.py   ← Single .schdoc → JSON parser
    ├── parse_board.py    ← Multi-sheet board parser + netlist (v2)
    ├── pdf_to_images.py  ← PDF → PNG converter
    └── requirements.txt  ← Python dependencies
```
