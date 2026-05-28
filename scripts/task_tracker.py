#!/usr/bin/env python3
"""Task tracking utility for government workspace."""
import json
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path(__file__).parent.parent

def update_inventory_timestamp(inventory_path: Path):
    """Update the Last Updated timestamp in INVENTORY.md."""
    if not inventory_path.exists():
        return
    
    content = inventory_path.read_text()
    timestamp = f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}"
    
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith("**Last Updated:**"):
            new_lines.append(timestamp)
        else:
            new_lines.append(line)
    
    inventory_path.write_text('\n'.join(new_lines))
    print(f"Updated: {inventory_path}")

def main():
    """Update all inventory timestamps."""
    for inventory in WORKSPACE_ROOT.rglob("INVENTORY.md"):
        update_inventory_timestamp(inventory)

if __name__ == "__main__":
    main()
