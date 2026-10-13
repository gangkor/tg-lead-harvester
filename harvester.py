#!/usr/bin/env python3
import urllib.request
import re
import csv
import json
import os
import sys
from datetime import datetime

class TGLeadHarvester:
    def __init__(self, output_dir="/sdcard/Download"):
        self.output_dir = output_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_channel_messages(self, channel_username: str):
        channel_clean = channel_username.replace("@", "").replace("https://t.me/", "").replace("t.me/", "").strip()
        url = f"https://t.me/s/{channel_clean}"
        req = urllib.request.Request(url, headers=self.headers)
        
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                html = response.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return {"error": f"Failed to access channel: {e}", "leads": []}

        raw_msgs = re.findall(r'<div class=\"tgme_widget_message_text[^\"]*\"[^>]*>(.*?)</div>', html, re.DOTALL)
        dates = re.findall(r'<time datetime=\"([^\"]+)\"', html)
        views = re.findall(r'<span class=\"tgme_widget_message_views\">([^<]+)</span>', html)
        
        leads = []
        for idx, raw in enumerate(raw_msgs):
            text = re.sub(r'<[^>]+>', ' ', raw).strip()
            text = ' '.join(text.split())
            
            emails = list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)))
            usernames = list(set(re.findall(r'@[a-zA-Z0-9_]{3,32}', text)))
            phones = list(set(re.findall(r'(?:\+?380|0|\+1|\+44)\d{9,11}', text)))
            links = list(set(re.findall(r'https?://[^\s<>"]+|t\.me/[a-zA-Z0-9_]+', text)))

            leads.append({
                "channel": f"@{channel_clean}",
                "date": dates[idx][:10] if idx < len(dates) else datetime.now().strftime("%Y-%m-%d"),
                "views": views[idx] if idx < len(views) else "N/A",
                "usernames": ", ".join(usernames) if usernames else "None",
                "emails": ", ".join(emails) if emails else "None",
                "phones": ", ".join(phones) if phones else "None",
                "links": ", ".join(links[:2]) if links else "None",
                "text_preview": text[:250]
            })

        return {"channel": channel_clean, "total_messages": len(raw_msgs), "leads_count": len(leads), "leads": leads}

    def export_to_csv(self, leads: list, channel_name: str) -> str:
        filename = f"TG_Leads_{channel_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = ["channel", "date", "views", "usernames", "emails", "phones", "links", "text_preview"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)

        return filepath

if __name__ == "__main__":
    harvester = TGLeadHarvester()
    target = sys.argv[1] if len(sys.argv) > 1 else "telegram"
    res = harvester.fetch_channel_messages(target)
    print(f"Parsed {res.get('leads_count')} messages from @{res.get('channel')}")
    if res.get("leads"):
        out = harvester.export_to_csv(res["leads"], res.get("channel"))
        print(f"Successfully generated CSV: {out}")
