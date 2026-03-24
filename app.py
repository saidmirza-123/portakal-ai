import os, json
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai

app = Flask(__name__)

# --- AYARLAR ---
# Buraya Google'dan aldığın API anahtarını yaz
API_KEY = "GOOGLE_API_KEY" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

MEMORY_FILE = "portakal_memory.json"

def get_mem():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_q = request.json.get("question")
    memory = get_mem()

    # Önce senin öğrettiğin bilgilere bakar
    for key in memory:
        if key.lower() in user_q.lower():
            return jsonify({"answer": memory[key], "source": "Özel Hafıza"})

    # Yoksa Gemini devreye girer
    try:
        sys_msg = "Senin adın Portakal AI. Mirza tarafından yapıldın. Çok zekisin, 3000 satıra kadar kod yazabilirsin. Cevabın sonunda kaynak belirt."
        response = model.generate_content(sys_msg + user_q)
        
        # Eğer kod isteniyorsa dosyaya yazar
        if "kod" in user_q.lower():
            with open("portakal_uretim.py", "w", encoding="utf-8") as f:
                f.write(response.text)
            return jsonify({"answer": response.text, "file": True})
            
        return jsonify({"answer": response.text, "file": False})
    except:
        return jsonify({"answer": "Şu an internete bağlanamadım!"})

@app.route('/teach', methods=['POST'])
def teach():
    data = request.json
    if data.get("pass") == "admin123":
        m = get_mem()
        m[data["q"]] = data["a"]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail"})

@app.route('/download')
def dl():
    return send_file("portakal_uretim.py", as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
