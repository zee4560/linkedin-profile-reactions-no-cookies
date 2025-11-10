import hashlib
import logging
import random
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple

from .utils_date import relative_token_from_days_ago

# Supported reaction types for demo generation
REACTION_TYPES = ["like", "appreciation", "empathy", "interest", "praise"]

@dataclass
class Author:
    firstName: str
    lastName: str
    headline: str
    profile_url: str
    profile_picture: str

@dataclass
class PostStats:
    totalReactionCount: int
    like: int
    appreciation: int
    empathy: int
    interest: int
    praise: int
    comments: int
    reposts: int

@dataclass
class Timestamps:
    relative: str

@dataclass
class Reaction:
    action: str
    text: str
    author: Author
    post_stats: PostStats
    timestamps: Timestamps

class LinkedInReactionsParser:
    """
    Parser/Fetcher facade.

    demo mode: returns deterministic, realistic-looking synthetic data per username.
    live mode: attempts a best-effort fetch (without authentication) by visiting the public profile.
              Since LinkedIn generally requires auth for detailed activity, we do not rely on it.
              Code will raise a clear error to avoid misleading behavior.
    """

    def __init__(self, user_agent: str, mode: str = "demo") -> None:
        self.user_agent = user_agent
        self.mode = mode

    def get_reactions_for_profile(self, username: str, pages: int = 1, per_page: int = 50) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if per_page <= 0:
            raise ValueError("per_page must be > 0")
        per_page = min(per_page, 100)

        if self.mode == "live":
            # We document the limitation and fail explicitly to avoid false promises.
            raise RuntimeError(
                "live mode is not supported without LinkedIn authentication; "
                "switch to --mode demo or provide an alternate public data source."
            )

        # DEMO MODE
        return self._demo_reactions(username=username, pages=pages, per_page=per_page)

    # -------------------------
    # Demo data generator
    # -------------------------
    def _demo_reactions(self, username: str, pages: int, per_page: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        # Seed RNG deterministically based on username so runs are stable
        seed = int(hashlib.sha256(username.encode("utf-8")).hexdigest(), 16) % (2**32)
        rnd = random.Random(seed)

        reactions: List[Dict[str, Any]] = []
        total_items = pages * per_page
        base_time = int(time.time())
        for i in range(total_items):
            # Simulate diversity in actions and content
            action = rnd.choice(REACTION_TYPES)
            # Some varied post texts
            snippets = [
                "Excited to announce our latest AI-powered solution for business analytics.",
                "A thoughtful take on data privacy and AI governance.",
                "Great write-up on scalable microservices with Kubernetes.",
                "Inspiring story of product-led growth in B2B SaaS.",
                "A deep dive into retrieval-augmented generation techniques.",
                "Reflections on leadership and team culture.",
                "A comprehensive guide to optimizing Postgres for analytics workloads.",
            ]
            text = rnd.choice(snippets)

            # Author generation
            author_first = rnd.choice(["Jane", "John", "Priya", "Wei", "Carlos", "Amira", "Noah", "Ava"])
            author_last = rnd.choice(["Doe", "Nguyen", "Khan", "Garcia", "Patel", "Zhang", "Ali", "Smith"])
            headline = rnd.choice(
                [
                    "Data Scientist at TechCorp",
                    "Staff Engineer at Cloudify",
                    "Product Manager at Growthly",
                    "AI Researcher at VisionLab",
                    "SRE at ScaleOps",
                    "Founder @ StartupX",
                ]
            )
            profile_url = f"https://linkedin.com/in/{author_first.lower()}{author_last.lower()}"
            profile_picture = f"https://media.licdn.com/{author_first.lower()}_{author_last.lower()}.jpg"

            # Reaction counts
            like = rnd.randint(50, 1500)
            appreciation = rnd.randint(0, 20)
            empathy = rnd.randint(0, 200)
            interest = rnd.randint(0, 100)
            praise = rnd.randint(0, 300)
            comments = rnd.randint(0, 150)
            reposts = rnd.randint(0, 120)
            total_reaction_count = like + appreciation + empathy + interest + praise

            # Relative time token (e.g., '5d', '2w')
            days_ago = rnd.randint(0, 90)
            relative = relative_token_from_days_ago(base_time, days_ago)

            reaction = Reaction(
                action=action,
                text=text,
                author=Author(
                    firstName=author_first,
                    lastName=author_last,
                    headline=headline,
                    profile_url=profile_url,
                    profile_picture=profile_picture,
                ),
                post_stats=PostStats(
                    totalReactionCount=total_reaction_count,
                    like=like,
                    appreciation=appreciation,
                    empathy=empathy,
                    interest=interest,
                    praise=praise,
                    comments=comments,
                    reposts=reposts,
                ),
                timestamps=Timestamps(relative=relative),
            )

            reactions.append(asdict(reaction))

        # Simple pagination token derivation
        pagination_token = hashlib.sha1(f"{username}:{pages}:{per_page}".encode("utf-8")).hexdigest()[:24]

        metadata = {
            "profile": username,
            "pages": pages,
            "per_page": per_page,
            "pagination_token": pagination_token,
            "mode": "demo",
        }
        return reactions, metadata