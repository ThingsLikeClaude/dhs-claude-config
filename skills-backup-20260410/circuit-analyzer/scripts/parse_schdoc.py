#!/usr/bin/env python3
"""Parse Altium .schdoc files → JSON (BOM + Netlist + Pin Map)

Usage:
    python parse_schdoc.py <schdoc_path> [--format json|bom|nets|pins|summary]

Output formats:
    json    - Full JSON with BOM, nets, power, pins (default)
    bom     - BOM table only
    nets    - Net labels and power nets only
    pins    - Pin map for FPGA port mapping
    summary - Human-readable summary
"""

import olefile
import sys
import json
import argparse
from collections import Counter, defaultdict


def parse_records(data: bytes) -> list[dict]:
    """Parse FileHeader stream into list of record dicts."""
    pos = 0
    records = []
    while pos < len(data):
        if pos + 4 > len(data):
            break
        length = int.from_bytes(data[pos:pos+2], 'little')
        if length <= 0 or length > 100000:
            pos += 1
            continue
        payload = data[pos+4:pos+4+length]
        text = payload.decode('latin-1').rstrip('\x00')
        fields = {}
        for f in text.split('|'):
            if '=' in f:
                k, v = f.split('=', 1)
                k = k.strip()
                if k.startswith('%UTF8%'):
                    fields[k[6:].lower()] = v
                elif k:
                    lk = k.lower()
                    if lk not in fields:
                        fields[lk] = v
        fields['_seq'] = len(records)
        records.append(fields)
        pos += 4 + length
    return records


def build_children_map(records: list[dict]) -> dict[str, list[dict]]:
    """Map ownerindex -> list of child records."""
    children = defaultdict(list)
    for r in records:
        oi = r.get('ownerindex', '')
        if oi:
            children[oi].append(r)
    return children


def resolve_owner_index(records: list[dict], children: dict) -> dict[str, str]:
    """Detect OwnerIndex mapping scheme and return comp_seq -> ref mapping.

    Two schemes exist:
    - Scheme A: OwnerIndex == Component.IndexInSheet (older files)
    - Scheme B: OwnerIndex == Component._seq - 1 (newer files)
    """
    components = [r for r in records if r.get('record') == '1']
    designators = [r for r in records if r.get('record') == '34'
                   and r.get('name', '').lower() == 'designator']

    desig_by_oi = {d.get('ownerindex', ''): d.get('text', '?') for d in designators}

    # Test Scheme A: OwnerIndex == IndexInSheet
    matches_a = 0
    for c in components[:10]:
        iis = c.get('indexinsheet', '')
        if iis in desig_by_oi:
            matches_a += 1

    # Test Scheme B: OwnerIndex == _seq - 1
    matches_b = 0
    for c in components[:10]:
        seq_minus_1 = str(c['_seq'] - 1)
        if seq_minus_1 in desig_by_oi:
            matches_b += 1

    scheme = 'A' if matches_a >= matches_b else 'B'

    # Build mapping: component -> designator text
    comp_to_ref = {}
    for c in components:
        if scheme == 'A':
            key = c.get('indexinsheet', '')
        else:
            key = str(c['_seq'] - 1)
        comp_to_ref[str(c['_seq'])] = desig_by_oi.get(key, '?')

    return comp_to_ref, scheme


def extract_bom(records, children, comp_to_ref):
    """Extract Bill of Materials."""
    bom = []
    for r in records:
        if r.get('record') != '1':
            continue
        lib_ref = r.get('libreference', '?')
        if lib_ref.lower().startswith('titleblock'):
            continue

        comp_seq = str(r['_seq'])
        ref = comp_to_ref.get(comp_seq, '?')

        # Get owner key for children lookup
        owner_key_a = r.get('indexinsheet', '')
        owner_key_b = str(r['_seq'] - 1)

        # Try both keys to find children
        child_list = children.get(owner_key_a, []) or children.get(owner_key_b, [])

        # Extract value from parameters
        value = ''
        for child in child_list:
            if child.get('record') == '41' and child.get('name', '') == 'Value':
                value = child.get('text', '')
                break

        # Count pins
        pins = [c for c in child_list if c.get('record') == '2']

        # Extract pin details
        pin_details = []
        for p in pins:
            pin_details.append({
                'number': p.get('designator', p.get('name', '?')),
                'name': p.get('name', ''),
                'electrical': _electrical_type(p.get('electrical', '')),
            })

        bom.append({
            'ref': ref,
            'lib_ref': lib_ref,
            'value': value,
            'pin_count': len(pins),
            'pins': pin_details,
            'location': {
                'x': _int(r.get('location.x', '0')),
                'y': _int(r.get('location.y', '0')),
            },
        })

    # Sort by reference designator
    bom.sort(key=_ref_sort_key)
    return bom


def extract_nets(records):
    """Extract net labels and power ports."""
    net_labels = []
    for r in records:
        if r.get('record') == '25':
            net_labels.append({
                'name': r.get('text', '?'),
                'location': {
                    'x': _int(r.get('location.x', '0')),
                    'y': _int(r.get('location.y', '0')),
                },
            })

    power_ports = []
    for r in records:
        if r.get('record') == '17':
            power_ports.append({
                'name': r.get('text', '?'),
                'style': r.get('style', ''),
                'location': {
                    'x': _int(r.get('location.x', '0')),
                    'y': _int(r.get('location.y', '0')),
                },
            })

    # Summarize
    net_names = sorted(set(n['name'] for n in net_labels))
    power_summary = Counter(p['name'] for p in power_ports)

    return {
        'net_labels': net_labels,
        'net_names': net_names,
        'power_ports': power_ports,
        'power_summary': dict(sorted(power_summary.items())),
    }


def extract_wiring_stats(records):
    """Extract wiring statistics."""
    wires = [r for r in records if r.get('record') == '27']
    junctions = [r for r in records if r.get('record') == '29']
    buses = [r for r in records if r.get('record') == '28']
    return {
        'wires': len(wires),
        'junctions': len(junctions),
        'buses': len(buses),
    }


def extract_connectors(bom):
    """Extract connector pin maps for FPGA port mapping."""
    connectors = []
    for b in bom:
        if b['pin_count'] >= 10 and any(k in b['lib_ref'].upper()
                                         for k in ('CON', 'HEADER', 'CONN', 'J')):
            connectors.append({
                'ref': b['ref'],
                'lib_ref': b['lib_ref'],
                'pin_count': b['pin_count'],
                'pins': b['pins'],
            })
    return connectors


def _electrical_type(val):
    types = {
        '0': 'Input', '1': 'IO', '2': 'Output', '3': 'OpenCollector',
        '4': 'Passive', '5': 'HiZ', '6': 'OpenEmitter', '7': 'Power',
    }
    return types.get(str(val).strip(), f'Unknown({val})')


def _int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def _ref_sort_key(item):
    ref = item['ref']
    prefix = ''.join(c for c in ref if c.isalpha())
    num = ''.join(c for c in ref if c.isdigit())
    return (prefix, int(num) if num else 0)


def parse_schdoc(path: str) -> dict:
    """Main entry: parse .schdoc file and return structured data."""
    ole = olefile.OleFileIO(path)

    # Read streams
    streams = {}
    for s in ole.listdir():
        name = '/'.join(s)
        streams[name] = ole.get_size(name)

    data = ole.openstream('FileHeader').read()
    ole.close()

    # Parse
    records = parse_records(data)
    children = build_children_map(records)
    comp_to_ref, scheme = resolve_owner_index(records, children)

    # Extract
    bom = extract_bom(records, children, comp_to_ref)
    nets = extract_nets(records)
    wiring = extract_wiring_stats(records)
    connectors = extract_connectors(bom)

    # Header info
    header = records[0] if records else {}

    # Classify power vs signal nets
    power_rail_names = set()
    signal_net_names = set()
    for name in nets['power_summary']:
        if any(k in name.upper() for k in ['V', 'GND', 'VCC', 'VDD', 'VSS']):
            power_rail_names.add(name)
        else:
            signal_net_names.add(name)

    # Component type summary
    type_counts = Counter()
    for b in bom:
        lr = b['lib_ref'].upper()
        if 'RESISTOR' in lr or lr.startswith('R_') or lr.startswith('R '):
            type_counts['Resistors'] += 1
        elif 'CAP' in lr:
            type_counts['Capacitors'] += 1
        elif lr.startswith('74'):
            type_counts['Logic ICs (74xx)'] += 1
        elif 'ULN' in lr or 'DRIVER' in lr:
            type_counts['Drivers'] += 1
        elif any(k in lr for k in ('CON', 'HEADER', 'CONN')):
            type_counts['Connectors'] += 1
        elif 'POWER' in lr or lr.startswith('L') and 'LS' not in lr:
            type_counts['Power/Filter'] += 1
        elif 'TP' in lr or 'TEST' in lr:
            type_counts['Test Points'] += 1
        elif 'JUMPER' in lr:
            type_counts['Jumpers'] += 1
        elif any(k in lr for k in ('FPGA', 'CPLD', 'XC', 'EP', 'CYCLONE', 'SPARTAN', 'ARTIX')):
            type_counts['FPGA/CPLD'] += 1
        elif any(k in lr for k in ('ADC', 'DAC', 'ADS', 'AD7', 'AD9', 'MCP', 'TLV')):
            type_counts['ADC/DAC'] += 1
        elif any(k in lr for k in ('OP', 'AMP', 'LM', 'TL', 'OPA', 'INA')):
            type_counts['Op-Amps'] += 1
        elif any(k in lr for k in ('REG', 'LDO', 'LM78', 'LM79', 'AMS')):
            type_counts['Regulators'] += 1
        else:
            type_counts['Other ICs'] += 1

    return {
        'file': path,
        'header': header.get('header', ''),
        'owner_scheme': scheme,
        'total_records': len(records),

        'bom': bom,
        'component_summary': dict(sorted(type_counts.items(), key=lambda x: -x[1])),

        'nets': {
            'labels': nets['net_names'],
            'label_count': len(nets['net_labels']),
        },
        'power': {
            'rails': sorted(power_rail_names),
            'signals_via_power_port': sorted(signal_net_names),
            'detail': nets['power_summary'],
        },
        'connectors': connectors,
        'wiring': wiring,

        'stats': {
            'components': len(bom),
            'pins_total': sum(b['pin_count'] for b in bom),
            'net_labels_unique': len(nets['net_names']),
            'power_port_instances': len(nets['power_ports']),
            'wires': wiring['wires'],
            'junctions': wiring['junctions'],
        },
    }


def format_summary(result: dict) -> str:
    """Human-readable summary."""
    lines = []
    lines.append(f"File: {result['file']}")
    lines.append(f"Records: {result['total_records']}, Scheme: {result['owner_scheme']}")
    lines.append("")

    # BOM
    lines.append(f"## BOM ({result['stats']['components']} components)")
    lines.append(f"{'Ref':<10} {'Type':<28} {'Value':<15} {'Pins':<5}")
    lines.append("-" * 62)
    for b in result['bom']:
        lines.append(f"{b['ref']:<10} {b['lib_ref']:<28} {b['value']:<15} {b['pin_count']:<5}")

    # Component summary
    lines.append(f"\n## Component Summary")
    for cat, cnt in result['component_summary'].items():
        lines.append(f"  {cat}: {cnt}")

    # Power rails
    lines.append(f"\n## Power Rails")
    for name in result['power']['rails']:
        cnt = result['power']['detail'].get(name, 0)
        lines.append(f"  {name}: {cnt}x")

    # Signal nets
    lines.append(f"\n## Signal Nets (via Power Ports): {len(result['power']['signals_via_power_port'])}")
    sigs = result['power']['signals_via_power_port']
    for i in range(0, len(sigs), 8):
        lines.append(f"  {', '.join(sigs[i:i+8])}")

    # Net labels
    lines.append(f"\n## Net Labels ({result['stats']['net_labels_unique']} unique)")
    lines.append(f"  {', '.join(result['nets']['labels'])}")

    # Connectors
    if result['connectors']:
        lines.append(f"\n## Connectors")
        for c in result['connectors']:
            lines.append(f"  {c['ref']}: {c['lib_ref']} ({c['pin_count']} pins)")

    # Wiring
    lines.append(f"\n## Wiring: {result['wiring']['wires']} wires, "
                 f"{result['wiring']['junctions']} junctions, "
                 f"{result['wiring']['buses']} buses")

    return '\n'.join(lines)


def format_bom(result: dict) -> str:
    """BOM table only."""
    lines = [f"{'Ref':<10} {'Type':<28} {'Value':<15} {'Pins':<5}",
             "-" * 62]
    for b in result['bom']:
        lines.append(f"{b['ref']:<10} {b['lib_ref']:<28} {b['value']:<15} {b['pin_count']:<5}")
    lines.append(f"\nTotal: {len(result['bom'])} components")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Parse Altium .schdoc files')
    parser.add_argument('schdoc_path', help='.schdoc file path')
    parser.add_argument('--format', '-f', default='json',
                        choices=['json', 'bom', 'nets', 'pins', 'summary'],
                        help='Output format (default: json)')
    args = parser.parse_args()

    result = parse_schdoc(args.schdoc_path)

    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.format == 'summary':
        print(format_summary(result))
    elif args.format == 'bom':
        print(format_bom(result))
    elif args.format == 'nets':
        print(json.dumps({
            'nets': result['nets'],
            'power': result['power'],
        }, indent=2, ensure_ascii=False))
    elif args.format == 'pins':
        print(json.dumps({
            'connectors': result['connectors'],
            'bom_pins': [{
                'ref': b['ref'],
                'lib_ref': b['lib_ref'],
                'pins': b['pins'],
            } for b in result['bom'] if b['pin_count'] > 0],
        }, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
