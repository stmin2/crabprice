import pandas as pd
import os

# CSV 읽기
csv_path = 'crustacean_prices.csv'
df = pd.read_csv(csv_path)

# HTML 테이블 생성
html_table = df.to_html(index=False, border=1, justify='center')

# 전체 HTML 문서로 감싸기
html_page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>줄포상회 갑각류 누적 시세</title>
  <style>
    body {{ font-family: sans-serif; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; text-align: center; }}
    th {{ background-color: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>줄포상회 갑각류 누적 시세</h1>
  {html_table}
</body>
</html>
"""

# 저장
output_path = os.path.join('docs', 'crustacean_prices_table.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_page)

print(f"✅ HTML 시세표 저장 완료: {output_path}")
