#!/usr/bin/env python3
"""Add enable_research: false to all experts by default."""
import json
from pathlib import Path

experts_file = Path(__file__).parent.parent / "experts.json"

print(f"Loading experts from: {experts_file}")

with open(experts_file) as f:
    experts = json.load(f)

print(f"Found {len(experts)} experts\n")

# Add enable_research: false to all experts
added_count = 0
for expert_id, expert_config in experts.items():
    if "enable_research" not in expert_config:
        expert_config["enable_research"] = False
        print(f"✓ Added enable_research: false to {expert_id}")
        added_count += 1
    else:
        print(f"  {expert_id} already has enable_research: {expert_config['enable_research']}")

# Save with pretty formatting
print(f"\nSaving updated experts.json...")
with open(experts_file, "w") as f:
    json.dump(experts, f, indent=2)
    f.write("\n")

print(f"\n✅ Updated {added_count} experts")
print(f"Total experts: {len(experts)}")
