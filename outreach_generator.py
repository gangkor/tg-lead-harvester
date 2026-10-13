#!/usr/bin/env python3
import csv
import json
import os
import sys

TEMPLATES = {
    "b2b_service": "Hey {username}! Saw your posts in {channel}. We help web3/crypto creators automate their lead gen and save 15+ hours weekly. Open to a quick 2-min breakdown?",
    "affiliate": "Hi {username}, loved the engagement in {channel}! We are looking for trusted partners in this niche with high rev-share. Mind if I share the details?",
    "general": "Hey {username}! Reaching out regarding your recent updates in {channel}. Would love to connect and share some synergistic ideas."
}

def generate_campaign(csv_path: str, template_key: str = "b2b_service", output_path: str = None):
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return None

    if not output_path:
        base, ext = os.path.splitext(csv_path)
        output_path = f"{base}_campaign.csv"

    out_rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            channel = row.get("channel", "@channel")
            raw_users = row.get("usernames", "None")
            if raw_users and raw_users != "None":
                users = [u.strip() for u in raw_users.split(",")]
                for u in users:
                    tmpl = TEMPLATES.get(template_key, TEMPLATES["general"])
                    msg = tmpl.format(username=u, channel=channel)
                    out_rows.append({
                        "channel": channel,
                        "username": u,
                        "email": row.get("emails", "None"),
                        "pitch_message": msg
                    })

    if out_rows:
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["channel", "username", "email", "pitch_message"])
            writer.writeheader()
            for r in out_rows:
                writer.writerow(r)
        print(f"Generated {len(out_rows)} personalized outreach pitches -> {output_path}")
        return output_path
    else:
        print("No users found to generate pitches.")
        return None

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "/sdcard/Download/TG_Leads_telegram_20261013_100802.csv"
    generate_campaign(src)
