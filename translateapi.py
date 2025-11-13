import requests
import time

def translate_batch(texts, source_lang, target_lang, batch_size=10, retry_limit=3):
    url = "https://websocket.tahrirchi.uz/handle-batch"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjUzNjYzNjMsImlhdCI6MTc2Mjc3NDM2Mywic3ViIjoiZjk0MTZkNjUtYmUyOC0xMWYwLTkzNGUtMDI0MmFjMTMwMDE4IiwidHNpZCI6IjZlN2JlNjhjLWMxMmUtNDU3Ny1hMzhiLWJhY2JmMzI1MzQ3MiIsInR5cGUiOjB9._3PJR_hy0zB3u8Eow6kbp7MttIppEde0c0IKohxOLMc"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "user-agent": "Mozilla/5.0"
    }

    results = []

    # batchlarga bo‘lish
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]

        for attempt in range(retry_limit):
            try:
                # APIga yuborish: har bir text alohida job
                payload = {
                    "jobs": [{"text": t} for t in batch],
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }

                response = requests.post(url, json=payload, headers=headers, timeout=20)
                if response.status_code == 429:
                    print("⚠️ Juda tez so‘rov! 5 soniya kutyapmiz...")
                    time.sleep(5)
                    continue

                if not response.ok:
                    print("❌ Server xatosi:", response.status_code, response.text)
                    break

                data = response.json()

                # API response 'sentences' formatida keladi
                if isinstance(data, dict) and "sentences" in data:
                    for s in data["sentences"]:
                        translated = s.get("translated", "")
                        results.append(translated)
                elif isinstance(data, dict) and "jobs" in data:
                    # eski format fallback
                    for job in data["jobs"]:
                        results.append(job.get("translated", ""))
                else:
                    results.extend(batch)  # agar tarjima bo‘lmasa originalni qo‘shish
                break

            except requests.RequestException as e:
                print(f"🔁 Tarmoq xatosi, qayta urinayapmiz ({attempt+1}/{retry_limit})...")
                time.sleep(2)

    return results


# # TEST
# texts = [
#     "МЕНЕЖМЕНТ МӘДЕНИЯТИ ҲӘМ УСЫЛЫ",
#     "Халық аралық бизнеске сезилерликтей тәсир көрсететуғын негизги социал-мәдений факторлар мәденият,минез-қулықдин,тил,Клиентлердиң қәлеўлери,Билимлендириў дәрежеси,үрп-әдет ҳәм қадаған етиў,сондай-ақ,сырт ел товарлар ҳәм хызметлерге None",
#     "Халық аралық бизнести жүргизиў жаңа базарларға кириў өз ишине алады.Компаниялар сырт ел қарыйдарлар менен ислеўде ямаса өзлериниң сырт ел филиаллары ушынмаркетингкампаниясын планластырыўда түрли мәдениятларға Салыстырмалы сезгир болыўлары керек.Бизнес басшылары жергиликли базардың исенимлери,қәдириятлары ҳәм үрп-әдетлерди үйрениўден басланыўлары керек.",
#     "Исбилерменлик сөйлесиўлер"
# ]

# result = translate_batch(texts, "kaa_Cyrl", "kaa_Latn")
# print(result)
