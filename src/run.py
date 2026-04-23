from __future__ import annotations

import argparse
import csv
from pathlib import Path

from slugify import slugify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate competitive intelligence briefs")
    parser.add_argument("--input", required=True, help="Competitors CSV")
    parser.add_argument("--output", default="out", help="Output directory")
    return parser.parse_args()


def score_competitor(pricing: float, traffic: int, offer_breadth: int, reviews: float) -> float:
    p = max(0.0, min(10.0, pricing / 500.0))
    t = max(0.0, min(10.0, traffic / 10000.0 * 10.0))
    o = max(0.0, min(10.0, offer_breadth))
    r = max(0.0, min(10.0, reviews / 5.0 * 10.0))
    score = (p * 0.25) + (t * 0.35) + (o * 0.2) + (r * 0.2)
    return round(score * 10, 2)


def main() -> None:
    args = parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["competitor_name"].strip()
            niche = row.get("niche", "general")
            pricing = float(row.get("avg_price", "0") or 0)
            traffic = int(row.get("monthly_visitors", "0") or 0)
            breadth = int(row.get("offer_breadth", "0") or 0)
            reviews = float(row.get("review_score", "0") or 0)

            score = score_competitor(pricing, traffic, breadth, reviews)
            rows.append(
                {
                    "competitor_name": name,
                    "niche": niche,
                    "avg_price": pricing,
                    "monthly_visitors": traffic,
                    "offer_breadth": breadth,
                    "review_score": reviews,
                    "competitive_score": score,
                }
            )

    rows.sort(key=lambda x: x["competitive_score"], reverse=True)

    with open(out / "competitive_table.csv", "w", encoding="utf-8", newline="") as f:
        fields = [
            "competitor_name",
            "niche",
            "avg_price",
            "monthly_visitors",
            "offer_breadth",
            "review_score",
            "competitive_score",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    for r in rows:
        slug = slugify(r["competitor_name"])
        action = "Differentiate with faster delivery + clearer offer packaging"
        if r["competitive_score"] > 70:
            action = "Avoid direct feature parity; position on niche specialization"
        elif r["competitive_score"] < 45:
            action = "Compete directly on offer clarity and proof assets"

        md = (
            f"# Competitive Brief - {r['competitor_name']}\n\n"
            f"- Niche: {r['niche']}\n"
            f"- Competitive score: {r['competitive_score']}/100\n"
            f"- Avg price: ${r['avg_price']}\n"
            f"- Monthly visitors: {r['monthly_visitors']}\n"
            f"- Offer breadth: {r['offer_breadth']}\n"
            f"- Review score: {r['review_score']}\n\n"
            f"## Recommended play\n"
            f"- {action}\n"
        )
        (out / f"brief_{slug}.md").write_text(md, encoding="utf-8")

    summary = ["# Competitive Intel Summary", "", "Top priorities:"]
    for r in rows[:3]:
        summary.append(f"- Track and counter-position against {r['competitor_name']} (score {r['competitive_score']})")
    (out / "summary.md").write_text("\n".join(summary), encoding="utf-8")

    print(f"Generated {len(rows)} competitive briefs -> {out / 'competitive_table.csv'}")


if __name__ == "__main__":
    main()
