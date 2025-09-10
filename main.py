import requests
import selectorlib
import smtplib, ssl
import time
import sqlite3

# URL to scrape
URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36'
}

# Database connection
connection = sqlite3.connect("data.db")
cursor = connection.cursor()

# Ensure events table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    band TEXT,
    city TEXT,
    date TEXT
)
""")
connection.commit()


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url, headers=HEADERS)
    return response.text


def extract(source):
    """Extract the required value using extract.yaml"""
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(event_info):
    """Send email notification when a new event is found"""
    host = "smtp.gmail.com"
    port = 465

    username = "sudhakar.sonkar07@gmail.com"
    password = "app-password"  # app password

    receiver = "sudhakar.sonkar07@gmail.com"
    context = ssl.create_default_context()

    subject = "🎶 New Tour Event Found!"
    body = f"""
    Hello Sudhakar 👋,

    A new tour has just been announced! 🎉

    📌 Event Details:
    -----------------
    🎸 Band: {event_info['band']}
    🏙 City: {event_info['city']}
    📅 Date: {event_info['date']}

    ⏰ Notification Time: {time.strftime("%Y-%m-%d %H:%M:%S")}

    Make sure you don’t miss it! 🚀

    Cheers,  
    Your Python Scraper 🤖
    """

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message.encode("utf-8"))

    print("✅ Detailed email was sent!")


def store(extracted):
    """Store new event in the database"""
    parts = [item.strip() for item in extracted.split(",")]
    if len(parts) != 3:  # safety check
        print("⚠️ Skipping invalid data:", extracted)
        return
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES (?, ?, ?)", parts)
    connection.commit()


def read(extracted):
    """Check if event already exists in DB"""
    parts = [item.strip() for item in extracted.split(",")]
    if len(parts) != 3:  # safety check
        return True  # treat invalid row as already existing
    band, city, date = parts
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM events WHERE band=? AND city=? AND date=?",
        (band, city, date)
    )
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print("🔎 Extracted:", extracted)

        # Skip invalid or empty results
        if not extracted or extracted.lower() == "no upcoming tours":
            print("ℹ️ No upcoming events right now...")
        else:
            exists = read(extracted)
            if not exists:  # not in DB
                band, city, date = [x.strip() for x in extracted.split(",")]
                store(extracted)
                send_email({
                    "band": band,
                    "city": city,
                    "date": date
                })
            else:
                print("ℹ️ Event already exists in DB, skipping...")

        time.sleep(2)  # run every 2 seconds
