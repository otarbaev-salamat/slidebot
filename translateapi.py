import requests




def translate(text,source_lang,target_lang):
    url = "https://websocket.tahrirchi.uz/handle-batch"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjUzNjYzNjMsImlhdCI6MTc2Mjc3NDM2Mywic3ViIjoiZjk0MTZkNjUtYmUyOC0xMWYwLTkzNGUtMDI0MmFjMTMwMDE4IiwidHNpZCI6IjZlN2JlNjhjLWMxMmUtNDU3Ny1hMzhiLWJhY2JmMzI1MzQ3MiIsInR5cGUiOjB9._3PJR_hy0zB3u8Eow6kbp7MttIppEde0c0IKohxOLMc"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }
    payload = {
        "jobs":[{
            "text":f"{text}",
            }],
        "source_lang":f"{source_lang}", # rus_Cyrl, eng_Latn, uzn_Latn, uzn_Cyrl, kaa_Latn, kaa_Cyrl
        "target_lang":f"{target_lang}", 
    }


    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.ok:
            try:
                data = response.json()
            except ValueError:
                data = response.text
            return data
        else:
            print("Server xatosi:", response.status_code)
            print("Javob matni:", response.text)

    except requests.Timeout:
        print("So'rov timeout qilindi (kutish vaqti tugadi).")
    except requests.ConnectionError:
        print("Tarmoqqa ulanishda xato yuz berdi.")
    except requests.RequestException as e:
        print("Requests xatosi:", str(e))



#print(translate('salom','uzn_Latn','kaa_Latn'))