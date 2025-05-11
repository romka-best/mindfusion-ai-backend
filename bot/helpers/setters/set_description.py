from aiogram import Bot

from bot.locales.types import LanguageCode


async def set_description(bot: Bot):
    await bot.set_my_short_description(
        short_description="""
ChatGPT | Claude | Gemini | Grok | DALL•E | Midjourney | Stable Diffusion | Flux | Suno | Runway | Luma
🛟 @roman_danilov
""",
    )

    await bot.set_my_description(
        description="""
Access to AI:

🔤 Text
• ChatGPT 4 Omni Mini
• ChatGPT 4 Omni
• ChatGPT 4.1 Mini
• ChatGPT 4.1
• ChatGPT o4-mini
• ChatGPT o3
• Claude 3.5 Haiku
• Claude 3.7 Sonnet
• Claude 3 Opus
• Gemini 2 Flash
• Gemini 2.5 Pro
• Gemini 1 Ultra
• Grok 3
• DeepSeek V3
• DeepSeek R1
• Perplexity

📝 Summary
• YouTube
• Video

🖼 Image
• DALL•E
• Midjourney
• Stable Diffusion
• Flux Pro
• Luma Photon
• FaceSwap
• Photoshop AI

🎵 Music
• MusicGen
• Suno

📹 Video
• Kling
• Runway
• Luma Ray
• Pika
""",
    )
    await bot.set_my_description(
        description="""
Доступ к нейросетям:

🔤 Текстовые
• ChatGPT 4 Omni Mini
• ChatGPT 4 Omni
• ChatGPT 4.1 Mini
• ChatGPT 4.1
• ChatGPT o4-mini
• ChatGPT o3
• Claude 3.5 Haiku
• Claude 3.7 Sonnet
• Claude 3 Opus
• Gemini 2 Flash
• Gemini 2.5 Pro
• Gemini 1 Ultra
• Grok 3
• DeepSeek V3
• DeepSeek R1
• Perplexity

📝 Резюме
• YouTube
• Видео

🖼 Графические
• DALL•E
• Midjourney
• Stable Diffusion
• Flux Pro
• Luma Photon
• FaceSwap
• Photoshop AI

🎵 Музыкальные
• MusicGen
• Suno

📹 Видео
• Kling
• Runway
• Luma Ray
• Pika
""",
        language_code=LanguageCode.RU,
    )
    await bot.set_my_description(
        description="""
Acceso a redes neuronales:

🔤 Texto
• ChatGPT 4 Omni Mini
• ChatGPT 4 Omni
• ChatGPT 4.1 Mini
• ChatGPT 4.1
• ChatGPT o4-mini
• ChatGPT o3
• Claude 3.5 Haiku
• Claude 3.7 Sonnet
• Claude 3 Opus
• Gemini 2 Flash
• Gemini 2.5 Pro
• Gemini 1 Ultra
• Grok 3
• DeepSeek V3
• DeepSeek R1
• Perplexity

📝 Resúmenes
• YouTube
• Video

🖼 Gráficos
• DALL•E
• Midjourney
• Stable Diffusion
• Flux Pro
• Luma Photon
• FaceSwap
• Photoshop IA

🎵 Música
• MusicGen
• Suno

📹 Video
• Kling
• Runway
• Luma Ray
• Pika
""",
        language_code=LanguageCode.ES,
    )
    await bot.set_my_description(
        description="""
AI मॉडल्स तक पहुंच:

🔤 टेक्स्ट जनरेशन
• ChatGPT 4 Omni Mini
• ChatGPT 4 Omni
• ChatGPT 4.1 Mini
• ChatGPT 4.1
• ChatGPT o4-mini
• ChatGPT o3
• Claude 3.5 Haiku
• Claude 3.7 Sonnet
• Claude 3 Opus
• Gemini 2 Flash
• Gemini 2.5 Pro
• Gemini 1 Ultra
• Grok 3
• DeepSeek V3
• DeepSeek R1
• Perplexity

📝 सारांश
• YouTube
• वीडियो

🖼 ग्राफ़िक्स
• DALL•E
• Midjourney
• Stable Diffusion
• Flux Pro
• Luma Photon
• FaceSwap
• Photoshop AI

🎵 म्यूज़िक
• MusicGen
• Suno

📹 वीडियो
• Kling
• Runway
• Luma Ray
• Pika
""",
        language_code=LanguageCode.HI,
    )
