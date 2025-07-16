import pandas as pd
import json
import argparse
from typing import Dict, List, Any, Union

#   in Terminal, use this: python mob_statblock_converter.py monsters.csv "2-4, 11, 15"
#   next steps:
#   file conversion - we're starting out with an xlsx. We need to pop out the first sheet to a tab-separated CSV (in
#   UTF-8), and then save that file as monsters.csv, THEN run 'python mob_converter.py monsters.csv "2-4, 11, 15"' in
#   Powershell. Ideally this would all happen in one fell swoop (pop-out, save to CSV in UTF-8, create json, and with a
#   decent UI/UX to boot), but as it stands we have to:
#       a) use the move/copy function in Excel,
#       b) save-to-(tab separated)-csv,
#       c) re-open in Notepad,
#       d) convert/save as UTF_8,
#       e) execute 'python mob_converter.py monsters.csv "2-4, 11, 15"' in terminal
#   This spits out the JSON we want


class GeneralizedMonsterConverter:
    def __init__(self, csv_file: str):
        self.df = pd.read_csv(csv_file, delimiter='\t')  # Assuming tab-separated
        self.field_config = self._get_field_configuration()
    
    def _get_field_configuration(self) -> Dict[str, Any]:
        """
        Define the field configuration here. This will be the mapping between
        JSON output structure and CSV column names, along with parsing rules.
        """
        return {
            'basic_info': {
                'name': {'column': 'Entry name', 'type': 'simple'},
                'creature_type': {'column': 'Creature', 'type': 'simple'},
                'frequency': {'column': 'frequency', 'type': 'simple'},
                'appearance_range': {
                    'type': 'range',
                    'columns': ['min\nApp', 'max\nApp']
                },
                'size': {'column': 'size', 'type': 'simple'},
                'alignment': {'column': 'Align.', 'type': 'simple'},
                'type': {'column': 'Type(s)', 'type': 'simple'}
            },
            'combat': {
                'ac': {'column': 'AC', 'type': 'simple'},
                'hd': {'column': 'HD (Thac0)', 'type': 'simple'},
                'de_facto_level': {'column': 'Eff. Level', 'type': 'simple'},
                'thac0': {'column': 'Thac0', 'type': 'simple'},
                'attacks': {
                    'type': 'correlated',
                    'columns': ['Attack type(s)', 'damage'],
                    'parser': 'attack_parser'
                },
                'hit_dice': {
                    'type': 'hit_dice',
                    'columns': ['d2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd10', 'd12', '+']
                }
            },
            'abilities': {
                'strength': {'column': 'Str', 'type': 'simple'},
                'intelligence': {
                    'type': 'range',
                    'columns': ['intMn', 'intMx']
                },
                'wisdom': {
                    'type': 'range', 
                    'columns': ['wisMin', 'wisMx']
                }
            },
            'movement': {
                'movement': {
                    'type': 'movement',
                    'columns': ['mov', 'fly', 'swm', 'brw', 'web', 'MC']
                }
            },
            'special': {
                'treasure': {'column': 'Treasure', 'type': 'simple'},
                'special_abilities': {'column': 'Special Abilities', 'type': 'simple'}
            },
            'experience_value': {
                'xp_base': {'column': 'XPbase', 'type': 'simple'},
                'xp_plus': {'column': 'XPplus', 'type': 'simple'},
                'monster_level': {'column': 'Level', 'type': 'simple'}
            },
            'class_levels': {
                'class_levels': {
                    'type': 'class_levels',
                    'columns': ['Mnstr', 'Fghtr', 'Paldn', 'Rnger', 'Bushi', 'Obrb', 'Samri', 'Clerc', 'Druid', 'Shuk',
                                'Shman', 'Monk', 'Thief', 'Asssn', 'MU', 'Illst', 'WJ', 'WD']
                }
            }
        }

    @staticmethod
    def parse_simple_field(value: Any) -> Union[str, None]:
        """Parse a simple field - just clean and return the value."""
        if pd.isna(value) or str(value).strip() == '-' or str(value).strip() == '':
            return None
        return str(value).strip()
    
    def parse_correlated_fields(self, row: pd.Series, columns: List[str], parser_type: str) -> Any:
        """Parse correlated fields that need to be processed together."""
        if parser_type == 'attack_parser':
            return self.parse_attacks(row, columns)
        # Add more parser types as needed
        return None
    
    def parse_hit_dice(self, row: pd.Series, columns: List[str]) -> Dict[str, Any]:
        """Parse hit dice columns into a structured format."""
        hit_dice = {}
        
        for col in columns:
            if col in row.index:
                value = row[col]
                # Skip null, empty, or zero values
                if pd.isna(value) or value == '' or int(value) == 0:
                    continue
                    
                # Convert to int if possible, otherwise keep as string
                try:
                    hit_dice[col] = int(value)
                except (ValueError, TypeError):
                    hit_dice[col] = str(value).strip()
        
        return hit_dice if hit_dice else None
    
    def parse_class_levels(self, row: pd.Series, columns: List[str]) -> Dict[str, Any]:
        """Parse class level columns into a structured format."""
        class_levels = {}
        
        for col in columns:
            if col in row.index:
                value = row[col]
                value_str = str(value).strip()
                # Only include non-zero, non-empty values
                if not pd.isna(value) and value_str != '' and value_str != '0' and value_str != '0.0':
                    try:
                        class_levels[col] = int(value)
                    except (ValueError, TypeError):
                        class_levels[col] = value_str
        
        return class_levels if class_levels else None
    
    def parse_attacks(self, row: pd.Series, columns: List[str]) -> List[Dict[str, str]]:
        """Parse attack type and damage into structured attack objects."""
        attacks = []
        
        if len(columns) != 2:
            return attacks
            
        attack_type_str = row[columns[0]] if columns[0] in row.index else ''
        damage_str = row[columns[1]] if columns[1] in row.index else ''
        
        # Handle empty or null values
        if pd.isna(attack_type_str) or pd.isna(damage_str):
            return attacks

        attack_type_str = str(attack_type_str).strip()
        damage_str = str(damage_str).strip()

        if attack_type_str == '-' or damage_str == '-':
            return attacks

        # Split damage by slash for multiple attacks
        damage_parts = [d.strip() for d in damage_str.split('/') if d.strip() and d.strip() != '-']
        attack_type_parts = [a.strip() for a in attack_type_str.split('/') if a.strip() and a.strip() != '-']

        # Handle mismatched counts
        if len(damage_parts) > 1 and len(attack_type_parts) == 1:
            attack_type_parts = attack_type_parts * len(damage_parts)
        elif len(attack_type_parts) > 1 and len(damage_parts) == 1:
            damage_parts = damage_parts * len(attack_type_parts)

        # Create attack objects
        for i, damage in enumerate(damage_parts):
            attack_type = attack_type_parts[i] if i < len(attack_type_parts) else attack_type_parts[0] \
                if attack_type_parts else "unknown"
            attacks.append({
                'attack_type': attack_type,
                'damage_range': damage
            })

        return attacks
    
    def parse_range_field(self, row: pd.Series, columns: List[str]) -> Dict[str, Any]:
        """Parse range fields (min/max pairs)."""
        result = {}
        if len(columns) == 2:
            min_val = row[columns[0]] if columns[0] in row.index else None
            max_val = row[columns[1]] if columns[1] in row.index else None
            
            if not pd.isna(min_val):
                result['min'] = min_val
            if not pd.isna(max_val):
                result['max'] = max_val
                
        return result if result else None
    
    def parse_movement(self, row: pd.Series, columns: List[str]) -> Dict[str, Any]:
        """Parse movement fields (mov, fly, swm, brw, web, MC) and return a dictionary."""
        movement_data = {}
        
        for col in columns:
            if col in row.index:
                value = row[col]
                # Keep 0s but filter out '-' entries
                if pd.isna(value) or value == '' or value == '-':
                    continue
                    
                # Convert to int if possible, otherwise keep as string
                try:
                    movement_data[col] = int(value)
                except (ValueError, TypeError):
                    movement_data[col] = str(value).strip()
        
        return movement_data if movement_data else None
    
    def parse_field_group(self, row: pd.Series, group_config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a group of fields based on their configuration."""
        result = {}
        
        for field_name, field_config in group_config.items():
            try:
                if not isinstance(field_config, dict):
                    print(f"Warning: field_config for {field_name} is not a dict: {type(field_config)}")
                    continue
                    
                if field_config.get('type') == 'simple':
                    column_name = field_config['column']
                    if column_name in row.index:
                        result[field_name] = self.parse_simple_field(row[column_name])
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
                elif field_config.get('type') == 'hit_dice':
                    columns = field_config['columns']
                    parsed_value = self.parse_hit_dice(row, columns)
                    if parsed_value:
                        result[field_name] = parsed_value
                elif field_config.get('type') == 'class_levels':
                    columns = field_config['columns']
                    parsed_value = self.parse_class_levels(row, columns)
                    if parsed_value:
                        result[field_name] = parsed_value
                elif field_config.get('type') == 'movement':
                    columns = field_config['columns']
                    parsed_value = self.parse_movement(row, columns)
                    if parsed_value:
                        result[field_name] = parsed_value
            except Exception as e:
                print(f"Error parsing field {field_name}: {e}")
                print(f"Field config: {field_config}")
                continue
        return result
    
    def parse_row(self, row: pd.Series) -> Dict[str, Any]:
        """Convert a single row to a structured dictionary using the field configuration."""
        monster = {}
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
    def parse_row_selection(row_selection: str) -> List[int]:             # parses row selection '2-4, 11, 15'...
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
    
    def convert_rows(self, row_selection: str) -> Dict[str, Any]:   # converts specified rows to JSON
        row_indices, creatures = self.parse_row_selection(row_selection), {}
        
        # Group monsters by name
        temp_monsters = {}
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
                
                # Add metadata
                monster['_metadata'] = {'original_row': row_idx}
                
                # Group by name
                if name not in temp_monsters:
                    temp_monsters[name] = {}
                
                # Use creature_type as the sub-key, fallback to row number if needed
                if creature_type in temp_monsters[name]:
                    creature_type = f"{creature_type}_Row_{row_idx}"
                
                temp_monsters[name][creature_type] = monster
            else:
                print(f"Skipping row {row_idx} due to parsing error")

        # All entries maintain the same structure
        creatures = temp_monsters

        return creatures

    @staticmethod
    def save_json(creatures: Dict[str, Any], output_file: str):
        """Save creatures to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(creatures, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(creatures)} creatures to {output_file}")
    
    def preview_columns(self):
        """Display available columns for mapping."""
        print("Available columns in the CSV:")
        for i, col in enumerate(self.df.columns):
            print(f"{i + 1}: {col}")
    
    def update_field_config(self, new_config: Dict[str, Any]):
        """Update field configuration."""
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
