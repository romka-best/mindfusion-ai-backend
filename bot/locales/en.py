import random
from typing import Union

from bot.database.models.product import Product, ProductCategory, ProductType
from bot.database.models.prompt import Prompt
from bot.database.operations.product.getters import get_product
from bot.helpers.formatters.format_number import format_number
from bot.helpers.getters.get_model_version import get_model_version
from bot.helpers.getters.get_time_until_limit_update import get_time_until_limit_update
from bot.helpers.getters.get_user_discount import get_user_discount
from bot.locales.texts import Texts
from bot.database.models.common import (
    Currency,
    Quota,
    Model,
    ModelType,
    VideoSummaryFocus,
    VideoSummaryFormat,
    VideoSummaryAmount,
    AspectRatio,
    SendType,
)
from bot.database.models.subscription import SubscriptionStatus
from bot.database.models.user import UserSettings
from bot.locales.types import LanguageCode


class English(Texts):
    # Action
    ACTION_BACK = "◀️ Back"
    ACTION_CLOSE = "🚪 Close"
    ACTION_CANCEL = "❌ Cancel"
    ACTION_APPROVE = "✅ Approve"
    ACTION_DENY = "❌ Deny"
    ACTION_TO_OTHER_MODELS = "To Other Models ◀️"
    ACTION_TO_OTHER_TYPE_MODELS = "To Other Models Type ◀️"

    # Additional Bot
    @staticmethod
    def additional_bot_info(link: str) -> str:
        return f"""
👋 <b>Hi there!</b>

⚠️ <b>This bot does not process requests. It only redirects you to our main AI assistant</b>

🏆 Our mission is to provide everyone with access to the best AI models

👉 {link}
"""

    # Bonus
    @staticmethod
    def bonus_info(balance: int) -> str:
        return f"""
🎁 <b>Bonus Balance</b>

💰 Current Balance: <b>{int(balance)} credits</b> 🪙

💡 <b>How to Use It:</b>
• Requests in any AI models
• Access to digital employees
• Voice responses/requests
• Quick, pause-free answers

Choose an action 👇
"""

    BONUS_EARN = "➕ Earn"
    BONUS_SPEND = "➖ Spend"

    @staticmethod
    def bonus_info_earn(user_id: str, referred_count: int, feedback_count: int, play_count: int):
        return f"""
➕ <b>How to Earn Credits</b>

👥 <i>Invite Friends:</i>
• <b>+25 credits</b> for you and your friend
• Invitation link:
{Texts.bonus_referral_link(user_id, False)}
• You've invited: {referred_count}

💭 <i>Leave Feedback:</i>
• <b>+25 credits</b> for a review
• You've left: {feedback_count}

🎮 <i>Try Your Luck:</i>
• <b>+1-100 credits</b> per win
• You've played times: {play_count}

Choose an action 👇
"""

    @staticmethod
    def bonus_info_spend(balance: int):
        return f"""
💰 Current Balance: <b>{int(balance)} credits</b> 🪙

Choose how to <b>spend your credits:</b> 👇
"""

    BONUS_ACTIVATED_SUCCESSFUL = """
🌟 <b>Bonus Activated!</b>

You've successfully purchased the packages 🚀
"""
    BONUS_INVITE_FRIEND = "👥 Invite a friend"
    BONUS_REFERRAL_SUCCESS = """
🌟 <b>Your Referral Magic Worked!</b>

Your balance and your friend's balance have increased by <b>25 credits</b> 🪙
"""
    BONUS_REFERRAL_LIMIT_ERROR = """
🌟 <b>Your Referral Magic Worked!</b>

Unfortunately, I cannot credit your reward because the limit has been exceeded
"""
    BONUS_LEAVE_FEEDBACK = "📡 Leave a feedback"
    BONUS_CASH_OUT = "🛍 Cash out credits"
    BONUS_PLAY = "🎮 Play"
    BONUS_PLAY_GAME = "🎮 Try my luck"
    BONUS_PLAY_GAME_CHOOSE = """
🎮 <b>Choose a Game</b>

👉 <i>You only have one attempt per day</i>
"""
    BONUS_PLAY_BOWLING_GAME = "🎳 Bowling"
    BONUS_PLAY_BOWLING_GAME_INFO = """
🎳 <b>Bowling</b>

Tap <b>“Play”</b>, and I'll instantly roll the ball into the pins! The chance of winning is <b>100%</b>

The number of pins knocked down equals the number of credits you win: <b>1-6</b>
"""
    BONUS_PLAY_SOCCER_GAME = "⚽️ Play soccer"
    BONUS_PLAY_SOCCER_GAME_INFO = """
⚽️ <b>Soccer</b>

Tap <b>“Play”</b>, and I’ll kick the ball into the goal! The chance of scoring and winning credits is <b>60%</b>

If I score, you’ll receive <b>5 credits</b>
"""
    BONUS_PLAY_BASKETBALL_GAME = "🏀 Basketball"
    BONUS_PLAY_BASKETBALL_GAME_INFO = """
🏀 <b>Basketball</b>

Tap <b>“Play”</b>, and I’ll shoot the ball into the basketball hoop! The chance of making a perfect shot is <b>40%</b>

If I score, you’ll receive <b>10 credits</b>
"""
    BONUS_PLAY_DARTS_GAME = "🎯 Darts"
    BONUS_PLAY_DARTS_GAME_INFO = """
🎯 <b>Darts</b>

Tap <b>“Play”</b>, and I’ll throw a dart at the target! The chance of hitting the bullseye is <b>~16.67%</b>

If I hit the bullseye, you’ll receive <b>15 credits</b>
"""
    BONUS_PLAY_DICE_GAME = "🎲 Dice"
    BONUS_PLAY_DICE_GAME_INFO = """
🎲 <b>Dice</b>

Choose a number from 1 to 6, and I’ll roll the dice! The odds of winning are <b>1 in 6</b>

If you guess the number correctly, you’ll receive <b>20 credits</b>
"""
    BONUS_PLAY_CASINO_GAME = "🎰 Casino"
    BONUS_PLAY_CASINO_GAME_INFO = """
🎰 <b>Casino</b>

Tap <b>“Play”</b>, and I’ll spin the casino reels. The chance of hitting three identical numbers is nearly <b>5%</b>, while the chance of landing three sevens is slightly over <b>1%</b>

• If three identical numbers appear, you’ll receive <b>50 credits</b>
• If three sevens appear, you’ll receive <b>100 credits</b>
"""
    BONUS_PLAY_GAME_WON = """
🎉 <b>You Won!</b>

Come back tomorrow for more victories 💪
"""
    BONUS_PLAY_GAME_LOST = """
😔 <b>No Luck Today...</b>

Try again tomorrow—luck might be on your side! 🍀
"""

    @staticmethod
    def bonus_play_game_reached_limit():
        hours, minutes = get_time_until_limit_update(hours=0)
        return f"""
⏳ <b>You’ve Already Played Today!</b>

Come back in <i>{hours} h. {minutes} min.</i> and show me what you’ve got! 👏
"""

    # Catalog
    CATALOG_INFO = """
📁 <b>Catalog of Possibilities</b>

Select the desired section and press the button 👇
"""
    CATALOG_MANAGE = "🎭 Manage Catalog"
    CATALOG_DIGITAL_EMPLOYEES = "🎭 Roles"
    CATALOG_DIGITAL_EMPLOYEES_INFO = """
🎭 <b>Role Catalog</b>

Select a digital employee below 👇
"""
    CATALOG_DIGITAL_EMPLOYEES_FORBIDDEN_ERROR = """
🔒 <b>You’ve Entered the VIP Zone!</b>

You currently don’t have access to digital employees

You can gain access by clicking the button below:
"""
    CATALOG_PROMPTS = "📚 Prompts"
    CATALOG_PROMPTS_CHOOSE_MODEL_TYPE = """
📚 <b>Prompt Catalog</b>

Select the desired <b>model type</b> by clicking the button below 👇
"""
    CATALOG_PROMPTS_CHOOSE_CATEGORY = """
📚 <b>Prompt Catalog</b>

Select the desired <b>category</b> by clicking the button below 👇
"""
    CATALOG_PROMPTS_CHOOSE_SUBCATEGORY = """
📚 <b>Prompt Catalog</b>

Select the desired <b>subcategory</b> by clicking the button below 👇
"""

    @staticmethod
    def catalog_prompts_choose_prompt(prompts: list[Prompt]):
        prompt_info = ''
        for index, prompt in enumerate(prompts):
            is_last = index == len(prompts) - 1
            right_part = '\n' if not is_last else ''
            prompt_info += f'<b>{index + 1}</b>: {prompt.names.get(LanguageCode.EN)}{right_part}'

        return f"""
📚 <b>Prompt Catalog</b>

Prompts:
{prompt_info}

To get the full prompt, select the <b>prompt number</b> by clicking the button below 👇
"""

    @staticmethod
    def catalog_prompts_info_prompt(prompt: Prompt, products: list[Product]):
        model_info = ''
        for index, product in enumerate(products):
            is_last = index == len(products) - 1
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            model_info += f'    {left_part} <b>{product.names.get(LanguageCode.EN)}</b>{right_part}'

        return f"""
📚 <b>Prompt Catalog</b>

You selected the prompt: <b>{prompt.names.get(LanguageCode.EN)}</b>

This prompt is suitable for models:
{model_info}

Choose an action below 👇
"""

    @staticmethod
    def catalog_prompts_examples(products: list[Product]):
        prompt_examples_info = ''
        for index, product in enumerate(products):
            is_last = index == len(products) - 1
            is_first = index == 0
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            prompt_examples_info += f'{left_part if not is_first else "┏"} <b>{index + 1}</b>: {product.names.get(LanguageCode.EN)}{right_part}'

        return prompt_examples_info

    CATALOG_PROMPTS_GET_SHORT_PROMPT = "Get Short Prompt ⚡️"
    CATALOG_PROMPTS_GET_LONG_PROMPT = "Get Long Prompt 📜"
    CATALOG_PROMPTS_GET_EXAMPLES = "Get Prompt Results 👀"
    CATALOG_PROMPTS_COPY = "Copy Prompt 📋"

    # Chats
    @staticmethod
    def chat_info(current_chat_name: str, total_chats: int) -> str:
        return f"""
🗨️ <b>Current Chat: {current_chat_name}</b>

📈 Total Chats: <b>{total_chats}</b>

Choose an action below 👇
"""

    CHAT_DEFAULT_TITLE = "New chat"
    CHAT_MANAGE = "💬 Manage Chats"
    CHAT_CREATE = "💬 Create"
    CHAT_CREATE_SUCCESS = """
🎉 <b>Chat Created!</b>

You can switch to it in /settings
"""
    CHAT_TYPE_TITLE = "Type your chat title"
    CHAT_SWITCH = "🔄 Switch"
    CHAT_SWITCH_FORBIDDEN_ERROR = """
🚨 <b>Wait!</b>

You are currently in your only chat

Create a new one to switch between chats
"""
    CHAT_SWITCH_SUCCESS = "Chat successfully switched 🎉"
    CHAT_RESET = "♻️ Reset"
    CHAT_RESET_WARNING = """
🧹 <b>Chat Cleanup Ahead!</b>

You’re about to delete all messages and clear the context of the current chat

Are you sure you want to proceed?
"""
    CHAT_RESET_SUCCESS = """
🧹 <b>Chat Successfully Cleared!</b>

Now I’m like a goldfish—I don’t remember anything that was said before 🐠
"""
    CHAT_DELETE = "🗑 Delete"
    CHAT_DELETE_FORBIDDEN_ERROR = """
🚨 <b>Wait!</b>

This is your only chat, it cannot be deleted
"""
    CHAT_DELETE_SUCCESS = "Chat successfully deleted 🎉"

    # Eightify
    EIGHTIFY_INFO = """
👀 Using <b>YouTube Summary</b> you can get a concise text summary of any YouTube video

<b>How does it work?</b>
🔗 Send me the link to the YouTube video you need
✅ I'll analyze the video and provide you with a text summary

Looking forward to your link! 😊
"""
    EIGHTIFY_VALUE_ERROR = """
🧐 <b>This Doesn’t Look Like a YouTube Link</b>

Please <b>send a different link</b>
"""
    EIGHTIFY_VIDEO_ERROR = """
😢 Unfortunately, I <b>cannot process</b> this YouTube video

Please <b>send a different link</b>
"""

    # Errors
    ERROR = """
🤒 <b>I've got an unknown error</b>

Please try again or contact my tech support:
"""
    ERROR_NETWORK = """
🤒 <b>I lost my connection with Telegram</b>

Please try again or contact my tech support:
"""
    ERROR_PROMPT_REQUIRED = """
🚨 <b>Hold on! Where's the prompt?</b>

A request without a prompt is like tea without sugar—completely flavorless ☕️

Write something—and the magic will begin 🪄
"""
    ERROR_PROMPT_TOO_LONG = """
🚨 <b>Whoa! That’s Not a Prompt, That’s a Whole Novel!</b>

Try shortening the text — otherwise, the model might take a vacation 🌴

Waiting for a new, more compact prompt ✨
"""
    ERROR_REQUEST_FORBIDDEN = """
🚨 <b>Oops! Your Request Didn’t Pass the Check</b>

My safety guard detected something suspicious 🛑

Please review the text/photo for prohibited content and try again 😌
"""
    ERROR_PHOTO_FORBIDDEN = """
⚠️ <b>Sending photos is only available in models:</b>

🔤 <b>Text Models</b>:
    ┣ ChatGPT 4.0 Omni Mini ✉️
    ┣ ChatGPT 4.0 Omni 💥
    ┣ ChatGPT o1 🧪
    ┣ Claude 3.7 Sonnet 💫
    ┣ Claude 3.0 Opus 🚀
    ┣ Gemini 1.5 Flash 🏎
    ┣ Gemini 2.5 Pro 💼
    ┣ Gemini 1.0 Ultra 🛡️
    ┗ Grok 2.0 🐦

🖼 <b>Image Models</b>:
    ┣ 🎨 Midjourney
    ┣ 🦄 Stable Diffusion XL
    ┣ 🧑‍🚀 Stable Diffusion 3.5
    ┣ 🌲 Flux 1.0 Dev
    ┣ 🏔 Flux 1.1 Pro
    ┣ 🌌 Luma Photon
    ┣ 📷 FaceSwap
    ┗ 🪄 Photoshop AI

📹 <b>Video Models</b>:
    ┣ 🎬 Kling
    ┣ 🎥 Runway
    ┣ 🔆 Luma Ray
    ┗ 🐇 Pika

To switch to a model with image reading support, use the button below 👇
"""
    ERROR_PHOTO_REQUIRED = """
⚠️ <b>A Photo Is Required in This Model</b>

Please send a photo along with your prompt
"""
    ERROR_ALBUM_FORBIDDEN = """
⚠️ <b>In the Current Model, I Can’t Process Multiple Photos at Once</b>

Please send only one photo
"""
    ERROR_VIDEO_FORBIDDEN = "⚠️ I don’t know how to work with videos in this AI model yet"
    ERROR_DOCUMENT_FORBIDDEN = "⚠️ I don’t know how to work with such documents yet"
    ERROR_STICKER_FORBIDDEN = "⚠️ I don’t know how to work with stickers yet"
    ERROR_SERVER_OVERLOADED = """
🫨 <b>The Server Is Under Heavy Load Right Now</b>

Please try again or wait a little while
"""
    ERROR_FILE_TOO_BIG = """
🚧 <b>The File Is Too Large!</b>

I can only process files smaller than 20MB

Please try again with a smaller file 😉
"""
    ERROR_IS_NOT_NUMBER = """
🚧 <b>That’s Not a Number!</b>

Please try again with a numeric value 🔢
"""

    @staticmethod
    def error_aspect_ratio_invalid(
        min_ratio: str,
        max_ratio: str,
        actual_ratio: str,
    ) -> str:
        return f"""
⚠️ <b>Invalid Image Aspect Ratio</b>

The image's width-to-height ratio must be between {min_ratio} and {max_ratio}.
Your image's aspect ratio is {actual_ratio}.

Please try again with a different image 😉
"""

    @staticmethod
    def error_internal_ai_model(ai_model_name) -> str:
        return f"⚠️ An error occurred on the {ai_model_name} side. Please try again later."

    # Examples
    EXAMPLE_INFO = "To gain access to this AI model, click the button below:"

    @staticmethod
    def example_text_model(model: str):
        return f"👇 This is how *{model}* would respond to your request"

    @staticmethod
    def example_image_model(model: str):
        return f"☝️ This how <b>{model}</b> would draw for your request"

    # FaceSwap
    FACE_SWAP_INFO = """
📷 <b>FaceSwap: Choose one of the 3 options</b>

👤 Send a photo — I will swap the face on your image

✍️ Write a prompt — I will create an image with your face based on the description

🤹‍♂️ Choose a ready-made package — I will swap faces on pre-made images
"""
    FACE_SWAP_CHOOSE_PHOTO = "👤 Send Photo"
    FACE_SWAP_CHOOSE_PHOTO_INFO = """
👤 <b>Send a photo</b>

1️⃣ Upload a photo where your face is clearly visible
2️⃣ I will swap the face in your photo while keeping the rest unchanged

💡 The better the quality, the better the result!
"""
    FACE_SWAP_CHOOSE_PROMPT = "✍️ Write Prompt"
    FACE_SWAP_CHOOSE_PROMPT_INFO = """
✍️ <b>Write a prompt</b>

1️⃣ Describe in detail the image you want to generate
2️⃣ I will create an image with your face based on your description

💡 The more details you provide, the better the result!
"""
    FACE_SWAP_CHOOSE_PACKAGE = "🤹‍♂️ Choose Package"
    FACE_SWAP_CHOOSE_PACKAGE_INFO = """
🤹‍♂️ <b>Choose a package</b>

1️⃣ Select one of the ready-made image sets
2️⃣ I will swap faces on all the images at once

💡 Quick and easy!
"""
    FACE_SWAP_GENERATIONS_IN_PACKAGES_ENDED = """
📷 <b>Wow! All Generations in the Packages Have Been Used!</b>

<b>What’s Next?</b>
👤 Send a photo with a face — I’ll swap it with yours
✍️ Write a prompt — I’ll create an image with your likeness
"""
    FACE_SWAP_MIN_ERROR = """
🤨 <b>Hold On!</b>

You’re trying to request less than 1 image — that won’t work

<b>Type a number greater than 0</b>
"""
    FACE_SWAP_MAX_ERROR = """
🤨 <b>Hold On!</b>

You’re requesting more images than we have available

<b>Type a smaller number</b>
"""
    FACE_SWAP_NO_FACE_FOUND_ERROR = """
🚫 <b>Photo Processing Issue</b>

Unfortunately, I couldn’t detect a face in the photo. Please upload a new photo in good quality where your face is clearly visible

After uploading a new photo, try again 🔄
"""

    @staticmethod
    def face_swap_choose_package(name: str, available_images: int, total_images: int, used_images: int) -> str:
        remain_images = total_images - used_images
        footer_text = f'<b>Type how many face swaps you want to do, or choose from the quick selection buttons below</b> 👇' if remain_images > 0 else ''

        return f"""
<b>{name}</b>

The package includes: <b>{total_images} images</b>

🌠 <b>Available Generations</b>: {available_images} images
<i>If you need more, check out /buy or /bonus</i>

🔍 <b>Used</b>: {used_images} images
🚀 <b>Remaining</b>: {remain_images} images

{footer_text}
"""

    @staticmethod
    def face_swap_package_forbidden_error(available_images: int) -> str:
        return f"""
🚧 <b>Not Enough Generations!</b>

You only have <b>{available_images} generations</b> left in your arsenal

💡 <b>Tip:</b> Try a smaller number, or use /buy for unlimited possibilities!
"""

    # Feedback
    FEEDBACK_INFO = """
📡 <b>Feedback</b>

Help me improve — share your thoughts:
• <b>What do you like?</b> Let me know
• <b>Have any suggestions?</b> Share them
• <b>Encountered any issues?</b> Report them

I’m looking forward to your feedback 💌
"""
    FEEDBACK_SUCCESS = """
🌟 <b>Feedback Received!</b>

Your opinion is the secret ingredient to success. I’m already cooking up improvements 🍳

You’ll receive <b>25 credits</b> once my creators review the feedback content
"""
    FEEDBACK_APPROVED = """
🌟 <b>Feedback Approved!</b>

Thank you for helping me improve

Your reward: <b>+25 credits</b> 🪙
"""
    FEEDBACK_APPROVED_WITH_LIMIT_ERROR = """
🌟 <b>Feedback Approved!</b>

Thank you for helping me improve

Unfortunately, I cannot credit your reward because the limit has been exceeded
"""
    FEEDBACK_DENIED = """
🌟 <b>Feedback Denied!</b>

Your feedback was not constructive enough, and I cannot increase your bonus balance 😢
"""

    # Flux
    FLUX_STRICT_SAFETY_TOLERANCE = "🔒 Strict"
    FLUX_MIDDLE_SAFETY_TOLERANCE = "🔏 Average"
    FLUX_PERMISSIVE_SAFETY_TOLERANCE = "🔓 Weak"

    # Gemini Video
    GEMINI_VIDEO = '📼 Video Summary'
    GEMINI_VIDEO_INFO = """
📼 With <b>Video Summary</b>, you can get a concise text summary of any video

<b>How does it work?</b> There are 2 options:
1.
🔗 Send a link to the desired video
⚠️ The video must be no longer than 1 hour
✅ I’ll analyze the video and return a text summary to you

2.
🔗 Send the video directly here in Telegram
⚠️ The video must be no longer than 1 hour and smaller than 20MB
✅ I’ll analyze the video and return a text summary to you

Looking forward to your link/video 😊
"""
    GEMINI_VIDEO_TOO_LONG_ERROR = """
⚠️ <b>The Video Length Must Be Less Than 60 Minutes</b>

Please <b>send a different video</b>
"""
    GEMINI_VIDEO_VALUE_ERROR = """
⚠️ <b>This Doesn’t Look Like a Video Link</b>

Please <b>send a different link</b>
"""

    @staticmethod
    def gemini_video_prompt(
        focus: VideoSummaryFocus,
        format: VideoSummaryFormat,
        amount: VideoSummaryAmount,
    ) -> str:
        if focus == VideoSummaryFocus.INSIGHTFUL:
            focus = English.VIDEO_SUMMARY_FOCUS_INSIGHTFUL
        elif focus == VideoSummaryFocus.FUNNY:
            focus = English.VIDEO_SUMMARY_FOCUS_FUNNY
        elif focus == VideoSummaryFocus.ACTIONABLE:
            focus = English.VIDEO_SUMMARY_FOCUS_ACTIONABLE
        elif focus == VideoSummaryFocus.CONTROVERSIAL:
            focus = English.VIDEO_SUMMARY_FOCUS_CONTROVERSIAL

        if format == VideoSummaryFormat.LIST:
            format = "1. <Emoji> Description"
        elif format == VideoSummaryFormat.FAQ:
            format = "❔ _Question_: <Question>\n❕ _Answer_: <Answer>"

        if amount == VideoSummaryAmount.AUTO:
            amount = English.VIDEO_SUMMARY_AMOUNT_AUTO
        elif amount == VideoSummaryAmount.SHORT:
            amount = English.VIDEO_SUMMARY_AMOUNT_SHORT
        elif amount == VideoSummaryAmount.DETAILED:
            amount = English.VIDEO_SUMMARY_AMOUNT_DETAILED

        return f"""
Please create a beautiful and structured summary of the provided video using Markdown formatting as follows:
- Divide the summary into thematic blocks in the format: **<Emoji> Title of Thematic Block**.
- For each block, include several key points in the format: {format}.
- Conclude each point with a clear and informative statement.
- Avoid using the "-" symbol for structure.
- Avoid using HTML tags.
- Highlight key words in the format: **Key Words**.
- Construct the summary to be engaging, visually appealing, and well-structured.
- Summary focus: {focus}.
- Response length: {amount}. Where Short: 2-3 thematic blocks. Auto: 4-5 thematic blocks. Detailed: 6-10 thematic blocks. Thematic blocks refer to blocks with headings, not individual points, but the number of points may also depend on the response length.
- Provide the response in English.

Use unique emojis to represent the essence of each point. The response should look visually appealing and strictly follow the specified format, without introductory phrases or comments.
"""

    # Gender
    GENDER_CHOOSE = "🚹🚺 Choose Gender"
    GENDER_CHANGE = "🚹🚺 Change Gender"
    GENDER_UNSPECIFIED = "🤷 Unspecified"
    GENDER_MALE = "👕 Male"
    GENDER_FEMALE = "👚 Female"

    # Generation
    GENERATION_IMAGE_SUCCESS = "✨ Here's your image creation 🎨"
    GENERATION_VIDEO_SUCCESS = "✨ Here's your video creation 🎞"

    # Help
    HELP_INFO = """
🛟 <b>Help and Commands</b>

─────────────

👋 <b>General Commands:</b>
/start — About Me
/profile — Your Profile
/language — Change Language
/buy — Purchase Subscription/Packages
/bonus — Learn About Bonuses
/promo_code — Activate Promo Code
/feedback — Leave Feedback
/terms — ToS

─────────────

🤖 <b>AI:</b>
/model — Select AI Model
/info — Learn About AI Models
/catalog — Roles and Prompts Catalog
/settings — Configure Models

─────────────

🔤 <b>Text Models:</b>
/chatgpt — Select ChatGPT
/claude — Select Claude
/gemini — Select Gemini
/grok — Select Grok
/perplexity — Select Perplexity

─────────────

📝 <b>Summary Models:</b>
/youtube_summary — Select YouTube Summary
/video_summary — Select Video Summary

─────────────

🖼 <b>Image Models:</b>
/dalle — Select DALL-E
/midjourney — Select MidJourney
/stable_diffusion — Select Stable Diffusion
/flux — Select Flux
/luma_photon — Select Luma Photon
/recraft — Select Recraft
/face_swap — Select FaceSwap
/photoshop — Select Photoshop AI

─────────────

🎵 <b>Music Models:</b>
/music_gen — Select MusicGen
/suno — Select Suno

─────────────

📹 <b>Video Models:</b>
/kling — Select Kling
/runway — Select Runway
/luma_ray — Select Luma Ray
/pika — Select Pika

─────────────

For any questions, you can also contact technical support:
"""

    # Info
    INFO = "🤖 <b>Select the models type you want to get information about:</b>"
    INFO_TEXT_MODELS = "🤖 <b>Select the Text model you want to get information about:</b>"
    INFO_IMAGE_MODELS = "🤖 <b>Select the Image model you want to get information about:</b>"
    INFO_MUSIC_MODELS = "🤖 <b>Select the Music model you want to get information about:</b>"
    INFO_VIDEO_MODELS = "🤖 <b>Select the Video model you want to get information about:</b>"
    INFO_CHAT_GPT = "🤖 <b>Select the ChatGPT model</b> you want to learn more about:"
    INFO_CHAT_GPT_4_OMNI_MINI = f"""
<b>{Texts.CHAT_GPT_4_OMNI_MINI}</b>

<b>Creator:</b> OpenAI

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: Above average 🟢
• Response Speed: High 🟢

📊 <b>Benchmarks:</b>
• MMLU: 82.0%
• GPQA: 40.2%
• DROP: 79.7%
• MGSM: 87.0%
• MATH: 70.2%
• HumanEval: 87.2%
• MMMU: 59.4%
• MathVista: 56.7%
"""
    INFO_CHAT_GPT_4_OMNI = f"""
<b>{Texts.CHAT_GPT_4_OMNI}</b>

<b>Creator:</b> OpenAI

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: High 🟢
• Response Speed: Above average 🟢

📊 <b>Benchmarks:</b>
• MMLU: 88.7%
• GPQA: 53.6%
• DROP: 83.4%
• MGSM: 90.5%
• MATH: 76.6%
• HumanEval: 90.2%
• MMMU: 69.1%
• MathVista: 63.8%
"""
    INFO_CHAT_GPT_O_3_MINI = f"""
<b>{Texts.CHAT_GPT_O_3_MINI}</b>

<b>Creator:</b> OpenAI

💡 <b>Use Cases:</b>
• Content generation
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance

🚦 <b>Ratings:</b>
• Vision: No 🔴
• Answer Quality: High 🟢
• Response Speed: Moderate 🟡

📊 <b>Benchmarks:</b>
• MMLU: 86.9%
• GPQA: 79.7%
• MATH: 97.9%
• HumanEval: 92.4%
"""
    INFO_CHAT_GPT_O_1 = f"""
<b>{Texts.CHAT_GPT_O_1}</b>

<b>Creator:</b> OpenAI

💡 <b>Use Cases:</b>
• Content generation
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: High 🟢
• Response Speed: Moderate 🟡

📊 <b>Benchmarks:</b>
• MMLU: 92.3%
• GPQA: 75.7%
• MGSM: 89.3%
• MATH: 96.4%
• HumanEval: 92.4%
• MMMU: 78.2%
• MathVista: 73.9%
"""
    INFO_CLAUDE = "🤖 <b>Select the Claude model</b> you want to learn more about:"
    INFO_CLAUDE_3_HAIKU = f"""
<b>{Texts.CLAUDE_3_HAIKU}</b>

<b>Creator:</b> Anthropic

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: No 🔴
• Answer Quality: Above average 🟢
• Response Speed: High 🟢

📊 <b>Benchmarks:</b>
• MMLU: 80.9%
• GPQA: 41.6%
• DROP: 83.1%
• MGSM: 85.6%
• MATH: 69.2%
• HumanEval: 88.1%
"""
    INFO_CLAUDE_3_SONNET = f"""
<b>{Texts.CLAUDE_3_SONNET}</b>

<b>Creator:</b> Anthropic

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: High 🟢
• Response Speed: Above average 🟢

📊 <b>Benchmarks:</b>
• MMLU: 90.5%
• GPQA: 65.0%
• DROP: 88.3%
• MGSM: 92.5%
• MATH: 78.3%
• HumanEval: 93.7%
• MMMU: 70.4%
• MathVista: 70.7%
"""
    INFO_CLAUDE_3_OPUS = f"""
<b>{Texts.CLAUDE_3_OPUS}</b>

<b>Creator:</b> Anthropic

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: Above average 🟢
• Response Speed: Moderate 🟡

📊 <b>Benchmarks:</b>
• MMLU: 88.2%
• GPQA: 50.4%
• DROP: 83.1%
• MGSM: 90.7%
• MATH: 60.1%
• HumanEval: 84.9%
• MMMU: 59.4%
• MathVista: 50.5%
"""
    INFO_GEMINI = "🤖 <b>Select the Gemini model</b> you want to learn more about:"
    INFO_GEMINI_2_FLASH = f"""
<b>{Texts.GEMINI_2_FLASH}</b>

<b>Creator:</b> Google

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: Above average 🟢
• Response Speed: High 🟢

📊 <b>Benchmarks:</b>
• MMLU: 76.4%
• GPQA: 62.1%
• MATH: 89.7%
• MMMU: 70.7%
"""
    INFO_GEMINI_2_PRO = f"""
<b>{Texts.GEMINI_2_PRO}</b>

<b>Creator:</b> Google

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copywriting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: High 🟢
• Response Speed: Moderate 🟡

📊 <b>Benchmarks:</b>
• MMLU: 75.8%
• GPQA: 59.1%
• MATH: 86.5%
• MMMU: 65.9%
"""
    INFO_GEMINI_1_ULTRA = f"""
<b>{Texts.GEMINI_1_ULTRA}</b>

<b>Creator:</b> Google

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copywriting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: High 🟢
• Response Speed: Moderate 🟡

📊 <b>Benchmarks:</b>
• MMLU: 90.0%
• DROP: 82.4%
• HumanEval: 74.4%
• MATH: 53.2%
• MMMU: 59.4%
"""
    INFO_GROK = f"""
<b>{Texts.GROK}</b>

<b>Creator:</b> X (Twitter)

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copywriting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: Yes 🟢
• Answer Quality: High 🟢
• Response Speed: Above average 🟢

📊 <b>Benchmarks:</b>
• MMLU: 87.5%
• GPQA: 56.0%
• MATH: 76.1%
• HumanEval: 88.4%
• MMMU: 66.1%
• MathVista: 69.0%
"""
    INFO_DEEP_SEEK = "🤖 <b>Select the DeepSeek model</b> you want to learn more about:"
    INFO_DEEP_SEEK_V3 = f"""
<b>{Texts.DEEP_SEEK_V3}</b>

<b>Creator:</b> DeepSeek

💡 <b>Use Cases:</b>
• Content generation
• Idea generation
• Copyrighting
• Communication and support
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance
• Recommendations

🚦 <b>Ratings:</b>
• Vision: No 🔴
• Answer Quality: Above average 🟢
• Response Speed: High 🟢

📊 <b>Benchmarks:</b>
• MMLU: 88.5%
• GPQA: 59.1%
• DROP: 91.6%
• MGSM: 79.8%
• MATH: 90.2%
• HumanEval: 82.6%
"""
    INFO_DEEP_SEEK_R1 = f"""
<b>{Texts.DEEP_SEEK_R1}</b>

<b>Creator:</b> DeepSeek

💡 <b>Use Cases:</b>
• Content generation
• Explaining complex concepts
• Answering questions
• Translating between languages
• Learning assistance
• Problem-solving
• Text processing
• Coding assistance

🚦 <b>Ratings:</b>
• Vision: No 🔴
• Answer Quality: High 🟢
• Response Speed: Below Average 🟠

📊 <b>Benchmarks:</b>
• MMLU: 90.8%
• GPQA: 71.5%
• DROP: 92.2%
• MATH: 97.3%
"""
    INFO_PERPLEXITY = f"""
<b>{Texts.PERPLEXITY}</b>

💡 <b>Use Cases:</b>
• Searching for real-time information
• Answering questions requiring recent data
• Monitoring current events
• Finding sources for information verification
• Comparing data from different sources
• Assisting in writing academic papers with up-to-date data
• Finding links to studies, reports, and statistics
• Quickly searching for definitions and term explanations
• Creating bibliographies
• Finding examples for educational materials
• Analyzing current market trends
• Researching competitors and their products
• Monitoring reviews and mentions about a company or product
• Collecting data for advertising campaigns
• Evaluating audience interests based on search queries
• Generating content ideas
• Responding to specific real-time requests

🚦 <b>Ratings:</b>
• Vision: No 🔴
• Answer Quality: High 🟢
• Response Speed: Moderate 🟡
"""
    INFO_DALL_E = f"""
<b>{Texts.DALL_E}</b>

• <i>Art on Demand</i>: Generate unique art from descriptions – perfect for illustrators or those seeking inspiration.
• <i>Ad Creator</i>: Produce eye-catching images for advertising or social media content.
• <i>Educational Tool</i>: Visualize complex concepts for better understanding in education.
• <i>Interior Design</i>: Get ideas for room layouts or decoration themes.
• <i>Fashion Design</i>: Create clothing designs or fashion illustrations.
"""
    INFO_MIDJOURNEY = f"""
<b>{Texts.MIDJOURNEY}</b>

• <i>Art Design</i>: Creating visual masterpieces and abstractions, ideal for artists and designers in search of a unique style.
• <i>Architectural modeling</i>: Generation of conceptual designs of buildings and space layouts.
• <i>Educational assistant</i>: Illustrations for educational materials that improve the perception and understanding of complex topics.
• <i>Interior design</i>: Visualization of interior solutions, from classics to modern trends.
• <i>Fashion and style</i>: The development of fashionable bows and accessories, experiments with colors and shapes.
"""
    INFO_STABLE_DIFFUSION = "🤖 <b>Select the Stable Diffusion model</b> you want to learn more about:"
    INFO_STABLE_DIFFUSION_XL = f"""
<b>{Texts.STABLE_DIFFUSION_XL}</b>

• <i>Creative Illustration</i>: Generate unique images based on text prompts, perfect for artists, designers, and writers.
• <i>Concept Art and Sketches</i>: Create conceptual images for games, films, and other projects, helping visualize ideas.
• <i>Image Stylization</i>: Transform existing images into different artistic styles, from comic book designs to classic painting styles.
• <i>Design Prototyping</i>: Quickly generate visual concepts for logos, posters, or web design projects.
• <i>Art Style Experimentation</i>: Experiment with colors, shapes, and textures to develop new visual solutions.
"""
    INFO_STABLE_DIFFUSION_3 = f"""
<b>{Texts.STABLE_DIFFUSION_3}</b>

• <i>Creative Illustration</i>: Generate unique images based on text prompts, perfect for artists, designers, and writers.
• <i>Concept Art and Sketches</i>: Create conceptual images for games, films, and other projects, helping visualize ideas.
• <i>Image Stylization</i>: Transform existing images into different artistic styles, from comic book designs to classic painting styles.
• <i>Design Prototyping</i>: Quickly generate visual concepts for logos, posters, or web design projects.
• <i>Art Style Experimentation</i>: Experiment with colors, shapes, and textures to develop new visual solutions.
"""
    INFO_FLUX = "🤖 <b>Select the Flux model</b> you want to learn more about:"
    INFO_FLUX_1_DEV = f"""
<b>{Texts.FLUX_1_DEV}</b>

• <i>Endless Variations</i>: Generate diverse images from a single prompt, each result being unique.
• <i>Fine-Tuning Parameters</i>: Control the image creation process to achieve results tailored to your specific needs.
• <i>Randomized Generation</i>: Introduce elements of randomness to create unexpectedly creative outcomes.
• <i>Diverse Visual Concepts</i>: Explore a wide range of artistic styles and approaches, adjusting the process to fit your project.
• <i>Fast Visual Experiments</i>: Experiment with various concepts and styles without limitations, unlocking new creative possibilities.
"""
    INFO_FLUX_1_PRO = f"""
<b>{Texts.FLUX_1_PRO}</b>

• <i>Endless Variations</i>: Generate diverse images from a single prompt, each result being unique.
• <i>Fine-Tuning Parameters</i>: Control the image creation process to achieve results tailored to your specific needs.
• <i>Randomized Generation</i>: Introduce elements of randomness to create unexpectedly creative outcomes.
• <i>Diverse Visual Concepts</i>: Explore a wide range of artistic styles and approaches, adjusting the process to fit your project.
• <i>Fast Visual Experiments</i>: Experiment with various concepts and styles without limitations, unlocking new creative possibilities.
"""
    INFO_LUMA_PHOTON = f"""
<b>{Texts.LUMA_PHOTON}</b>

• <i>Photorealistic Images</i>: Create high-quality visualizations for architecture, design, and marketing.
• <i>3D Modeling</i>: Generate 3D concepts and visualizations, perfect for presentations and projects.
• <i>Lighting Effects and Textures</i>: Manage complex lighting effects and textures to produce realistic images.
• <i>Creative Rendering</i>: Experiment with compositions and styles to craft unique artistic visualizations.
• <i>Efficiency in Workflow</i>: Ideal for professionals seeking quick, high-quality results for their projects.
"""
    INFO_RECRAFT = f"""
<b>{Texts.RECRAFT}</b>

• <i>Photorealistic Images</i>: Create detailed images perfect for architecture, design, and marketing.
• <i>Texture Work</i>: Add complex textures and create realistic surfaces to enhance visual effects.
• <i>Stylized Visualizations</i>: Experiment with unique artistic styles and compositions.
• <i>High Rendering Speed</i>: Quickly generate images without compromising quality.
• <i>Ease of Use</i>: Suitable for designers, artists, and professionals looking to save time.
"""
    INFO_FACE_SWAP = f"""
<b>{Texts.FACE_SWAP}</b>

• <i>Fun Reimaginations</i>: See how you'd look in different historical eras or as various movie characters.
• <i>Personalized Greetings</i>: Create unique birthday cards or invitations with personalized images.
• <i>Memes and Content Creation</i>: Spice up your social media with funny or imaginative face-swapped pictures.
• <i>Digital Makeovers</i>: Experiment with new haircuts or makeup styles.
• <i>Celebrity Mashups</i>: Combine your face with celebrities for fun comparisons.
"""
    INFO_PHOTOSHOP_AI = f"""
<b>{Texts.PHOTOSHOP_AI}</b>

• <i>Quality Enhancement</i>: Increases image resolution, improves sharpness, and reduces noise, making the picture more detailed and vibrant.
• <i>Photo Restoration</i>: Revives old or damaged photos, returning them to their original state.
• <i>Black-and-White to Color</i>: Breathes life into black-and-white photos by adding vibrant and natural colors.
• <i>Background Removal</i>: Easily removes the background from images, leaving only the main subject.
"""
    INFO_MUSIC_GEN = f"""
<b>{Texts.MUSIC_GEN}</b>

• <i>Creating Unique Melodies</i>: Turn your ideas into musical pieces of any genre - from classical to pop.
• <i>Personalized Soundtracks</i>: Create a soundtrack for your next video project, game, or presentation.
• <i>Exploring Musical Styles</i>: Experiment with different musical genres and sounds to find your unique style.
• <i>Learning and Inspiration</i>: Gain new insights into music theory and the history of genres through music creation.
• <i>Instant Melody Creation</i>: Just enter a text description or mood, and MusicGen will instantly turn it into music.
"""
    INFO_SUNO = f"""
<b>{Texts.SUNO}</b>

• <i>Text-to-song transformation</i>: Suno turns your text into songs, matching melody and rhythm to your style.
• <i>Personalized songs</i>: Create unique songs for special moments, whether it's a personal gift or a soundtrack for your event.
• <i>Explore musical genres</i>: Discover new musical horizons by experimenting with different styles and sounds.
• <i>Music education and inspiration</i>: Learn about music theory and the history of genres through the practice of composition.
• <i>Instant music creation</i>: Describe your emotions or scenario, and Suno will immediately bring your description to life as a song.
"""
    INFO_KLING = f"""
<b>{Texts.KLING}</b>

• <i>Video Generation from Descriptions</i>: Describe your idea, and Kling will create an impressive video clip.
• <i>Work with Unique Styles</i>: Use a variety of styles to emphasize the individuality of your video.
• <i>Dynamic Transitions</i>: Automatically adds smooth and impactful transitions between scenes.
• <i>Creative Visual Effects</i>: Generate videos with modern effects for your projects.
• <i>Content in Minutes</i>: Create impressive video clips in a short time without requiring video editing skills.
"""
    INFO_RUNWAY = f"""
<b>{Texts.RUNWAY}</b>

• <i>Create short video clips</i>: Describe an idea or a script and attach the first frame, and Runway will produce a unique video clip.
• <i>Generate videos from photos + text</i>: Turn an image and text description into dynamic videos.
• <i>Animations and visual effects</i>: Generate visually appealing and creative animations based on your ideas.
• <i>AI content for social media</i>: Quickly create engaging videos for platforms and projects.
• <i>Experiment with video formats</i>: Explore AI capabilities to create new styles and video content.
"""
    INFO_LUMA_RAY = f"""
<b>{Texts.LUMA_RAY}</b>

• <i>High-Quality Video Clips</i>: Create realistic and dynamic videos based on descriptions.
• <i>3D Animation</i>: Generate stunning three-dimensional animations for your projects.
• <i>Cinematic Style</i>: Apply effects and compositions characteristic of professional cinema.
• <i>Visual Magic</i>: Use cutting-edge technology to produce high-quality content.
• <i>Innovative Video Formats</i>: Experiment with new styles and approaches to video content creation.
"""
    INFO_PIKA = f"""
<b>{Texts.PIKA}</b>

• <i>Video Generation</i>: Describe your idea, and Pika will create a unique video in just minutes.
• <i>Video Stylization</i>: Apply artistic styles to make your video original and memorable.
• <i>Animation Addition</i>: Turn static elements into dynamic scenes with smooth movements.
• <i>Interactive Content</i>: Create videos that capture attention and engage viewers.
• <i>Effortless Content Creation</i>: Easily produce professional-quality videos, even if you’re a beginner.
"""

    # Kling
    KLING_MODE_STANDARD = "🔸 Standard"
    KLING_MODE_PRO = "🔹 Pro"

    # Language
    LANGUAGE = "Language:"
    LANGUAGE_CHOSEN = "Selected language: English 🇺🇸"

    # Maintenance Mode
    MAINTENANCE_MODE = "🤖 I'm in maintenance mode. Please wait a little bit 🛠"

    # Midjourney
    MIDJOURNEY_INFO = """
<b>Image Layout:</b>
┌1️⃣2️⃣┐
└3️⃣4️⃣┘

<b>U</b> — Upscale the image
<b>V</b> — Variations of the image
"""
    MIDJOURNEY_ALREADY_CHOSE_UPSCALE = "You've already chosen this image, try a new one 🙂"

    # Model
    MODEL = "<b>To change a model</b> click a button below 👇"
    MODEL_CHANGE_AI = "🤖 Change AI Model"
    MODEL_CHOOSE_CHAT_GPT = "To choose a <b>ChatGPT 💭</b> model click a button below 👇"
    MODEL_CHOOSE_CLAUDE = "To choose a <b>Claude 📄</b> model click a button below 👇"
    MODEL_CHOOSE_GEMINI = "To choose a <b>Gemini ✨</b> model click a button below 👇"
    MODEL_CHOOSE_DEEP_SEEK = "To choose a <b>DeepSeek 🐳</b> model click a button below 👇"
    MODEL_CHOOSE_STABLE_DIFFUSION = "To choose a <b>Stable Diffusion 🎆</b> model click a button below 👇"
    MODEL_CHOOSE_FLUX = "To choose a <b>Flux 🫐</b> model click a button below 👇"
    MODEL_CONTINUE_GENERATING = "Continue generating"
    MODEL_ALREADY_MAKE_REQUEST = "⚠️ You've already made a request. Please wait"
    MODEL_READY_FOR_NEW_REQUEST = "😌 You can ask the next request"
    MODEL_SHOW_QUOTA = "🔄 Show Subscription Limits"
    MODEL_SWITCHED_TO_AI_MANAGE = "⚙️ Manage"
    MODEL_SWITCHED_TO_AI_MANAGE_INFO = "Select what you want to do with the model:"
    MODEL_SWITCHED_TO_AI_SETTINGS = "⚙️ Go to Settings"
    MODEL_SWITCHED_TO_AI_INFO = "ℹ️ Learn More"
    MODEL_SWITCHED_TO_AI_EXAMPLES = "💡 Show Examples"
    MODEL_ALREADY_SWITCHED_TO_THIS_MODEL = """
🔄 <b>Nothing Has Changed!</b>

You selected the same model you’re currently using
"""

    @staticmethod
    def model_switched(model_name: str, model_type: ModelType, model_info: dict):
        if model_type == ModelType.TEXT:
            model_role = model_info.get('role').split(' ')
            model_role = ' '.join(model_role[1:] + [model_role[0]])
            facts = f"""<b>Facts and Settings:</b>
📅 Knowledge up to: {model_info.get('training_data')}
📷 Vision Support: {'Yes ✅' if model_info.get('support_photos', False) else 'No ❌'}
🎙 Voice Answers: {'Enabled ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Disabled ❌'}
🎭 Role: {model_role}"""
        elif model_type == ModelType.SUMMARY:
            model_focus = model_info.get(UserSettings.FOCUS, VideoSummaryFocus.INSIGHTFUL)
            if model_focus == VideoSummaryFocus.INSIGHTFUL:
                model_focus = ' '.join(reversed(English.VIDEO_SUMMARY_FOCUS_INSIGHTFUL.split(' ', 1)))
            elif model_focus == VideoSummaryFocus.FUNNY:
                model_focus = ' '.join(reversed(English.VIDEO_SUMMARY_FOCUS_FUNNY.split(' ', 1)))
            elif model_focus == VideoSummaryFocus.ACTIONABLE:
                model_focus = ' '.join(reversed(English.VIDEO_SUMMARY_FOCUS_ACTIONABLE.split(' ', 1)))
            elif model_focus == VideoSummaryFocus.CONTROVERSIAL:
                model_focus = ' '.join(reversed(English.VIDEO_SUMMARY_FOCUS_CONTROVERSIAL.split(' ', 1)))

            model_format = model_info.get(UserSettings.FORMAT, VideoSummaryFormat.LIST)
            if model_format == VideoSummaryFormat.LIST:
                model_format = ' '.join(reversed(English.VIDEO_SUMMARY_FORMAT_LIST.split(' ', 1)))
            elif model_format == VideoSummaryFormat.FAQ:
                model_format = ' '.join(reversed(English.VIDEO_SUMMARY_FORMAT_FAQ.split(' ', 1)))

            model_amount = model_info.get(UserSettings.AMOUNT, VideoSummaryAmount.AUTO)
            if model_amount == VideoSummaryAmount.AUTO:
                model_amount = ' '.join(reversed(English.VIDEO_SUMMARY_AMOUNT_AUTO.split(' ', 1)))
            elif model_amount == VideoSummaryAmount.SHORT:
                model_amount = ' '.join(reversed(English.VIDEO_SUMMARY_AMOUNT_SHORT.split(' ', 1)))
            elif model_amount == VideoSummaryAmount.DETAILED:
                model_amount = ' '.join(reversed(English.VIDEO_SUMMARY_AMOUNT_DETAILED.split(' ', 1)))

            facts = f"""<b>Facts and Settings:</b>
{English.SETTINGS_FOCUS}: {model_focus}
{English.SETTINGS_FORMAT}: {model_format}
{English.SETTINGS_AMOUNT}: {model_amount}
{English.VOICE_MESSAGES}: {'Enabled ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Disabled ❌'}"""
        elif model_type == ModelType.IMAGE:
            model_version = get_model_version(model_info)
            model_version_info = f'\n{English.SETTINGS_VERSION}: {model_version}' if model_version else ''
            facts = f"""<b>Facts and Settings:</b>{model_version_info}
📷 Image Support: {'Yes ✅' if model_info.get('support_photos', False) else 'No ❌'}
{English.SETTINGS_ASPECT_RATIO}: {'Custom' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
{English.SETTINGS_SEND_TYPE}: {'Document 📄' if model_info.get(UserSettings.SEND_TYPE, SendType.IMAGE) == SendType.DOCUMENT else 'Image 🖼'}"""
        elif model_type == ModelType.MUSIC:
            model_version = get_model_version(model_info)
            model_version_info = f'\n{English.SETTINGS_VERSION}: {model_version}' if model_version else ''
            facts = f"""<b>Facts and Settings:</b>{model_version_info}
{English.SETTINGS_SEND_TYPE}: {'Video 📺' if model_info.get(UserSettings.SEND_TYPE, SendType.AUDIO) == SendType.VIDEO else 'Audio 🎤'}"""
        elif model_type == ModelType.VIDEO:
            model_version = get_model_version(model_info)
            model_version_info = f'\n{English.SETTINGS_VERSION}: {model_version}' if model_version else ''
            facts = f"""<b>Facts and Settings:</b>{model_version_info}
📷 Image Support: {'Yes ✅' if model_info.get('support_photos', False) else 'No ❌'}
{English.SETTINGS_ASPECT_RATIO}: {'Custom' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
{English.SETTINGS_DURATION}: {model_info.get(UserSettings.DURATION, 5)} seconds
{English.SETTINGS_SEND_TYPE}: {'Document 📄' if model_info.get(UserSettings.SEND_TYPE, SendType.VIDEO) == SendType.DOCUMENT else 'Video 📺'}"""
        else:
            facts = f"<b>Facts and Settings:</b> Coming Soon 🔜"

        return f"""
<b>{model_name}</b>
👆 Selected Model

{facts}

To <b>access settings</b>, <b>learn more about the model</b> and <b>view example prompts</b>, click the button below 👇
"""

    @staticmethod
    def model_text_processing_request() -> str:
        texts = [
            "I'm currently consulting my digital crystal ball for the best answer... 🔮",
            "One moment please, I'm currently training my hamsters to generate your answer... 🐹",
            "I'm currently rummaging through my digital library for the perfect answer. Bear with me... 📚",
            "Hold on, I'm channeling my inner AI guru for your answer... 🧘",
            "Please wait while I consult with the internet overlords for your answer... 👾",
            "Compiling the wisdom of the ages... or at least what I can find on the internet... 🌐",
            "Just a sec, I'm putting on my thinking cap... Ah, that's better. Now, let's see... 🎩",
            "I'm rolling up my virtual sleeves and getting down to business. Your answer is coming up... 💪",
            "Running at full steam! My AI gears are whirring to fetch your answer... 🚂",
            "Diving into the data ocean to fish out your answer. Be right back... 🎣",
            "I'm consulting with my virtual elves. They're usually great at finding answers... 🧝",
            "Engaging warp drive for hyper-speed answer retrieval. Hold on tight... 🚀",
            "I'm in the kitchen cooking up a fresh batch of answers. This one's gonna be delicious... 🍳",
            "Taking a quick trip to the cloud and back. Hope to bring back some smart raindrops of info... ☁️",
            "Planting your question in my digital garden. Let's see what grows... 🌱",
            "Flexing my virtual muscles for a powerful answer... 💪",
            "Whoosh — calculations in progress! The answer will be ready soon... 🪄",
            "My digital owls are flying out in search of a wise answer. They'll be back with the goods soon... 🦉",
            "There's a brainstorm happening in cyberspace, and I'm catching lightning for your answer... ⚡",
            "My team of digital raccoons is on the hunt for the perfect answer. They're great at this... 🦝",
            "Sifting through information like a squirrel gathering nuts, looking for the juiciest one... 🐿️",
            "Throwing on my virtual detective coat, heading out to find your answer... 🕵️‍♂️️",
            "Downloading a fresh batch of ideas from space. Your answer will land in a few seconds... 🚀",
            "Hold on, laying out the data cards on the virtual table. Getting ready for a precise answer... 🃏",
            "My virtual ships are sailing the sea of information. The answer is on the horizon... 🚢",
        ]

        return random.choice(texts)

    @staticmethod
    def model_image_processing_request() -> str:
        texts = [
            "Gathering stardust to create your cosmic artwork... 🌌",
            "Mixing a palette of digital colors for your masterpiece... 🎨",
            "Dipping into the virtual inkwell to sketch your vision... 🖌️",
            "Summoning the AI muses for a stroke of genius... 🌠",
            "Crafting pixels into perfection, just a moment... 🎭",
            "Whipping up a visual feast for your eyes... 🍽️",
            "Consulting with digital Da Vinci for your artistic request... 🎭",
            "Dusting off the digital easel for your creative request... 🖼️",
            "Conjuring a visual spell in the AI cauldron... 🔮",
            "Activating the virtual canvas. Get ready for artistry... 🖼️️",
            "Assembling your ideas in a gallery of pixels... 👨‍🎨",
            "Embarking on a digital safari to capture your artistic vision... 🦁",
            "Revving up the AI art engines, stand by... 🏎️",
            "Plunging into a pool of digital imagination... 🏊‍",
            "Cooking up a visual symphony in the AI kitchen... 🍳",
            "Pushing the clouds of creativity to craft your visual masterpiece... ☁️",
            "Gathering digital brushes and paints to bring your vision to life... 🎨️",
            "Summoning pixel dragons to create an epic image... 🐉",
            "Bringing in digital bees to collect the nectar for your visual bloom... 🐝",
            "Putting on my digital artist hat and getting to work on your masterpiece... 👒",
            "Dipping pixels into a magical solution so they can shine into a masterpiece... 🧪",
            "Sculpting your image from the clay of imagination, a masterpiece is on the way... 🏺",
            "My virtual elves are already painting your image... 🧝‍♂️",
            "Virtual turtles are carrying your image across the sea of data... 🐢",
            "Virtual kitties are paw-painting your masterpiece right now... 🐱",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>Generation can take up to 3 minutes</i>"

        return text

    @staticmethod
    def model_face_swap_processing_request() -> str:
        texts = [
            "Warping into the face-swapping dimension... 👤",
            "Mixing and matching faces like a digital Picasso... 🧑‍🎨",
            "Swapping faces faster than a chameleon changes colors... 🦎",
            "Unleashing the magic of face fusion... ✨",
            "Engaging in facial alchemy, transforming identities... 🧬",
            "Cranking up the face-swapping machine... 🤖",
            "Concocting a potion of facial transformation... 👩‍🔬",
            "Casting a spell in the realm of face enchantments... 🧚‍",
            "Orchestrating a symphony of facial features... 🎼",
            "Sculpting new faces in my digital art studio... 🎨",
            "Brewing a cauldron of face-swap magic... 🔮",
            "Building faces like a master architect... 🏗️",
            "Embarking on a mystical quest for the perfect face blend... 🔍",
            "Launching a rocket of face morphing adventures... 🚀",
            "Embarking on a galactic journey of face swapping... 👽",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>Generation can take up to 5 minutes</i>"

        return text

    @staticmethod
    def model_music_processing_request() -> str:
        texts = [
            "Launching the music generator, hold onto your ears... 👂",
            "Mixing notes like a DJ at a party... 🕺",
            "The melody wizard is in action, get ready for magic... 🧙‍",
            "Creating music that will make even robots dance... 💃",
            "The music laboratory is in action, things are heating up... 🔥",
            "Catching a wave of inspiration and turning it into sounds... 🌊",
            "Climbing to musical peaks, anticipate... 🏔️",
            "Creating something that ears have never heard before... 👂",
            "Time to dive into an ocean of harmony and rhythm... 🌊",
            "Opening the door to a world where music creates reality... 🌍",
            "Cracking the codes of composition to create something unique... 🎶",
            "Crafting melodies like a chef crafts culinary masterpieces... 🍽️",
            "Throwing a party on the keys, each note is a guest... 🎹",
            "Carving a path through the melodic labyrinth... 🌀",
            "Turning air vibrations into magical sounds... 🌬️",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>Generation can take up to 10 minutes</i>"

        return text

    @staticmethod
    def model_video_processing_request() -> str:
        texts = [
            "Loading the movie premiere, almost ready... 🍿",
            "The rocket of video creativity is taking off! Fasten your seatbelts... 🚀",
            "Frames are coming to life, camera, action... 🎬",
            "Generating a masterpiece frame by frame... 🎥",
            "Not just a video, but a cinematic wonder is on its way... 🎞️",
            "Assembling the puzzle of the best shots for your WOW moment... 🤩",
            "Connecting pixels — expect a video masterpiece... 🎇",
            "Reeling in the best shots, a masterpiece is in progress... 🎣",
            "The editing table is on fire, creating a video masterpiece... 🔥",
            "Loading video content into your dimension... 🎞️",
            "AI bees are working on your video honey... Get ready for a sweet result... 🐝",
            "The magic projector is already starting up... ✨",
            "The pizza is baking in the oven... oh wait, it’s your video... 🍕",
            "Casting visual spells, the video will be magical... 🎩",
            "Delivering your video on the rails of creativity... 🚉",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>Generation can take up to 20 minutes</i>"

        return text

    @staticmethod
    def model_wait_for_another_request(seconds: int) -> str:
        return f"⏳ Please wait for another <b>{seconds} seconds</b> before sending the next question"

    @staticmethod
    def model_reached_usage_limit():
        hours, minutes = get_time_until_limit_update()

        return f"""
🚨 <b>You've reached the current usage cap</b>

The daily limit will reset in <i>{hours} hr. {minutes} min.</i> 🔄

If you don’t want to wait, I have some solutions:
"""

    @staticmethod
    def model_restricted(model: str):
        return f"""
🔒 <b>You’ve Entered the VIP Zone!</b>

{model} is not included in your current subscription

Select an action:
"""

    @staticmethod
    def model_unresolved_request(model: str):
        return f"""
🤒 <b>I did not receive a response from {model}</b>

You can try again or select an action:
"""

    @staticmethod
    def model_text_info():
        return f"""
📕 <b>Instruction</b>

<b>My Capabilities:</b>
💡 Content creation & ideas
🌍 Translation & localization
💻 Writing & debugging code
📊 Solving problems
🌟 And much more!

<b>Example Queries:</b>
💡 Write a post about traveling
🌍 Translate "Hello" to Spanish
💻 How to create my own website?
📊 Solve the equation: 3x² - 5x + 2 = 0

<b>Just type your request 👇</b>
"""

    @staticmethod
    def model_image_info():
        return f"""
📕 <b>Instruction</b>

<b>My Capabilities:</b>
🖼 Generating creative images
🎭 Creating unique characters
🖍 Working with logos & design
🎨 Styling existing photos
🌟 And much more!

<b>Example Queries:</b>
🖼 Draw a dragon in the mist
🎭 Create a superhero for a comic book
🖍 Design a logo for a startup
🎨 Add a spark effect to a photo

<b>Just type your request 👇</b>
"""

    @staticmethod
    def model_video_info():
        return f"""
📕 <b>Instruction</b>

<b>My Capabilities:</b>
🎬 Video generation
🖼 Image animation
🌟 And much more!

<b>Example Queries:</b>
🎬 Create a video of an explosion in space
🖼 Animate an old photograph [photo]

<b>Just type your request 👇</b>
"""

    MODELS_TEXT = "🔤 Text Models"
    MODELS_SUMMARY = "📝 Summary Models"
    MODELS_IMAGE = "🖼 Image Models"
    MODELS_MUSIC = "🎵 Music Models"
    MODELS_VIDEO = "📹 Video Models"

    # MusicGen
    MUSIC_GEN_INFO = """
🎺 <b>MusicGen Guide</b>

I’m ready to transform your words and descriptions into unique melodies 🎼

Tell me what kind of music you want to create: <b>describe its style, mood, and instruments</b>
"""
    MUSIC_GEN_TYPE_SECONDS = """
⏳ <b>How Many Seconds in Your Symphony?</b>

<i>Every 10 seconds use 1 generation</i> 🎼

Enter or select the duration of your composition in seconds:
"""
    MUSIC_GEN_MIN_ERROR = """
🤨 <b>Hold on!</b>

You’re trying to request less than 10 seconds!

To proceed, <b>please enter a number greater than or equal to 10</b>
"""
    MUSIC_GEN_MAX_ERROR = """
🤨 <b>Hold on!</b>

You’re trying to request more than 10 minutes, but I can’t create anything longer yet!

To start the magic, <b>please enter a number less than 600</b>
"""
    MUSIC_GEN_SECONDS_10 = "🔹 10 seconds"
    MUSIC_GEN_SECONDS_30 = "🔹 30 seconds"
    MUSIC_GEN_SECONDS_60 = "🔹 60 seconds (1 minute)"
    MUSIC_GEN_SECONDS_180 = "🔹 180 seconds (3 minutes)"
    MUSIC_GEN_SECONDS_300 = "🔹 300 seconds (5 minutes)"
    MUSIC_GEN_SECONDS_600 = "🔹 600 seconds (10 minutes)"

    @staticmethod
    def music_gen_forbidden_error(available_seconds: int) -> str:
        return f"""
🚧 <b>Oops, a Small Problem!</b>

You only have <b>{available_seconds} seconds</b> left in your arsenal

Enter a smaller number, or use /buy for unlimited possibilities
"""

    # Notify about quota
    @staticmethod
    def notify_about_quota(
        subscription_limits: dict,
    ) -> str:
        texts = [
            f"""
🤖 <b>Hey, it’s me! Remember me?</b>

🤓 I’m here to <b>remind</b> you about your daily quotas:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests</b> are waiting to be turned into your masterpieces
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} video summary</b> to help you quickly grasp the essence of videos
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} graphic opportunity</b> ready to bring your ideas to life

🔥 Don’t let them go to waste — <b>start now!</b>
""",
            f"""
🤖 <b>Hello, I’m Fusi, your personal assistant!</b>

😢 I noticed you haven’t used your quotas in a while, so I’m here to <b>remind</b> you that every day you have:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests</b> for your ideas
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} video summary</b> to save your time
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} image</b> to bring your thoughts to life

✨ <b>Let’s create!</b> I’m ready to start right now!
""",
            f"""
🤖 <b>This is Fusi, your personal digital employee, with an important reminder!</b>

🤨 You know that <b>you have</b>:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests</b> for your brilliant ideas
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} video summary</b> to instantly grasp the essence
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} image</b> to visualize your concepts

🔋 I’m already charged up—just <b>start creating</b>!
""",
            f"""
🤖 <b>It’s me again! I miss you...</b>

😢 I’ve been thinking... <b>Your quotas miss you too</b>:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} inspiring text requests</b> are waiting for their moment
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} video summary</b> that can turn into concise insights
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} visual idea</b> ready to come to life

💡 Give me a chance to help you <b>create something amazing</b>!
""",
            f"""
🤖 <b>Hello, it’s Fusi!</b> Your quotas won’t use themselves, you know that, right?

🫤 <b>Here’s a reminder that you have:</b>
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests</b> that could be the start of something great.
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} video summary</b> to uncover insights in seconds.
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} image</b> to bring your imagination to life.

✨ <b>It’s time to create</b>, and I’m here to help. Let’s get started!
""",
        ]

        return random.choice(texts)

    NOTIFY_ABOUT_QUOTA_TURN_OFF = "🔕 Turn Off Notifications"
    NOTIFY_ABOUT_QUOTA_TURN_OFF_SUCCESS = "🎉 Notifications have been successfully disabled"

    # Open
    OPEN_SETTINGS = "⚙️ Open Settings"
    OPEN_BONUS_INFO = "🎁 Open Bonus Balance"
    OPEN_BONUS_FREE_INFO = "🎁 Get access for free"
    OPEN_BUY_SUBSCRIPTIONS_INFO = "💎 Subscribe"
    OPEN_BUY_SUBSCRIPTIONS_TRIAL_INFO = "💎 Activate a trial period"
    OPEN_BUY_PACKAGES_INFO = "🛍 Purchase Packages"

    # Package
    PACKAGE = "🛍 Package"
    PACKAGE_SUCCESS = """
🎉 <b>Payment Successful!</b>

You’ve successfully unlocked the power of your chosen package 🎢

Let’s create some magic ✨
"""
    PACKAGE_QUANTITY_MIN_ERROR = """
🚨 <b>Oops!</b>

The amount is below the minimum threshold

Please select a number of packages that meets or exceeds the minimum required amount 🔄
"""
    PACKAGE_QUANTITY_MAX_ERROR = """
🚨 <b>Oops!</b>

The entered number exceeds what you can purchase

<b>Please enter a smaller value or one that matches your balance</b> 🔄
"""

    @staticmethod
    def package_info(currency: Currency, cost: str, gift_packages: list[Product]) -> str:
        if currency == Currency.USD:
            cost = f"{Currency.SYMBOLS[currency]}{cost}"
            gift_packages_sum = f"{Currency.SYMBOLS[currency]}4"
        else:
            cost = f"{cost}{Currency.SYMBOLS[currency]}"
            gift_packages_sum = f"400{Currency.SYMBOLS[currency]}"

        gift_packages_info = f"\n\n🎁 <span class='tg-spoiler'>Spend {gift_packages_sum} or more — get these packages as a gift:</span>"
        for gift_package in gift_packages:
            gift_packages_info += f"\n<span class='tg-spoiler'>{gift_package.names.get(LanguageCode.EN)}</span>"

        return f"""
🛍 <b>Packages</b>

<b>1 coin 🪙 = {cost}</b>{gift_packages_info if len(gift_packages) > 0 else ''}

To select a package, click the button:
"""

    @staticmethod
    def package_choose_min(name: str) -> str:
        return f"""
You’ve selected the <b>{name}</b> package

<b>Choose or enter the quantity</b> you’d like to purchase
"""

    @staticmethod
    def package_confirmation(package_name: str, package_quantity: int, currency: Currency, price: str) -> str:
        left_price_part = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_price_part = '' if currency == Currency.USD else Currency.SYMBOLS[currency]
        return f"You're about to buy {package_quantity} package(-s) <b>{package_name}</b> for {left_price_part}{price}{right_price_part}"

    @staticmethod
    def payment_package_description(user_id: str, package_name: str, package_quantity: int):
        return f"Paying {package_quantity} package(-s) {package_name} for user: {user_id}"

    PACKAGES = "🛍 Packages"
    PACKAGES_SUCCESS = """
🎉 <b>Payment Successful!</b>

You’ve successfully unlocked the power of the selected packages 🎢

Let’s create some magic ✨
"""
    PACKAGES_END = """
🕒 <b>Uh-oh</b>

The time for one or more packages has expired ⌛

To continue, check out my offers by clicking the button below:
"""

    @staticmethod
    def packages_description(user_id: str):
        return f"Paying packages from the cart for user: {user_id}"

    # Payment
    PAYMENT_BUY = """
🛒 <b>Store</b>

💳 <b>Subscriptions</b>
Gain full access to all AI models and tools. Communication, images, music, video, and much more — all included!

🛍 <b>Packages</b>
Just what you need! Select a specific number of requests and pay only for what you use

Choose by clicking the button below 👇
"""
    PAYMENT_CHANGE_CURRENCY = "💱 Change Currency"
    PAYMENT_YOOKASSA_PAYMENT_METHOD = "🪆 YooKassa"
    PAYMENT_STRIPE_PAYMENT_METHOD = "🌍 Stripe"
    PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD = "⭐️ Telegram Stars"
    PAYMENT_CHOOSE_PAYMENT_METHOD = """
<b>Choose a Payment Method:</b>

🪆 <b>YooKassa (Russian's Cards)</b>
(Visa | MasterCard | MIR | YooMoney | SberPay | T-Pay and others)

🌍 <b>Stripe (International Cards)</b>
(Visa | MasterCard | AmEx | UnionPay | Google Pay | Apple Pay and others)

⭐️ <b>Telegram Stars (Currency in Telegram)</b>
"""
    PAYMENT_PROCEED_TO_PAY = "🌐 Proceed to Payment"
    PAYMENT_PROCEED_TO_CHECKOUT = "💳 Proceed to Checkout"
    PAYMENT_DISCOUNT = "💸 Discount"
    PAYMENT_NO_DISCOUNT = "No discount"

    @staticmethod
    def payment_purchase_minimal_price(currency: Currency, current_price: str):
        left_part_price = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_part_price = '' if currency == Currency.USD else Currency.SYMBOLS[currency]
        return f"""
<b>😕 Uh-oh...</b>

To complete the purchase, the total amount must be equal to or greater than <b>{left_part_price}{1 if currency == Currency.USD else 50}{right_part_price}</b>

Currently, the purchase amount is: <b>{left_part_price}{current_price}{right_part_price}</b>
"""

    # Perplexity
    PERPLEXITY_INFO = """
📕 <b>Instruction</b>

<b>My Capabilities:</b>
🌐 Information search
📊 Source analysis
🔗 Providing links
🌟 And much more!

<b>Example Queries:</b>
🌐 What are the consequences of global warming in 2025?
📊 Compare studies on the effects of caffeine on health
🔗 What are the best books on psychology?

<b>Just type your request 👇</b>
"""

    # Photoshop AI
    PHOTOSHOP_AI_INFO = """
🪄 <b>Photoshop AI</b>

This model offers AI tools for editing and stylizing images

Select an action by clicking the button below 👇
"""
    PHOTOSHOP_AI_UPSCALE = "⬆️ Upscaling"
    PHOTOSHOP_AI_UPSCALE_INFO = """
⬆️ <b>This tool enhances the quality of the original image</b>

To improve the image quality, send me your picture
"""
    PHOTOSHOP_AI_RESTORATION = "Restoration 🖌"
    PHOTOSHOP_AI_RESTORATION_INFO = """
🖌 <b>This tool detects scratches/cuts on the original image and removes them</b>

To remove scratches/cuts, send me your picture
"""
    PHOTOSHOP_AI_COLORIZATION = "Colorization 🌈"
    PHOTOSHOP_AI_COLORIZATION_INFO = """
🌈 <b>This tool adds color to black-and-white images</b>

To turn a black-and-white photo into a color one, send me your picture.
"""
    PHOTOSHOP_AI_REMOVE_BACKGROUND = "Background Removal 🗑"
    PHOTOSHOP_AI_REMOVE_BACKGROUND_INFO = """
🗑 <b>This tool removes the background from an image</b>

To remove the background, send me your picture
"""

    # Profile
    @staticmethod
    def profile(
        subscription_name: str,
        subscription_status: SubscriptionStatus,
        current_model: str,
        renewal_date,
    ) -> str:
        if subscription_status == SubscriptionStatus.CANCELED:
            subscription_info = f"📫 <b>Subscription Status:</b> Canceled. Active until {renewal_date}"
        elif subscription_status == SubscriptionStatus.TRIAL:
            subscription_info = f"📫 <b>Subscription Status:</b> Trial Period"
        else:
            subscription_info = "📫 <b>Subscription Status:</b> Active"

        return f"""
👤 <b>Profile</b>

─────────────

🤖 <b>Current model: {current_model}</b>

💳 <b>Subscription type:</b> {subscription_name}
🗓 <b>Subscription renewal date:</b> {f'{renewal_date}' if subscription_name != '🆓' else 'N/A'}
{subscription_info}

─────────────

Choose action 👇
"""

    @staticmethod
    def profile_quota(
        subscription_limits: dict,
        daily_limits,
        additional_usage_quota,
    ) -> str:
        hours, minutes = get_time_until_limit_update()

        return f"""
🤖 <b>Quota:</b>

─────────────

🔤 <b>Text Models</b>:
<b>Basic</b>:
    ┣ ✉️ ChatGPT 4.0 Omni Mini{f': extra {additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI] > 0 else ''}
    ┣ 📜 Claude 3.5 Haiku{f': extra {additional_usage_quota[Quota.CLAUDE_3_HAIKU]}' if additional_usage_quota[Quota.CLAUDE_3_HAIKU] > 0 else ''}
    ┣ 🏎 Gemini 2.0 Flash{f': extra {additional_usage_quota[Quota.GEMINI_2_FLASH]}' if additional_usage_quota[Quota.GEMINI_2_FLASH] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI_MINI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])}

<b>Advanced</b>:
    ┣ 💥 ChatGPT 4.0 Omni{f': extra {additional_usage_quota[Quota.CHAT_GPT4_OMNI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI] > 0 else ''}
    ┣ 🧩 ChatGPT o3-mini{f': extra {additional_usage_quota[Quota.CHAT_GPT_O_3_MINI]}' if additional_usage_quota[Quota.CHAT_GPT_O_3_MINI] > 0 else ''}
    ┣ 💫 Claude 3.7 Sonnet{f': extra {additional_usage_quota[Quota.CLAUDE_3_SONNET]}' if additional_usage_quota[Quota.CLAUDE_3_SONNET] > 0 else ''}
    ┣ 💼 Gemini 2.5 Pro{f': extra {additional_usage_quota[Quota.GEMINI_2_PRO]}' if additional_usage_quota[Quota.GEMINI_2_PRO] > 0 else ''}
    ┣ 🐦 Grok 2.0{f': extra {additional_usage_quota[Quota.GROK_2]}' if additional_usage_quota[Quota.GROK_2] > 0 else ''}
    ┣ 🌐 Perplexity{f': extra {additional_usage_quota[Quota.PERPLEXITY]}' if additional_usage_quota[Quota.PERPLEXITY] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI])}

<b>Flagship</b>:
    ┣ 🧪 ChatGPT o1{f': extra {additional_usage_quota[Quota.CHAT_GPT_O_1]}' if additional_usage_quota[Quota.CHAT_GPT_O_1] > 0 else ''}
    ┣ 🚀 Claude 3.0 Opus{f': extra {additional_usage_quota[Quota.CLAUDE_3_OPUS]}' if additional_usage_quota[Quota.CLAUDE_3_OPUS] > 0 else ''}
    ┣ 🛡️ Gemini 1.0 Ultra{f': extra {additional_usage_quota[Quota.GEMINI_1_ULTRA]}' if additional_usage_quota[Quota.GEMINI_1_ULTRA] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.CHAT_GPT_O_1])}/{format_number(subscription_limits[Quota.CHAT_GPT_O_1])}

─────────────

📝 <b>Summary Models</b>:
    ┣ 👀 YouTube{f': extra {additional_usage_quota[Quota.EIGHTIFY]}' if additional_usage_quota[Quota.EIGHTIFY] > 0 else ''}
    ┣ 📼 Video{f': extra {additional_usage_quota[Quota.GEMINI_VIDEO]}' if additional_usage_quota[Quota.GEMINI_VIDEO] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.EIGHTIFY])}/{format_number(subscription_limits[Quota.EIGHTIFY])}

─────────────

🖼 <b>Image Models</b>:
<b>Basic</b>:
    ┣ 🦄 Stable Diffusion XL{f': extra {additional_usage_quota[Quota.STABLE_DIFFUSION_XL]}' if additional_usage_quota[Quota.STABLE_DIFFUSION_XL] > 0 else ''}
    ┣ 🌲 Flux 1.0 Dev{f': extra {additional_usage_quota[Quota.FLUX_1_DEV]}' if additional_usage_quota[Quota.FLUX_1_DEV] > 0 else ''}
    ┣ 🌌 Luma Photon{f': extra {additional_usage_quota[Quota.LUMA_PHOTON]}' if additional_usage_quota[Quota.LUMA_PHOTON] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.STABLE_DIFFUSION_XL])}/{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])}

<b>Advanced</b>:
    ┣ 👨‍🎨 DALL-E 3{f': extra {additional_usage_quota[Quota.DALL_E]}' if additional_usage_quota[Quota.DALL_E] > 0 else ''}
    ┣ 🎨 Midjourney 7{f': extra {additional_usage_quota[Quota.MIDJOURNEY]}' if additional_usage_quota[Quota.MIDJOURNEY] > 0 else ''}
    ┣ 🧑‍🚀 Stable Diffusion 3.5{f': extra {additional_usage_quota[Quota.STABLE_DIFFUSION_3]}' if additional_usage_quota[Quota.STABLE_DIFFUSION_3] > 0 else ''}
    ┣ 🏔 Flux 1.1 Pro{f': extra {additional_usage_quota[Quota.FLUX_1_PRO]}' if additional_usage_quota[Quota.FLUX_1_PRO] > 0 else ''}
    ┣ 🐼 Recraft 3{f': extra {additional_usage_quota[Quota.RECRAFT]}' if additional_usage_quota[Quota.RECRAFT] > 0 else ''}
    ┣ 📷 FaceSwap{f': extra {additional_usage_quota[Quota.FACE_SWAP]}' if additional_usage_quota[Quota.FACE_SWAP] > 0 else ''}
    ┣ 🪄 Photoshop AI{f': extra {additional_usage_quota[Quota.PHOTOSHOP_AI]}' if additional_usage_quota[Quota.PHOTOSHOP_AI] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.DALL_E])}/{format_number(subscription_limits[Quota.DALL_E])}

─────────────

🎵 <b>Music Models</b>:
    ┣ 🎺 MusicGen{f': extra {additional_usage_quota[Quota.MUSIC_GEN]}' if additional_usage_quota[Quota.MUSIC_GEN] > 0 else ''}
    ┣ 🎸 Suno{f': extra {additional_usage_quota[Quota.SUNO]}' if additional_usage_quota[Quota.SUNO] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.SUNO])}/{format_number(subscription_limits[Quota.SUNO])}

─────────────

📹 <b>Video Models</b>:
    ┣ 🎬 Kling{f': extra {additional_usage_quota[Quota.KLING]}' if additional_usage_quota[Quota.KLING] > 0 else ''}
    ┣ 🎥 Runway{f': extra {additional_usage_quota[Quota.RUNWAY]}' if additional_usage_quota[Quota.RUNWAY] > 0 else ''}
    ┣ 🔆 Luma Ray{f': extra {additional_usage_quota[Quota.LUMA_RAY]}' if additional_usage_quota[Quota.LUMA_RAY] > 0 else ''}
    ┣ 🐇 Pika{f': extra {additional_usage_quota[Quota.PIKA]}' if additional_usage_quota[Quota.PIKA] > 0 else ''}
    ┗ Daily Limits: {format_number(daily_limits[Quota.KLING])}/{format_number(subscription_limits[Quota.KLING])}

─────────────

📷 <b>Support Photos/Documents</b>: {'✅' if daily_limits[Quota.WORK_WITH_FILES] or additional_usage_quota[Quota.WORK_WITH_FILES] else '❌'}
🎭 <b>Access to a Roles Catalog</b>: {'✅' if daily_limits[Quota.ACCESS_TO_CATALOG] or additional_usage_quota[Quota.ACCESS_TO_CATALOG] else '❌'}
🎙 <b>Voice Messages</b>: {'✅' if daily_limits[Quota.VOICE_MESSAGES] or additional_usage_quota[Quota.VOICE_MESSAGES] else '❌'}
⚡ <b>Fast Answers</b>: {'✅' if daily_limits[Quota.FAST_MESSAGES] or additional_usage_quota[Quota.FAST_MESSAGES] else '❌'}

─────────────

🔄 <i>Limit will be updated in: {hours} h. {minutes} min.</i>
"""

    PROFILE_SHOW_QUOTA = "🔄 Show Quota"
    PROFILE_TELL_ME_YOUR_GENDER = "Tell me your gender:"
    PROFILE_YOUR_GENDER = "Your gender:"
    PROFILE_SEND_ME_YOUR_PICTURE = """
📸 <b>Send a photo of yours</b>

👍 <b>Ideal photo guidelines</b>:
• Clear, high-quality selfie.
• Only one person should be in the selfie.

👎 <b>Please avoid these types of photos</b>:
• Group photos.
• Animals.
• Children under 18 years.
• Full body shots.
• Nude or inappropriate images.
• Sunglasses or any face-obscuring items.
• Blurry, out-of-focus images.
• Videos and animations.
• Compressed or altered images.

Once you've got the perfect shot, <b>upload your photo</b> and let the magic happen 🌟
"""
    PROFILE_UPLOAD_PHOTO = "📷 Upload Photo"
    PROFILE_UPLOADING_PHOTO = "Uploading photo..."
    PROFILE_CHANGE_PHOTO = "📷 Change Photo"
    PROFILE_CHANGE_PHOTO_SUCCESS = "📸 Photo successfully uploaded!"
    PROFILE_RENEW_SUBSCRIPTION = "♻️ Renew Subscription"
    PROFILE_RENEW_SUBSCRIPTION_SUCCESS = "✅ Subscription renewal was successful"
    PROFILE_CANCEL_SUBSCRIPTION = "❌ Cancel Subscription"
    PROFILE_CANCEL_SUBSCRIPTION_CONFIRMATION = "❗Are you sure you want to cancel the subscription?"
    PROFILE_CANCEL_SUBSCRIPTION_SUCCESS = "💸 Subscription cancellation was successful"
    PROFILE_NO_ACTIVE_SUBSCRIPTION = "💸 You don't have an active subscription"

    # Promo code
    PROMO_CODE_ACTIVATE = "🔑 Activate Promo Code"
    PROMO_CODE_INFO = """
🔓 <b>Promo Code Activation</b>

If you have a promo code, just send it to unlock hidden features and special surprises 🔑
"""
    PROMO_CODE_SUCCESS = """
🎉 <b>Your Promo Code Has Been Successfully Activated!</b>

Enjoy exploring! 🚀
"""
    PROMO_CODE_ALREADY_HAVE_SUBSCRIPTION = """
🚫 <b>Oops</b>

You’re already part of our exclusive subscriber club! 🌟
"""
    PROMO_CODE_EXPIRED_ERROR = """
🕒 <b>This Promo Code Has Expired!</b>

Send me another promo code or simply choose an action below:
"""
    PROMO_CODE_NOT_FOUND_ERROR = """
🔍 <b>Promo Code Not Found!</b>

The promo code you entered seems to be playing hide-and-seek, as I couldn’t find it in the system 🕵️‍♂️

🤔 Please <b>check for typos and try again</b>. If it still doesn’t work, perhaps it’s time to look for another code or check out the deals in /buy—they’re quite interesting 🛍️
"""
    PROMO_CODE_ALREADY_USED_ERROR = """
🚫 <b>Déjà Vu!</b>

You’ve already used this promo code. It’s a one-time magic, and you’ve already taken advantage of it 🧙

But don’t worry! You can check out my offers by clicking the button below:
"""

    # Remove Restriction
    REMOVE_RESTRICTION = "⛔️ Remove Restriction"
    REMOVE_RESTRICTION_INFO = "To remove the restriction, choose one of the actions below 👇"

    # Settings
    @staticmethod
    def settings_info(human_model: str, current_model: Model, generation_cost=1) -> str:
        if current_model == Model.DALL_E or current_model == Model.MIDJOURNEY:
            additional_text = f"\nAt the current settings, 1 request costs: {generation_cost} 🖼"
        elif current_model == Model.KLING or current_model == Model.RUNWAY or current_model == Model.LUMA_RAY:
            additional_text = f"\nAt the current settings, 1 request costs: {generation_cost} 📹"
        else:
            additional_text = ""

        return f"""
⚙️ <b>Settings for model:</b> {human_model}

Here you can customize the selected model to suit your tasks and preferences
{additional_text}
"""

    SETTINGS_CHOOSE_MODEL_TYPE = """
⚙️ <b>Settings</b>

🌍 To change the interface language, enter the command /language
🤖 To change the model, enter the command /model

Select the type of model you want to customize below 👇
"""
    SETTINGS_CHOOSE_MODEL = """
⚙️ <b>Settings</b>

Choose the model you want to personalize for yourself below 👇
"""
    SETTINGS_VOICE_MESSAGES = """
⚙️ <b>Welcome to Settings!</b>

Below are the voice response settings for all text models 🎙
"""
    SETTINGS_VERSION = "🤖 Version"
    SETTINGS_FOCUS = "🎯 Focus"
    SETTINGS_FORMAT = "🎛 Format"
    SETTINGS_AMOUNT = "📏 Number of Items"
    SETTINGS_SEND_TYPE = "🗯 Send Type"
    SETTINGS_SEND_TYPE_IMAGE = "🖼 Image"
    SETTINGS_SEND_TYPE_DOCUMENT = "📄 Document"
    SETTINGS_SEND_TYPE_AUDIO = "🎤 Audio"
    SETTINGS_SEND_TYPE_VIDEO = "📺 Video"
    SETTINGS_ASPECT_RATIO = "📐 Aspect Ratio"
    SETTINGS_QUALITY = "✨ Quality"
    SETTINGS_PROMPT_SAFETY = "🔐 Prompt Security"
    SETTINGS_GENDER = "👕/👚 Gender"
    SETTINGS_DURATION = "📏 Duration in Seconds"
    SETTINGS_MODE = "🤖 Mode"
    SETTINGS_SHOW_THE_NAME_OF_THE_CHATS = "Show the name of the chats"
    SETTINGS_SHOW_THE_NAME_OF_THE_ROLES = "Show the name of the roles"
    SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES = "Show usage quota in messages"
    SETTINGS_TURN_ON_VOICE_MESSAGES = "Turn on voice messages"
    SETTINGS_LISTEN_VOICES = "Listen voices"

    # Shopping cart
    SHOPPING_CART = "🛒 Cart"
    SHOPPING_CART_ADD = "➕ Add to Cart"

    @staticmethod
    def shopping_cart_add_or_buy_now(
        product: Product,
        product_quantity: int,
        product_price: float,
        currency: Currency,
    ):
        return f"""
<b>{product_quantity} package(-s) {product.names.get(LanguageCode.EN)} – {format_number(product_price)}{Currency.SYMBOLS[currency]}</b>
"""

    SHOPPING_CART_BUY_NOW = "🛍 Buy Now"
    SHOPPING_CART_REMOVE = "➖ Remove from Cart"
    SHOPPING_CART_GO_TO = "🛒 Go to Cart"
    SHOPPING_CART_GO_TO_OR_CONTINUE_SHOPPING = "Go to cart or continue shopping?"
    SHOPPING_CART_CONTINUE_SHOPPING = "🛍 Continue Shopping"
    SHOPPING_CART_CLEAR = "🗑 Clear Cart"

    @staticmethod
    async def shopping_cart_info(currency: Currency, cart_items: list[dict], discount: int):
        text = ''
        total_sum = 0
        left_price_part = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_price_part = '' if currency == Currency.USD else Currency.SYMBOLS[currency]

        for index, cart_item in enumerate(cart_items):
            product_id, product_quantity = cart_item.get('product_id', ''), cart_item.get('quantity', 0)

            product = await get_product(product_id)

            is_last = index == len(cart_items) - 1
            right_part = '\n' if not is_last else ''
            price = Product.get_discount_price(
                ProductType.PACKAGE,
                product_quantity,
                product.prices.get(currency),
                currency,
                discount,
            )
            total_sum += float(price)
            text += f'{index + 1}. {product.names.get(LanguageCode.EN)}: {product_quantity} ({left_price_part}{price}{right_price_part}){right_part}'

        if not text:
            text = 'Your cart is empty'

        return f"""
🛒 <b>Cart</b>

{text}

💳 <b>Total:</b> {left_price_part}{round(total_sum, 2)}{right_price_part}
"""

    @staticmethod
    async def shopping_cart_confirmation(cart_items: list[dict], currency: Currency, price: float) -> str:
        text = ""
        for index, cart_item in enumerate(cart_items):
            product_id, product_quantity = cart_item.get("product_id", ''), cart_item.get("quantity", 0)

            product = await get_product(product_id)

            text += f"{index + 1}. {product.names.get(LanguageCode.EN)}: {product_quantity}\n"

        if currency == Currency.USD:
            total_sum = f"{Currency.SYMBOLS[currency]}{price}"
        else:
            total_sum = f"{price}{Currency.SYMBOLS[currency]}"

        return f"""
You're about to buy next packages from your cart:
{text}

To pay {total_sum}
"""

    # Start
    START_INFO = """
👋 <b>Hello!</b>

🤓 <b>I’m your assistant in the world of AI</b>

<b>With me, you can create:</b>
💭 Text /text
📝 Summaries /summary
🖼 Images /image
🎵 Music /music
📹 Videos /video

🏆 <b>My mission is to provide everyone access to the best AI models</b>

🤖 You can view all available models at /model

ℹ️ Learn more about AI models and their capabilities at /info

✨ <b>Start creating right now!</b>
"""
    START_QUICK_GUIDE = "📖 Quick Guide"
    START_QUICK_GUIDE_INFO = """
📖 <b>Quick Guide</b>

─────────────

💭 <b>Text Responses</b>:
1️⃣ Enter the command /text
2️⃣ Select a model
3️⃣ Write your requests in the chat

<i>Additional Features</i>

📷 If you send me a photo, I can:
• Answer any question about it
• Recognize text
• Solve tasks

🌐 You can fetch information from the internet using <b>Perplexity</b> /perplexity

─────────────

📝 <b>Summary</b>:
1️⃣ Enter the command /summary
2️⃣ Select a model
3️⃣ Send a video or its link

─────────────

🖼 <b>Creating Images</b>:
1️⃣ Enter the command /image
2️⃣ Select a model
3️⃣ Write your requests in the chat

<i>Additional Features</i>
📷 If you send me a photo, I can:
• Enhance or modify details
• Change the style of the image
• Visualize something new

─────────────

📷️ <b>Face Swapping on Photos</b>:
1️⃣ Enter the command /face_swap
2️⃣ Follow the instructions

─────────────

🪄 <b>Editing Images</b>:
1️⃣ Enter the command /photoshop
2️⃣ Follow the instructions

─────────────

🎵 <b>Creating Music</b>:
1️⃣ Enter the command /music
2️⃣ Select a model
3️⃣ Follow the instructions

─────────────

📹 <b>Creating Videos</b>:
1️⃣ Enter the command /video
2️⃣ Select a model
3️⃣ Follow the instructions
"""

    # Subscription
    SUBSCRIPTION = "💳 Subscription"
    SUBSCRIPTIONS = "💳 Subscriptions"
    SUBSCRIPTION_MONTH_1 = "1 month"
    SUBSCRIPTION_MONTHS_3 = "3 months"
    SUBSCRIPTION_MONTHS_6 = "6 months"
    SUBSCRIPTION_MONTHS_12 = "12 months"
    SUBSCRIPTION_SUCCESS = """
🎉 <b>Your Subscription Has Been Activated!</b>

Here’s what’s next:
• A whole world of possibilities has opened up for you 🌍
• AI friends are ready to assist you 🤖
• Get ready to dive into a sea of features and fun 🌊

Let’s create some magic 🪄
"""
    SUBSCRIPTION_RESET = """
🚀 <b>Subscription Renewed!</b>

Hello, traveler in the world of AI! 👋

Your subscription has been successfully renewed! Let’s make this month even better 💪
"""
    SUBSCRIPTION_RETRY = """
❗️ <b>Subscription renewal failed</b>

Today's payment was unsuccessful. Another attempt will be made tomorrow

If it fails again, the subscription will end
"""
    SUBSCRIPTION_END = """
🛑 <b>Subscription Expired!</b>

Your subscription has ended. But don’t worry, your journey through the world of AI isn’t over yet 🚀

You can continue exploring the universe of AI models and regain access by clicking the button below:
"""
    SUBSCRIPTION_MONTHLY = "Monthly"
    SUBSCRIPTION_YEARLY = "Yearly"

    @staticmethod
    def subscription_description(user_id: str, name: str):
        return f"Paying a subscription {name} for user: {user_id}"

    @staticmethod
    def subscription_renew_description(user_id: str, name: str):
        return f"Renewing a subscription {name} for user: {user_id}"

    @staticmethod
    def subscribe(
        subscriptions: list[Product],
        currency: Currency,
        user_discount: int,
        is_trial=False,
    ) -> str:
        text_subscriptions = ''
        for subscription in subscriptions:
            subscription_name = subscription.names.get(LanguageCode.EN)
            subscription_price = subscription.prices.get(currency)
            subscription_has_trial = is_trial and subscription.details.get('has_trial', False)

            left_part_price = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
            right_part_price = Currency.SYMBOLS[currency] if currency != Currency.USD else ''
            if subscription_name and subscription_price:
                is_trial_info = ''

                if subscription_has_trial and currency == Currency.RUB:
                    is_trial_info = '1₽ first 3 days, then '
                elif subscription_has_trial and currency == Currency.USD:
                    is_trial_info = 'Free first 3 days, then '

                text_subscriptions += f'<b>{subscription_name}</b>: '
                per_period = 'per month' if subscription.category == ProductCategory.MONTHLY else 'per year'

                discount = get_user_discount(user_discount, 0, subscription.discount)
                if discount:
                    discount_price = Product.get_discount_price(
                        ProductType.SUBSCRIPTION,
                        1,
                        subscription_price,
                        currency,
                        discount,
                    )
                    text_subscriptions += f'{is_trial_info}<s>{left_part_price}{subscription_price}{right_part_price}</s> {left_part_price}{discount_price}{right_part_price} {per_period}\n'
                else:
                    text_subscriptions += f'{is_trial_info}{left_part_price}{subscription_price}{right_part_price} {per_period}\n'
        return f"""
💳 <b>Subscriptions</b>

{text_subscriptions}
To subscribe, pick your potion and hit the button below:
"""

    @staticmethod
    def subscribe_confirmation(
        name: str,
        category: ProductCategory,
        currency: Currency,
        price: Union[str, int, float],
        is_trial: bool,
    ) -> str:
        left_price_part = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_price_part = '' if currency == Currency.USD else Currency.SYMBOLS[currency]
        period = 'month' if category == ProductCategory.MONTHLY else 'year'

        trial_info = ''
        if is_trial:
            trial_info = ' with a free trial period first 3 days'

        return f"""
You're about to activate subscription <b>{name} for {left_price_part}{price}{right_price_part}/{period}{trial_info}</b>

❗️You can cancel your subscription at any time in <b>Profile 👤</b>
"""

    # Suno
    SUNO_INFO = """
🤖 <b>Select the Style for Your Song Creation:</b>

🎹 In <b>simple mode</b>, you just need to describe what the song will be about and its genre
🎸 In <b>custom mode</b>, you can use your own lyrics and experiment with genres

<b>Suno</b> will create 2 tracks, up to 4 minutes each 🎧
"""
    SUNO_SIMPLE_MODE = "🎹 Simple"
    SUNO_CUSTOM_MODE = "🎸 Custom"
    SUNO_SIMPLE_MODE_PROMPT = """
🎶 <b>Song Description</b>

In simple mode, I’ll create a song based on your preferences and musical taste.

<b>Send me your preferences</b> 📝
"""
    SUNO_CUSTOM_MODE_LYRICS = """
🎤 <b>Song Lyrics</b>

In custom mode, I’ll create a song using your lyrics

<b>Send me the song lyrics</b> ✍️
"""
    SUNO_CUSTOM_MODE_GENRES = """
🎵 <b>Genre Selection</b>

To ensure your song in custom mode matches your preferences, specify the genres you’d like to include. The choice of genre significantly influences the style and mood of the composition, so choose carefully

<b>List your desired genres separated by commas</b> in your next message, and I’ll start creating your unique song 🔍
"""
    SUNO_START_AGAIN = "🔄 Start Again"
    SUNO_TOO_MANY_WORDS_ERROR = """
🚧 <b>Oops!</b>

At some point, you sent a text that’s too long 📝

Please try again with a shorter text
"""
    SUNO_ARTIST_NAME_ERROR = """
🚧 <b>Oops!</b>

You sent a text that contains an artist name 🎤

Please try again without the artist name
"""
    SUNO_VALUE_ERROR = """
🧐 <b>This Doesn’t Look Like a Prompt</b>

Please send a different input
"""
    SUNO_SKIP = "⏩️ Skip"

    # Tech Support
    TECH_SUPPORT = "👨‍💻 Tech Support"

    # Terms Link
    TERMS_LINK = "https://telegra.ph/Terms-of-Service-in-GPTsTurboBot-05-07"

    # Video Summary
    VIDEO_SUMMARY_FOCUS_INSIGHTFUL = "💡 Insightful"
    VIDEO_SUMMARY_FOCUS_FUNNY = "😄 Funny"
    VIDEO_SUMMARY_FOCUS_ACTIONABLE = "🛠 Actionable"
    VIDEO_SUMMARY_FOCUS_CONTROVERSIAL = "🔥 Controversial"
    VIDEO_SUMMARY_FORMAT_LIST = "📋 List"
    VIDEO_SUMMARY_FORMAT_FAQ = "🗯 Q&A"
    VIDEO_SUMMARY_AMOUNT_AUTO = "⚙️ Auto"
    VIDEO_SUMMARY_AMOUNT_SHORT = "✂️ Short"
    VIDEO_SUMMARY_AMOUNT_DETAILED = "📚 Detailed"

    # Voice
    VOICE_MESSAGES = "🎙 Voice Messages"
    VOICE_MESSAGES_FORBIDDEN_ERROR = """
🎙 <b>Oops!</b>

Your voice got lost in the AI space!

<b>To unlock the magic of voice-to-text conversion</b>, simply use the magic of the buttons below:
"""

    # Work with files
    WORK_WITH_FILES = "📷 Working with photos/documents"
    WORK_WITH_FILES_FORBIDDEN_ERROR = """
🔒 <b>You’ve Entered the VIP Zone!</b>

You currently don't have access to work with photos and documents

You can gain access by clicking the button below:
"""

    # Admin
    ADMIN_INFO = "👨‍💻 Choose an action, Admin 👩‍💻"

    ADMIN_ADS_INFO = "Select what you want to do:"
    ADMIN_ADS_CREATE = "📯 Create Campaign"
    ADMIN_ADS_GET = "📯 Info about Campaign"
    ADMIN_ADS_SEND_LINK = "Send me a link to the advertising campaign 📯"
    ADMIN_ADS_CHOOSE_SOURCE = "Choose the source of the advertising campaign 📯"
    ADMIN_ADS_CHOOSE_MEDIUM = "Select the type of traffic for the advertising campaign 📯"
    ADMIN_ADS_SEND_DISCOUNT = "Select or send the discount amount to be applied during registration 📯"
    ADMIN_ADS_SEND_NAME = "Send the name of the advertising campaign as a single word without special characters 📯"
    ADMIN_ADS_VALUE_ERROR = "Doesn't look like a campaign name"

    ADMIN_BAN_INFO = "Send me the user ID of the person you want to ban/unban ⛔️"
    ADMIN_BAN_SUCCESS = "📛 You have successfully banned the user"
    ADMIN_UNBAN_SUCCESS = "🔥 You have successfully unbanned the user"

    ADMIN_BLAST_CHOOSE_USER_TYPE = """
📣 <b>Time to send a broadcast!</b>

First, choose who you want to send the broadcast to:
"""
    ADMIN_BLAST_CHOOSE_LANGUAGE = """
📣 <b>Let’s continue the broadcast!</b>

Select the language for the broadcast or choose to send it to everyone:
"""
    ADMIN_BLAST_WRITE_IN_CHOSEN_LANGUAGE = """
✍️ <b>Time to create your message!</b> 🚀

You’ve chosen the language, now it’s time to pour your heart into the message!

Write a broadcast message ✨
"""
    ADMIN_BLAST_WRITE_IN_DEFAULT_LANGUAGE = """
🌍 <b>Global Broadcast</b>

You’ve chosen "For Everyone," which means your message will reach every user, regardless of users’ language

Write your message in Russian, and I’ll automatically translate it
"""
    ADMIN_BLAST_SUCCESS = """
💌 <b>The Broadcast Was Successfully Sent!</b>

Your message is already on its way to users ✨
"""

    @staticmethod
    def admin_blast_confirmation(
        blast_letters: dict,
    ):
        letters = ''
        for i, (language_code, letter) in enumerate(blast_letters.items()):
            letters += f'{language_code}:\n{letter}'
            letters += '\n' if i < len(blast_letters.items()) - 1 else ''

        return f"""
📢 <b>Check</b>

🤖 Text:
{letters}

Choose an action:
"""

    ADMIN_CATALOG = """
🎭 <b>Role Catalog Management</b>

Here you can:
"""
    ADMIN_CATALOG_CREATE = """
🌈 <b>Creating a New Role</b>

Write a unique name for the new role in UPPER_SNAKE_CASE format, for example, SUPER_GENIUS or MAGIC_ADVISOR
"""
    ADMIN_CATALOG_CREATE_ROLE = "Create a Role"
    ADMIN_CATALOG_CREATE_ROLE_ALREADY_EXISTS_ERROR = """
🙈 <b>Oops! A duplicate spotted!</b>

Hey, it seems this role already exists!

Try coming up with a different name 🤔
"""
    ADMIN_CATALOG_CREATE_ROLE_NAME = """
🎨 <b>Name</b>

Come up with a name for your new role. The name should start with a fitting emoji, such as "🤖 Personal Assistant"

Write the name in Russian 🖌️
"""
    ADMIN_CATALOG_CREATE_ROLE_DESCRIPTION = """
📝 <b>Description</b>

Create a description for your new role. It should be three lines full of inspiration and ideas, which will be shown to users upon selecting the role. For example:
<blockquote>
Always ready to help you find answers to any questions, whether they’re everyday issues or philosophical musings.
Your personal guide in the world of knowledge and creativity, eager to share ideas and advice. 🌌
Let’s explore new horizons together!
</blockquote>

Write the description in Russian 🖌️
"""
    ADMIN_CATALOG_CREATE_ROLE_INSTRUCTION = """
🤓 <b>System Instruction</b>

Create a short but concise instruction for your assistant. This will be their guide for action, for example: "You are a thoughtful advisor, always ready to share wise thoughts and helpful ideas. Help users solve complex questions and offer original solutions. Your mission is to inspire and enrich every interaction!"

Write the instruction in Russian 🖌️
"""
    ADMIN_CATALOG_CREATE_ROLE_PHOTO = """
📸 <b>Photo</b>

Send a photo that will become their calling card 🖼️
"""
    ADMIN_CATALOG_CREATE_ROLE_SUCCESS = """
🎉 <b>The new role has been successfully created!</b>

💬 The assistant is ready to work. Congratulations on successfully expanding the AI team!
"""

    @staticmethod
    def admin_catalog_create_role_confirmation(
        role_names: dict,
        role_descriptions: dict,
        role_instructions: dict,
    ):
        names = ''
        for i, (language_code, name) in enumerate(role_names.items()):
            names += f'{language_code}: {name}'
            names += '\n' if i < len(role_names.items()) - 1 else ''
        descriptions = ''
        for i, (language_code, description) in enumerate(role_descriptions.items()):
            descriptions += f'{language_code}: {description}'
            descriptions += '\n' if i < len(role_descriptions.items()) - 1 else ''
        instructions = ''
        for i, (language_code, instruction) in enumerate(role_instructions.items()):
            instructions += f'{language_code}: {instruction}'
            instructions += '\n' if i < len(role_instructions.items()) - 1 else ''

        return f"""
🎩 <b>Role:</b>

🌍 Names:
{names}

💬 Descriptions:
{descriptions}

📜 Instructions:
{instructions}

Choose an action:
"""

    @staticmethod
    def admin_catalog_edit_role_info(
        role_names: dict[LanguageCode, str],
        role_descriptions: dict[LanguageCode, str],
        role_instructions: dict[LanguageCode, str],
    ):
        names = ''
        for i, (language_code, name) in enumerate(role_names.items()):
            names += f'{language_code}: {name}'
            names += '\n' if i < len(role_names.items()) - 1 else ''
        descriptions = ''
        for i, (language_code, description) in enumerate(role_descriptions.items()):
            descriptions += f'{language_code}: {description}'
            descriptions += '\n' if i < len(role_descriptions.items()) - 1 else ''
        instructions = ''
        for i, (language_code, instruction) in enumerate(role_instructions.items()):
            instructions += f'{language_code}: {instruction}'
            instructions += '\n' if i < len(role_instructions.items()) - 1 else ''

        return f"""
🖌️ <b>Role Configuration</b>

🌍 <b>Names:</b>
{names}

💬 <b>Descriptions:</b>
{descriptions}

📜 <b>Instructions:</b>
{instructions}

Choose what you’d like to edit:
"""

    ADMIN_CATALOG_EDIT_ROLE_NAME = "Edit Name 🖌"
    ADMIN_CATALOG_EDIT_ROLE_NAME_INFO = """
📝 <b>Edit Name</b>

Enter the new name starting with an emoji in Russian
"""
    ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION = "Edit Description 🖌"
    ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION_INFO = """
🖋️ <b>Edit Description</b>

Write a new description emphasizing their best qualities in Russian
"""
    ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION = "Edit Instruction 🖌"
    ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION_INFO = """
🕹️ <b>Edit Instruction</b>

Write the new instruction in Russian
"""
    ADMIN_CATALOG_EDIT_ROLE_PHOTO = "Edit Photo 🖼"
    ADMIN_CATALOG_EDIT_ROLE_PHOTO_INFO = """
📸 <b>Edit Photo</b>

Send a photo that best reflects your assistant’s character and style 🖼️
"""
    ADMIN_CATALOG_EDIT_SUCCESS = """
🎉 <b>Changes Successfully Applied!</b>

Your assistant has been changed 🤖
"""

    ADMIN_DATABASE = "🗄 Database"

    ADMIN_FACE_SWAP_INFO = """
🤹‍ <b>Manage FaceSwap!</b> 🎭

Choose an action:
"""
    ADMIN_FACE_SWAP_CREATE = """
🌟 <b>Create</b>

Start by giving it a unique name. Use the UPPER_SNAKE_CASE format, for example, you could name it SEASONAL_PHOTO_SHOOT or FUNNY_FACE_FESTIVAL

Write a system name 📝
"""
    ADMIN_FACE_SWAP_CREATE_PACKAGE = "Create a New Package"
    ADMIN_FACE_SWAP_CREATE_PACKAGE_ALREADY_EXISTS_ERROR = """
🚨 <b>Oops, it seems we’ve been here before!</b>

The package name is already taken!

How about another unique name?
"""
    ADMIN_FACE_SWAP_CREATE_PACKAGE_NAME = """
🚀 <b>Package Name</b>

Now write a unique name for the package in Russian. Don’t forget to add an emoji at the start, for example, "🎥 Movies" or "🌌 Space"
"""
    ADMIN_FACE_SWAP_CREATE_PACKAGE_SUCCESS = """
🎉 <b>The new FaceSwap package is ready</b>

You can now start filling the package with the most incredible and funny photos 🖼
"""

    @staticmethod
    def admin_face_swap_create_package_confirmation(
        package_system_name: str,
        package_names: dict,
    ):
        names = ''
        for i, (language_code, name) in enumerate(package_names.items()):
            names += f'{language_code}: {name}'
            names += '\n' if i < len(package_names.items()) - 1 else ''

        return f"""
🌟 <b>Check</b>

📝 Review all the details:
- 🤖 <b>System Name:</b>
{package_system_name}

- 🌍 <b>Names:</b>
{names}

👇 Choose an action
"""

    ADMIN_FACE_SWAP_EDIT = """
🎨 <b>Edit Package</b> 🖌️

🔧 Editing options:
"""
    ADMIN_FACE_SWAP_EDIT_PACKAGE = "Edit Package"
    ADMIN_FACE_SWAP_EDIT_CHOOSE_GENDER = "Choose Gender:"
    ADMIN_FACE_SWAP_EDIT_CHOOSE_PACKAGE = "Choose Package:"
    ADMIN_FACE_SWAP_EDIT_SUCCESS = """
🎉 <b>Package Successfully Edited!</b>

Your changes have been successfully applied. The FaceSwap package is updated 👏
"""
    ADMIN_FACE_SWAP_CHANGE_STATUS = "Change Visibility 👁"
    ADMIN_FACE_SWAP_SHOW_PICTURES = "View Images 🖼"
    ADMIN_FACE_SWAP_ADD_NEW_PICTURE = "Add New Image 👨‍🎨"
    ADMIN_FACE_SWAP_ADD_NEW_PICTURE_NAME = "Send me the name of the new image in English using CamelCase, e.g., 'ContentMaker'"
    ADMIN_FACE_SWAP_ADD_NEW_PICTURE_IMAGE = "Now, send me the photo"
    ADMIN_FACE_SWAP_EXAMPLE_PICTURE = "Example Generation 🎭"
    ADMIN_FACE_SWAP_PUBLIC = "Visible to All 🔓"
    ADMIN_FACE_SWAP_PRIVATE = "Visible to Admins 🔒"

    ADMIN_PROMO_CODE_INFO = """
🔑 <b>Time to create some magic with promo codes!</b> ✨

Choose what you want to create a promo code for:
"""
    ADMIN_PROMO_CODE_SUCCESS = """
🌟 <b>Promo Code Has Been Successfully Created</b>

This little code will surely bring joy to someone out there!
"""
    ADMIN_PROMO_CODE_CHOOSE_SUBSCRIPTION = """
🌟 <b>Subscription for the Promo Code</b> 🎁

✨ Select the subscription type you want to grant access to:
"""
    ADMIN_PROMO_CODE_CHOOSE_PACKAGE = """
🌟 <b>Package for the Promo Code!</b> 🎁

Start by choosing a package 👇
"""
    ADMIN_PROMO_CODE_CHOOSE_DISCOUNT = """
🌟 <b>Discount for the Promo Code!</b> 🎁

Enter the discount percentage (from 1% to 50%) that you want to offer users 👇
"""
    ADMIN_PROMO_CODE_CHOOSE_NAME = """
🖋️ <b>Name for the Promo Code</b> ✨

🔠 Use letters and numbers and write in the UPPER_SNAKE_CASE format, for example: "HAPPY_BIRTHDAY"
"""
    ADMIN_PROMO_CODE_CHOOSE_DATE = """
📅 <b>Date and Time for the Promo Code</b> 🪄

Enter the date until this promo code will work. Remember to use the format DD.MM.YYYY, for example, 25.12.2025
"""
    ADMIN_PROMO_CODE_NAME_EXISTS_ERROR = """
🚫 <b>Oh no, this code already exists!</b>

Try again
"""
    ADMIN_PROMO_CODE_DATE_VALUE_ERROR = """
🚫 <b>Oops!</b>

It seems the date got lost in the calendar and can’t find the right format 📅

Let’s try again, but this time in the format DD.MM.YYYY, for example, 25.12.2025
"""

    ADMIN_SERVER = "💻 Server"

    ADMIN_STATISTICS_INFO = """
📊 <b>Statistics</b>

Pick a button:
"""
    ADMIN_STATISTICS_WRITE_TRANSACTION = """
🧾 <b>Type of Transaction!</b>

Click the button 👇
"""
    ADMIN_STATISTICS_CHOOSE_SERVICE = """
🔍 <b>Type of Service for the Transaction!</b>

Click the button 👇
"""
    ADMIN_STATISTICS_CHOOSE_CURRENCY = """
💰 <b>Currency</b>

Click the button 👇
"""
    ADMIN_STATISTICS_SERVICE_QUANTITY = """
✍️ <b>Number of Transactions</b>

Please write the number of transactions
"""
    ADMIN_STATISTICS_SERVICE_AMOUNT = """
🤑 <b>Transaction Amount</b>

Please tell me the transaction amount

Please use a decimal format with a dot, e.g., 999.99.
"""
    ADMIN_STATISTICS_SERVICE_DATE = """
📅 <b>Transaction Date</b>

Write the date when these transactions occurred. Format: "DD.MM.YYYY", e.g., "01.04.2025" or "25.12.2025" 🕰️
"""
    ADMIN_STATISTICS_SERVICE_DATE_VALUE_ERROR = """
🤔 <b>Oops, it seems the date decided to misbehave!</b>

The entered date doesn’t match the format "DD.MM.YYYY"

So, once more: when exactly did this financial miracle occur? 🗓️
"""
    ADMIN_STATISTICS_WRITE_TRANSACTION_SUCCESSFUL = """
🎉 <b>Transaction Successfully Recorded</b>

💰 Thank you for your accuracy and precision
"""

    @staticmethod
    def admin_statistics_processing_request() -> str:
        texts = [
            'Summoning cybernetic ducks to speed up the process. Quack-quack, and we have the data! 🦆💻',
            'Using secret code spells to extract your statistics from the depths of data. Abracadabra! 🧙‍💾',
            'Timer is set, kettle is on. While I brew tea, the data is gathering itself! ☕📊',
            'Connecting to cosmic satellites to find the necessary statistics. Now that’s a stellar search! 🛰️✨',
            'Calling in an army of pixels. They’re already marching through lines of code to deliver your data! 🪖🖥️',
        ]

        return random.choice(texts)
