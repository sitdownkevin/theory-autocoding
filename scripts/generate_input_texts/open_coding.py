from pathlib import Path
import json


def main():
    with open("prompts/02-open_coding.md", "r") as f:
        prompt = f.read()

    data_dir = Path("data") / "raw" / "20251230"
    post_files = data_dir.glob("POST_*.json")

    input_texts = []

    for post_file in post_files:
        with open(post_file, "r") as f:
            data = json.load(f)

            post_info = data["post_info"]
            subreddit = post_info["subreddit"]
            comments = data["comments"]

            for comment in comments:
                input_text = prompt.format(
                    subreddit=subreddit,
                    post_title=post_info["title"],
                    post_content=post_info["content"],
                    content=comment["content"],
                )
                input_texts.append(input_text)

    Path("data/input_texts").mkdir(parents=True, exist_ok=True)
    with open(Path("data") / "input_texts" / "open_coding.json", "w") as f:
        json.dump(input_texts, f, indent=4)


if __name__ == "__main__":
    main()
