import anthropic
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]  # App password de Gmail
ANTHROPIC_KEY   = os.environ["ANTHROPIC_API_KEY"]

def fetch_news():
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": """Buscá las 5 noticias más importantes y recientes de hoy sobre publicidad y marketing creativo.
Para cada noticia incluí título, resumen de 2-3 oraciones y fuente.
Respondé SOLO en JSON sin backticks:
{"fecha":"DD/MM/YYYY","noticias":[{"titulo":"...","resumen":"...","fuente":"..."}]}"""
        }]
    )
    text = next(b.text for b in response.content if b.type == "text")
    import json
    return json.loads(text.strip())

def build_html(data):
    fecha = data.get("fecha", datetime.now().strftime("%d/%m/%Y"))
    items = "".join(f"""
    <div style="margin-bottom:24px;padding:16px;background:#f9f9f9;border-left:3px solid #e94560;border-radius:4px;">
      <p style="font-size:11px;color:#888;margin:0 0 4px">{i+1}. {n['fuente']}</p>
      <h3 style="margin:0 0 8px;font-size:16px;color:#1a1a2e">{n['titulo']}</h3>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#555">{n['resumen']}</p>
    </div>""" for i, n in enumerate(data.get("noticias", [])))
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#333">
      <h2 style="color:#1a1a2e;border-bottom:2px solid #e94560;padding-bottom:8px">
        📢 Noticias de Publicidad y Marketing — {fecha}
      </h2>
      {items}
      <p style="font-size:12px;color:#aaa;text-align:center;margin-top:32px">
        Generado automáticamente · Agente de Noticias Creativas
      </p>
    </div>"""

def send_email(html, fecha):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📢 Noticias de Publicidad y Marketing — {fecha}"
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
    send_email(html, data.get("fecha", datetime.now().strftime("%d/%m/%Y")))
