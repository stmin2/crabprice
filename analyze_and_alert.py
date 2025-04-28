import os
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# 📋 설정
CRUSTACEANS = ["대게", "킹크랩", "홍게", "꽃게", "털게"]
DATA_FILE = 'crustacean_prices.csv'
NTFY_TOPIC = 'your-ntfy-topic'  # 여기에 ntfy 토픽 이름 설정
THRESHOLD = 0.85  # 평균 대비 15% 저렴할 때 알림

# 📄 오늘 데이터 읽기
def load_today_data(docs_dir='docs'):
    candidates = [f for f in os.listdir(docs_dir) if f.endswith('_crustaceans.html')]
    candidates = sorted(candidates, reverse=True)
    if not candidates:
        print("❌ 갑각류 요약 파일이 없습니다.")
        exit(1)

    latest_file = candidates[0]
    date_str = latest_file.split('_')[0]

    with open(os.path.join(docs_dir, latest_file), 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    table_rows = soup.find_all('tr')[1:]  # 첫 번째 row는 헤더
    today_data = {}
    for row in table_rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            item = cols[0].text.strip()
            min_price = int(cols[1].text.strip())  # ⬅️ 최저가(min)를 2번째 td에서 가져옴
            today_data[item] = min_price

    return date_str, today_data

# 📊 누적 데이터 불러오기
def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['date', 'item', 'price'])

# 📝 누적 데이터 저장
def save_history(df):
    df.to_csv(DATA_FILE, index=False)

# 🔔 알림 보내기 (ntfy)
def send_alert(message):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    try:
        requests.post(url, data=message.encode('utf-8'))
        print(f"✅ 알림 전송: {message}")
    except Exception as e:
        print(f"❌ 알림 실패: {e}")

# 🏁 메인 실행
if __name__ == "__main__":
    today_date, today_prices = load_today_data()
    print(f"오늘 날짜: {today_date}, 오늘 시세 (최저가 기준): {today_prices}")

    history_df = load_history()

    # 오늘 데이터 누적 기록
    new_entries = []
    for item, price in today_prices.items():
        new_entries.append({"date": today_date, "item": item, "price": price})

    history_df = pd.concat([history_df, pd.DataFrame(new_entries)], ignore_index=True)
    save_history(history_df)

    # 평균 가격 계산 및 저렴 감지
    alerts = []
    for item in CRUSTACEANS:
        item_history = history_df[history_df['item'] == item]
        if len(item_history) > 1:
            average_price = item_history['price'].astype(float).mean()
            today_price = today_prices.get(item)

            if today_price and today_price <= average_price * THRESHOLD:
                alerts.append(f"🦀 {item} 오늘 최저가 {today_price}원 (평균 {int(average_price)}원) ⬇ 저렴!")

    # 알림 전송
    if alerts:
        message = f"[줄포상회 시세 알림 - 최저가 기준]\n" + "\n".join(alerts)
        send_alert(message)
    else:
        print("📈 오늘은 특별히 저렴한 갑각류가 없습니다.")
