# TG-Lead Harvester Pro v2.1 - Ghost Edition
# Engine for scraping groups with hidden member lists and auto-outreach

import asyncio
import aiohttp
from telethon import TelegramClient
from telethon.tl.types import UserStatusRecently

async def ghost_harvest(client: TelegramClient, chat_entity, limit: int = 2000):
    leads = {}
    print(f"[*] Deploying Ghost-Scraper on: {chat_entity.title}...")
    
    # Iterate message history instead of restricted GetParticipantsRequest
    async for message in client.iter_messages(chat_entity, limit=limit):
        sender = message.sender
        if not sender or sender.bot or sender.is_self:
            continue
            
        if sender.username and sender.id not in leads:
            is_active = isinstance(sender.status, UserStatusRecently)
            leads[sender.id] = {
                "id": sender.id,
                "username": f"@{sender.username}",
                "first_name": sender.first_name,
                "last_seen_recent": is_active,
                "last_message_snippet": (message.text[:50] + "...") if message.text else "[Media]",
                "message_date": str(message.date)
            }
            
    print(f"[✓] Extracted {len(leads)} ultra-fresh leads from message stream!")
    return list(leads.values())

async def push_to_webhook(webhook_url: str, lead: dict):
    if not webhook_url:
        return
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=lead, timeout=5) as resp:
                if resp.status == 200:
                    print(f"[->] Synced @{lead['username']} to CRM/Sheets")
        except Exception as e:
            print(f"[!] Webhook error: {e}")
