#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML"]
# ///
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

def create_skill_block(category: str, skills: Dict[str, Union[int, Dict, List]], height: int = None) -> List[str]:
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
        
    # If a specific height is requested, pad with empty lines
    if height is not None:
        content_height = len(content_lines)
        padding_needed = height - content_height - 2  # -2 for top and bottom borders
        if padding_needed > 0:
            for _ in range(padding_needed):
                lines.append(create_box_content("", max_width))
    
    # Add footer
    lines.append(create_box_bottom(max_width))
    
    return lines

def tile_blocks(blocks: List[List[str]], max_line_length: int = 80) -> List[str]:
    if not blocks:
        return []
    
    # Find the height of the tallest block
    max_height = max(len(block) for block in blocks)
    
    # Recreate blocks with uniform height
    uniform_blocks = []
    for block in blocks:
        # Extract category and skills from the original block
        category = block[0][2:block[0].index('─')]  # Extract category from header
        skills_data = {}
        current_category = None
        
        # Parse the block content to rebuild the skills data
        for line in block[1:-1]:  # Skip header and footer
            line = line[2:-1].rstrip()  # Remove box borders and trailing spaces
            if not line:
                continue
            if line.startswith('├─ '):
                current_category = line[3:]
                skills_data[current_category] = []
            elif line.startswith('│  ├─ '):
                if current_category:
                    skills_data[current_category].append(line[6:])
            elif '[' in line:
                name = line[:12].strip()
                level = line.count('█')
                skills_data[name] = level
        
        # Recreate the block with uniform height
        uniform_block = create_skill_block(category.strip(), skills_data, max_height)
        uniform_blocks.append(uniform_block)
    
    # Combine blocks horizontally with spacing
    block_spacing = 1
    final_lines = []
    
    # Initialize first line
    current_line = ""
    
    # Add each block to the line
    for block in uniform_blocks:
        if current_line and len(current_line) + len(block[0]) + block_spacing > max_line_length:
            break  # Stop if adding another block would exceed max length
        
        # Add spacing if this isn't the first block
        if current_line:
            current_line += " " * block_spacing
        
        # Add this block
        for i, block_line in enumerate(block):
            if i >= len(final_lines):
                final_lines.append(current_line + block_line)
            else:
                final_lines[i] += " " * block_spacing + block_line
        
        # Update current line width for next iteration
        current_line = final_lines[0][:len(final_lines[0])]
    
    return final_lines

def generate_skills_display(yaml_file: str, max_line_length: int = 200) -> str:
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