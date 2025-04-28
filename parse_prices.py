import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from jinja2 import Template

# 🦀 갑각류 종류 필터링 리스트
CRUSTACEANS = ["대게", "킹크랩", "홍게", "꽃게", "털게"]

# 📄 시세 내용 파싱 함수
def parse_price_text(text):
    lines = text.splitlines()
    price_data = []

    patterns = [
        r'(?P<item>[가-힣a-zA-Z/()\d\-]+)\s*(?P<unit>kg)\s*(?P<price>[\d,]+)원',
        r'(?P<item>[가-힣a-zA-Z/()\d\-]+)\s*(?P<unit>\d+g)\s*[-:]?\s*(?P<price>[\d,\.]+)원',
    ]

    for line in lines:
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                name = match.group('item').strip()
                unit = match.group('unit')
                price_str = match.group('price').replace(',', '').replace('.', '')
                try:
                    price = int(price_str)
                except ValueError:
                    continue
                price_data.append({"item": name, "unit": unit, "price": price})

    return price_data

# 🦀 갑각류 품목만 추출
def filter_crustaceans(price_list):
    grouped = {c: [] for c in CRUSTACEANS}

    for entry in price_list:
        name = entry['item']
        price = entry['price']

        for crust in CRUSTACEANS:
            if crust in name:
                grouped[crust].append(price)

    return grouped

# 📈 최소/중간/최대 요약
def summarize_prices(grouped_prices):
    summary = []

    for crust, prices in grouped_prices.items():
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            mid_price = int(sum(prices) / len(prices))  # 평균값
            summary.append({"item": crust, "min": min_price, "mid": mid_price, "max": max_price})

    return summary

# 📄 갑각류 요약 HTML 생성
def generate_crustacean_html(summary_list, date_str, output_dir='docs'):
    os.makedirs(output_dir, exist_ok=True)

    template = Template("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8">
      <title>{{ date }} 갑각류 시세 요약</title>
      <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
      </style>
    </head>
    <body>
      <h1>{{ date }} 줄포상회 갑각류 시세 요약</h1>
      <table>
        <tr><th>품목</th><th>최소(원)</th><th>중간(원)</th><th>최대(원)</th></tr>
        {% for row in summary %}
        <tr><td>{{ row.item }}</td><td>{{ row.min }}</td><td>{{ row.mid }}</td><td>{{ row.max }}</td></tr>
        {% endfor %}
      </table>
    </body>
    </html>
    """)

    html = template.render(date=f"{date_str[:4]}년 {int(date_str[4:6])}월 {int(date_str[6:])}일", summary=summary_list)

    with open(os.path.join(output_dir, f"{date_str}_crustaceans.html"), 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 갑각류 시세 저장 완료: docs/{date_str}_crustaceans.html")

# 📑 index.html 갱신
def update_index_html(output_dir='docs'):
    html_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.html') and f != 'index.html'])

    grouped = {}
    for filename in html_files:
        key = filename.split('_')[0].replace('.html', '')
        grouped.setdefault(key, []).append(filename)

    list_html = ''
    for date, files in grouped.items():
        try:
            readable = datetime.strptime(date, "%Y%m%d").strftime("%Y년 %m월 %d일")
        except ValueError:
            readable = date
        list_html += f"<li>{readable}<ul>"
        for file in sorted(files):
            label = (
                "원문" if "raw" in file else
                "파싱" if "parsed" in file else
                "갑각류 요약" if "crustaceans" in file else
                "기타"
            )
            list_html += f'<li><a href="{file}">{label}</a></li>'
        list_html += "</ul></li>\n"

    index_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>줄포상회 시세표 목록</title>
</head>
<body>
  <h1>줄포상회 시세표 목록</h1>
  <ul>
    {list_html}
  </ul>
</body>
</html>
"""

    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("✅ index.html 갱신 완료")

# 🏁 메인 실행부
if __name__ == "__main__":
    date_str = datetime.today().strftime("%Y%m%d")  # 오늘 날짜로 자동 인식

    # 가장 최신 raw 파일 자동 찾기
    candidates = [f for f in os.listdir('docs') if f.endswith('_raw.html')]
    candidates = sorted(candidates, reverse=True)
    if not candidates:
        print("❌ raw 파일이 없습니다.")
        exit(1)

    latest_raw = candidates[0]
    date_str = latest_raw.split('_')[0]

    with open(f'docs/{latest_raw}', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        content = soup.find('div').get_text(separator='\n')

    price_list = parse_price_text(content)
    grouped_crustaceans = filter_crustaceans(price_list)
    summarized = summarize_prices(grouped_crustaceans)

    generate_crustacean_html(summarized, date_str)
    update_index_html()
