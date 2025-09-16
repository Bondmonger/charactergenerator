import pandas as pd
import json
import argparse
from typing import Dict, List, Any, Union

#   in Terminal, use this: python mob_statblock_converter.py monsters.csv "2-4, 11, 15, 2365"
#   or this: python mob_statblock_converter.py monsters_test.csv "1-2366"
#   next steps:
#   file conversion - we're starting out with an xlsx. We need to pop out the first sheet to a tab-separated CSV (in
#   UTF-8), and then save that file as monsters.csv, THEN run 'python mob_converter.py monsters.csv "2-4, 11, 15"' in
#   Powershell. Ideally this would all happen in one fell swoop (pop-out, save to CSV in UTF-8, create json, and with a
#   decent UI/UX to boot), but as it stands we have to:
#       a) use the move/copy function in Excel,
#       b) trim out row 1 (the column headers need to be at the top)
#       c) save-to-(tab separated)-csv, [Text (Tab delimited) (*.txt)]
#       d) re-open in Notepad,
#       e) convert/save with UTF-8 encoding, without file extension .txt, manually appending .csv to file name
#       f) execute 'python mob_converter.py monsters.csv "2-4, 11, 15"' in terminal
#   This spits out the JSON we want
#
#   punchlist:
#   COMPLETE 6) let's capture the size values in a new parsing method
#   COMPLETE 1) let's strip the " from movement(s)
#   COMPLETE 3) let's handle blanks better: strength, treasure (actually "-"), special abilities
#   COMPLETE 4) let's get ac, hd and thac0 returning integers
#   COMPLETE 2) let's merge hit dice, movement and class levels
#   COMPLETE 5) let's sort out de_facto_level (Eff. Level vs. HD (Thac0))


class GeneralizedMonsterConverter:
    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file, delimiter='\t')     # reads the csv, then selectively forces numeric conversion
        numeric_columns = ['weight', 'length', 'XPbase', 'XPplus', 'frequency']
        for col in numeric_columns:
            if col in self.df.columns:                                                      # strips commas...
                self.df[col] = self.df[col].astype(str).str.replace(',', '').astype(float)  # ...converts to FLOAT
        self.field_config = self._get_field_configuration()     # first and last lines are all we actually need here

    def _get_field_configuration(self) -> Dict[str, Any]:
        return {                    # map CSV name column(s) to JSON output structure, along with parsing rules
            'basic_info': {         # currently, this only parses fields in the second tier (name, creature_type, etc.)
                'name': {'column': 'Entry name', 'type': 'simple'},
                'creature_type': {'column': 'Creature', 'type': 'simple'},
                'frequency': {'column': 'frequency', 'type': 'simple'},
                'appearance_range': {'columns': ['min\nApp', 'max\nApp'], 'type': 'range'},
                'alignment': {'column': 'Align.', 'type': 'simple'},
                'mob_type': {'column': 'Type(s)', 'type': 'simple'}},
            'size': {
                'size': {'columns': ['size', 'length', 'dimension', 'weight'], 'type': 'multi_field'}},
            'combat': {
                'ac': {'column': 'AC', 'type': 'simple'},
                'hit_dice': {'columns': ['d2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd10', 'd12', '+'],
                             'type': 'multi_field'},
                'hd_thac0': {'column': 'HD (Thac0)', 'type': 'simple'},
                'hd_saves': {'column': 'Eff. Level', 'type': 'simple'},
                'thac0': {'column': 'Thac0', 'type': 'simple'},
                'attacks': {'type': 'correlated', 'columns': ['Attack type(s)', 'damage'], 'parser': 'attack_parser'}},
            'abilities': {
                'strength': {'column': 'Str', 'type': 'simple'},
                'intelligence': {'columns': ['intMn', 'intMx'], 'type': 'range'},
                'wisdom': {'columns': ['wisMin', 'wisMx'], 'type': 'range'}},
            'movement': {
                'movement': {'columns': ['mov', 'fly', 'swm', 'brw', 'web', 'MC'], 'type': 'multi_field'}},
            'special': {
                'treasure': {'column': 'Treasure', 'type': 'simple'},
                'special_abilities': {'column': 'Special Abilities', 'type': 'simple'}},
            'experience_value': {
                'xp_base': {'column': 'XPbase', 'type': 'simple'},
                'xp_plus': {'column': 'XPplus', 'type': 'simple'},
                'monster_level': {'column': 'Level', 'type': 'simple'}},
            'class_levels': {
                'class_levels': {
                    'type': 'multi_field',
                    'columns': ['Monster', 'Fighter', 'Paladin', 'Ranger', 'Bushi', 'Oriental Barbarian', 'Samurai',
                                'Cleric', 'Druid', 'Shukenja', 'Shaman', 'Monk', 'Thief', 'Assassin', 'Magic User',
                                'Illusionist', 'Wu-jen', 'Witchdoctor']}}}

    @staticmethod
    def parse_simple_field(value: Any) -> Union[int, float, str, None]:     # parse a simple field
        if pd.isna(value) or (s := str(value).strip()) in ('', '-'):        # strips string and re-defines as s
            return None                                                     # return nothing if '-' or ''
        try:
            f = float(s)                                                    # calculate the FLOAT
            return int(f) if f.is_integer() else f                          # return INT if whole, otherwise FLOAT
        except ValueError:
            return s                                                        # ...if neither, return STR

    def parse_correlated_fields(self, row: pd.Series, columns: List[str], parser_type: str) -> Any:
        if parser_type == 'attack_parser':                                  # parse correlated fields
            return self.parse_attacks(row, columns)                         # add more parser types as needed
        return None

    def parse_multi_field(self, row: pd.Series, columns: List[str]) -> Dict[str, Any]:
        class_levels = {}                                                   # parse columns to structured format
        for col in columns:
            if col in row.index:
                value = row[col]
                if pd.isna(value) or value == '' or value == 0 or value == '-':
                    continue                                                # skip nulls and blanks
                class_levels[col] = self.parse_simple_field(value)          # passes to parse_simple_field()
        return class_levels if class_levels else None
    
    def parse_attacks(self, row: pd.Series, columns: List[str]) -> List[Dict[str, str]]:
        attacks = []            # parses attack type and damage into structured attack objects
        if len(columns) != 2:   # error-handling (if it's not 1:1, return an empty list)
            return attacks
        attack_type_str = row[columns[0]] if columns[0] in row.index else ''
        damage_str = row[columns[1]] if columns[1] in row.index else ''
        if pd.isna(attack_type_str) or pd.isna(damage_str):             # handles empty or null values
            return attacks
        attack_type_str = str(attack_type_str).strip()
        damage_str = str(damage_str).strip()
        if attack_type_str == '-' or damage_str == '-':
            return attacks
        damage_parts = [d.strip() for d in damage_str.split('/') if d.strip() and d.strip() != '-']
        attack_type_parts = [a.strip() for a in attack_type_str.split('/') if a.strip() and a.strip() != '-']
        if len(damage_parts) > 1 and len(attack_type_parts) == 1:       # handles mismatched counts
            attack_type_parts = attack_type_parts * len(damage_parts)
        elif len(attack_type_parts) > 1 and len(damage_parts) == 1:
            damage_parts = damage_parts * len(attack_type_parts)
        for i, damage in enumerate(damage_parts):                       # creates attack objects
            attack_type = attack_type_parts[i] if i < len(attack_type_parts) else attack_type_parts[0] \
                if attack_type_parts else "unknown"
            attacks.append({
                'attack_type': attack_type,
                'damage_range': damage
            })
        return attacks
    
    def parse_range_field(self, row: pd.Series, columns: List[str]) -> Dict[str, Any]:
        result = {}             # parse range fields (min/max pairs
        if len(columns) == 2:
            min_val = row[columns[0]] if columns[0] in row.index else None
            max_val = row[columns[1]] if columns[1] in row.index else None
            if not pd.isna(min_val):
                result['min'] = int(min_val)
            if not pd.isna(max_val):
                result['max'] = int(max_val)
        return result if result else None
    
    def parse_field_group(self, row: pd.Series, group_config: Dict[str, Any]) -> Dict[str, Any]:
        result = {}                     # Parses groups of fields based on configuration (simple, correlated, etc.)
        for field_name, field_config in group_config.items():
            try:
                if not isinstance(field_config, dict):
                    print(f"Warning: field_config for {field_name} is not a dict: {type(field_config)}")
                    continue
                if field_config.get('type') == 'simple':
                    column_name = field_config['column']
                    if column_name in row.index and \
                            (parsed_value := self.parse_simple_field(row[column_name])) is not None:
                        result[field_name] = parsed_value
                elif field_config.get('type') == 'correlated':
                    columns = field_config['columns']
                    parser_type = field_config.get('parser', 'default')
                    parsed_value = self.parse_correlated_fields(row, columns, parser_type)
                    if parsed_value:
                        result[field_name] = parsed_value
                elif field_config.get('type') == 'range':
                    columns = field_config['columns']
                    parsed_value = self.parse_range_field(row, columns)
                    if parsed_value:
                        result[field_name] = parsed_value
                elif field_config.get('type') == 'multi_field':
                    columns = field_config['columns']
                    parsed_value = self.parse_multi_field(row, columns)
                    if parsed_value:
                        result[field_name] = parsed_value
            except Exception as e:
                print(f"Error parsing field {field_name}: {e}")
                print(f"Field config: {field_config}")
                continue
        return result
    
    def parse_row(self, row: pd.Series) -> Dict[str, Any]:
        monster = {}                    # converts single row to structured dictionary using the field configuration
        for group_name, group_config in self.field_config.items():
            try:
                parsed_group = self.parse_field_group(row, group_config)
                if parsed_group:
                    monster[group_name] = parsed_group
            except Exception as e:
                print(f"Error parsing group {group_name}: {e}")
                print(f"Group config: {group_config}")
                continue
        return monster

    @staticmethod
    def parse_row_selection(row_selection: str) -> List[int]:             # converts row selection '2-4, 11, 15'...
        parts, rows = [part.strip() for part in row_selection.split(',')], []   # ...into a list of rows
        print(f"Parsing row selection: '{row_selection}'")
        print(f"Parts: {parts}")
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                range_rows = list(range(start, end + 1))
                print(f"Range {start}-{end} expands to: {range_rows}")
                rows.extend(range_rows)
            else:
                row_num = int(part)
                print(f"Single row: {row_num}")
                rows.append(row_num)
        result = sorted(list(set(rows)))
        print(f"Final row list: {result}")
        return result
    
    def convert_rows(self, row_selection: str) -> Dict[str, Any]:       # converts specified rows to JSON
        row_indices, creatures = self.parse_row_selection(row_selection), {}
        temp_monsters = {}                                              # group monsters by name
        for row_idx in row_indices:
            pandas_idx = row_idx - 1
            if pandas_idx < 0 or pandas_idx >= len(self.df):
                print(f"Warning: Row {row_idx} is out of range. Skipping.")
                continue
            row = self.df.iloc[pandas_idx]
            monster = self.parse_row(row)
            if isinstance(monster, dict):
                name = monster.get('basic_info', {}).get('name', f'Unknown_Row_{row_idx}')
                creature_type = monster.get('basic_info', {}).get('creature_type')
                if not name or name == 'None':
                    name = f'Unknown_Row_{row_idx}'
                if not creature_type or creature_type == 'None':
                    creature_type = name
                monster['_metadata'] = {'original_row': row_idx}        # adds metadata
                if name not in temp_monsters:                           # groups by name
                    temp_monsters[name] = {}
                if creature_type in temp_monsters[name]:                # uses creature_type as sub-key
                    creature_type = f"{creature_type}_Row_{row_idx}"
                temp_monsters[name][creature_type] = monster
            else:
                print(f"Skipping row {row_idx} due to parsing error")
        creatures = temp_monsters
        return creatures

    @staticmethod
    def save_json(creatures: Dict[str, Any], output_file: str):     # saves creatures to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(creatures, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(creatures)} creatures to {output_file}")
    
    def preview_columns(self):                                      # displays available columns for mapping
        print("Available columns in the CSV:")
        for i, col in enumerate(self.df.columns):
            print(f"{i + 1}: {col}")
    
    def update_field_config(self, new_config: Dict[str, Any]):      # updates field configuration
        self.field_config.update(new_config)


def main():
    parser = argparse.ArgumentParser(description='Convert monster CSV rows to JSON using generalized parsing')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('rows', help='Row selection (e.g., "2-4, 11, 15")')
    parser.add_argument('-o', '--output', help='Output JSON file', default='monsters.json')
    parser.add_argument('--preview', action='store_true', help='Preview available columns')
    args = parser.parse_args()
    try:
        converter = GeneralizedMonsterConverter(args.csv_file)
        if args.preview:
            converter.preview_columns()
            return
        creatures = converter.convert_rows(args.rows)
        converter.save_json(creatures, args.output)
        print(f"\nConverted {len(creatures)} creatures:")
        for name, variants in creatures.items():
            variant_rows = [variant['_metadata']['original_row'] for variant in variants.values()]
            if len(variant_rows) == 1:
                print(f"  Row {variant_rows[0]}: {name}")
            else:
                print(f"  Rows {', '.join(map(str, variant_rows))}: {name} ({len(variants)} variants)")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 
