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

def generate_skills_display(yaml_file: str) -> str:
    with open(yaml_file, 'r') as f:
        skills_data = yaml.safe_load(f)
    
    # Create blocks and stack them vertically
    all_lines = []
    for category, skills in skills_data.items():
        block = create_skill_block(category, skills)
        all_lines.extend(block)
        all_lines.append('')  # Add blank line between blocks
    
    return '\n'.join(all_lines)

if __name__ == "__main__":
    print(generate_skills_display("skills.yml"))