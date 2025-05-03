import pandas as pd
import os
from bs4 import BeautifulSoup
import shutil


# 설정
DOCS_DIR = "docs"
HISTORY_CSV = "crustacean_prices.csv"
TARGET_ITEMS = ["대게", "킹크랩", "홍게", "꽃게", "털게"]

# 누적 리스트
records = []

# HTML 파일 순회
for filename in sorted(os.listdir(DOCS_DIR)):
    if filename.endswith("_crustaceans.html"):
        date = filename.split("_")[0]
        path = os.path.join(DOCS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            rows = soup.find_all("tr")[1:]  # 헤더 제외

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    item = cols[0].text.strip()
                    if item in TARGET_ITEMS:
                        min_price = int(cols[1].text.strip())
                        mid_price = int(cols[2].text.strip())
                        max_price = int(cols[3].text.strip())
                        records.append({
                            "date": date,
                            "item": item,
                            "min_price": min_price,
                            "mid_price": mid_price,
                            "max_price": max_price
                        })

# 저장
df = pd.DataFrame(records).sort_values(["item", "date"])
df.to_csv(HISTORY_CSV, index=False)
print(f"✅ 누적 시세 저장 완료: {HISTORY_CSV}")

shutil.copy("crustacean_prices.csv", "docs/crustacean_prices.csv")
