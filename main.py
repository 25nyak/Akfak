import asyncio
import os
from playwright.async_api import async_playwright
import requests

# Secrets from GitHub/Environment
FIVESIM_KEY = os.getenv("FIVESIM_API_KEY")
PROXY_URL = os.getenv("DATAIMPULSE_PROXY") # user:pass@host:port

async def create_telegram_account(browser, account_id):
    # 1. Setup Mobile Emulation (mimicking an iPhone or Android)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        viewport={'width': 390, 'height': 844},
        has_touch=True,
        proxy={"server": f"http://{PROXY_URL}"}
    )
    
    page = await context.new_page()
    print(f"[*] Instance {account_id}: Requesting number from 5sim...")

    # 2. Get Number from 5sim
    # Note: Use 'google' or 'telegram' based on your GitHub input
    res = requests.get(f"https://5sim.net/v1/user/buy/activation/ANY/ANY/telegram?api_key={FIVESIM_KEY}").json()
    order_id, phone = res['id'], res['phone']

    try:
        # 3. Automation Logic (Example: Telegram Web)
        await page.goto("https://web.telegram.org/k/")
        # Use Playwright selectors to input 'phone'
        # await page.fill('input[name="phone"]', phone)
        
        print(f"[+] Instance {account_id}: Number {phone} entered. Waiting for SMS...")

        # 4. Poll 5sim for SMS
        code = None
        for _ in range(24): # Wait 2 minutes max
            await asyncio.sleep(5)
            check = requests.get(f"https://5sim.net/v1/user/check/{order_id}?api_key={FIVESIM_KEY}").json()
            if check.get('sms'):
                code = check['sms'][0]['code']
                break
        
        if code:
            print(f"[!] Instance {account_id}: Code received: {code}")
            # await page.fill('input[name="otp"]', code)
            # Finish registration...
        else:
            requests.get(f"https://5sim.net/v1/user/cancel/{order_id}?api_key={FIVESIM_KEY}")
            print(f"[-] Instance {account_id}: Timeout. Order cancelled.")

    finally:
        await context.close()

async def main(amount):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [create_telegram_account(browser, i) for i in range(int(amount))]
        await asyncio.gather(*tasks)
        await browser.close()

if __name__ == "__main__":
    import sys
    asyncio.run(main(sys.argv[2]))
