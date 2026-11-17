#!/usr/bin/env python3
"""Update trimoco.com Google review counts, cards, and schema from Places API (New).

Requires env GOOGLE_PLACES_API_KEY. Never prints or writes the key.
Exits 0 with no file changes when the public site already matches the API.
Does not touch Lynbrook mentions or street addresses.

This script is intended to run from the feat/google-reviews-auto-update
workflow and should not be merged to main until a key is in place.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PLACE_ID = "ChIJ__8beJpkwokRkhfKdrDJYuM"
REVIEWS_URL = f"https://search.google.com/local/reviews?placeid={PLACE_ID}"
BUSINESS_ID = "https://www.trimoco.com/#business"
PLACES_URL = f"https://places.googleapis.com/v1/places/{PLACE_ID}"
# rating + userRatingCount are Place Details Enterprise; reviews raise the
# request to Place Details Enterprise + Atmosphere.
FIELD_MASK = "rating,userRatingCount,reviews"
REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC = REPO_ROOT / "public"
JSON_PATH = PUBLIC / "data" / "google-reviews.json"
MAX_REVIEWS = 5  # Places API (New) returns at most 5 reviews
AVATAR_STYLES = (
    ("bg-accent", "text-accent-fg"),
    ("bg-secondary", "text-secondary-fg"),
)

STAR_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" '
    'stroke-width="0" aria-hidden="true"> '
    '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2">'
    "</polygon> </svg>"
)


def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def fetch_place(api_key: str) -> dict:
    req = urllib.request.Request(
        PLACES_URL,
        headers={
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not print response bodies; they can echo request metadata.
        die(f"Places API request failed with HTTP {exc.code}")
    except urllib.error.URLError as exc:
        die(f"Places API request failed: {exc.reason}")
    return payload


def normalize(payload: dict) -> dict:
    rating = payload.get("rating")
    count = payload.get("userRatingCount")
    if rating is None or count is None:
        die("Places API response missing rating or userRatingCount")
    try:
        count_i = int(count)
        rating_f = float(rating)
    except (TypeError, ValueError):
        die("Places API returned a non-numeric rating or userRatingCount")
    if count_i < 0 or not (1.0 <= rating_f <= 5.0):
        die("Places API returned an out-of-range rating or count")

    reviews = []
    for item in (payload.get("reviews") or [])[:MAX_REVIEWS]:
        author = ((item.get("authorAttribution") or {}).get("displayName") or "").strip()
        text_obj = item.get("text") or item.get("originalText") or {}
        body = (text_obj.get("text") or "").strip()
        try:
            star = int(item.get("rating") or 0)
        except (TypeError, ValueError):
            star = 0
        if not author or not body or star < 1 or star > 5:
            continue
        reviews.append(
            {
                "author": author,
                "rating": star,
                "text": body,
                "publishTime": item.get("publishTime") or "",
                "relativePublishTimeDescription": item.get("relativePublishTimeDescription") or "",
            }
        )
    rating_display = f"{rating_f:.1f}"
    return {
        "placeId": PLACE_ID,
        "rating": rating_f,
        "ratingDisplay": rating_display,
        "userRatingCount": count_i,
        "reviewsUrl": REVIEWS_URL,
        "reviews": reviews,
    }


def initial_for(name: str) -> str:
    for ch in name.strip():
        if ch.isalnum():
            return ch.upper()
    return "?"


def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def stars_html(rating: int) -> str:
    return (
        f'<div class="star-rating gap-[3px]" role="img" aria-label="{rating} out of 5 stars"> '
        + "".join(STAR_SVG for _ in range(rating))
        + " </div>"
    )


def card_html(review: dict, index: int) -> str:
    name = review["author"]
    body = review["text"]
    initial = initial_for(name)
    text_id = f"review-text-{index}"
    avatar_bg, avatar_fg = AVATAR_STYLES[index % len(AVATAR_STYLES)]
    return (
        f'<article data-review-card class="snap-start shrink-0 grow-0 basis-[min(calc(85vw-0.5rem),340px)] '
        f'md:basis-[calc((100%-1.25rem)/2)] lg:basis-[calc((100%-2*1.25rem)/3)] relative flex flex-col gap-4 '
        f'overflow-hidden p-7 bg-surface-raised rounded-lg border border-card-warm-border shadow-sm-warm" '
        f'aria-label="Review from {escape_html(name)}"> '
        f'<!-- Decorative opening quote --> '
        f'<div class="pointer-events-none absolute bottom-3 right-4 select-none font-heading leading-none text-secondary" '
        f'style="font-size: 5.5rem; opacity: 0.10; line-height: 1" aria-hidden="true">&#8221;</div> '
        f'<!-- Stars --> {stars_html(review["rating"])} '
        f'<!-- Quote --> <blockquote class="m-0 flex-1"> '
        f'<p id="{text_id}" class="text-[0.9375rem] text-text-secondary leading-[1.7] italic m-0" data-review-text> '
        f"{escape_html(body)} </p> </blockquote> "
        f'<button type="button" class="text-sm font-semibold text-accent self-start -mt-2" data-review-toggle '
        f'aria-controls="{text_id}" aria-expanded="false" hidden>\nSee more\n</button> '
        f'<!-- Author --> <footer class="flex items-center gap-3 pt-4 border-t border-border"> '
        f'<div class="w-10 h-10 rounded-full flex items-center justify-center font-heading text-base font-bold flex-shrink-0 {avatar_bg} {avatar_fg}" aria-hidden="true"> {escape_html(initial)} </div> '
        f'<div class="flex flex-col gap-[2px]"> <span class="text-[0.9rem] font-semibold text-text">{escape_html(name)}</span> '
        f'<span class="text-xs text-text-muted"> Google review   </span> </div> </footer> </article>'
    )


def review_schema(data: dict) -> str:
    graph = []
    for review in data["reviews"]:
        graph.append(
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": review["author"]},
                "itemReviewed": {"@id": BUSINESS_ID},
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": str(review["rating"]),
                    "bestRating": "5",
                    "worstRating": "1",
                },
                "reviewBody": review["text"],
            }
        )
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(", ", ": "))


def count_label(n: int) -> str:
    return f"{n} Google reviews" if n != 1 else "1 Google review"


def see_all_label(n: int) -> str:
    return f"See all {n} reviews on Google" if n != 1 else "See the review on Google"


def see_all_html(n: int) -> str:
    return (
        f'<p class="mt-6 text-center m-0"><a href="{REVIEWS_URL}" target="_blank" rel="noopener" '
        f'class="text-sm text-text-secondary underline underline-offset-2 hover:text-accent">'
        f"{see_all_label(n)}</a></p>"
    )


def patch_localbusiness(raw: str, data: dict) -> str:
    obj = json.loads(raw)
    if not (isinstance(obj, dict) and "LocalBusiness" in str(obj.get("@type"))):
        return raw
    obj["aggregateRating"] = {
        "@type": "AggregateRating",
        "ratingValue": data["ratingDisplay"],
        "bestRating": "5",
        "worstRating": "1",
        "reviewCount": str(data["userRatingCount"]),
    }
    return json.dumps(obj, separators=(", ", ": "))


def is_review_graph(obj) -> bool:
    return (
        isinstance(obj, dict)
        and isinstance(obj.get("@graph"), list)
        and obj["@graph"]
        and obj["@graph"][0].get("@type") == "Review"
    )


def _visible_reviews(html: str) -> list[tuple[str, str, int]]:
    found = []
    for article in re.findall(r'<article\b[^>]*data-review-card[^>]*>.*?</article>', html, re.S):
        name_m = re.search(r'aria-label="Review from ([^"]+)"', article)
        body_m = re.search(r'data-review-text>\s*(.*?)\s*</p>', article, re.S)
        rating_m = re.search(r'aria-label="(\d+) out of 5 stars"', article)
        if not (name_m and body_m and rating_m):
            continue
        found.append((name_m.group(1), re.sub(r"\s+", " ", body_m.group(1)).strip(), int(rating_m.group(1))))
    return found


def replace_review_cards(html: str, data: dict, rel: str) -> str:
    if not data["reviews"] or 'id="reviews-track"' not in html:
        return html
    incoming = [
        (r["author"], re.sub(r"\s+", " ", r["text"]).strip(), int(r["rating"]))
        for r in data["reviews"]
    ]
    if _visible_reviews(html) == incoming:
        return html
    cards = "".join(card_html(r, i) for i, r in enumerate(data["reviews"]))
    # End the replacement at the dots comment so inner </div> tags in cards are ignored.
    pattern = re.compile(
        r'(<div id="reviews-track"[^>]*> )(?:<article\b.*?</article>)+( </div> <!-- Dots \+ nav — always visible -->)',
        re.S,
    )
    new_html, n = pattern.subn(rf"\1{cards}\2", html, count=1)
    if n != 1:
        die(f"Could not locate the review cards track to update in {rel}")
    return new_html


def patch_html(text: str, data: dict, rel: str) -> str:
    lynbrook = text.count("Lynbrook") + text.count("lynbrook")
    had_street = "Concord St" in text or "20 Concord" in text
    original = text
    n = data["userRatingCount"]
    rating = data["ratingDisplay"]

    # Visible count on the existing Google reviews link (any prior integer).
    text = re.sub(
        r'(<a href="' + re.escape(REVIEWS_URL) + r'"[^>]*>)\d+ Google reviews(</a>)',
        rf"\g<1>{count_label(n)}\2",
        text,
    )
    # See-all link text, or insert it if a reviews section is missing one.
    see = see_all_html(n)
    if re.search(r"See all \d+ reviews on Google|See the review on Google", text):
        text = re.sub(
            r">See all \d+ reviews on Google<|>See the review on Google<",
            f">{see_all_label(n)}<",
            text,
        )
    elif 'id="reviews"' in text:
        anchor = "</button> </div> </div> <!-- CTA — shown only on homepage -->"
        if text.count(anchor) != 1:
            die(f"Unexpected See all insertion point in {rel}")
        text = text.replace(
            anchor,
            f"</button> </div> {see} </div> <!-- CTA — shown only on homepage -->",
            1,
        )

    # Summary rating numeral next to the stars (reviews section only).
    if 'id="reviews"' in text:
        text = re.sub(
            r'(id="reviews"[\s\S]*?<span class="font-heading text-5xl font-bold text-accent leading-none">)(\d+(?:\.\d+)?)(</span>)',
            rf"\g<1>{rating}\3",
            text,
            count=1,
        )
        text = re.sub(
            r'(id="reviews"[\s\S]*?aria-label=")\d+(?:\.\d+)? out of 5 stars(")',
            rf"\g<1>{rating} out of 5 stars\2",
            text,
            count=1,
        )
        text = replace_review_cards(text, data, rel)

    # JSON-LD: AggregateRating on every LocalBusiness; Review graph only
    # on pages that show review cards, and only for the reviews shown.
    scripts = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', text, re.S))
    review_ld = review_schema(data) if data["reviews"] and 'id="reviews"' in text else None
    inserted_review = False
    pieces = []
    last = 0
    for m in scripts:
        pieces.append(text[last:m.start()])
        raw = m.group(1)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            pieces.append(m.group(0))
            last = m.end()
            continue
        if isinstance(obj, dict) and "LocalBusiness" in str(obj.get("@type")):
            block = f'<script type="application/ld+json">{patch_localbusiness(raw, data)}</script>'
            if review_ld and not inserted_review:
                block += f'<script type="application/ld+json">{review_ld}</script>'
                inserted_review = True
            pieces.append(block)
        elif is_review_graph(obj):
            if review_ld and not inserted_review:
                pieces.append(f'<script type="application/ld+json">{review_ld}</script>')
                inserted_review = True
            elif review_ld and inserted_review:
                # Drop a duplicate review graph (already inserted after LocalBusiness).
                pass
            # If this page should no longer have review schema, drop it.
        else:
            pieces.append(m.group(0))
        last = m.end()
    pieces.append(text[last:])
    text = "".join(pieces)

    if text.count("Lynbrook") + text.count("lynbrook") != lynbrook:
        die(f"Refusing to write {rel}: Lynbrook mention count would change")
    if ("Concord St" in text or "20 Concord" in text) and not had_street:
        die(f"Refusing to write {rel}: a street address would be introduced")
    if text == original:
        return text
    return text


def write_json(data: dict) -> bool:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if JSON_PATH.exists() and JSON_PATH.read_text("utf-8") == rendered:
        return False
    JSON_PATH.write_text(rendered, encoding="utf-8")
    return True


def main() -> None:
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not api_key:
        print("GOOGLE_PLACES_API_KEY is not set; skipping updates.")
        raise SystemExit(0)

    data = normalize(fetch_place(api_key))
    json_changed = write_json(data)
    html_changed = 0
    for path in sorted(PUBLIC.rglob("*.html")):
        original = path.read_text("utf-8")
        updated = patch_html(original, data, str(path.relative_to(PUBLIC)))
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            html_changed += 1

    if not json_changed and not html_changed:
        print(
            f"No changes: {data['ratingDisplay']} from {data['userRatingCount']} reviews "
            f"({len(data['reviews'])} on the page)."
        )
        return
    print(
        f"Updated {html_changed} HTML files and "
        f"{'wrote' if json_changed else 'left'} {JSON_PATH.relative_to(REPO_ROOT)} "
        f"to {data['ratingDisplay']} from {data['userRatingCount']} Google reviews "
        f"({len(data['reviews'])} marked up on the page)."
    )


if __name__ == "__main__":
    main()
