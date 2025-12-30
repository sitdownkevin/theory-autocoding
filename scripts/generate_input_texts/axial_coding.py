from pathlib import Path
import json


def main():
    with open("prompts/03-axial_coding.md", "r") as f:
        prompt = f.read()

    with open("data/coding_results/open_coding_clustered.json", "r") as f:
        open_coding_results = json.load(f)

    input_texts = []
    for k, v in open_coding_results.items():
        if k == "-1": continue
        input_text = prompt.format(
            cluster_label=k,
            subcategories=json.dumps(v, indent=4)
        )
        input_texts.append(input_text)

    Path("data/input_texts").mkdir(parents=True, exist_ok=True)
    with open(Path("data") / "input_texts" / "axial_coding.json", "w") as f:
        json.dump(input_texts, f, indent=4)

if __name__ == "__main__":
    main()
