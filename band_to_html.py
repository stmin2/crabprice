import os
import json
import datetime
from urllib import request
from jinja2 import Template
from dotenv import load_dotenv
import os

# .env 파일의 내용을 환경 변수로 로드
load_dotenv()

# 환경 변수에서 값 읽기
token = os.getenv('BAND_TOKEN')
band_key = os.getenv('BAND_KEY')



def update_index_html(docs_dir='docs'):
    html_files = sorted(
        [f for f in os.listdir(docs_dir) if f.endswith('.html') and f != 'index.html']
    )

    list_items = ''
    for filename in html_files:
        date_str = filename.replace('.html', '')
        try:
            readable = datetime.datetime.strptime(date_str, "%Y%m%d").strftime("%Y년 %m월 %d일")
        except ValueError:
            readable = date_str  # 예외 시 파일명 그대로
        list_items += f'<li><a href="{filename}">{readable}</a></li>\n'

    index_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>줄포상회 시세표 목록</title>
</head>
<body>
  <h1>줄포상회 시세표 목록</h1>
  <ul>
    {list_items}
  </ul>
</body>
</html>
"""

    with open(os.path.join(docs_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("✅ index.html 갱신 완료")


# 1. Band API 호출
def get_band_post(token, band_key):
    url = f'https://openapi.band.us/v2/band/posts?access_token={token}&band_key={band_key}'
    res = request.urlopen(request.Request(url))
    data = json.loads(res.read().decode("utf8"))
    items = data['result_data']['items']
    
    for item in items:
        if '시세표' in item['content'] and '줄포상회' in item['author']['name']:
            return item
    return None

# 2. HTML 생성
def generate_html(post, template_path='template.html', out_dir='docs'):
    date_str = extract_date(post['content']) or datetime.datetime.now().strftime('%Y%m%d')
    filename = f"{date_str}.html"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())
    
    html = template.render(
        title=f"줄포상회 {date_str} 시세표",
        author=post['author']['name'],
        content=post['content']
    )
    
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 저장 완료: docs/{filename}")
    return filename

# 3. 날짜 추출
def extract_date(text):
    import re
    match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', text)
    if match:
        today = datetime.date.today()
        month = int(match.group(1))
        day = int(match.group(2))
        year = today.year if today.month <= month else today.year + 1  # 연도 추정
        return f"{year}{month:02d}{day:02d}"
    return None

# 4. 메인 실행
if __name__ == "__main__":
    # ⬇️ 여기에 실제 토큰/밴드키 넣으세요
    token = os.getenv('BAND_TOKEN') or 'YOUR_ACCESS_TOKEN'
    band_key = os.getenv('BAND_KEY') or 'YOUR_BAND_KEY'

    post = get_band_post(token, band_key)
    if post:
        html_filename = generate_html(post)
    else:
        print("❌ 시세글을 찾을 수 없습니다.")


    # 시세글 HTML 저장 후 index 갱신
    update_index_html()