import yaml
from typing import Dict, List, Union

def create_progress_bar(level: int, max_level: int = 10) -> str:
    return f"[{'█' * level}{'─' * (max_level - level)}]"

def get_proficiency_letter(level: int) -> str:
    return 'E' if level >= 9 else 'A' if level >= 7 else 'I' if level >= 5 else 'B'

def format_skill_line(name: str, progress_bar: str, proficiency: str) -> str:
    return f"{name.ljust(12)} {progress_bar} {proficiency}"

def format_category_line(name: str) -> str:
    return f"├─ {name}"

def format_subcategory_line(name: str) -> str:
    return f"│  ├─ {name}"

def create_box_top(title: str, width: int) -> str:
    remaining_width = width - len(title) - len("  ") # padding characters
    return f"┌ {title} {'─' * remaining_width}┐"

def create_box_bottom(width: int) -> str:
    return f"└{'─' * width}┘"

def create_box_content(content: str, width: int) -> str:
    content_margin = 1  # accounts for "│ " and "│"
    return f"│ {content.ljust(width - content_margin)}│"

def create_skill_block(category: str, skills: Dict[str, Union[int, Dict, List]]) -> List[str]:
    # First generate all content lines without borders
    content_lines = []
    
    for key, value in skills.items():
        if isinstance(value, int):
            # Skill with level
            progress = create_progress_bar(value)
            prof = get_proficiency_letter(value)
            content_lines.append(format_skill_line(key, progress, prof))
        elif isinstance(value, (dict, list)):
            # Category with subitems
            content_lines.append(format_category_line(key))
            if isinstance(value, dict):
                for subkey in value:
                    content_lines.append(format_subcategory_line(subkey))
            else:  # list
                for item in value:
                    content_lines.append(format_subcategory_line(item))
    
    # Find the maximum width needed
    box_min_width = len(category) + 3  # "┌─ " + title
    content_min_width = max(len(line) for line in content_lines) + 2  # "│ " + content + "│"
    max_width = max(box_min_width, content_min_width)
    
    # Now create the box with proper width
    lines = []
    lines.append(create_box_top(category, max_width))
    
    # Add content with proper padding
    for line in content_lines:
        lines.append(create_box_content(line, max_width))
    
    # Add footer
    lines.append(create_box_bottom(max_width))
    
    return lines

def tile_blocks(blocks: List[List[str]], max_line_length: int = 80) -> List[str]:
    if not blocks:
        return []
    
    # Sort blocks by height (descending) to minimize gaps
    blocks = sorted(blocks, key=len, reverse=True)
    
    # First determine which blocks go in which rows
    rows = [[]]  # List of lists of blocks
    row_widths = [0]  # Current width of each row
    block_spacing = 1
    
    for block in blocks:
        block_width = len(block[0])  # Width of current block
        
        # Try to find a row where this block fits
        row_found = False
        for i, (row, current_width) in enumerate(zip(rows, row_widths)):
            if current_width + block_width + block_spacing <= max_line_length:
                # Block fits in this row
                rows[i].append(block)
                row_widths[i] += block_width + block_spacing
                row_found = True
                break
        
        if not row_found:
            # Start a new row
            rows.append([block])
            row_widths.append(block_width)
    
    # Now combine blocks in each row horizontally, then combine rows vertically
    final_lines = []
    
    for row in rows:
        # Find max height for this row
        max_height = max(len(block) for block in row)
        
        # Combine blocks in this row
        row_lines = []
        for i in range(max_height):
            line = ""
            for block in row:
                block_width = len(block[0])
                if i < len(block):
                    line += block[i] + " " * block_spacing
                else:
                    line += " " * (block_width + block_spacing)
            row_lines.append(line.rstrip())
        
        # Add this row's lines to final result
        final_lines.extend(row_lines)
        final_lines.append("")  # Add blank line between rows
    
    return final_lines[:-1]  # Remove last blank line

def generate_skills_display(yaml_file: str, max_line_length: int = 80) -> str:
    with open(yaml_file, 'r') as f:
        skills_data = yaml.safe_load(f)
    
    # Create individual blocks
    blocks = []
    for category, skills in skills_data.items():
        blocks.append(create_skill_block(category, skills))
    
    # Tile blocks both horizontally and vertically
    result = tile_blocks(blocks, max_line_length)
    
    return '\n'.join(result)

if __name__ == "__main__":
    print(generate_skills_display("skills.yml"))