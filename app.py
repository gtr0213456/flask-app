from flask import Flask, render_template, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'some_secret_key'

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

def current_time_period():
    """根據目前時間回傳時辰和陰陽"""
    now = datetime.now()
    hour, minute = now.hour, now.minute

    # 判斷陰陽(早晚)
    yin_yang = "陽早" if minute <= 60 else "陰晚"

    # 對應時辰
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not check_limits():
            return render_template('index.html', error="今日使用次數已達上限，請明天再試。")

        if 'heavenly_union' in request.form:
            result = get_elements(12, datetime.now().month, datetime.now().day)
            return render_template('index.html', result=result)

        try:
            n1 = normalize_number(request.form['n1'] or 1)
            n2 = normalize_number(request.form['n2'] or 1)
            n3 = normalize_number(request.form['n3'] or 1)
            result = get_elements(n1, n2, n3)
            return render_template('index.html', result=result)
        except ValueError:
            return render_template('index.html', error="請輸入有效的數字")

    # 顯示目前日期和時辰
    now = datetime.now().strftime('%Y/%m/%d')
    time_period = current_time_period()
    return render_template('index.html', date=now, time_period=time_period)

if __name__ == '__main__':
    app.run(debug=True)
