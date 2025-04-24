import openai
OPENAI_API_KEY="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"

# API kalitingizni shu yerga yozing
openai.api_key = OPENAI_API_KEY  # Masalan: "sk-..."

def ask_chatgpt(prompt_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Agar GPT-4 sizda mavjud bo‘lmasa, 'gpt-3.5-turbo' ni yozing
        messages=[
            {"role": "system", "content": "Siz foydalanuvchiga yordam beruvchi aqlli yordamchisiz."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message['content']

# Foydalanuvchi so‘rovini yuborish
if __name__ == "__main__":
    while True:
        user_input = input("Savolingizni yozing (chiqish uchun 'exit'): ")
        if user_input.lower() == 'exit':
            break
        javob = ask_chatgpt(user_input)
        print("ChatGPT javobi:\n", javob)
