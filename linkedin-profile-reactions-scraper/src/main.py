import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from extractors.linkedin_reactions_parser import LinkedInReactionsParser
from outputs.export_to_json import export_reactions

DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "settings.example.json"
DEFAULT_PROFILES_FILE = Path(__file__).parents[2] / "data" / "input_profiles.txt"
DEFAULT_OUTPUT_FILE = Path(__file__).parents[2] / "data" / "sample_output.json"

def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        logging.warning("Config file %s not found. Falling back to defaults.", config_path)
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_profiles(profiles_file: Path) -> List[str]:
    if not profiles_file.exists():
        logging.warning("Profiles file %s not found. Using an example username.", profiles_file)
        return ["janedoe"]
    usernames: List[str] = []
    with open(profiles_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Accept either full URLs or usernames
            if "linkedin.com" in line:
                # Extract the last non-empty segment
                parts = [p for p in line.split("/") if p]
                usernames.append(parts[-1])
            else:
                usernames.append(line)
    if not usernames:
        usernames = ["janedoe"]
        logging.info("No profiles found in file; defaulting to %s", usernames)
    return usernames

def run(
    mode: str,
    profiles: List[str],
    pages: int,
    limit: int,
    user_agent: str,
    output_file: Path,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    parser = LinkedInReactionsParser(user_agent=user_agent, mode=mode)
    all_results: List[Dict[str, Any]] = []
    for username in profiles:
        logging.info("Fetching reactions for profile: %s (mode=%s, pages=%d, limit=%d)", username, mode, pages, limit)
        reactions, meta = parser.get_reactions_for_profile(username=username, pages=pages, per_page=limit)
        all_results.append(
            {
                "profile": username,
                "reactions": reactions,
                "metadata": meta,
            }
        )

    # For parity with the README example, if only one profile, flatten the structure.
    if len(all_results) == 1:
        payload = {
            "reactions": all_results[0]["reactions"],
            "metadata": all_results[0]["metadata"],
        }
    else:
        payload = {
            "profiles": all_results,
            "metadata": {"profiles_count": len(all_results)},
        }

    export_reactions(payload, output_file)
    return all_results, payload

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape and analyze public LinkedIn user reactions without logging in."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to settings JSON (defaults to settings.example.json)",
    )
    parser.add_argument(
        "--profiles-file",
        type=str,
        default=str(DEFAULT_PROFILES_FILE),
        help="Path to a text file containing LinkedIn profile usernames or URLs (one per line).",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to fetch per profile (each page has up to --limit reactions).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum reactions per page to return (demo mode supports up to 100).",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        choices=["demo", "live"],
        help="Fetch mode. 'demo' uses deterministic synthetic data; 'live' attempts real fetch (best-effort).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_FILE),
        help="Output JSON file.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(levelname)s: %(message)s")

    config = load_config(Path(args.config))
    mode = args.mode or config.get("mode", "demo")
    user_agent = config.get(
        "user_agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    pages = args.pages
    limit = args.limit
    output_file = Path(args.output)

    # Ensure output dir
    os.makedirs(output_file.parent, exist_ok=True)

    profiles = read_profiles(Path(args.profiles_file))
    _, payload = run(
        mode=mode,
        profiles=profiles,
        pages=pages,
        limit=limit,
        user_agent=user_agent,
        output_file=output_file,
    )
    logging.info("Wrote %d bytes to %s", len(json.dumps(payload, ensure_ascii=False).encode("utf-8")), output_file)

if __name__ == "__main__":
    main()