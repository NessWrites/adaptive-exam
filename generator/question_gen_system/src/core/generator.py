import random
from typing import Tuple, Dict, Optional

class SkeletonGenerator:
    def __init__(self, schema: list):
        self.schema = schema

    def _get_topic_node(self, domain_name: str, unit_name: str, topic_name: str) -> Dict:
        """Helper to navigate the nested Python list/dict structure."""
        schema = self.schema

        domain = next((sch for sch in schema if sch['domain'] == domain_name), None)
        if not domain:
            raise ValueError(f"Domain '{domain_name}' not found in schema.")
        
        unit = next((u for u in domain["units"] if u["unit"] == unit_name), None)
        if not unit:
            raise ValueError(f"Unit '{unit_name}' not found in schema.")
            
        topic = next((t for t in unit["topics"] if t["topic"] == topic_name), None)
        if not topic:
            raise ValueError(f"Topic '{topic_name}' not found in unit '{unit_name}'.")
            
        return topic

    def generate_skeleton(
        self, domain_name: str, unit_name: str, topic_name: str, level: int
    ) -> Tuple[str, str, Optional[str]]:
        """
        Selects random axes based on Bloom level, picks the template,
        and interpolates. Returns: (concept_id, interpolated_skeleton, context_or_none)
        """
        topic_node = self._get_topic_node(domain_name, unit_name, topic_name)
        axes = topic_node["variation_axes"]

        # 1. Find the template for the requested Bloom level
        template = next((t for t in topic_node["templates"] if t["level"] == level), None)
        if not template:
            raise ValueError(f"No template found for Bloom level {level}.")

        stem = template["stem"]

        # 2. Dynamically build selections based on placeholders in the template
        selections = {"OBJECT_TYPE": random.choice(axes["object_type"])}
        if "[CONTEXT]" in stem:
            selections["CONTEXT"] = random.choice(axes["context"])
        if "[CONSTRAINT]" in stem:
            selections["CONSTRAINT"] = random.choice(axes["constraint"])

        # 3. Interpolate the template
        for placeholder, value in selections.items():
            stem = stem.replace(f"[{placeholder}]", value)

        # 4. Return concept, interpolated skeleton, and context if it exists
        return topic_node["concept"], stem, selections.get("CONTEXT")