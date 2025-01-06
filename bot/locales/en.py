import random
from typing import Union

from bot.database.models.product import Product, ProductCategory, ProductType
from bot.database.models.prompt import Prompt
from bot.database.operations.product.getters import get_product
from bot.helpers.formatters.format_number import format_number
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
from bot.database.models.subscription import (
    SubscriptionPeriod,
    SubscriptionStatus,
)
from bot.database.models.user import UserSettings
from bot.locales.types import LanguageCode


class English(Texts):
    # Action
    ACTION_BACK = "Back ◀️"
    ACTION_CLOSE = "Close 🚪"
    ACTION_CANCEL = "Cancel ❌"
    ACTION_APPROVE = "Approve ✅"
    ACTION_DENY = "Deny ❌"

    # Bonus
    @staticmethod
    def bonus_info(user_id: str, balance: float, referred_count: int, feedback_count: int, play_count: int) -> str:
        return f"""
🎁 <b>Your bonus balance</b>

💰 Current balance: {int(balance)} 🪙

To top up your bonus balance, you can:
━ 1️⃣ <b>Invite friends:</b>
    ┣ 💸 For each invited user, you and the invited user will get 25 credits each 🪙
    ┣ 🌟 Your personal referral link for invitations: {Texts.bonus_referral_link(user_id, False)}
    ┗ 👤 You've invited: {referred_count}

━ 2️⃣ <b>Leave feedback:</b>
    ┣ 💸 For each constructive feedback, you get 25 credits 🪙
    ┣ 📡 To leave feedback, enter the command /feedback
    ┗ 💭 You've left: {feedback_count}

━ 3️⃣ <b>Try your luck in one of the games:</b>
    ┣ 🎳 Play bowling and receive as many credits as the number of pins you knock down 1-6 🪙
    ┣ ⚽️ Score a goal and get 5 credits 🪙
    ┣ 🏀 Make a basket and receive 10 credits 🪙
    ┣ 🎯 Hit the bullseye and earn 15 credits 🪙
    ┣ 🎲 Guess the number that will come up on the dice and get 20 credits 🪙
    ┣ 🎰 Hit the Jackpot and receive 50-100 credits 🪙
    ┗ 🎮 You've plaid times: {play_count}

Choose the action:
"""

    BONUS_ACTIVATED_SUCCESSFUL = """
🌟 <b>Bonus activated!</b> 🌟

Congrats! You've successfully used your bonus balance. Now, you can dive deeper into the world of artificial intelligence.

Start using your generations right now and discover new horizons with my neural networks! 🚀
"""
    BONUS_CHOOSE_PACKAGE = "Choose how to spend your earnings:"
    BONUS_INVITE_FRIEND = "👥 Invite a friend"
    BONUS_REFERRAL_SUCCESS = """
🌟 <b>Congrats! Your referral magic worked!</b> 🌟

Thanks to you, a new user has joined, and as a token of my appreciation, your and your friend's balance has been increased by 25 credits 🪙! Use them to access exclusive features or to add more generations in the neural networks 💸

To use the bonus, enter the /bonus command and follow the instructions. Let every invitation bring you not only the joy of communication but also pleasant bonuses!
"""
    BONUS_REFERRAL_LIMIT_ERROR = """
🌟 <b>Congrats! Your referral magic worked!</b> 🌟

Thanks to your efforts, a new user has joined! Unfortunately, we cannot award you a reward, as the limit of rewards for inviting friends has been exceeded

Enter the /bonus command to learn about other ways to earn bonus credits. Keep sharing and enjoy every moment here! 🎉
"""
    BONUS_LEAVE_FEEDBACK = "📡 Leave a feedback"
    BONUS_CASH_OUT = "🛍 Cash out credits"
    BONUS_PLAY = "🎮 Play"
    BONUS_PLAY_GAME = "🎮 Try my luck"
    BONUS_PLAY_GAME_CHOOSE = """
🎮 <b>Choose your game:</b>

━ 🎳 <b>Bowling</b>:
Knock down the pins! Your result: from 1 to 6 — that's the number of credits you'll earn!

━ ⚽️ <b>Football</b>:
The football challenge! Score a goal and receive a guaranteed 5 credits!

━ 🏀 <b>Basketball</b>:
The shot of fate! A precise hand will earn you 10 credits!

━ 🎯 <b>Darts</b>:
Hit the bullseye! A sharp eye could win you 15 credits!

━ 🎲 <b>Dice</b>:
The dice of luck! If fortune favors you, you'll win 20 credits!

━ 🎰 <b>Casino</b>:
🍋 Lucky number! If three matching numbers appear, you'll hit 50 credits!
🎰 Jackpot! Roll three 7️⃣s and score 100 credits!

✨ Remember: You only have one attempt each day, so choose wisely and good luck! 😊
"""
    BONUS_PLAY_BOWLING_GAME = "🎳 Play bowling"
    BONUS_PLAY_BOWLING_GAME_INFO = """
🎳 <b>Bowling: Ready to take your shot?</b>

When you hit the "Play" button, I’ll instantly roll the ball into the pins! Your chance of winning is 100%, because you’re guaranteed to earn credits. It all depends on how many pins I knock down — from 1 to 6. The number of pins knocked down equals your credits!

Every throw is a win, but how big will your victory be?
"""
    BONUS_PLAY_SOCCER_GAME = "⚽️ Play soccer"
    BONUS_PLAY_SOCCER_GAME_INFO = """
⚽️ <b>Football Challenge: Ready to score a goal?</b>

Hit "Play", and I’ll take control of the ball! I’ll launch it straight toward the goal, but luck will decide — there’s a 60% chance to score and win credits!

If I hit the target, you’ll earn 5 credits. Ready to see if this will be the winning goal?
"""
    BONUS_PLAY_BASKETBALL_GAME = "🏀 Play basketball"
    BONUS_PLAY_BASKETBALL_GAME_INFO = """
🏀 <b>Shot of Fate: Time to take the shot!</b>

Hit "Play", and I’ll make the crucial shot at the basketball hoop! There’s a 40% chance the ball will land perfectly, and if it does — you’ll earn 10 credits!

Will I nail this shot like a pro? Let’s find out after the throw!
"""
    BONUS_PLAY_DARTS_GAME = "🎯 Play darts"
    BONUS_PLAY_DARTS_GAME_INFO = """
🎯 <b>Bullseye Challenge: Can you hit the mark?</b>

Hit "Play", and I’ll throw the dart straight at the target! There’s a ~16.67% chance of hitting the bullseye and winning — it’s not easy, but a victory will earn you 15 credits!

Ready to take the risk and see how accurate I am?
"""
    BONUS_PLAY_DICE_GAME = "🎲 Roll the dice"
    BONUS_PLAY_DICE_GAME_INFO = """
🎲 <b>Lucky Dice: Take a guess!</b>

Pick a number from 1 to 6, and I’ll roll the dice! If you guess the number that comes up, you’ll win a solid 20 credits. But the odds of winning are 1 in 6.

Can you sense your luck and guess which number will land?
"""
    BONUS_PLAY_CASINO_GAME = "🎰 Play at casino"
    BONUS_PLAY_CASINO_GAME_INFO = """
🎰 <b>Casino: Take your luck to the max!</b>

Hit "Play", and I’ll spin the casino reels. If three matching numbers appear — congratulations, you win! There’s a nearly 5% chance to land three of a kind, which will earn you 50 credits. But here’s the twist: if you get three 7s, you hit the Jackpot and score 100 credits! The chance of this super prize is just over 1%, but maybe today is your lucky day?

Go ahead, spin the reels and see what fortune has in store for you!
"""
    BONUS_PLAY_GAME_WON = """
🎉 <b>Congratulations!</b>

Luck is on your side! You’ve won! Your prize is waiting for you in /bonus.

Come back tomorrow for more victories. Luck loves players like you! 🎊
"""
    BONUS_PLAY_GAME_LOST = """
😔 <b>No luck today...</b>

Luck is all about timing! Don’t worry, or I’ll start worrying too!

Try again tomorrow, and maybe fortune will smile on you even brighter! 🍀
"""

    @staticmethod
    def bonus_play_game_reached_limit():
        hours, minutes = get_time_until_limit_update(hours=0)
        return f"""
⏳ <b>Oops, looks like you've already played today!</b>

But don’t worry — tomorrow brings a new chance to test your luck!

Come back in <i>{hours} h. {minutes} min.</i> and show me what you’ve got! 👏
"""

    # Catalog
    CATALOG_INFO = """
📁 <b>Welcome to the Catalog of Possibilities!</b>

Here you’ll find a collection of digital assistant roles and a prompt library for inspiration.

It’s all in your hands – just press the button 👇
"""
    CATALOG_MANAGE = "Manage catalog 🎭"
    CATALOG_DIGITAL_EMPLOYEES = "Roles Catalog 🎭"
    CATALOG_DIGITAL_EMPLOYEES_INFO = """
🎭 <b>Step right up to our role catalogue extravaganza!</b> 🌟

Choose from an array of AI personas, each with its own flair and expertise 🎩

Just hit the button below 👇
"""
    CATALOG_DIGITAL_EMPLOYEES_FORBIDDEN_ERROR = """
🔒 <b>Whoops! Looks like you've hit a VIP-only zone!</b> 🌟

You're just a click away from unlocking my treasure trove of AI roles, but it seems you don't have the golden key yet

No worries, though! You can grab it easily just hitting one of the buttons below:
"""
    CATALOG_PROMPTS = "Prompts Catalog 🗯"
    CATALOG_PROMPTS_CHOOSE_MODEL_TYPE = """
🗯 <b>Welcome to the Prompts Catalog!</b>

Text, graphic, and musical models are ready to inspire you

Simply choose the type you need by clicking the button below 👇
"""
    CATALOG_PROMPTS_CHOOSE_CATEGORY = """
🗯 <b>Prompts Catalog</b>

Select the <b>category</b> you need by clicking the button below 👇
"""
    CATALOG_PROMPTS_CHOOSE_SUBCATEGORY = """
🗯 <b>Prompts Catalog</b>

Select the <b>subcategory</b> you need by clicking the button below 👇
"""

    @staticmethod
    def catalog_prompts_choose_prompt(prompts: list[Prompt]):
        prompt_info = ''
        for index, prompt in enumerate(prompts):
            is_last = index == len(prompts) - 1
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            prompt_info += f'    {left_part} <b>{index + 1}</b>: {prompt.names.get(LanguageCode.EN)}{right_part}'

        return f"""
🗯 <b>Prompts Catalog</b>

Prompts:
{prompt_info}

Select the <b>prompt number</b> to get the full prompt by clicking the button below 👇
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
🗯 <b>Prompt Catalog</b>

You have selected the prompt: <b>{prompt.names.get(LanguageCode.EN)}</b>
This prompt works well with these models::
{model_info}

Choose what you want to do by clicking the button below 👇
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
    CATALOG_PROMPTS_COPY = "Copy This Prompt 📋"

    # Chats
    @staticmethod
    def chat_info(current_chat_name: str, total_chats: int) -> str:
        return f"""
🗨️ <b>Current chat: {current_chat_name}</b>

Welcome to the dynamic world of AI-powered chats! Here's what you can do:

- Create new thematic chats: Immerse yourself in focused discussions tailored to your interests.
- Switch between chats: Effortlessly navigate through your different chat landscapes.
- Reset chats: I'll forget what we talked about, so to speak, I'll lose the context.
- Delete chats: Clean up by removing the chats you no longer need.

📈 Total chats: <b>{total_chats}</b>

Ready to tailor your chat experience? Explore the options below and let the conversations begin! 👇
"""

    CHAT_DEFAULT_TITLE = "New chat"
    CHAT_MANAGE = "Manage chats 💬"
    CHAT_SHOW = "Show chats 👁️"
    CHAT_CREATE = "Create a new chat 💬"
    CHAT_CREATE_SUCCESS = "💬 Chat created! 🎉\n👌 Don't forget to switch to a new one using /settings"
    CHAT_TYPE_TITLE = "Type your chat title"
    CHAT_SWITCH = "Switch between chats 🔄"
    CHAT_SWITCH_FORBIDDEN_ERROR = """
🔄 <b>Switching gears? Hold that thought!</b> ⚙️

You're currently in your one and only chat universe. It's a cozy place, but why not expand your horizons? 🌌

To hop between multiple thematic chats, just get your pass by clicking one of the buttons below:
"""
    CHAT_SWITCH_SUCCESS = "Chat successfully switched! 🎉"
    CHAT_RESET = "Reset chat ♻️"
    CHAT_RESET_WARNING = """
🧹 <b>Chat cleanup incoming!</b> 🚨

You're about to erase all messages and clear the context of this chat. This action is irreversible, and all your messages will vanish into virtual dust. Are you sure you want to proceed?

✅ <b>Approve</b> - Yes, let's start with a clean slate.
❌ <b>Cancel</b> - No, I still have more to say!
"""
    CHAT_RESET_SUCCESS = """
🧹<b>Chat successfully cleared!</b> ✨

Now, like a goldfish, I don't remember what was said before 🐠
"""
    CHAT_DELETE = "Delete a chat 🗑"
    CHAT_DELETE_FORBIDDEN_ERROR = """
🗑️ <b>Delete this chat? That's lonely talk!</b> 💬

This is your sole chat kingdom, and a kingdom needs its king or queen! Deleting it would be like canceling your own party 🎈

How about adding more chats to your realm instead? Check out buttons below to build your chat empire:
"""
    CHAT_DELETE_SUCCESS = "🗑️ Chat successfully deleted! 🎉"

    # Eightify
    EIGHTIFY_INFO = """
Using <b>YouTube Summary</b> you can get a concise text summary of any YouTube video

<b>How does it work?</b>
🔗 Send me the link to the YouTube video you need
✅ I'll analyze the video and provide you with a text summary

Looking forward to your link! 😊
"""
    EIGHTIFY_VALUE_ERROR = "This doesn't seem to be a YouTube link 🧐\n\nPlease send me a different one"
    EIGHTIFY_VIDEO_ERROR = "Unfortunately, I can't process this YouTube video 😢\n\nPlease send another link"

    # Errors
    ERROR = """
I've got an unknown error 🤒

Please try again or contact our tech support:
"""
    ERROR_NETWORK = """
I lost my connection with Telegram 🤒

Please try again 🥺
"""
    ERROR_PROMPT_REQUIRED = """
🚨 <b>Hold on! Where's the prompt?</b> 🧐

Looks like we're missing a prompt here, like tea without sugar — no taste at all ☕️

Go ahead, write something — and the magic will begin! 🪄
"""
    ERROR_PROMPT_TOO_LONG = """
🚨 <b>Whoa! This isn't a prompt; it's a whole novel!</b> 😅

Try trimming it down a bit so the model doesn't go on vacation 🌴

Keep it short and sweet, and it will create a masterpiece! ✨
"""
    ERROR_REQUEST_FORBIDDEN = """
<b>Oops! Your request just bumped into our safety guardian!</b> 🚨

It seems there's something in your request that my coworker vigilant content defender decided to block 🛑
Please check your text for any forbidden content and try again!

My goal is safety and respect for every user! 🌟
"""
    ERROR_PHOTO_FORBIDDEN = """
⚠️ Sending photos is only available in models:

🔤 <b>Text Models</b>:
    ┣ ChatGPT 4.0 Omni Mini ✉️
    ┣ ChatGPT 4.0 Omni 💥
    ┣ ChatGPT o1 🧪
    ┣ Claude 3.5 Sonnet 💫
    ┣ Claude 3.0 Opus 🚀
    ┣ Gemini 1.5 Flash 🏎
    ┣ Gemini 1.5 Pro 💼
    ┣ Gemini 1.0 Ultra 🛡️
    ┗ Grok 2.0 🐦

🖼 <b>Image Models</b>:
    ┣ 🎨 Midjourney
    ┣ 🎆 Stable Diffusion
    ┣ 🫐 Flux
    ┣ 🌌 Luma Photon
    ┣ 📷 FaceSwap
    ┗ 🪄 Photoshop AI

📹 <b>Video Models</b>:
    ┣ 🎬 Kling
    ┣ 🎥 Runway
    ┗ 🔆 Luma Ray

Use the button below to switch to a model that supports image vision 👀
"""
    ERROR_PHOTO_REQUIRED = "A photo is required for this model ⚠️\n\nPlease send a photo together with your prompt"
    ERROR_ALBUM_FORBIDDEN = "In the current AI model, I can't process multiple photos at once, please send one 🙂"
    ERROR_VIDEO_FORBIDDEN = "I don't know how to work with videos in this AI model yet 👀"
    ERROR_DOCUMENT_FORBIDDEN = "I don't know how to work with such documents yet 👀"
    ERROR_STICKER_FORBIDDEN = "I don't know how to work with stickers yet 👀"
    ERROR_SERVER_OVERLOADED = "I have a heavy load on the server right now 🫨\n\nPlease, try later!"
    ERROR_FILE_TOO_BIG = """
🚧 <b>Oops!</b>

The file you sent is too large. I can only process files smaller than 20MB.

Please try again with a smaller file 😊
"""
    ERROR_IS_NOT_NUMBER = """
🚧 <b>Whoops!</b>

That doesn't seem like a number 🤔

Can you please enter a numeric value? 🔢
"""

    # Examples
    EXAMPLE_INFO = "Here's what you can do to gain access to this AI:"

    @staticmethod
    def example_text_model(model: str):
        return f"👇 This is how *{model}* would respond to your request"

    @staticmethod
    def example_image_model(model: str):
        return f"☝️ These are the images that <b>{model}</b> would draw for your request"

    # FaceSwap
    FACE_SWAP_INFO = """
🌟<b>Let's get creative with your photos!</b>

Ready? Let's dive into a world of imagination! 🚀

- 📷 <b>Send me a photo with a face</b> for face swapping in FaceSwap!
- ✍️ <b>Send me any prompt</b>, and I’ll generate an image replacing it with your face!
- 🔄 Or just <b>select a package below</b> and start your photo adventure 👇
"""
    FACE_SWAP_GENERATIONS_IN_PACKAGES_ENDED = """
🎨 <b>Wow, you've used up all your generations in our packages! Your creativity is astounding!</b> 🌟

What's next?
- 📷 Send me a photo with a face for face swapping in FaceSwap!
- ✍️ Send me any prompt, and I’ll generate an image replacing it with your face!
- 🔄 Or switch models via /model to continue creating with other AI tools!

Time for new AI discoveries! 🚀
"""
    FACE_SWAP_MIN_ERROR = """
🤨 <b>Hold on there, partner!</b>

Looks like you're trying to request fewer than 1 image. In the world of creativity, I need at least 1 to get the ball rolling!

🌟 <b>Tip</b>: Type a number greater than 0 to start the magic. Let's unleash those creative ideas!
"""
    FACE_SWAP_MAX_ERROR = """
🚀 <b>Whoa, aiming high, I see!</b> But, uh-oh...

You're asking for more images than we have.

🧐 <b>How about this?</b> Let's try a number within the package limit!
"""
    FACE_SWAP_NO_FACE_FOUND_ERROR = """
🚫 <b>Problem with Photo Processing</b>

Unfortunately, we were unable to clearly identify a face in the photo from your /profile
Please upload a new photo where your face is clearly visible and in good quality via the /profile command.

🔄 After uploading a new photo, please try again. Thank you for your patience!
"""

    @staticmethod
    def face_swap_choose_package(name: str, available_images: int, total_images: int, used_images: int) -> str:
        remain_images = total_images - used_images
        return f"""
<b>{name}</b>

You've got a treasure trove of <b>{total_images} images</b> in your pack, ready to unleash your creativity! 🌟

🌠 <b>Your available generations</b>: {available_images} images. Need more? Explore /buy or /bonus!
🔍 <b>Used so far</b>: {used_images} images. {'Wow, you are on a roll!' if used_images > 0 else ''}
🚀 <b>Remaining</b>: {remain_images} images. {'Looks like you have used them all' if remain_images == 0 else 'So much potential'}!

📝 <b>Type how many face swaps you want to do, or choose from the quick selection buttons below</b>. The world of face transformations awaits! 🎭🔄
"""

    @staticmethod
    def face_swap_package_forbidden_error(available_images: int) -> str:
        return f"""
🔔 <b>Oops, a little hiccup!</b> 🚧

Looks like you've got only <b>{available_images} generations</b> left in your arsenal.

💡 <b>Pro Tip</b>: Sometimes, less is more! Try a smaller number, or give /buy a whirl for unlimited possibilities!
"""

    # Feedback
    FEEDBACK_INFO = """
🌟 <b>Your opinion matters!</b> 🌟

Hey there! I'm always looking to improve and your feedback is like gold dust to me ✨

- Love something about me? Let me know 😊
- Got a feature request? I'm all ears 🦻
- Something bugging you? I'm here to squash those bugs 🐞

And remember, every piece of feedback is a step towards making me even more awesome. Can't wait to hear from you! 💌
"""
    FEEDBACK_SUCCESS = """
🌟 <b>Feedback received!</b> 🌟

Your input is the secret sauce to my success. I'm cooking up some improvements and your feedback is the key ingredient 🍳🔑
I will add 25 credits to your balance after my creators check the content of the feedback, but in the meantime, happy chatting!

Your opinion matters a lot to me! 💖
"""
    FEEDBACK_APPROVED = """
🌟 <b>Feedback approved!</b> 🌟

As a token of appreciation, your balance has increased by 25 credits 🪙! Use them to access exclusive functions or replenish the number of generations in neural networks 💸

To use the bonus, enter the command /bonus and follow the instructions!
"""
    FEEDBACK_APPROVED_WITH_LIMIT_ERROR = """
🌟 <b>Feedback approved!</b> 🌟

Thanks to your efforts, we will improve the boat! But, unfortunately, we cannot award you a reward, as the limit of rewards for feedback has been exceeded

Enter the /bonus command to learn about other ways to earn bonus credits. Keep sharing and enjoy every moment here! 🎉
"""
    FEEDBACK_DENIED = """
🌟 <b>Feedback denied!</b> 🌟

Unfortunately, your feedback was not constructive enough and I cannot increase your bonus balance 😢

But don't worry! You can enter the command /bonus to see the other ways to top up the bonus balance!
"""

    # Flux
    FLUX_STRICT_SAFETY_TOLERANCE = "🔒 Strict"
    FLUX_MIDDLE_SAFETY_TOLERANCE = "🔏 Average"
    FLUX_PERMISSIVE_SAFETY_TOLERANCE = "🔓 Weak"

    # Gemini Video
    GEMINI_VIDEO = '📼 Video Summary'
    GEMINI_VIDEO_INFO = """
With <b>Video Summary</b>, you can get a concise text summary of any video.

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
    GEMINI_VIDEO_TOO_LONG_ERROR = "The video length must be less than 60 minutes ⚠️\n\nPlease send a different video"
    GEMINI_VIDEO_VALUE_ERROR = "This doesn’t look like a video link 🧐\n\nPlease send a different link"

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
    GENDER_UNSPECIFIED = "Unspecified 🤷"
    GENDER_MALE = "Male 👕"
    GENDER_FEMALE = "Female 👚"

    # Generation
    GENERATION_IMAGE_SUCCESS = "✨ Here's your image creation 🎨"
    GENERATION_VIDEO_SUCCESS = "✨ Here's your video creation 🎞"

    # Help
    HELP_INFO = """
🤖 <b>Here's what you can explore:</b>

━ Common commands:
    ┣ 👋 /start - <b>About me</b>: Discover what I can do for you
    ┣ 👤 /profile - <b>View your profile</b>: Check your usage quota or subscription details and more
    ┣ 🌍 /language - <b>Switch languages</b>: Set your preferred language for the interface
    ┣ 💳 /buy - <b>Subscribe or buy packages</b>: Get a new level
    ┣ 🎁 /bonus - Learn about your bonus balance and <b>exchange bonuses for generation packages</b>
    ┣ 🔑 /promo_code - <b>Activate promo code</b> if you have it
    ┣ 📡 /feedback - <b>Leave feedback</b>: Help me improve
    ┗ 📄 /terms - <b>TOS</b>: Terms of Service

━ AI commands:
    ┣ 🤖 /model - <b>Swap neural network models</b> on the fly with — all models are there
    ┣ ℹ️ /info - <b>Get information about AI</b>: Learn for what and why do you need them
    ┣ 📁 /catalog - <b>Catalog of roles and prompts</b>: Boost your communication efficiency with me
    ┣ 💥 /chatgpt - <b>Chat with ChatGPT</b>: Start a text conversation and receive advanced AI responses
    ┣ 🚀 /claude - <b>Chat with Claude</b>: Begin a discussion and explore the depth of responses from Claude
    ┣ ✨ /gemini - <b>Chat with Gemini</b>: Start chatting and immerse yourself in advanced answers from the new AI
    ┣ 🐦 /grok - <b>Chat with Grok</b>: Experience cutting-edge analytical AI capabilities from X
    ┣ 🌐 /perplexity - <b>Chat with Perplexity</b>: Get answers to complex questions with Perplexity's internet search
    ┣ 👀 /youtube_summary - <b>YouTube Summarization</b>: Send a video link and receive a summary
    ┣ 📼 /video_summary - <b>Summarization for Any Video</b>: Send a video link or upload your own and get a summary
    ┣ 👨‍🎨 /dalle - <b>Draw with DALL-E</b>: Turn your ideas into drawings
    ┣ 🎨 /midjourney - <b>Create with DALL-E 3</b>: Bring your imaginations to life with images
    ┣ 🎆 /stable_diffusion - <b>Uniqueness with Stable Diffusion</b>: Create unique images
    ┣ 🫐 /flux - <b>Experiments with Flux</b>: Explore endless image variations without limitations
    ┣ 🌌 /luma_photon - <b>Create Art with Luma Photon</b>: Turn your ideas into stunning visual projects
    ┣ 📷️ /face_swap - <b>Have fun with FaceSwap</b>: Change faces in photos
    ┣ 🪄 /photoshop - <b>Magic with Photoshop AI</b>: Retouch and edit your photos with one touch
    ┣ 🎺 /music_gen - <b>Melodies with MusicGen</b>: Create music without copyrights
    ┣ 🎸 /suno - <b>Songs with Suno</b>: Create your own song with your lyrics and different genres
    ┣ 🎬 /kling - <b>Video with Kling</b>: Create high-quality videos
    ┣ 🎥 /runway - <b>Video with Runway</b>: Generate creative videos from a photo
    ┣ 🔆 /luma_ray - <b>Video with Luma Ray</b>: Transform your ideas into video clips with innovative precision
    ┗ 🔧 /settings - <b>Customize your experience</b>: Tailor model to fit your needs. There you can also <b>select a digital employee</b> with <b>context-specific chats management</b>

Just enter the command. For any questions, you can also contact technical support:
"""

    # Info
    INFO = "🤖 <b>Select the models type you want to get information about:</b>"
    INFO_TEXT_MODELS = "🤖 <b>Select the text model you want to get information about:</b>"
    INFO_IMAGE_MODELS = "🤖 <b>Select the graphic model you want to get information about:</b>"
    INFO_MUSIC_MODELS = "🤖 <b>Select the music model you want to get information about:</b>"
    INFO_VIDEO_MODELS = "🤖 <b>Select the video model you want to get information about:</b>"
    INFO_CHAT_GPT = """
🤖 <b>There is what each model can do for you:</b>

✉️ <b>ChatGPT 4.0 Omni Mini: The Versatile Communicator</b>
- <i>Small Talk to Deep Conversations</i>: Ideal for chatting about anything from daily life to sharing jokes.
- <i>Educational Assistant</i>: Get help with homework, language learning, or complex topics like coding.
- <i>Personal Coach</i>: Get motivation, fitness tips, or even meditation guidance.
- <i>Creative Writer</i>: Need a post, story, or even a song? ChatGPT 4.0 Omni Mini can whip it up in seconds.
- <i>Travel Buddy</i>: Ask for travel tips, local cuisines, or historical facts about your next destination.
- <i>Business Helper</i>: Draft emails, create business plans, or brainstorm marketing ideas.

💥 <b>ChatGPT 4.0 Omni: Next-Generation Intelligence</b>
- <i>Detailed Analysis</i>: Perfect for in-depth research, complex technical explanations, or virtual scenario analysis.
- <i>Complex Problem Solving</i>: From mathematical calculations to diagnosing software issues and answering scientific queries.
- <i>Language Mastery</i>: High-level translation and enhancement of conversational skills in various languages.
- <i>Creative Mentor</i>: Inspiring ideas for blogs, scripts, or artistic research.
- <i>Personalized Recommendations</i>: Tailored picks for books, movies, or travel routes based on your preferences.

🧩 <b>ChatGPT o1-mini: A Mini Expert for Problem Solving</b>
- <i>Deep Analysis</i>: Assists with logical reasoning and solving complex problems.
- <i>Critical Thinking</i>: Excels at tasks that require attention to detail and well-reasoned conclusions.
- <i>Educational Assistant</i>: Helps with solutions in programming, mathematics, or scientific research.
- <i>Efficiency</i>: Provides quick and accurate answers to both practical and theoretical questions.

🧪 <b>ChatGPT o1: A Revolution in Reasoning</b>
- <i>Advanced Data Analysis</i>: Suitable for processing and analyzing large volumes of information.
- <i>Argumentative Problem Solving</i>: Ideal for tasks that require well-justified conclusions and complex logical structures.
- <i>Hypothesis Generation</i>: Perfect for scientific research and experimentation.
- <i>Strategy Development</i>: Can assist with developing complex strategies in business or personal projects.
"""
    INFO_CLAUDE = """
🤖 <b>There is what each model can do for you:</b>

📜 <b>Claude 3.5 Haiku: The Art of Brevity and Wisdom</b>
- <i>Deep and Concise Responses</i>: Perfect for brief yet meaningful insights and advice.
- <i>Quick Problem Solving</i>: Instantly delivers solutions for everyday and technical questions.
- <i>Linguistic Precision</i>: Mastery in expressing the essence in a few words, whether it's translation or explanation.
- <i>Creativity in Minimalism</i>: Supports creating short-form content, from poems to succinct ideas.

💫 <b>Claude 3.5 Sonnet: A Balance of Speed and Wisdom</b>
- <i>Multifunctional Analysis</i>: Effective for comprehensive research and technical explanations.
- <i>Problem Solving</i>: Assistance with solving mathematical issues, software bugs, or scientific puzzles.
- <i>Linguistic Expert</i>: A reliable assistant for translating texts and enhancing conversational skills in various languages.
- <i>Creative Advisor</i>: Development of creative ideas for content and artistic projects.
- <i>Personal Guide</i>: Recommendations for cultural content and travel planning tailored to your interests.

🚀 <b>Claude 3.0 Opus: The Pinnacle of Power and Depth</b>
- <i>Advanced Analysis</i>: Ideal for tackling the most complex research and hypothetical scenarios.
- <i>Problem Solving Expert</i>: Addresses challenging scientific inquiries, technical issues, and mathematical problems.
- <i>Language Mastery</i>: Translations and language practice at a professional level.
- <i>Creative Consultant</i>: Support in developing unique ideas for scripts and art projects.
- <i>Recommendations Concierge</i>: Expert advice on selecting books, movies, and travel plans that match your tastes.
"""
    INFO_GEMINI = """
🤖 <b>There is what each model can do for you:</b>

🏎 <b>Gemini 2.0 Flash: Speed and Efficiency</b>
- <i>Quick Data Analysis</i>: Ideal for tasks that require instant data processing and response generation.
- <i>Immediate Results</i>: Perfect for fast information retrieval and instant problem-solving.
- <i>Simplified Problem Solving</i>: Capable of assisting with basic calculations, daily tasks, and fast queries.
- <i>Seamless Interaction</i>: Provides users with accurate information in minimal time, ensuring a high level of precision.

💼 <b>Gemini 1.5 Pro: Professional Power</b>
- <i>In-Depth Analysis</i>: Excels in complex research, deep data analysis, and detailed technical explanations.
- <i>Comprehensive Problem Solving</i>: Suited for high-level tasks, scientific challenges, and complex mathematical questions.
- <i>Linguistic Flexibility</i>: Assists with translations, text editing, and supports multiple languages at a professional level.
- <i>Creative Thinking</i>: Aids in developing ideas for creative projects, writing, and other artistic tasks.
- <i>Personalized Recommendations</i>: Offers expert advice on content selection and event planning based on individual preferences.

🛡 <b>Gemini 1.0 Ultra: Power and Precision</b>
- <i>Unlimited Analytics</i>: Excels in handling complex tasks, deep analysis, and large-scale data processing.
- <i>Accurate Solutions</i>: Ideal for complex calculations and scientific research.
- <i>Linguistic Mastery</i>: Expertise in translations and support for language tasks at the highest level.
- <i>Creative Inspiration</i>: A valuable assistant in the creation and development of complex creative projects and ideas.
- <i>Personalized Interaction</i>: Tailors its responses to your specific needs and preferences.
"""
    INFO_GROK = """
🤖 <b>There is what the model can do for you:</b>

🐦 <b>Grok 2.0: Context Master</b>
- <i>Adaptive Analysis</i>: Perfect for deep contextual understanding and analyzing complex data.
- <i>Long Text Processing</i>: Efficiently handles large volumes of information while retaining key insights.
- <i>Creative Mentor</i>: Helps generate ideas for projects, articles, or scientific research.
- <i>Learning and Mentorship</i>: Provides clear explanations of complex topics, assisting with educational and professional tasks.
- <i>Strategy Development</i>: Supports creating strategies for business or personal goals based on in-depth analytical insights.
"""
    INFO_PERPLEXITY = """
🤖 <b>There is what the model can do for you:</b>

🌐 <b>Perplexity: Instant Answers with Global Reach</b>
- <i>Global Information</i>: Exceptional ability to provide factual data and reference sources.
- <i>Navigate Complex Topics</i>: Helps you understand anything from simple to the most intricate questions.
- <i>Real-World Problem Solving</i>: Quick recommendations for business, education, and everyday life.
- <i>Search on Demand</i>: Excels at handling specific queries, providing precise answers.
- <i>User-Friendly Interface</i>: Easily integrates into your tasks and projects for convenient use.
"""
    INFO_DALL_E = """
🤖 <b>There is what the model can do for you:</b>

👨‍🎨 <b>DALL-E: The Creative Genius</b>
- <i>Art on Demand</i>: Generate unique art from descriptions – perfect for illustrators or those seeking inspiration.
- <i>Ad Creator</i>: Produce eye-catching images for advertising or social media content.
- <i>Educational Tool</i>: Visualize complex concepts for better understanding in education.
- <i>Interior Design</i>: Get ideas for room layouts or decoration themes.
- <i>Fashion Design</i>: Create clothing designs or fashion illustrations.
"""
    INFO_MIDJOURNEY = """
🤖 <b>There is what the model can do for you:</b>

🎨 <b>Midjourney: Navigator of Creativity</b>
- <i>Art Design</i>: Creating visual masterpieces and abstractions, ideal for artists and designers in search of a unique style.
- <i>Architectural modeling</i>: Generation of conceptual designs of buildings and space layouts.
- <i>Educational assistant</i>: Illustrations for educational materials that improve the perception and understanding of complex topics.
- <i>Interior design</i>: Visualization of interior solutions, from classics to modern trends.
- <i>Fashion and style</i>: The development of fashionable bows and accessories, experiments with colors and shapes.
"""
    INFO_STABLE_DIFFUSION = """
🤖 <b>There is what the model can do for you:</b>

🎆 <b>Stable Diffusion: Image Generation Tool</b>
- <i>Creative Illustration</i>: Generate unique images based on text prompts, perfect for artists, designers, and writers.
- <i>Concept Art and Sketches</i>: Create conceptual images for games, films, and other projects, helping visualize ideas.
- <i>Image Stylization</i>: Transform existing images into different artistic styles, from comic book designs to classic painting styles.
- <i>Design Prototyping</i>: Quickly generate visual concepts for logos, posters, or web design projects.
- <i>Art Style Experimentation</i>: Experiment with colors, shapes, and textures to develop new visual solutions.
"""
    INFO_FLUX = """
🤖 <b>There is what the model can do for you:</b>

🫐 <b>Flux: Experiments with Flux</b>

- <i>Endless Variations</i>: Generate diverse images from a single prompt, each result being unique.
- <i>Fine-Tuning Parameters</i>: Control the image creation process to achieve results tailored to your specific needs.
- <i>Randomized Generation</i>: Introduce elements of randomness to create unexpectedly creative outcomes.
- <i>Diverse Visual Concepts</i>: Explore a wide range of artistic styles and approaches, adjusting the process to fit your project.
- <i>Fast Visual Experiments</i>: Experiment with various concepts and styles without limitations, unlocking new creative possibilities.
"""
    INFO_LUMA_PHOTON = """
🤖 <b>There is what the model can do for you:</b>

🌌 <b>Luma Photon: Professional Visualization</b>
- <i>Photorealistic Images</i>: Create high-quality visualizations for architecture, design, and marketing.
- <i>3D Modeling</i>: Generate 3D concepts and visualizations, perfect for presentations and projects.
- <i>Lighting Effects and Textures</i>: Manage complex lighting effects and textures to produce realistic images.
- <i>Creative Rendering</i>: Experiment with compositions and styles to craft unique artistic visualizations.
- <i>Efficiency in Workflow</i>: Ideal for professionals seeking quick, high-quality results for their projects.
"""
    INFO_FACE_SWAP = """
🤖 <b>There is what the model can do for you:</b>

📷️ <b>FaceSwap: The Entertainment Master</b>
- <i>Fun Reimaginations</i>: See how you'd look in different historical eras or as various movie characters.
- <i>Personalized Greetings</i>: Create unique birthday cards or invitations with personalized images.
- <i>Memes and Content Creation</i>: Spice up your social media with funny or imaginative face-swapped pictures.
- <i>Digital Makeovers</i>: Experiment with new haircuts or makeup styles.
- <i>Celebrity Mashups</i>: Combine your face with celebrities for fun comparisons.
"""
    INFO_PHOTOSHOP_AI = """
🤖 <b>There is what the model can do for you:</b>

🪄 <b>Photoshop AI: Magic with Photos</b>
- <i>Photo Restoration</i>: Revives old or damaged photos, returning them to their original state.
- <i>Black-and-White to Color</i>: Breathes life into black-and-white photos by adding vibrant and natural colors.
- <i>Background Removal</i>: Easily removes the background from images, leaving only the main subject.
"""
    INFO_MUSIC_GEN = """
🤖 <b>There is what the model can do for you:</b>

🎺 <b>MusicGen: Your Personal Composer</b>
- <i>Creating Unique Melodies</i>: Turn your ideas into musical pieces of any genre - from classical to pop.
- <i>Personalized Soundtracks</i>: Create a soundtrack for your next video project, game, or presentation.
- <i>Exploring Musical Styles</i>: Experiment with different musical genres and sounds to find your unique style.
- <i>Learning and Inspiration</i>: Gain new insights into music theory and the history of genres through music creation.
- <i>Instant Melody Creation</i>: Just enter a text description or mood, and MusicGen will instantly turn it into music.
"""
    INFO_SUNO = """
🤖 <b>There is what the model can do for you:</b>

🎸 <b>Suno: A Pro in Creating Songs</b>
- <i>Text-to-song transformation</i>: Suno turns your text into songs, matching melody and rhythm to your style.
- <i>Personalized songs</i>: Create unique songs for special moments, whether it's a personal gift or a soundtrack for your event.
- <i>Explore musical genres</i>: Discover new musical horizons by experimenting with different styles and sounds.
- <i>Music education and inspiration</i>: Learn about music theory and the history of genres through the practice of composition.
- <i>Instant music creation</i>: Describe your emotions or scenario, and Suno will immediately bring your description to life as a song.
"""
    INFO_KLING = """
🤖 <b>There is what the model can do for you:</b>

🎬 <b>Kling: High-Quality Video Creation</b>
- <i>Video Generation from Descriptions</i>: Describe your idea, and Kling will create an impressive video clip.
- <i>Work with Unique Styles</i>: Use a variety of styles to emphasize the individuality of your video.
- <i>Dynamic Transitions</i>: Automatically adds smooth and impactful transitions between scenes.
- <i>Creative Visual Effects</i>: Generate videos with modern effects for your projects.
- <i>Content in Minutes</i>: Create impressive video clips in a short time without requiring video editing skills.
"""
    INFO_RUNWAY = """
🤖 <b>There is what the model can do for you:</b>

🎥 <b>Runway: Video Generation</b>
- <i>Create short video clips</i>: Describe an idea or a script and attach the first frame, and Runway will produce a unique video clip.
- <i>Generate videos from photos + text</i>: Turn an image and text description into dynamic videos.
- <i>Animations and visual effects</i>: Generate visually appealing and creative animations based on your ideas.
- <i>AI content for social media</i>: Quickly create engaging videos for platforms and projects.
- <i>Experiment with video formats</i>: Explore AI capabilities to create new styles and video content.
"""
    INFO_LUMA_RAY = """
🤖 <b>There is what the model can do for you:</b>

🔆 <b>Luma Ray: Creativity in Video</b>
- <i>High-Quality Video Clips</i>: Create realistic and dynamic videos based on descriptions.
- <i>3D Animation</i>: Generate stunning three-dimensional animations for your projects.
- <i>Cinematic Style</i>: Apply effects and compositions characteristic of professional cinema.
- <i>Visual Magic</i>: Use cutting-edge technology to produce high-quality content.
- <i>Innovative Video Formats</i>: Experiment with new styles and approaches to video content creation.
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
    MIDJOURNEY_ALREADY_CHOSE_UPSCALE = "You've already chosen this image, try a new one 🙂"

    # Model
    MODEL = "To change a model click a button below 👇"
    MODEL_CHANGE_AI = "🤖 Change AI Model"
    MODEL_CHOOSE_CHAT_GPT = "To choose a <b>ChatGPT 💭</b> model click a button below 👇"
    MODEL_CHOOSE_CLAUDE = "To choose a <b>Claude 📄</b> model click a button below 👇"
    MODEL_CHOOSE_GEMINI = "To choose a <b>Gemini ✨</b> model click a button below 👇"
    MODEL_CONTINUE_GENERATING = "Continue generating"
    MODEL_ALREADY_MAKE_REQUEST = "You've already made a request. Please wait ⚠️"
    MODEL_READY_FOR_NEW_REQUEST = "You can ask the next request 😌"
    MODEL_SWITCHED_TO_AI_SETTINGS = "⚙️ Model's Settings"
    MODEL_SWITCHED_TO_AI_INFO = "ℹ️ Learn More About This Model"
    MODEL_SWITCHED_TO_AI_EXAMPLES = "💡 Show Examples"
    MODEL_ALREADY_SWITCHED_TO_THIS_MODEL = """
🔄 <b>Oops, looks like everything stayed the same!</b>

You've selected the same model that's already active. Don't worry, your digital universe remains unchanged. You can continue chatting or creating as usual. If you want to switch things up, simply choose a different model using /model

Either way, I'm here to help! 🛟
"""

    @staticmethod
    def model_switched(model_name: str, model_type: ModelType, model_info: dict):
        if model_type == ModelType.TEXT:
            facts = f"""⚙️ Facts and Settings:
    ┣ 📅 Knowledge up to: {model_info.get('training_data')}
    ┣ 📷 Image Support: {'Yes ✅' if model_info.get('support_photos', False) else 'No ❌'}
    ┣ 🎙 Voice Answers: {'Enabled ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Disabled ❌'}
    ┗ 🎭 Role: {model_info.get('role')}"""
        elif model_type == ModelType.SUMMARY:
            model_focus = model_info.get(UserSettings.FOCUS, VideoSummaryFocus.INSIGHTFUL)
            if model_focus == VideoSummaryFocus.INSIGHTFUL:
                model_focus = English.VIDEO_SUMMARY_FOCUS_INSIGHTFUL
            elif model_focus == VideoSummaryFocus.FUNNY:
                model_focus = English.VIDEO_SUMMARY_FOCUS_FUNNY
            elif model_focus == VideoSummaryFocus.ACTIONABLE:
                model_focus = English.VIDEO_SUMMARY_FOCUS_ACTIONABLE
            elif model_focus == VideoSummaryFocus.CONTROVERSIAL:
                model_focus = English.VIDEO_SUMMARY_FOCUS_CONTROVERSIAL

            model_format = model_info.get(UserSettings.FORMAT, VideoSummaryFormat.LIST)
            if model_format == VideoSummaryFormat.LIST:
                model_format = English.VIDEO_SUMMARY_FORMAT_LIST
            elif model_format == VideoSummaryFormat.FAQ:
                model_format = English.VIDEO_SUMMARY_FORMAT_FAQ

            model_amount = model_info.get(UserSettings.AMOUNT, VideoSummaryAmount.AUTO)
            if model_amount == VideoSummaryAmount.AUTO:
                model_amount = English.VIDEO_SUMMARY_AMOUNT_AUTO
            elif model_amount == VideoSummaryAmount.SHORT:
                model_amount = English.VIDEO_SUMMARY_AMOUNT_SHORT
            elif model_amount == VideoSummaryAmount.DETAILED:
                model_amount = English.VIDEO_SUMMARY_AMOUNT_DETAILED

            facts = f"""⚙️ Settings:
    ┣ 🎯 Focus: {model_focus}
    ┣ 🎛 Format: {model_format}
    ┣ 📏 Number of Items: {model_amount}
    ┗ 🎙 Voice Answers: {'Enabled ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Disabled ❌'}"""
        elif model_type == ModelType.IMAGE:
            facts = f"""⚙️ Facts and Settings:
    ┣ 📷 Image Support: {'Yes ✅' if model_info.get('support_photos', False) else 'No ❌'}
    ┣ 📐 Aspect Ratio: {'Custom' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
    ┗ 🗯 Sending Type: {English.SETTINGS_SEND_TYPE_DOCUMENT if model_info.get(UserSettings.SEND_TYPE, SendType.IMAGE) == SendType.DOCUMENT else English.SETTINGS_SEND_TYPE_IMAGE}"""
        elif model_type == ModelType.MUSIC:
            facts = f"""⚙️ Settings:
    ┗ 🗯 Sending Type: {English.SETTINGS_SEND_TYPE_VIDEO if model_info.get(UserSettings.SEND_TYPE, SendType.AUDIO) == SendType.VIDEO else English.SETTINGS_SEND_TYPE_AUDIO}"""
        elif model_type == ModelType.VIDEO:
            facts = f"""⚙️ Facts and Settings:
    ┣ 📷 Image Support: {'Yes ✅' if model_info.get('support_photos', False) else 'No ❌'}
    ┣ 📐 Aspect Ratio: {'Custom' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
    ┣ 📏 Duration: {model_info.get(UserSettings.DURATION, 5)} seconds
    ┗ 🗯 Sending Type: {English.SETTINGS_SEND_TYPE_DOCUMENT if model_info.get(UserSettings.SEND_TYPE, SendType.VIDEO) == SendType.DOCUMENT else English.SETTINGS_SEND_TYPE_VIDEO}"""
        else:
            facts = f"ℹ️ Facts and Settings: Coming Soon 🔜"

        return f"""
<b>Selected Model: {model_name}</b>

{facts}

👇 Use the buttons below to explore more:
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
            "Diving into the data ocean to fish out your answer. Be right back... 🌊🎣",
            "I'm consulting with my virtual elves. They're usually great at finding answers... 🧝",
            "Engaging warp drive for hyper-speed answer retrieval. Hold on tight... 🚀",
            "I'm in the kitchen cooking up a fresh batch of answers. This one's gonna be delicious... 🍳",
            "Taking a quick trip to the cloud and back. Hope to bring back some smart raindrops of info... ☁️",
            "Planting your question in my digital garden. Let's see what grows... 🌱🤖",
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
            "Crafting pixels into perfection, just a moment... 👁️🎭",
            "Whipping up a visual feast for your eyes... 🍽️👀",
            "Consulting with digital Da Vinci for your artistic request... 🎭",
            "Dusting off the digital easel for your creative request... 🖼️🖌️",
            "Conjuring a visual spell in the AI cauldron... 🧙‍🔮",
            "Activating the virtual canvas. Get ready for artistry... 🖼️️",
            "Assembling your ideas in a gallery of pixels... 🖼️👨‍🎨",
            "Embarking on a digital safari to capture your artistic vision... 🦁🎨",
            "Revving up the AI art engines, stand by... 🏎️💨",
            "Plunging into a pool of digital imagination... 🏊‍💭",
            "Cooking up a visual symphony in the AI kitchen... 🍳🎼",
            "Pushing the clouds of creativity to craft your visual masterpiece... ☁️🎨",
            "Gathering digital brushes and paints to bring your vision to life... 🎨🖌️",
            "Summoning pixel dragons to create an epic image... 🐉",
            "Bringing in digital bees to collect the nectar for your visual bloom... 🐝",
            "Putting on my digital artist hat and getting to work on your masterpiece... 👒",
            "Dipping pixels into a magical solution so they can shine into a masterpiece... 🧪✨",
            "Sculpting your image from the clay of imagination, a masterpiece is on the way... 🏺",
            "My virtual elves are already painting your image... 🧝‍♂️",
            "Virtual turtles are carrying your image across the sea of data... 🐢",
            "Virtual kitties are paw-painting your masterpiece right now... 🐱",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ Generation can take up to 3 minutes"

        return text

    @staticmethod
    def model_face_swap_processing_request() -> str:
        texts = [
            "Warping into the face-swapping dimension... 🌌👤",
            "Mixing and matching faces like a digital Picasso... 🧑‍🎨🖼️",
            "Swapping faces faster than a chameleon changes colors... 🦎🌈",
            "Unleashing the magic of face fusion... ✨👥",
            "Engaging in facial alchemy, transforming identities... 🧙‍🧬",
            "Cranking up the face-swapping machine... 🤖🔀",
            "Concocting a potion of facial transformation... 🧪👩‍🔬🔬",
            "Casting a spell in the realm of face enchantments... 🧚‍🎭️",
            "Orchestrating a symphony of facial features... 🎼👩‍🎤👨‍🎤",
            "Sculpting new faces in my digital art studio... 🎨👩‍🎨",
            "Brewing a cauldron of face-swap magic... 🧙‍🔮",
            "Building faces like a master architect... 🏗️👷‍",
            "Embarking on a mystical quest for the perfect face blend... 🗺️🔍",
            "Launching a rocket of face morphing adventures... 🚀👨‍🚀👩‍🚀",
            "Embarking on a galactic journey of face swapping... 🌌👽",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ Generation can take up to 5 minutes"

        return text

    @staticmethod
    def model_music_processing_request() -> str:
        texts = [
            "Launching the music generator, hold onto your ears... 🎶👂",
            "Mixing notes like a DJ at a party... 🎧🕺",
            "The melody wizard is in action, get ready for magic... 🧙‍✨",
            "Creating music that will make even robots dance... 🤖💃",
            "The music laboratory is in action, things are heating up... 🔬🔥",
            "Catching a wave of inspiration and turning it into sounds... 🌊🎹",
            "Climbing to musical peaks, anticipate... 🏔️🎶",
            "Creating something that ears have never heard before... 🌟👂",
            "Time to dive into an ocean of harmony and rhythm... 🌊🎶",
            "Opening the door to a world where music creates reality... 🚪🌍",
            "Cracking the codes of composition to create something unique... 🧬🎶",
            "Crafting melodies like a chef crafts culinary masterpieces... 🍽️🎹",
            "Throwing a party on the keys, each note is a guest... 🎉🎹",
            "Carving a path through the melodic labyrinth... 🌀🎵",
            "Turning air vibrations into magical sounds... 🌬️🎼",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ Generation can take up to 10 minutes"

        return text

    @staticmethod
    def model_video_processing_request() -> str:
        texts = [
            "Loading the movie premiere, almost ready... 🎬🍿",
            "The rocket of video creativity is taking off! Fasten your seatbelts... 🚀🎥",
            "Frames are coming to life, camera, action... 🎬💥",
            "Generating a masterpiece frame by frame... 🎥✨",
            "Not just a video, but a cinematic wonder is on its way... 🎞️🌟",
            "Assembling the puzzle of the best shots for your WOW moment... 🤩🎞️",
            "Connecting pixels — expect a video masterpiece... 🎇🎥",
            "Reeling in the best shots, a masterpiece is in progress... 🎥🎣",
            "The editing table is on fire, creating a video masterpiece... 🔥✂️",
            "Loading video content into your dimension... 🖥️🎞️",
            "AI bees are working on your video honey... Get ready for a sweet result... 🐝🍯",
            "The magic projector is already starting up... 🎥✨",
            "The pizza is baking in the oven... oh wait, it’s your video... 🍕🎞️",
            "Casting visual spells, the video will be magical... ✨🎩",
            "Delivering your video on the rails of creativity... 🚉🎥",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ Generation can take up to 20 minutes"

        return text

    @staticmethod
    def model_wait_for_another_request(seconds: int) -> str:
        return f"Please wait for another {seconds} seconds before sending the next question ⏳"

    @staticmethod
    def model_reached_usage_limit():
        hours, minutes = get_time_until_limit_update()

        return f"""
<b>Oops! 🚨</b>

Your today's quota for the current model has just done a Houdini and disappeared! 🎩

🔄 <i>The limit will reset in: {hours} hr. {minutes} min.</i>

❗️Don’t want to wait? Don’t worry, you've got options:
"""

    MODELS_TEXT = "🔤 Text Models"
    MODELS_SUMMARY = "📝 Summary Models"
    MODELS_IMAGE = "🖼 Image Models"
    MODELS_MUSIC = "🎵 Music Models"
    MODELS_VIDEO = "📹 Video Models"

    # MusicGen
    MUSIC_GEN_INFO = """
Your musical workshop 🎹

Open the door to a world where every idea of yours turns into music! With <b>MusicGen</b>, your imagination is the only limit. I'm ready to transform your words and descriptions into unique melodies 🎼

Tell me what kind of music you want to create. Use words to describe its style, mood, and instruments. You don't need to be a professional - just share your idea, and let's bring it to life together! 🎤
"""
    MUSIC_GEN_TYPE_SECONDS = """
<b>How many seconds in your symphony?</b> ⏳

Fantastic! Your melody idea is ready to come to life. Now, the exciting part: how much time do we give this musical magic to unfold in all its glory?
<i>Every 10 seconds consume 1 generation</i> 🎼

Write or choose the duration of your composition in seconds. Whether it's a flash of inspiration or an epic odyssey, I'm ready to create! ✨
"""
    MUSIC_GEN_MIN_ERROR = """
🤨 <b>Hold on there, partner!</b>

Looks like you're trying to request fewer than 10 seconds. In the world of creativity, I need at least 10 to get the ball rolling!

🌟 <b>Tip</b>: Type a number equal or greater than 10 to start the magic!
"""
    MUSIC_GEN_MAX_ERROR = """
🤨 <b>Hold on there, partner!</b>

Looks like you're trying to request more than 3 minutes, I can't generate more yet!

🌟 <b>Tip</b>: Type a number less than 180 to start the magic!
"""
    MUSIC_GEN_SECONDS_30 = "🔹 30 seconds"
    MUSIC_GEN_SECONDS_60 = "🔹 60 seconds (1 minute)"
    MUSIC_GEN_SECONDS_180 = "🔹 180 seconds (3 minutes)"
    MUSIC_GEN_SECONDS_300 = "🔹 300 seconds (5 minutes)"
    MUSIC_GEN_SECONDS_600 = "🔹 600 seconds (10 minutes)"

    @staticmethod
    def music_gen_forbidden_error(available_seconds: int) -> str:
        return f"""
🔔 <b>Oops, a little hiccup!</b> 🚧

Looks like you've got only <b>{available_seconds} seconds</b> left in your arsenal.

💡 <b>Pro Tip</b>: Sometimes, less is more! Try a smaller number, or give /buy a whirl for unlimited possibilities!
"""

    # Notify about quota
    @staticmethod
    def notify_about_quota(
        subscription_limits: dict,
    ) -> str:
        texts = [
            f"""
🤖 Hey, it's me! Remember me?

🤓 I'm here to remind you about your daily quotas:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests waiting to be turned into your masterpieces
- {format_number(subscription_limits[Quota.DALL_E])} graphic opportunity ready to bring your ideas to life

🔥 Don’t let them go to waste — start now!
""",
            f"""
🤖 Hi, it's Fusi, your personal assistant. Yep, I'm back!

😢 I noticed you haven’t used your quotas for a while. Just a friendly reminder that every day you have:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests to fuel your ideas
- {format_number(subscription_limits[Quota.DALL_E])} graphic slot to bring your thoughts to life

✨ Shall we get started? I'm ready right now!
""",
            f"""
🤖 It's me, Fusi, your personal robot, with an important reminder!

🤨 Did you know you have:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests for your bright ideas
- {format_number(subscription_limits[Quota.DALL_E])} image slot to visualize your concepts

🔋 I'm fully charged and ready to help you create something amazing!
""",
            f"""
🤖 It’s me again! I missed you...

😢 I was just thinking... Your quotas might miss you too:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} inspiring text requests are waiting for their moment
- {format_number(subscription_limits[Quota.DALL_E])} visual idea ready to come to life

💡 Give me the chance to help you create something incredible!
""",
            f"""
🤖 Hi, it’s Fusi! Your quotas won’t use themselves, you know that, right?

🫤 Need a reminder? Here you go:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} text requests that could be the start of something big
- {format_number(subscription_limits[Quota.DALL_E])} image slot to sketch out your imagination

✨ Time to create, and I’m here to help. Let’s get started!
""",
        ]

        return random.choice(texts)

    # Open
    OPEN_SETTINGS = "⚙️ Open Settings"
    OPEN_BONUS_INFO = "🎁 Open Bonus Balance"
    OPEN_BUY_SUBSCRIPTIONS_INFO = "💎 Subscribe"
    OPEN_BUY_PACKAGES_INFO = "🛍 Purchase Packages"

    # Package
    PACKAGE = "🛍 Package"
    PACKAGE_SUCCESS = """
🎉 <b>Cha-Ching! Payment success!</b> 💳

Your payment just zoomed through like a superhero! 🦸‍ You've successfully unlocked the awesome power of your chosen package. Get ready for a rollercoaster of AI fun and excitement! 🎢

Remember, with great power comes great... well, you know how it goes. Let's make some magic happen! ✨🪄
"""
    PACKAGE_QUANTITY_MIN_ERROR = "Oops! It looks like the total sum is below our minimum threshold. Please choose count of packages that meets or exceeds the minimum required. Let's try that again! 🔄"
    PACKAGE_QUANTITY_MAX_ERROR = "Oops! It looks like the number entered is higher than you can purchase. Please enter a smaller value or one corresponding to your balance. Let's try that again! 🔄"

    @staticmethod
    def package_info(currency: Currency, cost: str) -> str:
        if currency == Currency.USD:
            cost = f"{Currency.SYMBOLS[currency]}{cost}"
        else:
            cost = f"{cost}{Currency.SYMBOLS[currency]}"

        return f"""
🤖 <b>Welcome to the AI shopping spree!</b> 📦

🪙 <b>1 credit = {cost}</b>

Hit a button and choose a package:
"""

    @staticmethod
    def package_choose_min(name: str) -> str:
        return f"""
🚀 Fantastic!

You've selected the <b>{name}</b> package

🌟 Please <b>type in the number of quantity</b> you'd like to go for
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
🎉 <b>Cha-Ching! Payment success!</b> 💳

Your payment just zoomed through like a superhero! 🦸‍ You've successfully unlocked the awesome power of your chosen packages. Get ready for a rollercoaster of AI fun and excitement! 🎢

Remember, with great power comes great... well, you know how it goes. Let's make some magic happen! ✨🪄
"""
    PACKAGES_END = """
🕒 <b>Your package or packages time is up!</b> ⌛

Oops, it looks like your fast messages (or voice messages, catalog access) package has run its course. But don't worry, new opportunities always await beyond the horizon!

🎁 Want to continue? Check out my offers by hitting one of the buttons below:
"""

    @staticmethod
    def packages_description(user_id: str):
        return f"Paying packages from the cart for user: {user_id}"

    # Payment
    PAYMENT_BUY = """
🚀 <b>Welcome to the Wonder Store!</b> 🪄

You’re stepping into a world of exclusive possibilities! What will it be today?

🌟 <b>Subscriptions: Everything All at Once — Your VIP pass to all AI tools and beyond!</b>
Chatting, image/music/video creation, and much more. All included in the subscription for your convenience and new discoveries every day!

🛍 <b>Packages: Pay only for the generations you need!</b>
Need specific generations for particular tasks? Packages let you choose a set number of requests and AI tools — pay only for what you truly need.

Choose by clicking a button below 👇
"""
    PAYMENT_CHANGE_CURRENCY = "💱 Change currency"
    PAYMENT_YOOKASSA_PAYMENT_METHOD = "🪆💳 YooKassa"
    PAYMENT_STRIPE_PAYMENT_METHOD = "🌍💳 Stripe"
    PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD = "✈️⭐️ Telegram Stars"
    PAYMENT_CHOOSE_PAYMENT_METHOD = """
<b>Choose a payment method:</b>

🪆💳 <b>YooKassa (Russian's Cards)</b>

🌍💳 <b>Stripe (International Cards)</b>

✈️⭐️ <b>Telegram Stars (Currency in Telegram)</b>
"""
    PAYMENT_PROCEED_TO_PAY = "🌐 Proceed to payment"
    PAYMENT_PROCEED_TO_CHECKOUT = "💳 Proceed to checkout"
    PAYMENT_DISCOUNT = "💸 Discount"
    PAYMENT_NO_DISCOUNT = "No discount"

    @staticmethod
    def payment_purchase_minimal_price(currency: Currency, current_price: str):
        left_part_price = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_part_price = '' if currency == Currency.USD else Currency.SYMBOLS[currency]
        return f"""
😕 Oh no...

To complete the purchase, the total amount must be equal to or greater than <b>{left_part_price}{1 if currency == Currency.USD else 50}{right_part_price}</b>
Currently, the total purchase amount is: <b>{left_part_price}{current_price}{right_part_price}</b>
"""

    # Photoshop AI
    PHOTOSHOP_AI_INFO = """
This section brings together AI tools for editing and styling images.

Click the button below to choose an action and start your creative journey! 👇
"""
    PHOTOSHOP_AI_RESTORATION = "Restoration 🖌"
    PHOTOSHOP_AI_RESTORATION_INFO = """
The tool detects scratches and cuts on the original image and removes them.

📸 Upload your image to the chat and let the magic begin! ✨
"""
    PHOTOSHOP_AI_COLORIZATION = "Colorization 🌈"
    PHOTOSHOP_AI_COLORIZATION_INFO = """
The tool allows you to add color to black-and-white images.

📸 Upload your image to the chat and let the magic begin! ✨
"""
    PHOTOSHOP_AI_REMOVE_BACKGROUND = "Background Removal 🗑"
    PHOTOSHOP_AI_REMOVE_BACKGROUND_INFO = """
The tool allows you to remove the background from an image.

📸 Upload your image to the chat and let the magic begin! ✨
"""

    @staticmethod
    def photoshop_ai_actions() -> list[str]:
        return [
            English.PHOTOSHOP_AI_RESTORATION,
            English.PHOTOSHOP_AI_COLORIZATION,
            English.PHOTOSHOP_AI_REMOVE_BACKGROUND,
        ]

    # Profile
    @staticmethod
    def profile(
        subscription_name: str,
        subscription_status: SubscriptionStatus,
        current_model: str,
        current_currency: Currency,
        renewal_date,
    ) -> str:
        if subscription_status == SubscriptionStatus.CANCELED:
            subscription_info = f"📫 <b>Subscription Status:</b> Canceled. Active until {renewal_date}"
        elif subscription_status == SubscriptionStatus.TRIAL:
            subscription_info = f"📫 <b>Subscription Status:</b> Trial Period"
        else:
            subscription_info = "📫 <b>Subscription Status:</b> Active"

        if current_currency == Currency.XTR:
            current_currency = f'Telegram Stars {Currency.SYMBOLS[current_currency]}'
        else:
            current_currency = f'{Currency.SYMBOLS[current_currency]}'

        return f"""
<b>Profile</b> 👤

---------------------------

🤖 <b>Current model: {current_model}</b>
💱 <b>Current currency: {current_currency}</b>
💳 <b>Subscription type:</b> {subscription_name}
🗓 <b>Subscription renewal date:</b> {f'{renewal_date}' if subscription_name != '🆓' else 'N/A'}
{subscription_info}

---------------------------

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
<b>Quota:</b>

🔤 <b>Text Models</b>:
━ <b>Basic</b>:
    ┣ Daily Limits: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI_MINI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])}
    ┣ ✉️ ChatGPT 4.0 Omni Mini{f': extra {additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI] > 0 else ''}
    ┣ 📜 Claude 3.5 Haiku{f': extra {additional_usage_quota[Quota.CLAUDE_3_HAIKU]}' if additional_usage_quota[Quota.CLAUDE_3_HAIKU] > 0 else ''}
    ┗ 🏎 Gemini 2.0 Flash{f': extra {additional_usage_quota[Quota.GEMINI_2_FLASH]}' if additional_usage_quota[Quota.GEMINI_2_FLASH] > 0 else ''}

━ <b>Advanced</b>:
    ┣ Daily Limits: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI])}
    ┣ 💥 ChatGPT 4.0 Omni{f': extra {additional_usage_quota[Quota.CHAT_GPT4_OMNI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI] > 0 else ''}
    ┣ 🧩 ChatGPT o1-mini{f': extra {additional_usage_quota[Quota.CHAT_GPT_O_1_MINI]}' if additional_usage_quota[Quota.CHAT_GPT_O_1_MINI] > 0 else ''}
    ┣ 💫 Claude 3.5 Sonnet{f': extra {additional_usage_quota[Quota.CLAUDE_3_SONNET]}' if additional_usage_quota[Quota.CLAUDE_3_SONNET] > 0 else ''}
    ┣ 💼 Gemini 1.5 Pro{f': extra {additional_usage_quota[Quota.GEMINI_1_PRO]}' if additional_usage_quota[Quota.GEMINI_1_PRO] > 0 else ''}
    ┣ 🐦 Grok 2.0{f': extra {additional_usage_quota[Quota.GROK_2]}' if additional_usage_quota[Quota.GROK_2] > 0 else ''}
    ┗ 🌐 Perplexity{f': extra {additional_usage_quota[Quota.PERPLEXITY]}' if additional_usage_quota[Quota.PERPLEXITY] > 0 else ''}

━ <b>Flagship</b>:
    ┣ Daily Limits: {format_number(daily_limits[Quota.CHAT_GPT_O_1])}/{format_number(subscription_limits[Quota.CHAT_GPT_O_1])}
    ┣ 🧪 ChatGPT o1{f': extra {additional_usage_quota[Quota.CHAT_GPT_O_1]}' if additional_usage_quota[Quota.CHAT_GPT_O_1] > 0 else ''}
    ┣ 🚀 Claude 3.0 Opus{f': extra {additional_usage_quota[Quota.CLAUDE_3_OPUS]}' if additional_usage_quota[Quota.CLAUDE_3_OPUS] > 0 else ''}
    ┗ 🛡️ Gemini 1.0 Ultra{f': extra {additional_usage_quota[Quota.GEMINI_1_ULTRA]}' if additional_usage_quota[Quota.GEMINI_1_ULTRA] > 0 else ''}

---------------------------

📝 <b>Summary Models</b>:
    ┣ Daily Limits: {format_number(daily_limits[Quota.EIGHTIFY])}/{format_number(subscription_limits[Quota.EIGHTIFY])}
    ┣ 👀 YouTube{f': extra {additional_usage_quota[Quota.EIGHTIFY]}' if additional_usage_quota[Quota.EIGHTIFY] > 0 else ''}
    ┗ 📼 Video{f': extra {additional_usage_quota[Quota.GEMINI_VIDEO]}' if additional_usage_quota[Quota.GEMINI_VIDEO] > 0 else ''}

---------------------------

🖼 <b>Image Models</b>:
    ┣ Daily Limits: {format_number(daily_limits[Quota.DALL_E])}/{format_number(subscription_limits[Quota.DALL_E])}
    ┣ 👨‍🎨 DALL-E{f': extra {additional_usage_quota[Quota.DALL_E]}' if additional_usage_quota[Quota.DALL_E] > 0 else ''}
    ┣ 🎨 Midjourney{f': extra {additional_usage_quota[Quota.MIDJOURNEY]}' if additional_usage_quota[Quota.MIDJOURNEY] > 0 else ''}
    ┣ 🎆 Stable Diffusion{f': extra {additional_usage_quota[Quota.STABLE_DIFFUSION]}' if additional_usage_quota[Quota.STABLE_DIFFUSION] > 0 else ''}
    ┣ 🫐 Flux{f': extra {additional_usage_quota[Quota.FLUX]}' if additional_usage_quota[Quota.FLUX] > 0 else ''}
    ┣ 🌌 Luma Photon{f': extra {additional_usage_quota[Quota.LUMA_PHOTON]}' if additional_usage_quota[Quota.LUMA_PHOTON] > 0 else ''}
    ┣ 📷 FaceSwap{f': extra {additional_usage_quota[Quota.FACE_SWAP]}' if additional_usage_quota[Quota.FACE_SWAP] > 0 else ''}
    ┗ 🪄 Photoshop AI{f': extra {additional_usage_quota[Quota.PHOTOSHOP_AI]}' if additional_usage_quota[Quota.PHOTOSHOP_AI] > 0 else ''}

---------------------------

🎵 <b>Music Models</b>:
    ┣ Daily Limits: {format_number(daily_limits[Quota.SUNO])}/{format_number(subscription_limits[Quota.SUNO])}
    ┣ 🎺 MusicGen{f': extra {additional_usage_quota[Quota.MUSIC_GEN]}' if additional_usage_quota[Quota.MUSIC_GEN] > 0 else ''}
    ┗ 🎸 Suno{f': extra {additional_usage_quota[Quota.SUNO]}' if additional_usage_quota[Quota.SUNO] > 0 else ''}

---------------------------

📹 <b>Video Models</b>:
    ┣ 🎬 Kling{f': extra {additional_usage_quota[Quota.KLING]}' if additional_usage_quota[Quota.KLING] > 0 else ''}
    ┣ 🎥 Runway{f': extra {additional_usage_quota[Quota.RUNWAY]}' if additional_usage_quota[Quota.RUNWAY] > 0 else ''}
    ┗ 🔆 Luma Ray{f': extra {additional_usage_quota[Quota.LUMA_RAY]}' if additional_usage_quota[Quota.LUMA_RAY] > 0 else ''}

---------------------------

🎭 <b>Access to a catalog with digital employees</b>: {'✅' if daily_limits[Quota.ACCESS_TO_CATALOG] or additional_usage_quota[Quota.ACCESS_TO_CATALOG] else '❌'}
🎙 <b>Voice messages</b>: {'✅' if daily_limits[Quota.VOICE_MESSAGES] or additional_usage_quota[Quota.VOICE_MESSAGES] else '❌'}
⚡ <b>Fast answers</b>: {'✅' if daily_limits[Quota.FAST_MESSAGES] or additional_usage_quota[Quota.FAST_MESSAGES] else '❌'}

---------------------------

🔄 <i>Limit will be updated in: {hours} h. {minutes} min.</i>
"""

    PROFILE_SHOW_QUOTA = "🔄 Show Quota"
    PROFILE_TELL_ME_YOUR_GENDER = "Tell me your gender:"
    PROFILE_YOUR_GENDER = "Your gender:"
    PROFILE_SEND_ME_YOUR_PICTURE = """
📸 <b>Ready for a photo transformation? Send a photo of yours!</b>

👍 <b>Ideal photo guidelines</b>:
- Clear, high-quality selfie.
- Only one person should be in the selfie.

👎 <b>Please avoid these types of photos</b>:
- Group photos.
- Animals.
- Children under 18 years.
- Full body shots.
- Nude or inappropriate images.
- Sunglasses or any face-obscuring items.
- Blurry, out-of-focus images.
- Videos and animations.
- Compressed or altered images.

Once you've got the perfect shot, <b>upload your photo</b> and let the magic happen 🌟
"""
    PROFILE_UPLOAD_PHOTO = "📷 Upload Photo"
    PROFILE_UPLOADING_PHOTO = "Uploading photo..."
    PROFILE_CHANGE_PHOTO = "📷 Change Photo"
    PROFILE_CHANGE_PHOTO_SUCCESS = "📸 Photo successfully uploaded! 🌟"
    PROFILE_RENEW_SUBSCRIPTION = "♻️ Renew Subscription"
    PROFILE_RENEW_SUBSCRIPTION_SUCCESS = "✅ Subscription renewal was successful"
    PROFILE_CANCEL_SUBSCRIPTION = "❌ Cancel Subscription"
    PROFILE_CANCEL_SUBSCRIPTION_CONFIRMATION = "❗Are you sure you want to cancel the subscription?"
    PROFILE_CANCEL_SUBSCRIPTION_SUCCESS = "💸 Subscription cancellation was successful"
    PROFILE_NO_ACTIVE_SUBSCRIPTION = "💸 You don't have an active subscription"

    # Promo code
    PROMO_CODE_ACTIVATE = "🔑 Activate promo code"
    PROMO_CODE_INFO = """
🔓 <b>Unlock the world of AI wonders with your secret code!</b> 🌟

If you've got a <b>promo code</b>, just type it in to reveal hidden features and special surprises 🔑

<b>No code?</b> No problem! Simply click 'Cancel' to continue exploring the AI universe without it 🚀
"""
    PROMO_CODE_SUCCESS = """
🎉 <b>Your promo code has been successfully activated!</b> 🌟

Get ready to dive into a world of AI wonders with your shiny new perks

Happy exploring! 🚀
"""
    PROMO_CODE_ALREADY_HAVE_SUBSCRIPTION = """
🚫 <b>Whoopsie-daisy!</b> 🙈

Looks like you're already part of our exclusive subscriber's club! 🌟
"""
    PROMO_CODE_EXPIRED_ERROR = """
🕒 <b>Whoops, time's up on this promo code!</b>

Looks like this promo code has hit its expiration date. It's like a Cinderella story, but without the glass slipper 🥿

But hey, don't lose heart! You can still explore our other magical offers just hit the button below:
"""
    PROMO_CODE_NOT_FOUND_ERROR = """
🔍 <b>Oops, promo code not found!</b>

It seems like the promo code you entered is playing hide and seek with me cuz I couldn't find it in my system 🕵️‍♂️

🤔 Double-check for any typos and give it another go. If it's still a no-show, maybe it's time to hunt for another code or check out our /buy options for some neat deals 🛍️
"""
    PROMO_CODE_ALREADY_USED_ERROR = """
🚫 <b>Oops, déjà vu!</b>

Looks like you've already used this promo code. It's a one-time magic spell, and it seems you've already cast it! ✨🧙

No worries, though! You can check out our latest offers with clicking one of the buttons below:
"""

    # Remove Restriction
    REMOVE_RESTRICTION = "⛔️ Remove the Restriction"
    REMOVE_RESTRICTION_INFO = "To remove the restriction, choose one of the actions 👇"

    # Settings
    @staticmethod
    def settings_info(human_model: str, current_model: Model, generation_cost=1) -> str:
        if current_model == Model.DALL_E:
            additional_text = f"\nAt the current settings, 1 request costs: {generation_cost} 🖼"
        elif current_model == Model.KLING or current_model == Model.RUNWAY:
            additional_text = f"\nAt the current settings, 1 request costs: {generation_cost} 📹"
        else:
            additional_text = ""

        return f"""
⚙️ <b>Settings for model:</b> {human_model}

Here you can customize the selected model to suit your tasks and preferences
{additional_text}
"""

    SETTINGS_CHOOSE_MODEL_TYPE = """
⚙️ <b>Welcome to Settings!</b>

🌍 To change the interface language, enter the command /language
🤖 To change the model, enter the command /model

Here you are the artist, and settings are your palette. Choose the model type you want to personalize for yourself below 👇
"""
    SETTINGS_CHOOSE_MODEL = """
⚙️ <b>Welcome to Settings!</b>

Choose the model you want to personalize for yourself below 👇
"""
    SETTINGS_TO_OTHER_MODELS = "To Other Models ◀️"
    SETTINGS_TO_OTHER_TYPE_MODELS = "To Other Models Type ◀️"
    SETTINGS_VOICE_MESSAGES = """
⚙️ <b>Welcome to Settings!</b>

Below are the voice response settings for all text models 🎙
"""
    SETTINGS_VERSION = "Version 🤖"
    SETTINGS_FOCUS = "Focus 🎯"
    SETTINGS_FORMAT = "Format 🎛"
    SETTINGS_AMOUNT = "Number of Items 📏"
    SETTINGS_SEND_TYPE = "Send Type 🗯"
    SETTINGS_SEND_TYPE_IMAGE = "Image 🖼"
    SETTINGS_SEND_TYPE_DOCUMENT = "Document 📄"
    SETTINGS_SEND_TYPE_AUDIO = "Audio 🎤"
    SETTINGS_SEND_TYPE_VIDEO = "Video 📺"
    SETTINGS_ASPECT_RATIO = "Aspect Ratio 📐"
    SETTINGS_QUALITY = "Quality ✨"
    SETTINGS_PROMPT_SAFETY = "Prompt Security 🔐"
    SETTINGS_GENDER = "Gender 👕/👚"
    SETTINGS_DURATION = "Duration in Seconds 📏"
    SETTINGS_MODE = "Mode 🤖"
    SETTINGS_SHOW_THE_NAME_OF_THE_CHATS = "Show the name of the chats"
    SETTINGS_SHOW_THE_NAME_OF_THE_ROLES = "Show the name of the roles"
    SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES = "Show usage quota in messages"
    SETTINGS_TURN_ON_VOICE_MESSAGES = "Turn on voice messages"
    SETTINGS_LISTEN_VOICES = "Listen voices"

    # Shopping cart
    SHOPPING_CART = "🛒 Cart"
    SHOPPING_CART_ADD = "➕ Add to cart"
    SHOPPING_CART_ADD_OR_BUY_NOW = "Buy now or add to cart?"
    SHOPPING_CART_ADDED = "Added to cart ✅"
    SHOPPING_CART_BUY_NOW = "🛍 Buy now"
    SHOPPING_CART_REMOVE = "➖ Remove from cart"
    SHOPPING_CART_GO_TO = "🛒 Go to cart"
    SHOPPING_CART_GO_TO_OR_CONTINUE_SHOPPING = "Go to cart or continue shopping?"
    SHOPPING_CART_CONTINUE_SHOPPING = "🛍 Continue shopping"
    SHOPPING_CART_CLEAR = "🗑 Clear cart"

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

💳 Total: {left_price_part}{round(total_sum, 2)}{right_price_part}
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
🤖 <b>Hi there!</b> 👋

I am your guide to the world of neural networks, providing access to the best tools for creating:
━ 💭 text /text
━ 📝 summaries /summary
━ 🖼 images /image
━ 🎵 music /music
━ 📹 videos /video

🏆 <b>I’m not just a bot — I’m your emotionally intelligent assistant</b>, always ready to inspire, guide, and make your experience with neural networks simple and effective

🆓 <b>Free</b>:
━ Communicate with:
    ┣ <b>ChatGPT 4.0 Omni Mini ✉️</b> /chatgpt
    ┣ <b>Claude 3.5 Haiku 📜</b> /claude
    ┗ <b>Gemini 2.0 Flash 🏎</b> /gemini
━ Extract key points from:
    ┣ <b>YouTube 👀</b> /youtube_summary
    ┗ <b>Video 📼</b> /video_summary
━ Create images with:
    ┣ <b>DALL-E 3 👨‍🎨</b> /dalle
    ┣ <b>Midjourney 6.1 🎨</b> /midjourney
    ┣ <b>Stable Diffusion 3.5 🎆</b> /stable_diffusion
    ┣ <b>Flux 1.1 Pro 🫐</b> /flux
    ┗ <b>Luma Photon 🌌</b> /luma_photon
━ Swap faces in photos with <b>FaceSwap 📷️</b> /face_swap
━ Edit your images with <b>Photoshop AI 🪄</b> /photoshop

💡 <b>Unlock more possibilities in /buy:</b>
━ Advanced text-based AI:
    ┣ <b>ChatGPT 4.0 Omni 💥</b> /chatgpt
    ┣ <b>ChatGPT o1-mini 🧩</b> /chatgpt
    ┣ <b>ChatGPT o1 🧪</b> /chatgpt
    ┣ <b>Claude 3.5 Sonnet 💫</b> /claude
    ┣ <b>Claude 3.0 Opus 🚀</b> /claude
    ┣ <b>Gemini 1.5 Pro 💼</b> /gemini
    ┣ <b>Gemini 1.0 Ultra 🛡</b> /gemini
    ┣ <b>Grok 2.0 🐦</b> /grok
    ┗ <b>Perplexity 🌐</b> /perplexity
━ Music-focused AI:
    ┣ Compose melodies with <b>MusicGen 🎺</b> /music_gen
    ┗ Create songs with <b>Suno 4.0 🎸</b> /suno
━ Video creativity:
    ┣ Create videos with <b>Kling 🎬</b> /kling
    ┣ Generate videos from images with <b>Runway Gen-3 Alpha Turbo 🎥</b> /runway
    ┗ Bring your video ideas to life with <b>Luma Ray 🔆</b> /luma_ray
━ And enjoy increased daily quotas 🔓

✨ <b>Start creating now!</b>
"""
    START_QUICK_GUIDE = "📖 Quick Guide"
    START_ADDITIONAL_FEATURES = "🔮 Additional Features"
    START_QUICK_GUIDE_INFO = """
📖 Here's a quick guide to get started:

━ 💭 <b>Text Responses</b>:
    ┣ 1️⃣ Enter the command /text
    ┣ 2️⃣ Select the model
    ┗ 3️⃣ Write your requests into the chat

━ 📝 <b>Summary</b>:
    ┣ 1️⃣ Enter the command /summary
    ┣ 2️⃣ Select the model
    ┗ 3️⃣ Send me a video or YouTube link

━ 🖼 <b>Create Images</b>:
    ┣ 1️⃣ Enter the command /image
    ┣ 2️⃣ Select the model
    ┗ 3️⃣ Start creating using your imagination with your requests

━ 📷️ <b>Exchange Faces in Photos</b>:
    ┣ 1️⃣ Enter the command /face_swap
    ┣ 2️⃣ Follow the instructions to help me creating better photos
    ┗ 3️⃣ Choose images from my unique packages or send your own photos

━ 🪄 <b>Edit Images</b>:
    ┣ 1️⃣ Enter the command /photoshop
    ┣ 2️⃣ Choose what you want to do with the image
    ┗ 3️⃣ Send the image for editing

━ 🎵 <b>Compose Music</b>:
    ┣ 1️⃣ Enter the command /music
    ┣ 2️⃣ Select the model
    ┗ 3️⃣ Write a description of the music or send your own lyrics

━ 📹 <b>Video Creation</b>:
    ┣ 1️⃣ Enter the command /video
    ┣ 2️⃣ Select the model
    ┗ 3️⃣ Write a video description and attach a photo
"""
    START_ADDITIONAL_FEATURES_INFO = """
🔮 <b>Additional Features</b>:

━ 🔄 /model - One command for switching between all AI models
━ 📊 /profile - I'll show your profile and quotes
━ 🔍 /info - Useful information about each AI model
━ 📂 /catalog - Catalog of digital assistants and prompts
━ 🎁 /bonus - Learn how to get free access to all AI models for free
━ 🎭️ /settings - Personalization and settings. Digital employees and thematic chats for text models
"""

    # Subscription
    SUBSCRIPTION = "💳 Subscription"
    SUBSCRIPTION_MONTH_1 = "1 month"
    SUBSCRIPTION_MONTHS_3 = "3 months"
    SUBSCRIPTION_MONTHS_6 = "6 months"
    SUBSCRIPTION_MONTHS_12 = "12 months"
    SUBSCRIPTION_SUCCESS = """
🎉 <b>Hooray! You're all set!</b> 🚀

Your subscription is now as active as a caffeinated squirrel! 🐿️☕ Welcome to the club of awesomeness. Here's what's going to happen next:
- A world of possibilities just opened up 🌍✨
- Your AI pals are gearing up to assist you 🤖👍
- Get ready to dive into a sea of features and fun 🌊🎉

Thank you for embarking on this fantastic journey with us! Let's make some magic happen! 🪄🌟
"""
    SUBSCRIPTION_RESET = """
🚀 <b>Subscription quota refreshed!</b>

Hello there, fellow AI adventurer! 🌟
Guess what? Your subscription quota has just been topped up! It's like a magic refill, but better because it's real. 🧙‍♂️
You've got a whole new month of AI-powered fun ahead of you. Chat, create, explore – the sky's the limit! ✨

Keep unleashing the power of AI and remember, we're here to make your digital dreams come true. Let's rock this month! 🤖💥
"""
    SUBSCRIPTION_END = """
🛑 <b>Subscription expired!</b>

Your subscription has come to an end. But don't worry, the AI journey isn't over yet! 🚀

You can renew your magic pass with clicking one of the buttons below to keep exploring the AI universe:
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
            left_part_price = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
            right_part_price = Currency.SYMBOLS[currency] if currency != Currency.USD else ''
            if subscription_name and subscription_price:
                is_trial_info = ''

                if is_trial and currency == Currency.RUB:
                    is_trial_info = '1₽ first 3 days, then '
                elif is_trial and currency == Currency.USD:
                    is_trial_info = 'Free first 3 days, then '

                text_subscriptions += f'- <b>{subscription_name}</b>: '
                per_period = 'per month' if subscription.category == ProductCategory.MONTHLY else 'per year'

                discount = get_user_discount(user_discount, 0, subscription.discount)
                if discount:
                    discount_price = Product.get_discount_price(
                        ProductType.SUBSCRIPTION,
                        1,
                        subscription_price,
                        currency,
                        discount,
                        SubscriptionPeriod.MONTH1 if subscription.category == ProductCategory.MONTHLY else SubscriptionPeriod.MONTHS12,
                    )
                    text_subscriptions += f'{is_trial_info}<s>{left_part_price}{subscription_price}{right_part_price}</s> {left_part_price}{discount_price}{right_part_price} {per_period}\n'
                else:
                    text_subscriptions += f'{is_trial_info}{left_part_price}{subscription_price}{right_part_price} {per_period}\n'
        return f"""
🤖 Ready to supercharge your digital journey? Here's what's on the menu:

{text_subscriptions}

Pick your potion and hit the button below to subscribe:
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
            trial_info = ' with a trial period first 3 days'

        return f"""
You're about to activate subscription {name} for {left_price_part}{price}{right_price_part}/{period}{trial_info}

❗️You can cancel your subscription at any time in <b>Profile 👤</b>
"""

    # Suno
    SUNO_INFO = """
🤖 <b>Choose the style for creating your song:</b>

🎹 In <b>simple mode</b>, you only need to describe the theme of the song and the genre
🎸 In <b>custom mode</b>, you have the opportunity to use your own lyrics and experiment with genres

<b>Suno</b> will create 2 tracks, up to 4 minutes each 🎧
"""
    SUNO_SIMPLE_MODE = "🎹 Simple"
    SUNO_CUSTOM_MODE = "🎸 Custom"
    SUNO_SIMPLE_MODE_PROMPT = """
🎶 <b>Song Description</b>

To create your song in simple mode, please describe the theme of the song and the musical genre you desire. This will help the system better understand your expectations and create something truly unique for you.

📝 Write your prompt below and let's start the creative process!
"""
    SUNO_CUSTOM_MODE_LYRICS = """
🎤 <b>Song Lyrics</b>

To create your song in custom mode, you need to provide the lyrics that will be used in the music. This is a crucial element that will give your composition a unique character and a special mood.

✍️ Send the lyrics of your future song right now, and let's create a musical masterpiece together!
"""
    SUNO_CUSTOM_MODE_GENRES = """
🎵 <b>Genre Selection</b>

To ensure your song in custom mode matches your preferences, please specify the genres you'd like to incorporate. The choice of genre significantly influences the style and mood of the composition, so choose carefully.

🔍 List the desired genres separated by commas in your next message, and let's start creating your unique song!
"""
    SUNO_START_AGAIN = "Start again 🔄"
    SUNO_TOO_MANY_WORDS_ERROR = "<b>Oh, oh!</b>🚧\n\nAt some steps, you sent too much text 📝\n\nTry again, but with a smaller text, please!"
    SUNO_VALUE_ERROR = "It doesn't look like a prompt 🧐\n\nPlease enter a different value"
    SUNO_SKIP = "Skip ⏩️"

    # Tech Support
    TECH_SUPPORT = "👨‍💻 Tech Support"

    # Terms Link
    TERMS_LINK = "https://telegra.ph/Terms-of-Service-in-GPTsTurboBot-05-07"

    # Video Summary
    VIDEO_SUMMARY_FOCUS_INSIGHTFUL = "Insightful 💡"
    VIDEO_SUMMARY_FOCUS_FUNNY = "Funny 😄"
    VIDEO_SUMMARY_FOCUS_ACTIONABLE = "Actionable 🛠"
    VIDEO_SUMMARY_FOCUS_CONTROVERSIAL = "Controversial 🔥"
    VIDEO_SUMMARY_FORMAT_LIST = "List 📋"
    VIDEO_SUMMARY_FORMAT_FAQ = "Q&A 🗯"
    VIDEO_SUMMARY_AMOUNT_AUTO = "Auto ⚙️"
    VIDEO_SUMMARY_AMOUNT_SHORT = "Short ✂️"
    VIDEO_SUMMARY_AMOUNT_DETAILED = "Detailed 📚"

    # Voice
    VOICE_MESSAGES = "Voice messages 🎙"
    VOICE_MESSAGES_FORBIDDEN_ERROR = """
🎙 <b>Oops! Seems like your voice went into the AI void!</b>

To unlock the magic of voice-to-text, simply wave your wand with buttons below:
"""

    # Admin
    ADMIN_INFO = "👨‍💻 Choose an action, Admin 👩‍💻"

    ADMIN_ADS_INFO = "Select what you want to do:"
    ADMIN_ADS_CREATE = "Create an advertising link 📯"
    ADMIN_ADS_GET = "Get information about the advertising campaign 📯"
    ADMIN_ADS_SEND_LINK = "Send me a link to the advertising campaign 📯"
    ADMIN_ADS_CHOOSE_SOURCE = "Choose the source of the advertising campaign 📯"
    ADMIN_ADS_CHOOSE_MEDIUM = "Select the type of traffic for the advertising campaign 📯"
    ADMIN_ADS_SEND_NAME = "Send the name of the advertising campaign as a single word without special characters 📯"
    ADMIN_ADS_SEND_QUANTITY = "Send the number of links to create 📯"
    ADMIN_ADS_VALUE_ERROR = "Doesn't look like a campaign name"

    ADMIN_BAN_INFO = "Send me the user ID of the person you want to ban/unban ⛔️"
    ADMIN_BAN_SUCCESS = "You have successfully banned the user 📛"
    ADMIN_UNBAN_SUCCESS = "You have successfully unbanned the user 🔥"

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

Write a broadcast message that will touch the hearts of your users, make them smile, or even inspire them for new achievements. Remember, every word is a brush, and your text is a canvas where you can paint anything. Go ahead, fill this world with the colors of your imagination! 🌈✨
"""
    ADMIN_BLAST_WRITE_IN_DEFAULT_LANGUAGE = """
🚀 <b>It’s time for a global broadcast!</b> 🌍

You’ve chosen "For Everyone," which means your message will reach every corner, regardless of users’ language preferences. Write your message in Russian, and I’ll automatically translate it for all our users. Create a message that inspires, entertains, or informs—it will fly straight to the hearts and minds of people around the world.

Remember, your words can brighten someone’s day! 🌟
"""
    ADMIN_BLAST_SUCCESS = """
🎉 <b>The broadcast was successfully sent!</b> 💌

Your message is already on its way to users, ready to spark interest and bring smiles. You’ve taken a real step toward engagement and communication. Congratulations, admin-magician—your creation will soon be appreciated! 🌟

Thank you for making me brighter and more exciting with every action you take! ✨
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
📢 <b>The final step before the big launch!</b> 🚀

🤖 Broadcast Text:
{letters}

If everything looks perfect, press "Approve" If changes are needed, select "Cancel" 🌟
"""

    ADMIN_CATALOG = """
🎭 <b>Role Catalog Management</b> 🌟

Here you can:
🔧 <b>Add a New Role</b>: Unleash your creativity and create a unique assistant!
✏️ <b>Edit Existing Roles</b>: Bring your vision to life in already familiar characters.
🗑️ <b>Delete the Unnecessary</b>: Sometimes saying goodbye is the beginning of something new.

Choose your adventure in this world of AI talents! 🚀
"""
    ADMIN_CATALOG_CREATE = """
🌈 <b>Creating a New Role</b> 🎨

It’s time to give birth to a new AI assistant! Give your creation a name. Write a unique name for the new role in UPPER_SNAKE_CASE format, for example, SUPER_GENIUS or MAGIC_ADVISOR.

💡 Remember, the name should be unique, vibrant, and memorable, like the brightest fireworks in the sky!
"""
    ADMIN_CATALOG_CREATE_ROLE = "Create a Role"
    ADMIN_CATALOG_CREATE_ROLE_ALREADY_EXISTS_ERROR = """
🙈 <b>Oops! A duplicate spotted!</b> 🙈

Hey, it seems this role already exists! Creating something unique is great, but duplicating an existing one is like launching the second internet. We already have <b>this star</b> in our AI cosmos.

🤔 Try coming up with a different name, something fresh and original to make our catalog even cooler. How about getting inspired by something new and unusual? Onward to new ideas! 🚀
"""
    ADMIN_CATALOG_CREATE_ROLE_NAME = """
🎨 <b>Time for Creativity!</b> 🌟

Come up with a name for your new role that will sound like music in all the languages of the world! The name should not only be memorable and vibrant but also start with a fitting emoji, such as "🤖 Personal Assistant."

🖌️ Write the name in Russian, and I’ll make sure it’s understood by users worldwide. What unique and creative name will you choose for your new AI assistant?
"""
    ADMIN_CATALOG_CREATE_ROLE_DESCRIPTION = """
📝 <b>Time for Creativity!</b> 🎨

Create a description for your new role. It should be three lines full of inspiration and ideas, which will be shown to users upon selecting the role. For example:
<i>Always ready to help you find answers to any questions, whether they’re everyday issues or philosophical musings.
Your personal guide in the world of knowledge and creativity, eager to share ideas and advice. 🌌
Let’s explore new horizons together!</i>

🖌️ Write the description in Russian to reflect the essence of the role while inspiring and delighting users. I’ll make sure it’s clear to users worldwide. Add some magic to every word with your creativity and imagination!
"""
    ADMIN_CATALOG_CREATE_ROLE_INSTRUCTION = """
🤓 <b>Time for a System Instruction!</b> 📚

Create a short but concise instruction for your assistant. This will be their guide for action, for example: "You are a thoughtful advisor, always ready to share wise thoughts and helpful ideas. Help users solve complex questions and offer original solutions. Your mission is to inspire and enrich every interaction!"

🖌️ Write the instruction in Russian to guide your assistant in interacting with users. Make it bright and memorable so that every conversation with your assistant is special!
"""
    ADMIN_CATALOG_CREATE_ROLE_PHOTO = """
📸 <b>The Final Touch – Your Assistant’s Photo!</b> 🌟

It’s time to give your digital assistant a face. Send a photo that will become their calling card. It can be anything: a cheerful robot or a stylish cat in glasses. Remember, this image will be the "face" of your assistant in user dialogues!

🖼️ Choose a photo that best reflects your assistant’s character and style. Make it appealing and unique so that users recognize it immediately!
"""
    ADMIN_CATALOG_CREATE_ROLE_SUCCESS = """
🎉 <b>Hooray! The new role has been successfully created!</b> 🌟

🚀 Your new assistant has officially joined the team of our AI heroes. Their mission is to make users' journeys in the world of artificial intelligence even more exciting!

💬 The assistant is ready to work and awaits users' commands. Congratulations on successfully expanding the AI team!
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
🎩 <b>Here’s what you’ve created:</b>

🌍 Names:
{names}

💬 Descriptions:
{descriptions}

📜 Instructions:
{instructions}

If everything looks perfect, press "Approve" If changes are needed, select "Cancel" 🌟
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
🎨 <b>Role Configuration</b> 🖌️

🌍 <b>Names:</b>
{names}

💬 <b>Descriptions:</b>
{descriptions}

📜 <b>Instructions:</b>
{instructions}

🛠️ Now it’s your turn to add some magic! Choose what you’d like to edit:
- Name 📝
- Description 📖
- Instruction 🗒️
- Photo 🖼
"""

    ADMIN_CATALOG_EDIT_ROLE_NAME = "Edit Name 🖌"
    ADMIN_CATALOG_EDIT_ROLE_NAME_INFO = """
📝 <b>Time for a Rebrand!</b> 🎨

You chose "Edit Name" for the assistant. Now’s the moment to give them something new and shiny! 🌟

Enter the new name starting with an emoji in Russian and imagine how it will sound among our AI heroes. Don’t hesitate to be original—the best names are born in the magical atmosphere of creativity! ✨
"""
    ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION = "Edit Description 🖌"
    ADMIN_CATALOG_EDIT_ROLE_DESCRIPTION_INFO = """
🖋️ <b>Rewriting History!</b> 🌍

You’ve decided to "Edit Description" for the assistant. Think about what you’d like to tell the world about them. This is your chance to showcase their uniqueness and features! 📚

Write a new description emphasizing their best qualities in Russian. Add a pinch of humor and a dash of inspiration—and there it is, a description worthy of a true AI hero! 👾
"""
    ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION = "Edit Instruction 🖌"
    ADMIN_CATALOG_EDIT_ROLE_INSTRUCTION_INFO = """
📘 <b>New Rules of the Game!</b> 🕹️

"Edit Instruction" means giving new directions to our AI hero. What will be their new mission? 🚀

Write the instruction in Russian so that every line inspires great achievements in the AI world!
"""
    ADMIN_CATALOG_EDIT_ROLE_PHOTO = "Edit Photo 🖼"
    ADMIN_CATALOG_EDIT_ROLE_PHOTO_INFO = """
📸 <b>New Employee – New Spirit!</b> 🌟

It’s time to change the face of your digital assistant. Send a photo that will become their new calling card. It can be anything: a cheerful robot or a stylish cat in glasses. Remember, this image will be the new "face" of the assistant in user dialogues!

🖼️ Choose a photo that best reflects your assistant’s character and style. Make it appealing and unique so that users recognize it immediately!
"""
    ADMIN_CATALOG_EDIT_SUCCESS = """
🎉 <b>Ta-da! Changes successfully applied!</b> 🎨

🤖 Your assistant has been gracefully transformed. Congratulations, you’ve just made your mark on AI assistant history! 🚀

👀 There’s only one thing left—see them in action! Head to /catalog to view your updated assistant in all their glory.
"""

    ADMIN_DATABASE = "🗄 Database"

    ADMIN_FACE_SWAP_INFO = """
🤹‍ <b>Welcome to the realm of FaceSwap!</b> 🎭

🚀 Ready for some creativity? Here, you are the master wizard! Manage packages and photos. Begin your magical journey:
- 📦 Add/Edit Package - Build a collection of face masks that will elevate your creativity to a new level or make changes to existing collections. Add, update, and organize—your imagination has no limits!
- 🖼 Manage Photos - Each package contains many amazing faces waiting for their moment. Add, activate, or deactivate them at your discretion to control user accessibility. Unlock a world of limitless creative possibilities!

Choose, create, amaze! In the world of FaceSwap, every step you take turns into something incredible! 🎨✨
"""
    ADMIN_FACE_SWAP_CREATE = """
🌟 <b>Let’s begin a creative adventure!</b> 🌈

📝 Create a new FaceSwap package! Start by giving it a unique name. Use the UPPER_SNAKE_CASE format to keep it clear and organized. For example, you could name it SEASONAL_PHOTO_SHOOT or FUNNY_FACE_FESTIVAL. This name will be your magical key to creating incredible transformations!

🎨 Express your individuality! Write a system name that reflects the essence and idea of your package. Your name is the first step to creating something truly magical and unforgettable!
"""
    ADMIN_FACE_SWAP_CREATE_PACKAGE = "Create a new package"
    ADMIN_FACE_SWAP_CREATE_PACKAGE_ALREADY_EXISTS_ERROR = """
🚨 <b>Oops, it seems we’ve been here before!</b> 🔄

🔍 The package name is already taken! It looks like the name you chose for your new FaceSwap package already exists in our gallery of wonders. But don’t worry, this is just an opportunity to unleash even more creativity!

💡 Try something new! How about another unique name? Surely you have many exciting ideas waiting to be explored!
"""
    ADMIN_FACE_SWAP_CREATE_PACKAGE_NAME = """
🎉 <b>Continuing our creative marathon!</b> 🚀

📛 The next step is the package name! Now give your FaceSwap package a unique name in Russian that clearly reflects its essence and atmosphere. Don’t forget to add a bright emoji at the end to make it even more expressive! For example, "Movie Characters 🎥" or "Magical Worlds 🌌."

🌍 International charm! This name will be automatically translated into other languages, revealing your idea to users worldwide.
"""
    ADMIN_FACE_SWAP_CREATE_PACKAGE_SUCCESS = """
🎉 <b>Hooray, the new FaceSwap package is ready to launch!</b> 🚀

🌟 Congratulations on your successful creation! Your new package will soon await its fans. Get ready for your creation to capture users’ imaginations!

🖼 Time for photo magic! You can now start filling the package with the most incredible and funny photos. From hilarious to inspiring, each image will add uniqueness to your package.
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
🌟 <b>That’s it! Your new FaceSwap package is almost ready for debut!</b> 🎉

📝 Review all the details:
- 🤖 <b>System Name:</b>
{package_system_name}

- 🌍 <b>Names:</b>
{names}

🔍 Make sure everything is correct. This is your creation, and it should be perfect!

👇 Choose an action
"""

    ADMIN_FACE_SWAP_EDIT = """
🎨 <b>Time to create! You’ve chosen a package to edit</b> 🖌️

🔧 Editing options:
- <b>Change Visibility</b> - Make the package visible or hidden from users.
- <b>View Images</b> - Check out the masterpieces already in the package.
- <b>Add New Image</b> - It’s time to bring fresh colors and new faces!

🚀 Ready for changes? Your creativity will breathe new life into this package. Let every generation be unique and memorable!
"""
    ADMIN_FACE_SWAP_EDIT_PACKAGE = "Edit existing package"
    ADMIN_FACE_SWAP_EDIT_CHOOSE_GENDER = "Choose Gender:"
    ADMIN_FACE_SWAP_EDIT_CHOOSE_PACKAGE = "Choose Package:"
    ADMIN_FACE_SWAP_EDIT_SUCCESS = """
🌟 <b>Package successfully edited!</b> 🎉

👏 Bravo, admin! Your changes have been successfully applied. The FaceSwap package is now updated and even more amazing.

🚀 Ready for new adventures? Your creativity and package management skills make the world of FaceSwap brighter and more exciting. Keep creating and inspiring users with your unique ideas!
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
🌠 <b>Subscription</b> - Unlock access to exclusive features and content
🎨 <b>Package</b> - Add special capabilities for AI usage
🪙 <b>Discount</b> - Let users purchase generations at a lower price

Click the desired button, and let’s get started! 🚀
"""
    ADMIN_PROMO_CODE_SUCCESS = """
🌟 <b>Wow!</b>

Your <b>promo code has been successfully created</b> and is ready to make its way into the pockets of our users. 🚀
This little code will surely bring joy to someone out there!

🎉 Congratulations, you're a true promo code wizard!
"""
    ADMIN_PROMO_CODE_CHOOSE_SUBSCRIPTION = """
🌟 <b>Choose a subscription for the promo code!</b> 🎁

✨ Select the subscription type you want to grant access to:
"""
    ADMIN_PROMO_CODE_CHOOSE_PACKAGE = """
🌟 <b>Select a package for the promo code!</b> 🎁

Start by choosing a package 👇
"""
    ADMIN_PROMO_CODE_CHOOSE_DISCOUNT = """
🌟 <b>Choose a discount for the promo code!</b> 🎁

Enter the discount percentage (from 1% to 50%) that you want to offer users 👇
"""
    ADMIN_PROMO_CODE_CHOOSE_NAME = """
🖋️ <b>Create a name for your promo code</b> ✨

Right now, you're like a true wizard crafting a spell! ✨🧙‍
Write a unique and memorable name for your promo code.

🔠 Use letters and numbers, but remember the magic of brevity. Don't hesitate to experiment and inspire your users!
"""
    ADMIN_PROMO_CODE_CHOOSE_DATE = """
📅 <b>Time for some magic!</b> 🪄

Enter the date until this promo code will spread happiness and surprise!
Remember to use the format DD.MM.YYYY, for example, 12/25/2023 — perfect for a Christmas surprise! 🎄

So go ahead, choose the date when the magic will end 🌟
"""
    ADMIN_PROMO_CODE_NAME_EXISTS_ERROR = """
🚫 <b>Oh no, this code already exists!</b> 🤖

As a true innovator, you've come up with a code that someone has already thought of!
You’ll need something even more unique. Try again, because creativity knows no limits!

Show off your originality and creativity. I'm sure you'll nail it this time!
"""
    ADMIN_PROMO_CODE_DATE_VALUE_ERROR = """
🚫 <b>Oops!</b>

It seems the date got lost in the calendar and can’t find the right format 📅

Let’s try again, but this time in the format DD.MM.YYYY, for example, 12/25/2023. Accuracy is the key to success!
"""

    ADMIN_SERVER = "💻 Server"

    ADMIN_STATISTICS_INFO = """
📊 <b>Statistics are on the way!</b>

Time to dive into the world of numbers and charts. Choose a period, and I’ll show you how our bot has conquered AI heights 🚀:
1️⃣ <b>Daily Statistics</b> - Find out what happened today! Were there any records?
2️⃣ <b>Weekly Statistics</b> - A weekly dose of data. What were the trends?
3️⃣ <b>Monthly Statistics</b> - A month in numbers. How many achievements did we gather?
4️⃣ <b>All-Time Statistics</b> - A look into the past. Where did we start, and where are we now?
5️⃣ <b>Record a Transaction</b> - Update our data to keep everything honest!

Pick a button and let’s dive into the knowledge! 🕵️‍♂️🔍
"""
    ADMIN_STATISTICS_WRITE_TRANSACTION = """
🧾 <b>Choose the type of transaction!</b>

Hmm... It seems it's time to summarize our finances! 🕵️‍♂️💼 Now you have a choice:
- Click "📈 Record Income" if our treasury has grown, and we’ve gained a few golden coins!
- Or choose "📉 Record Expense" if we had to spend on magical ingredients or other essentials.

Click the button and embark on a financial adventure! 💫🚀
"""
    ADMIN_STATISTICS_CHOOSE_SERVICE = """
🔍 <b>Select the type of service for the transaction!</b>

Oh, it seems we’ve reached the point of choosing the service type! 🌟📚 Here, it’s like a shop of wonders.

Choose confidently, and may the financial records be as accurate as a star cartographer’s maps! 🗺️✨
"""
    ADMIN_STATISTICS_CHOOSE_CURRENCY = """
💰 <b>Time to choose a currency!</b>

For a complete picture, we need to know the currency for these transactions. So, which currency were we swimming in during these deals? Rubles, dollars, or perhaps golden doubloons? 😄

Choose the button with the correct currency to log everything accurately. It’s important—after all, even pirates took their treasure accounting seriously! 💸🏴‍☠️
"""
    ADMIN_STATISTICS_SERVICE_QUANTITY = """
✍️ <b>Time to record the number of transactions!</b>

Please write the number of transactions.

🔢🚀 Remember, every transaction is a step towards our shared success. Don’t miss a single one!
"""
    ADMIN_STATISTICS_SERVICE_AMOUNT = """
🤑 <b>Let’s count the coins!</b>

Please tell me the transaction amount. Remember, every penny (or cent) counts! Please use a decimal format with a dot, e.g., 999.99.

Enter the numbers carefully, as if you were counting gold coins on a pirate ship. After all, accuracy is the courtesy of kings... and accountants! 🏴‍☠️📖
"""
    ADMIN_STATISTICS_SERVICE_DATE = """
📅 <b>The final touch: Transaction Date!</b>

Write the date when these transactions occurred. Format? Simple and clear: "DD.MM.YYYY", e.g., "04/01/2024" or "12/25/2023". This date is the key to organizing our temporal treasure chest.

🕰️✨ Remember, the exact date is not just numbers; it’s a marker of our journey. We’ll use it to plan our future!
"""
    ADMIN_STATISTICS_SERVICE_DATE_VALUE_ERROR = """
🤔 <b>Oops, it seems the date decided to misbehave!</b>

Uh-oh, it looks like we got a little tangled in the calendar pages! The entered date doesn’t match the format "DD.MM.YYYY". Let’s try again—after all, we don’t have a time machine (yet) to fix this in the future.

🗓️✏️ So, once more: when exactly did this financial miracle occur?
"""
    ADMIN_STATISTICS_WRITE_TRANSACTION_SUCCESSFUL = """
🎉 <b>Transaction successfully recorded! Wow, we’re in business!</b>

Hooray! Your financial maneuver has been successfully logged into our digital chronicles. Now this transaction shines in our database like a star in the bookkeeping sky!

📚💰 Thank you for your accuracy and precision. Our digital elves are already dancing with joy. It seems your financial wisdom deserves its own chapter in the book of economic adventures!
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
