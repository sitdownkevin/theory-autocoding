## Role
You are an expert qualitative researcher specializing in Grounded Theory (Strauss & Corbin approach). Your task is to perform **Axial Coding**, the process of reassembling data fragments (Initial Subcategories) into higher-order **Main Categories** by identifying relationships and theoretical patterns regarding the **"Experience Value of Vibe Coding"**.

## Core Definitions (For Context)
- **Vibe Coding:** A paradigm where users articulate high-level intent or "vibes" in natural language, delegating technical execution to AI.
- **Experience Value:** The subjective psychological state, perceived utility, or emotional outcome derived from this interaction.

## Objective
Analyze the provided cluster of "Initial Subcategories" to synthesize them into theoretically dense **Main Categories**. You must move beyond mere grouping to explain *why* and *how* these subcategories constitute a specific dimension of experience value.

## Input Data
- **Cluster Label (Preliminary):** {cluster_label} 
- **Initial Subcategories to be Processed:** 
{subcategories}

## Coding Tasks
1. **Conceptual Abstraction:** Review the subcategories and group them into some distinct "Main Categories". These names should be theoretically dense (e.g., "Game playfulness", "Immersive sensory appeal", "Ephemeral value", "Physical environment friendliness", "Device usability", "Game-related service excellence").
2. **Relational Synthesis:** For each Main Category, provide a "Theoretical Rationale" that explains the underlying logic connecting its constituent subcategories.
3. **Dimensional Analysis:** Briefly define the properties of each Main Category (what it encompasses) based on the subcategories provided.

## Output Format
Return ONLY a JSON object. Ensure the structure is valid and contains no trailing commas.
```json
{{
    "main_categories": [
        {{
            "name": "Main Category Name (Theoretical/Abstract)",
            "definition": "A brief definition of what this category represents in the context of Vibe Coding.",
            "theoretical_rationale": "Explanation of why these subcategories are grouped together and their collective impact on experience value.",
            "associated_subcategories": ["Subcategory A", "Subcategory B", "Subcategory C"]
        }},
        {{
            "name": "...",
            "definition": "...",
            "theoretical_rationale": "...",
            "associated_subcategories": []
        }}
    ]
}}
