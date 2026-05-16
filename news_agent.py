import anthropic
import smtplib
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]  # App password de Gmail
ANTHROPIC_KEY   = os.environ["ANTHROPIC_API_KEY"]

TOPICS = """
- Campañas ganadoras y trabajos destacados de festivales: Cannes Lions, D&AD, Clio Awards, One Show, Webby Awards, Epica Awards, Spikes Asia
- Novedades de agencias globales: CPB Group, Wieden+Kennedy, TBWA, AlmaPBBDO, DAVID, AKQA, DDB, Droga5, BBDO, McCann, Santo Buenos Aires, Lola MullenLowe
- Noticias de medios especializados: Adweek, The Drum, Little Black Book, Campaign, LBB
- Branding y diseño gráfico: nuevas identidades, rebrands, proyectos de estudios como Sagmeister & Walsh, Chermayeff & Geismar, Bureau Borsche, MetaDesign
- Tipografía y lettering: nuevas tipografías, proyectos de Sudtipos, Animography, diseñadores de tipo
- Dirección de arte y producción audiovisual: trabajos de directores como Michel Gondry, Spike Jonze, Ridley Scott
- OOH, activaciones, casos creativos innovadores
- Packaging creativo y diseño de producto
"""

def fetch_news():
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Search for the 5 most important and recent news stories from today about the following topics in the creative advertising world:

{TOPICS}

Prioritize news from sources like Adweek, The Drum, LBB, Campaign, Cannes Lions, D&AD, and the agencies and studios listed.
For each story include a title, a 2-3 sentence summary, and the source.
All titles and summaries MUST be written in English.
Reply ONLY in JSON with no backticks or markdown:
{{"date":"DD/MM/YYYY","news":[{{"title":"...","summary":"...","source":"..."}}]}}"""
        }]
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text.strip())

def build_html(data):
    fecha = data.get("date", datetime.now().strftime("%d/%m/%Y"))
    items = "".join(f"""
    <div style="margin-bottom:24px;padding:16px;background:#f9f9f9;border-left:3px solid #e94560;border-radius:4px;">
      <p style="font-size:11px;color:#888;margin:0 0 4px">{i+1}. {n['source']}</p>
      <h3 style="margin:0 0 8px;font-size:16px;color:#1a1a2e">{n['title']}</h3>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#555">{n['summary']}</p>
    </div>""" for i, n in enumerate(data.get("news", [])))
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#333">
      <h2 style="color:#1a1a2e;border-bottom:2px solid #e94560;padding-bottom:8px">
        🎬 Creative News · {fecha}
      </h2>
      <p style="font-size:13px;color:#888;margin:-8px 0 20px">
        Advertising · Branding · Design · Awards · Agencies
      </p>
      {items}
      <p style="font-size:12px;color:#aaa;text-align:center;margin-top:32px">
        Based on All Things Advertising &amp; Infoextravaganza · Auto-generated
      </p>
    </div>"""

def send_email(html, fecha):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎬 Creative News · {fecha}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(SENDER_EMAIL, SENDER_PASSWORD)
        s.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Email enviado.")

if __name__ == "__main__":
    data = fetch_news()
    html = build_html(data)
    send_email(html, data.get("date", datetime.now().strftime("%d/%m/%Y")))
