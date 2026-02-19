import random
from typing import Tuple, Dict

class SkeletonGenerator:
    def __init__(self, schema: list):
        self.schema = schema

    def _get_topic_node(self,domain_name: str, unit_name: str, topic_name: str) -> Dict:
        """Helper to navigate the nested Python list/dict structure."""
        # Assuming domain is the first element
        schema = self.schema

        domain = next((sch for sch in schema if sch['domain'] == domain_name), None)
        if not domain:
            raise ValueError(f"Domain '{domain_name} not found in schema.")
        
        unit = next((u for u in domain["units"] if u["unit"] == unit_name), None)
        if not unit:
            raise ValueError(f"Unit '{unit_name}' not found in schema.")
            
        topic = next((t for t in unit["topics"] if t["topic"] == topic_name), None)
        if not topic:
            raise ValueError(f"Topic '{topic_name}' not found in unit '{unit_name}'.")
            
        return topic
        

    def generate_skeleton(self,domain_name, unit_name: str, topic_name: str, level: int) -> Tuple[str, str]:
        """
        Selects random axes, picks the template, and interpolates.
        Returns: (concept_id, interpolated_skeleton)
        """
        topic_node = self._get_topic_node(domain_name, unit_name, topic_name)
        axes = topic_node["variation_axes"]
        
        # 1. Randomly select one value from each axis
        selections = {
            "CONTEXT": random.choice(axes["context"]),
            "OBJECT_TYPE": random.choice(axes["object_type"]),
            "CONSTRAINT": random.choice(axes["constraint"])
        }
        
        # 2. Find the template matching the Bloom Level
        template = next((t for t in topic_node["templates"] if t["level"] == level), None)
        if not template:
            raise ValueError(f"No template found for Bloom level {level}.")
            
        # 3. Interpolate the stem
        skeleton = template["stem"]
        for placeholder, value in selections.items():
            skeleton = skeleton.replace(f"[{placeholder}]", value)
            
        return topic_node["concept"], skeleton