import time
from playwright.sync_api import sync_playwright
import subprocess

def run_verification():
    # Start the server in background
    server = subprocess.Popen(["python3", "app.py"])
    time.sleep(3) # Wait for server to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Login Page
            page.goto("http://127.0.0.1:5000")
            page.screenshot(path="verification/login_page.png")

            # 2. Perform Login as Admin
            page.click("text=Admin")
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "admin123")
            page.click("button:has-text('Sign In')")

            # 3. Admin Dashboard
            time.sleep(1)
            page.screenshot(path="verification/admin_dashboard.png")

            # 4. Open Chat (if any request exists)
            # We'll create one first by logging in as student
            page.goto("http://127.0.0.1:5000/logout")
            page.click("text=Student")
            page.fill("input[name='username']", "user1")
            page.fill("input[name='password']", "user123")
            page.click("button:has-text('Sign In')")

            page.click("button:has-text('Request New Thesis')")
            page.fill("#req-title", "Playwright Verification Thesis")
            page.fill("#req-desc", "Verifying the UI/UX with automated tools.")
            page.click("#submit-req-btn")
            time.sleep(4) # Wait for randomizer spin
            page.screenshot(path="verification/receiver_assigned.png")

            # 5. Chat Hub
            page.click("text=Open Chat Hub")
            time.sleep(1)
            page.screenshot(path="verification/chat_nexus.png")

            browser.close()
    finally:
        server.terminate()

if __name__ == "__main__":
    run_verification()
