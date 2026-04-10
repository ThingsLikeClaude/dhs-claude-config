#!/usr/bin/env python3
"""Parse multi-sheet Altium board project → Unified JSON

Usage:
    python parse_board.py <directory_or_file> [--format json|summary|netlist]
    python parse_board.py FPGA/LT1000/PCB/LT1000_DRIVE_BOARD/ -f summary
    python parse_board.py sheet1.schdoc sheet2.schdoc -f netlist

Features (v2):
    - Multi-sheet batch parsing with merged BOM
    - Cross-sheet net unification (same net name = same net)
    - Wire-based netlist construction (Union-Find)
    - Pin-to-net connectivity mapping
"""

import os
import sys
import json
import argparse
import glob
from collections import Counter, defaultdict
from parse_schdoc import parse_schdoc, parse_records, build_children_map, resolve_owner_index, _int, _electrical_type


# ---------------------------------------------------------------------------
# Union-Find for wire connectivity
# ---------------------------------------------------------------------------

class UnionFind:
    """Disjoint set for coordinate-based net connectivity."""

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def build_netlist_single_sheet(data: bytes) -> dict:
    """Build wire-based netlist from a single sheet's raw data.

    Returns dict with:
        nets: list of {name, pins: [{ref, pin_number, pin_name}], labels: [str]}
        unconnected_pins: list of pins not on any named net
    """
    records = parse_records(data)
    children = build_children_map(records)
    comp_to_ref, scheme = resolve_owner_index(records, children)

    uf = UnionFind()

    def coord_key(x, y):
        return (int(x), int(y))

    def pin_hotspot(pin_record):
        """Calculate pin's electrical connection point using pinconglomerate rotation."""
        px = _int(pin_record.get('location.x', '0'))
        py = _int(pin_record.get('location.y', '0'))
        length = _int(pin_record.get('pinlength', '0'))
        cong = _int(pin_record.get('pinconglomerate', '0'))
        rot = cong & 0x03  # lower 2 bits = rotation
        if rot == 0:    return px + length, py      # right
        elif rot == 1:  return px, py + length      # up
        elif rot == 2:  return px - length, py      # left
        elif rot == 3:  return px, py - length      # down
        return px, py

    # Track what's at each coordinate
    coord_to_pins = defaultdict(list)     # coord -> [(ref, pin_num, pin_name)]
    coord_to_netlabels = defaultdict(list) # coord -> [net_name]
    coord_to_power = defaultdict(list)     # coord -> [power_name]

    # 1. Extract component pins with hotspot locations
    components = [r for r in records if r.get('record') == '1']
    for comp in components:
        comp_seq = str(comp['_seq'])
        ref = comp_to_ref.get(comp_seq, '?')
        lib_ref = comp.get('libreference', '?')
        if lib_ref.lower().startswith('titleblock'):
            continue

        # Find children via both schemes
        owner_key_a = comp.get('indexinsheet', '')
        owner_key_b = str(comp['_seq'] - 1)
        child_list = children.get(owner_key_a, []) or children.get(owner_key_b, [])

        for child in child_list:
            if child.get('record') != '2':
                continue
            hx, hy = pin_hotspot(child)
            pin_num = child.get('designator', child.get('name', '?'))
            pin_name = child.get('name', '')
            ck = coord_key(hx, hy)
            coord_to_pins[ck].append((ref, pin_num, pin_name))
            uf.find(ck)

    # 2. Extract wires — union their endpoints
    # Wire fields: x1,y1 and x2,y2 (NOT location.x/corner.x)
    wires = [r for r in records if r.get('record') == '27']
    for w in wires:
        x1 = _int(w.get('x1', w.get('location.x', '0')))
        y1 = _int(w.get('y1', w.get('location.y', '0')))
        x2 = _int(w.get('x2', w.get('corner.x', '0')))
        y2 = _int(w.get('y2', w.get('corner.y', '0')))
        uf.union(coord_key(x1, y1), coord_key(x2, y2))

    # 3. Extract net labels
    for r in records:
        if r.get('record') == '25':
            x = _int(r.get('location.x', '0'))
            y = _int(r.get('location.y', '0'))
            name = r.get('text', '?')
            ck = coord_key(x, y)
            coord_to_netlabels[ck].append(name)
            uf.find(ck)

    # 4. Extract power ports
    for r in records:
        if r.get('record') == '17':
            x = _int(r.get('location.x', '0'))
            y = _int(r.get('location.y', '0'))
            name = r.get('text', '?')
            ck = coord_key(x, y)
            coord_to_power[ck].append(name)
            uf.find(ck)

    # 5. Extract junctions — they just union coordinates at the same point
    # (junctions are already at wire intersection points, union handles them)

    # 6. Group everything by Union-Find root
    root_to_pins = defaultdict(list)
    root_to_labels = defaultdict(set)

    for ck, pins in coord_to_pins.items():
        root = uf.find(ck)
        for p in pins:
            root_to_pins[root].append(p)

    for ck, labels in coord_to_netlabels.items():
        root = uf.find(ck)
        for l in labels:
            root_to_labels[root].add(l)

    for ck, powers in coord_to_power.items():
        root = uf.find(ck)
        for p in powers:
            root_to_labels[root].add(p)

    # 7. Build net list
    nets = []
    unconnected = []
    all_roots = set(list(root_to_pins.keys()) + list(root_to_labels.keys()))

    for root in sorted(all_roots):
        pins = root_to_pins.get(root, [])
        labels = root_to_labels.get(root, set())

        # Name the net
        if labels:
            net_name = sorted(labels)[0]
            if len(labels) > 1:
                aliases = sorted(labels)
            else:
                aliases = []
        elif pins:
            net_name = f"N_{root[0]}_{root[1]}"
            aliases = []
        else:
            continue

        pin_list = [{'ref': p[0], 'pin': p[1], 'name': p[2]} for p in pins]

        if len(pins) == 1 and not labels:
            unconnected.append(pin_list[0])
        else:
            net_entry = {
                'name': net_name,
                'pins': pin_list,
                'pin_count': len(pin_list),
            }
            if aliases:
                net_entry['aliases'] = aliases
            nets.append(net_entry)

    # Sort: named nets first, then anonymous
    nets.sort(key=lambda n: (n['name'].startswith('N_'), n['name']))

    return {
        'nets': nets,
        'net_count': len(nets),
        'total_connections': sum(n['pin_count'] for n in nets),
        'unconnected_pins': unconnected,
    }


# ---------------------------------------------------------------------------
# Multi-sheet board parsing
# ---------------------------------------------------------------------------

def find_schdoc_files(path: str) -> list[str]:
    """Find all .schdoc files in a directory, sorted by name."""
    if os.path.isfile(path):
        return [path]

    patterns = ['*.schdoc', '*.SchDoc', '*.SCHDOC']
    files = set()
    for pat in patterns:
        files.update(glob.glob(os.path.join(path, pat)))
        files.update(glob.glob(os.path.join(path, '**', pat), recursive=True))

    # Sort: numbered files first (01_xxx, Page1, Sheet01), then alphabetical
    def sort_key(f):
        base = os.path.basename(f).lower()
        # Extract leading number
        num = ''
        for c in base:
            if c.isdigit():
                num += c
            else:
                break
        return (int(num) if num else 999, base)

    return sorted(files, key=sort_key)


def parse_board(paths: list[str]) -> dict:
    """Parse multiple .schdoc files and merge into a unified board view.

    Args:
        paths: List of .schdoc file paths or a single directory path
    """
    # Resolve file list
    all_files = []
    for p in paths:
        all_files.extend(find_schdoc_files(p))

    if not all_files:
        return {'error': 'No .schdoc files found', 'searched': paths}

    # Parse each sheet
    sheets = []
    merged_bom = []
    merged_net_names = set()
    merged_power_summary = Counter()
    merged_signal_nets = set()
    merged_power_rails = set()
    total_wires = 0
    total_junctions = 0
    total_buses = 0
    type_counts = Counter()
    all_netlists = []
    errors = []

    for filepath in all_files:
        try:
            result = parse_schdoc(filepath)

            sheet_name = os.path.basename(filepath)
            sheet_info = {
                'file': sheet_name,
                'path': filepath,
                'components': result['stats']['components'],
                'nets': result['stats']['net_labels_unique'],
                'wires': result['wiring']['wires'],
                'scheme': result['owner_scheme'],
            }
            sheets.append(sheet_info)

            # Tag BOM entries with sheet source
            for b in result['bom']:
                b['sheet'] = sheet_name
                merged_bom.append(b)

            # Merge nets
            merged_net_names.update(result['nets']['labels'])
            for rail in result['power']['rails']:
                merged_power_rails.add(rail)
            for sig in result['power']['signals_via_power_port']:
                merged_signal_nets.add(sig)
            for name, cnt in result['power']['detail'].items():
                merged_power_summary[name] += cnt

            # Merge wiring stats
            total_wires += result['wiring']['wires']
            total_junctions += result['wiring']['junctions']
            total_buses += result['wiring']['buses']

            # Merge component types
            for cat, cnt in result['component_summary'].items():
                type_counts[cat] += cnt

            # Build per-sheet netlist
            import olefile
            ole = olefile.OleFileIO(filepath)
            raw_data = ole.openstream('FileHeader').read()
            ole.close()
            sheet_netlist = build_netlist_single_sheet(raw_data)
            sheet_netlist['sheet'] = sheet_name
            all_netlists.append(sheet_netlist)

        except Exception as e:
            errors.append({'file': os.path.basename(filepath), 'error': str(e)})

    # Deduplicate BOM — same ref on different sheets = same physical component
    # (multi-part components like 74LS08 gates)
    bom_by_ref = defaultdict(list)
    for b in merged_bom:
        bom_by_ref[b['ref']].append(b)

    deduplicated_bom = []
    for ref, entries in sorted(bom_by_ref.items(), key=lambda x: _ref_sort_key_str(x[0])):
        if len(entries) == 1:
            deduplicated_bom.append(entries[0])
        else:
            # Merge: combine pins, keep first entry's metadata
            merged = dict(entries[0])
            all_pins = []
            all_sheets = set()
            for e in entries:
                all_pins.extend(e.get('pins', []))
                all_sheets.add(e.get('sheet', ''))
            merged['pins'] = all_pins
            merged['pin_count'] = len(all_pins)
            merged['sheets'] = sorted(all_sheets)
            deduplicated_bom.append(merged)

    # Cross-sheet net unification with pin deduplication
    # Phase 1: Collect all nets per sheet
    unified_nets = defaultdict(lambda: {'pins': [], 'sheets': set(), 'aliases': set()})
    for sheet_nl in all_netlists:
        sheet_name = sheet_nl['sheet']
        for net in sheet_nl['nets']:
            key = net['name']
            unified_nets[key]['pins'].extend(net['pins'])
            unified_nets[key]['sheets'].add(sheet_name)
            if 'aliases' in net:
                unified_nets[key]['aliases'].update(net['aliases'])

    # Phase 2: Merge nets that share a pin (same ref.pin_num in multiple nets)
    # This handles cross-sheet connectivity where the same pin appears in
    # a named net on one sheet and an anonymous net on another sheet.
    pin_to_net = {}  # 'ref.pin' -> net_name (prefer named over anonymous)
    merge_map = {}   # net_name -> canonical_net_name

    # First pass: named nets claim pins
    for name in sorted(unified_nets.keys()):
        if name.startswith('N_'):
            continue
        for pin in unified_nets[name]['pins']:
            pk = f"{pin['ref']}.{pin['pin']}"
            if pk in pin_to_net:
                # This pin already claimed by another named net — merge them
                existing = pin_to_net[pk]
                if existing != name:
                    merge_map[name] = existing
            else:
                pin_to_net[pk] = name

    # Second pass: anonymous nets — check if their pins belong to named nets
    for name in list(unified_nets.keys()):
        if not name.startswith('N_'):
            continue
        target = None
        for pin in unified_nets[name]['pins']:
            pk = f"{pin['ref']}.{pin['pin']}"
            if pk in pin_to_net:
                target = pin_to_net[pk]
                break
        if target:
            merge_map[name] = target
        else:
            # No overlap — register anonymous net's pins
            for pin in unified_nets[name]['pins']:
                pk = f"{pin['ref']}.{pin['pin']}"
                pin_to_net[pk] = name

    # Apply merges
    for src, dst in merge_map.items():
        # Follow merge chain
        while dst in merge_map:
            dst = merge_map[dst]
        unified_nets[dst]['pins'].extend(unified_nets[src]['pins'])
        unified_nets[dst]['sheets'].update(unified_nets[src]['sheets'])
        unified_nets[dst]['aliases'].update(unified_nets[src]['aliases'])
        unified_nets[dst]['aliases'].discard(dst)
        del unified_nets[src]

    # Phase 3: Deduplicate pins within each net
    cross_sheet_nets = []
    for name in sorted(unified_nets.keys(), key=lambda n: (n.startswith('N_'), n)):
        entry = unified_nets[name]
        # Deduplicate pins by ref.pin
        seen = set()
        deduped_pins = []
        for p in entry['pins']:
            pk = f"{p['ref']}.{p['pin']}"
            if pk not in seen:
                seen.add(pk)
                deduped_pins.append(p)

        net_obj = {
            'name': name,
            'pins': deduped_pins,
            'pin_count': len(deduped_pins),
            'sheets': sorted(entry['sheets']),
            'cross_sheet': len(entry['sheets']) > 1,
        }
        aliases = entry.get('aliases', set())
        if aliases:
            net_obj['aliases'] = sorted(aliases)
        cross_sheet_nets.append(net_obj)

    # Stats
    cross_sheet_count = sum(1 for n in cross_sheet_nets if n['cross_sheet'])

    return {
        'board': {
            'directory': os.path.dirname(all_files[0]) if all_files else '',
            'sheet_count': len(sheets),
            'sheets': sheets,
        },
        'bom': deduplicated_bom,
        'component_summary': dict(sorted(type_counts.items(), key=lambda x: -x[1])),
        'nets': {
            'labels': sorted(merged_net_names),
            'label_count': len(merged_net_names),
        },
        'power': {
            'rails': sorted(merged_power_rails),
            'signals_via_power_port': sorted(merged_signal_nets),
            'detail': dict(sorted(merged_power_summary.items())),
        },
        'netlist': cross_sheet_nets,
        'netlist_stats': {
            'total_nets': len(cross_sheet_nets),
            'named_nets': sum(1 for n in cross_sheet_nets if not n['name'].startswith('N_')),
            'anonymous_nets': sum(1 for n in cross_sheet_nets if n['name'].startswith('N_')),
            'cross_sheet_nets': cross_sheet_count,
            'total_pin_connections': sum(n['pin_count'] for n in cross_sheet_nets),
        },
        'wiring': {
            'wires': total_wires,
            'junctions': total_junctions,
            'buses': total_buses,
        },
        'stats': {
            'sheets': len(sheets),
            'components': len(deduplicated_bom),
            'components_raw': len(merged_bom),
            'pins_total': sum(b['pin_count'] for b in deduplicated_bom),
            'net_labels_unique': len(merged_net_names),
            'cross_sheet_nets': cross_sheet_count,
            'wires': total_wires,
        },
        'errors': errors,
    }


def _ref_sort_key_str(ref):
    prefix = ''.join(c for c in ref if c.isalpha())
    num = ''.join(c for c in ref if c.isdigit())
    return (prefix, int(num) if num else 0)


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_board_summary(result: dict) -> str:
    """Human-readable multi-sheet board summary."""
    lines = []
    board = result['board']
    stats = result['stats']

    lines.append(f"## Board: {board['directory']}")
    lines.append(f"Sheets: {board['sheet_count']}")
    lines.append("")

    # Sheet list
    lines.append("### Sheets")
    for i, s in enumerate(board['sheets'], 1):
        lines.append(f"  {i:2d}. {s['file']} ({s['components']} comp, {s['nets']} nets, {s['wires']} wires)")
    lines.append("")

    # BOM summary
    lines.append(f"### BOM ({stats['components']} unique components, {stats['components_raw']} raw entries)")
    lines.append(f"{'Ref':<12} {'Type':<28} {'Value':<15} {'Pins':<5} {'Sheet(s)'}")
    lines.append("-" * 80)
    for b in result['bom']:
        sheet_info = b.get('sheets', [b.get('sheet', '?')])
        if isinstance(sheet_info, list) and len(sheet_info) > 1:
            sheet_str = f"[{len(sheet_info)} sheets]"
        elif isinstance(sheet_info, list):
            sheet_str = sheet_info[0] if sheet_info else '?'
        else:
            sheet_str = sheet_info
        lines.append(f"{b['ref']:<12} {b['lib_ref']:<28} {b['value']:<15} {b['pin_count']:<5} {sheet_str}")

    # Component summary
    lines.append(f"\n### Component Summary")
    for cat, cnt in result['component_summary'].items():
        lines.append(f"  {cat}: {cnt}")

    # Power rails
    lines.append(f"\n### Power Rails")
    for name in result['power']['rails']:
        cnt = result['power']['detail'].get(name, 0)
        lines.append(f"  {name}: {cnt}x")

    # Netlist summary
    nl = result['netlist_stats']
    lines.append(f"\n### Netlist")
    lines.append(f"  Total nets: {nl['total_nets']}")
    lines.append(f"  Named nets: {nl['named_nets']}")
    lines.append(f"  Anonymous nets: {nl['anonymous_nets']}")
    lines.append(f"  Cross-sheet nets: {nl['cross_sheet_nets']}")
    lines.append(f"  Total pin connections: {nl['total_pin_connections']}")

    # Cross-sheet nets detail
    cross = [n for n in result['netlist'] if n['cross_sheet']]
    if cross:
        lines.append(f"\n### Cross-Sheet Nets ({len(cross)})")
        for n in cross[:50]:
            sheets_str = ', '.join(n['sheets'])
            pins_str = ', '.join(f"{p['ref']}.{p['pin']}" for p in n['pins'][:8])
            if len(n['pins']) > 8:
                pins_str += f" ... (+{len(n['pins'])-8})"
            lines.append(f"  {n['name']}: {n['pin_count']} pins across [{sheets_str}]")
            lines.append(f"    {pins_str}")

    # Errors
    if result['errors']:
        lines.append(f"\n### Errors ({len(result['errors'])})")
        for e in result['errors']:
            lines.append(f"  {e['file']}: {e['error']}")

    return '\n'.join(lines)


def format_netlist(result: dict) -> str:
    """Netlist-focused output."""
    lines = []
    lines.append(f"## Netlist ({result['netlist_stats']['total_nets']} nets)")
    lines.append("")

    for net in result['netlist']:
        if net['name'].startswith('N_'):
            continue  # Skip anonymous nets in display
        cross = " [CROSS-SHEET]" if net['cross_sheet'] else ""
        lines.append(f"  {net['name']}{cross}:")
        for p in net['pins']:
            lines.append(f"    {p['ref']}.{p['pin']} ({p['name']})")
        lines.append("")

    # Summary
    nl = result['netlist_stats']
    lines.append(f"Named: {nl['named_nets']}, Anonymous: {nl['anonymous_nets']}, Cross-sheet: {nl['cross_sheet_nets']}")
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Parse multi-sheet Altium board project',
        epilog='Examples:\n'
               '  python parse_board.py FPGA/LT1000/PCB/LT1000_DRIVE_BOARD/\n'
               '  python parse_board.py sheet1.schdoc sheet2.schdoc -f netlist\n'
               '  python parse_board.py . --depth 0 -f summary',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('paths', nargs='+', help='Directory or .schdoc file(s)')
    parser.add_argument('--format', '-f', default='json',
                        choices=['json', 'summary', 'netlist'],
                        help='Output format (default: json)')
    args = parser.parse_args()

    result = parse_board(args.paths)

    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False, default=list))
    elif args.format == 'summary':
        print(format_board_summary(result))
    elif args.format == 'netlist':
        print(format_netlist(result))


if __name__ == '__main__':
    main()
