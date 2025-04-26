import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from jinja2 import Template

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

def generate_parsed_html(price_list, date_str, output_dir='docs'):
    os.makedirs(output_dir, exist_ok=True)

    template = Template("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8">
      <title>{{ date }} 시세표 (파싱)</title>
      <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
      </style>
    </head>
    <body>
      <h1>{{ date }} 줄포상회 시세표 (파싱)</h1>
      <table>
        <tr><th>항목</th><th>단위</th><th>가격(원)</th></tr>
        {% for row in prices %}
        <tr><td>{{ row.item }}</td><td>{{ row.unit }}</td><td>{{ row.price }}</td></tr>
        {% endfor %}
      </table>
    </body>
    </html>
    """)

    html = template.render(date=f"{date_str[:4]}년 {int(date_str[4:6])}월 {int(date_str[6:])}일", prices=price_list)

    with open(os.path.join(output_dir, f"{date_str}_parsed.html"), 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 파싱된 시세 저장 완료: docs/{date_str}_parsed.html")

def update_index_html(output_dir='docs'):
    html_files = sorted(
        [f for f in os.listdir(output_dir) if f.endswith('.html') and f != 'index.html']
    )

    grouped = {}
    for filename in html_files:
        key = filename.split('_')[0].replace('.html', '')
        grouped.setdefault(key, []).append(filename)

    list_html = ''
    for date, files in grouped.items():
        try:
            readable = datetime.strptime(date, "%Y%m%d").strftime("%Y년 %m월 %d일")
        except ValueError:
            readable = date  # 날짜 파싱 실패 시 그냥 파일명 그대로
        list_html += f"<li>{readable}<ul>"
        for file in sorted(files):
            label = '원문' if 'raw' in file else ('파싱' if 'parsed' in file else '기타')
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


if __name__ == "__main__":
    date_str = '20250426'  # 예시

    with open(f'docs/{date_str}_raw.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        content = soup.find('div').get_text(separator='\n')

    price_list = parse_price_text(content)
    generate_parsed_html(price_list, date_str)
    update_index_html()
