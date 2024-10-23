from flask import Flask, render_template, request, session
from datetime import datetime
import os
import openai  # 確保導入 OpenAI 模組

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# 設置 OpenAI API 密鑰
openai.api_key = os.getenv('OPENAI_API_KEY')  # 從環境變數中獲取 API 密鑰

# 六神六煞與五行方位對應表
elements = [
    "大安=1东方木青龙", "留连=2西南木青龙", "速喜=3正南火朱雀", 
    "赤口=4西方金白虎", "小吉=5北方水玄武", "空亡=6中土藤蛇", 
    "病符=7西南金白虎", "桃花=8东北土勾陈", "天德=9西北金白虎"
]

def get_elements(n1, n2, n3):
    """根據輸入數字計算對應的六神和方位"""
    first_index = (n1 - 1) % len(elements)
    second_index = (n1 + n2 - 2) % len(elements)
    third_index = (n1 + n2 + n3 - 3) % len(elements)
    return elements[first_index], elements[second_index], elements[third_index]

def current_yin_yang(minute):
    """根據分鐘判斷陰陽"""
    return "陽早" if minute < 30 else "陰晚"

def current_time_period(hour, minute):
    """根據當前小時和分鐘返回對應的時辰"""
    yin_yang = current_yin_yang(minute)
    periods = [
        ("子時", 23, 1), ("丑時", 1, 3), ("寅時", 3, 5), ("卯時", 5, 7),
        ("辰時", 7, 9), ("巳時", 9, 11), ("午時", 11, 13), ("未時", 13, 15),
        ("申時", 15, 17), ("酉時", 17, 19), ("戌時", 19, 21), ("亥時", 21, 23)
    ]
    
    for name, start, end in periods:
        if start <= hour < end or (start > end and (hour >= start or hour < end)):
            return f"{yin_yang} {name}"
    
    return "未知時辰"

def normalize_number(number):
    """處理數字，忽略小數點和大於四位數的狀況"""
    total = sum(int(digit) for digit in str(int(float(number))))
    while total >= 10000:  # 若結果超過四位數，繼續加總
        total = sum(int(digit) for digit in str(total))
    return total

def check_limits():
    """檢查使用次數限制"""
    if 'usage_count' not in session:
        session['usage_count'] = 0
    if session['usage_count'] >= 3:
        return False
    session['usage_count'] += 1
    return True

def generate_analysis(keyword, elements_result):
    """使用 ChatGPT 根據關鍵字和元素生成綜合解析"""
    prompt = f"根據以下元素 {elements_result} 和關鍵字 '{keyword}'，請提供一個綜合解析。"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 或者使用其他可用的模型
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not check_limits():
            return render_template('index.html', error="今日使用次數已達上限，請明天再試。")

        try:
            n1 = normalize_number(request.form.get('n1', 1))
            n2 = normalize_number(request.form.get('n2', 1))
            n3 = normalize_number(request.form.get('n3', 1))
            keyword = request.form.get('keyword', '')  # 獲取關鍵字

            # 獲取六神和方位
            elements_result = get_elements(n1, n2, n3)

            # 使用 ChatGPT 生成綜合解析
            analysis = generate_analysis(keyword, elements_result)

            return render_template('index.html', result=elements_result, analysis=analysis)
        except ValueError:
            return render_template('index.html', error="請輸入有效的數字")

    # 顯示目前日期和時辰
    now = datetime.now().strftime('%Y/%m/%d')
    hour, minute = datetime.now().hour, datetime.now().minute
    time_period = current_time_period(hour, minute)
    return render_template('index.html', date=now, time_period=time_period)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
