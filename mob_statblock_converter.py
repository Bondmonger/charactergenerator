import pandas as pd
import json
import argparse
from typing import Dict, List, Any, Union

#   in Terminal, use:
#       python mob_statblock_converter.py "monster manual index (NPC_test).xlsx" "2-4, 11, 15, 2365"
#       python mob_statblock_converter.py "monster manual index (NPC_test).xlsx" "1-2392"


class GeneralizedMonsterConverter:
    def __init__(self, csv_file: str, config: Dict[str, Any]):
        self.df = pd.read_excel(csv_file, sheet_name="Mobstats", header=1)  # row index 1 = second row in Excel
        numeric_columns = ['weight', 'length', 'XPbase', 'XPplus', 'frequency']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = (self.df[col].astype(str).str.replace(',', '').astype(float))
        self.field_config = config
        self.parsers = {'simple': self._parse_simple, 'range': self._parse_range, 'multi_field': self._parse_multi,
                        'correlated': self._parse_correlated}

    @staticmethod
    def parse_simple_field(value: Any) -> Union[int, float, str, None]:
        if pd.isna(value) or (s := str(value).strip()) in ('', '-'):
            return None
        try:
            f = float(s)
            return int(f) if f.is_integer() else f
        except ValueError:
            return s

    def _parse_simple(self, row: pd.Series, cfg: Dict[str, Any]):
        col = cfg['column']
        if col not in row.index:
            return None
        return self.parse_simple_field(row[col])

    def _parse_range(self, row: pd.Series, cfg: Dict[str, Any]):
        cols, result = cfg['columns'], {}
        if len(cols) != 2:
            return None
        lo_raw, hi_raw = row.get(cols[0]), row.get(cols[1])
        lo, hi = self.parse_simple_field(lo_raw), self.parse_simple_field(hi_raw)
        if isinstance(lo, (int, float)):
            result['min'] = int(lo)
        if isinstance(hi, (int, float)):
            result['max'] = int(hi)
        return result or None

    def _parse_multi(self, row: pd.Series, cfg: Dict[str, Any]):
        result = {}
        for col in cfg['columns']:
            val = row.get(col)
            parsed = self.parse_simple_field(val)
            if parsed is not None:
                result[col] = parsed
        return result or None

    def _parse_correlated(self, row: pd.Series, cfg: Dict[str, Any]):
        parser_name = cfg.get('parser')
        if not parser_name:
            return None
        parser = getattr(self, parser_name, None)
        if not parser:
            raise ValueError(f"Missing correlated parser: {parser_name}")
        return parser(row, cfg['columns'])

    def parse_attacks(self, row: pd.Series, columns: List[str]) -> List[Dict[str, str]]:
        attacks = []
        if len(columns) != 2:
            return attacks
        attack_type_str, damage_str = row.get(columns[0]), row.get(columns[1])
        if pd.isna(attack_type_str) or pd.isna(damage_str):
            return attacks
        attack_type_parts = [a.strip() for a in str(attack_type_str).split('/') if a.strip() and a.strip() != '-']
        damage_parts = [d.strip() for d in str(damage_str).split('/') if d.strip() and d.strip() != '-']
        if len(damage_parts) > 1 and len(attack_type_parts) == 1:
            attack_type_parts *= len(damage_parts)
        elif len(attack_type_parts) > 1 and len(damage_parts) == 1:
            damage_parts *= len(attack_type_parts)
        for i, damage in enumerate(damage_parts):
            attacks.append({'attack_type': attack_type_parts[i] if i < len(attack_type_parts) else 'unknown',
                            'damage_range': damage})
        return attacks

    def parse_group(self, row: pd.Series, group_cfg: Dict[str, Any]):
        result = {}
        for name, cfg in group_cfg.items():
            if 'type' in cfg:
                parser = self.parsers.get(cfg['type'])
                if not parser:
                    continue
                value = parser(row, cfg)
                if value is not None:
                    result[name] = value
            else:
                nested = self.parse_group(row, cfg)
                if nested:
                    result[name] = nested
        return result or None

    def parse_row(self, row: pd.Series) -> Dict[str, Any]:
        monster = {}
        for group_name, group_cfg in self.field_config.items():
            parsed = self.parse_group(row, group_cfg)
            if parsed:
                monster[group_name] = parsed
        return monster

    @staticmethod
    def parse_row_selection(row_selection: str) -> List[int]:
        rows = set()
        for part in map(str.strip, row_selection.split(',')):
            if '-' in part:
                start, end = map(int, part.split('-'))
                rows.update(range(start, end + 1))
            else:
                rows.add(int(part))
        return sorted(rows)

    def convert_rows(self, row_selection: str) -> Dict[str, Any]:
        creatures = {}
        for row_idx in self.parse_row_selection(row_selection):
            pandas_idx = row_idx - 1
            if pandas_idx < 0 or pandas_idx >= len(self.df):
                continue
            row = self.df.iloc[pandas_idx]
            monster = self.parse_row(row)
            name = monster.get('basic_info', {}).get('name') or f'Unknown_Row_{row_idx}'
            creature_type = monster.get('basic_info', {}).get('creature_type') or name
            monster['_metadata'] = {'original_row': row_idx}
            creatures.setdefault(name, {})
            if creature_type in creatures[name]:
                creature_type = f"{creature_type}_Row_{row_idx}"
            creatures[name][creature_type] = monster
        return creatures

    @staticmethod
    def save_json(creatures: Dict[str, Any], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(creatures, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file')
    parser.add_argument('rows')
    parser.add_argument('-o', '--output', default='monsters.json')
    args = parser.parse_args()
    with open('field_config.json', encoding='utf-8') as f:
        config = json.load(f)
    converter = GeneralizedMonsterConverter(args.csv_file, config)
    creatures = converter.convert_rows(args.rows)
    converter.save_json(creatures, args.output)


if __name__ == "__main__":
    main()