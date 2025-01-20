import random
from typing import Union

from bot.database.models.product import Product, ProductType, ProductCategory
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
from bot.database.models.subscription import (
    SubscriptionPeriod,
    SubscriptionStatus,
)
from bot.database.models.user import UserSettings
from bot.locales.types import LanguageCode


class Spanish(Texts):
    # Action
    ACTION_BACK = "◀️ Atrás"
    ACTION_CLOSE = "🚪 Cerrar"
    ACTION_CANCEL = "❌ Cancelar"
    ACTION_APPROVE = "✅ Aprobar"
    ACTION_DENY = "❌ Rechazar"
    ACTION_TO_OTHER_MODELS = "◀️ A otros modelos"
    ACTION_TO_OTHER_TYPE_MODELS = "◀️ A otros tipos de modelos"

    # Additional Bot
    @staticmethod
    def additional_bot_info(link: str) -> str:
        return f"""
👋 <b>¡Hola!</b>

⚠️ <b>Este bot no procesa solicitudes. Solo te redirige a nuestro asistente de IA principal</b>

🏆 Nuestra misión es brindar acceso a los mejores modelos de IA para todos.

👉 {link}
"""

    # Bonus
    @staticmethod
    def bonus_info(balance: int) -> str:
        return f"""
🎁 <b>Saldo de Bonificación</b>

💰 En la cuenta: <b>{int(balance)} créditos</b> 🪙

💡 <b>En qué gastarlo:</b>
• Solicitudes en cualquier red neuronal
• Acceso a empleados digitales
• Respuestas/solicitudes de voz
• Respuestas rápidas y sin pausas

Elige una acción 👇
"""

    BONUS_EARN = "➕ Ganar"
    BONUS_SPEND = "➖ Gastar"

    @staticmethod
    def bonus_info_earn(user_id: str, referred_count: int, feedback_count: int, play_count: int):
        return f"""
➕ <b>Cómo ganar créditos</b>

👥 <i>Invitar a amigos:</i>
• <b>+25 créditos</b> para ti y tu amigo
• Enlace de invitación:
{Texts.bonus_referral_link(user_id, False)}
• Amigos invitados: {referred_count}

💭 <i>Dejar comentarios:</i>
• <b>+25 créditos</b> por tu opinión
• Comentarios enviados: {feedback_count}

🎮 <i>Probar suerte:</i>
• <b>+1-100 créditos</b> por ganar
• Juegos jugados: {play_count}

Elige una acción 👇
"""

    @staticmethod
    def bonus_info_spend(balance: int):
        return f"""
💰 En la cuenta: <b>{int(balance)} créditos</b> 🪙

Elige cómo <b>gastar tus créditos:</b> 👇
"""

    BONUS_ACTIVATED_SUCCESSFUL = """
🌟 <b>¡Bono Activado!</b>

Has adquirido los paquetes con éxito 🚀
"""
    BONUS_INVITE_FRIEND = "👥 Invitar a un amigo"
    BONUS_REFERRAL_SUCCESS = """
🌟 <b>¡Tu magia de referidos funcionó!</b>

Tu saldo y el de tu amigo aumentaron en <b>25 créditos</b> 🪙
"""
    BONUS_REFERRAL_LIMIT_ERROR = """
🌟 <b>¡Tu magia de referidos funcionó!</b>

Lamentablemente, no puedo otorgarte la recompensa porque se ha excedido el límite
"""
    BONUS_LEAVE_FEEDBACK = "📡 Dejar un comentario"
    BONUS_CASH_OUT = "🛍 Retirar créditos"
    BONUS_PLAY = "🎮 Jugar"
    BONUS_PLAY_GAME = "🎮 Probar suerte"
    BONUS_PLAY_GAME_CHOOSE = """
🎮 <b>Elige un juego</b>

👉 <i>Solo tienes un intento al día</i>
"""
    BONUS_PLAY_BOWLING_GAME = "🎳 Bolos"
    BONUS_PLAY_BOWLING_GAME_INFO = """
🎳 <b>Bolos</b>

Presiona <b>«Jugar»</b>, y lanzaré la bola a los bolos al instante. ¡La probabilidad de ganar es del <b>100%</b>!

El número de bolos derribados será la cantidad de créditos ganados: <b>1-6</b>
"""
    BONUS_PLAY_SOCCER_GAME = "⚽️ Fútbol"
    BONUS_PLAY_SOCCER_GAME_INFO = """
⚽️ <b>Fútbol</b>

Presiona <b>«Jugar»</b>, y lanzaré la pelota a la portería. ¡La probabilidad de marcar gol y ganar créditos es del <b>60%</b>!

Si anoto, recibirás <b>5 créditos</b>
"""
    BONUS_PLAY_BASKETBALL_GAME = "🏀 Baloncesto"
    BONUS_PLAY_BASKETBALL_GAME_INFO = """
🏀 <b>Baloncesto</b>

Presiona <b>«Jugar»</b>, y lanzaré la pelota al aro de baloncesto. La probabilidad de encestar es del <b>40%</b>

Si anoto, recibirás <b>10 créditos</b>
"""
    BONUS_PLAY_DARTS_GAME = "🎯 Dardos"
    BONUS_PLAY_DARTS_GAME_INFO = """
🎯 <b>Dardos</b>

Presiona <b>«Jugar»</b>, y lanzaré un dardo al blanco. La probabilidad de dar en el centro es de aproximadamente <b>16.67%</b>

Si acierto en el centro, recibirás <b>15 créditos</b>
"""
    BONUS_PLAY_DICE_GAME = "🎲 Dados"
    BONUS_PLAY_DICE_GAME_INFO = """
🎲 <b>Dados</b>

Elige un número del 1 al 6, y lanzaré el dado. La probabilidad de ganar es de <b>1 en 6</b>

Si adivinas el número que saldrá, recibirás <b>20 créditos</b>
"""
    BONUS_PLAY_CASINO_GAME = "🎰 Casino"
    BONUS_PLAY_CASINO_GAME_INFO = """
🎰 <b>Casino</b>

Presiona <b>«Jugar»</b>, y giraré los carretes del casino. La probabilidad de obtener tres números iguales es de casi <b>5%</b>. La probabilidad de obtener tres sietes es ligeramente superior al <b>1%</b>

• Si aparecen tres números iguales, recibirás <b>50 créditos</b>
• Si aparecen tres sietes, recibirás <b>100 créditos</b>
"""
    BONUS_PLAY_GAME_WON = """
🎉 <b>¡Ganaste!</b>

Vuelve mañana por más victorias 💪
"""
    BONUS_PLAY_GAME_LOST = """
😔 <b>No tuviste suerte hoy...</b>

Inténtalo de nuevo mañana; ¡quizás la suerte esté de tu lado! 🍀
"""

    @staticmethod
    def bonus_play_game_reached_limit():
        hours, minutes = get_time_until_limit_update(hours=0)
        return f"""
⏳ <b>¡Ya has jugado hoy!</b>

Vuelve en <i>{hours} h. {minutes} min.</i> y muéstrame de qué eres capaz. 👏
"""

    # Catalog
    CATALOG_INFO = """
📁 <b>Catálogo de Posibilidades</b>

Selecciona la sección que necesitas y presiona el botón 👇
"""
    CATALOG_MANAGE = "🎭 Gestión del Catálogo"
    CATALOG_DIGITAL_EMPLOYEES = "🎭 Roles"
    CATALOG_DIGITAL_EMPLOYEES_INFO = """
🎭 <b>Catálogo de Roles</b>

Selecciona un empleado digital abajo 👇
"""
    CATALOG_DIGITAL_EMPLOYEES_FORBIDDEN_ERROR = """
🔒 <b>¡Has entrado en la zona VIP!</b>

Aún no tienes acceso a los empleados digitales

Puedes obtenerlo presionando el botón de abajo:
"""
    CATALOG_PROMPTS = "📚 Prompts"
    CATALOG_PROMPTS_CHOOSE_MODEL_TYPE = """
📚 <b>Catálogo de Prompts</b>

Selecciona el <b>tipo de modelo</b> que necesitas presionando el botón abajo 👇
"""
    CATALOG_PROMPTS_CHOOSE_CATEGORY = """
📚 <b>Catálogo de Prompts</b>

Selecciona la <b>categoría</b> que necesitas presionando el botón abajo 👇
"""
    CATALOG_PROMPTS_CHOOSE_SUBCATEGORY = """
📚 <b>Catálogo de Prompts</b>

Selecciona la <b>subcategoría</b> que necesitas presionando el botón abajo 👇
"""

    @staticmethod
    def catalog_prompts_choose_prompt(prompts: list[Prompt]):
        prompt_info = ''
        for index, prompt in enumerate(prompts):
            is_last = index == len(prompts) - 1
            right_part = '\n' if not is_last else ''
            prompt_name = prompt.names.get(LanguageCode.ES) or prompt.names.get(LanguageCode.EN)
            prompt_info += f'<b>{index + 1}</b>: {prompt_name}{right_part}'

        return f"""
📚 <b>Catálogo de Prompts</b>

{prompt_info}

Para obtener el prompt completo, selecciona el <b>número del prompt</b> presionando el botón abajo 👇
"""

    @staticmethod
    def catalog_prompts_info_prompt(prompt: Prompt, products: list[Product]):
        model_info = ''
        for index, product in enumerate(products):
            is_last = index == len(products) - 1
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            product_name = product.names.get(LanguageCode.ES) or product.names.get(LanguageCode.EN)
            model_info += f'    {left_part} <b>{product_name}</b>{right_part}'

        return f"""
📚 <b>Catálogo de Prompts</b>

Has seleccionado el prompt: <b>{prompt.names.get(LanguageCode.ES) or prompt.names.get(LanguageCode.EN)}</b>

Este prompt es compatible con los modelos:
{model_info}

Selecciona una acción abajo 👇
"""

    @staticmethod
    def catalog_prompts_examples(products: list[Product]):
        prompt_examples_info = ''
        for index, product in enumerate(products):
            is_last = index == len(products) - 1
            is_first = index == 0
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            product_name = product.names.get(LanguageCode.ES) or product.names.get(LanguageCode.EN)
            prompt_examples_info += f'{left_part if not is_first else "┏"} <b>{index + 1}</b>: {product_name}{right_part}'

        return prompt_examples_info

    CATALOG_PROMPTS_GET_SHORT_PROMPT = "Obtener prompt corto ⚡️"
    CATALOG_PROMPTS_GET_LONG_PROMPT = "Obtener prompt largo 📜"
    CATALOG_PROMPTS_GET_EXAMPLES = "Obtener ejemplos del prompt 👀"
    CATALOG_PROMPTS_COPY = "Copiar prompt 📋"

    # Chats
    @staticmethod
    def chat_info(current_chat_name: str, total_chats: int) -> str:
        return f"""
🗨️ <b>Chat Actual: {current_chat_name}</b>

📈 Total de chats: <b>{total_chats}</b>

Selecciona una acción abajo 👇
"""

    CHAT_DEFAULT_TITLE = "Nuevo chat"
    CHAT_MANAGE = "💬 Gestión de Chats"
    CHAT_CREATE = "💬 Crear Nuevo"
    CHAT_CREATE_SUCCESS = """
🎉 <b>¡Chat Creado!</b>

Puedes cambiar a este chat en /settings
"""
    CHAT_TYPE_TITLE = "Escribe el nombre del chat"
    CHAT_SWITCH = "🔄 Cambiar"
    CHAT_SWITCH_FORBIDDEN_ERROR = """
🚨 <b>¡Espera!</b>

Actualmente estás en tu único chat.

Crea uno nuevo para poder cambiar entre ellos.
"""
    CHAT_SWITCH_SUCCESS = "Chat cambiado con éxito 🎉"
    CHAT_RESET = "♻️ Restablecer"
    CHAT_RESET_WARNING = """
🧹 <b>¡Limpieza de Chat en Camino!</b>

Estás a punto de borrar todos los mensajes y restablecer el contexto del chat actual.

¿Estás seguro de que deseas continuar?
"""
    CHAT_RESET_SUCCESS = """
🧹<b>¡Chat Restablecido con Éxito!</b>

Ahora, como un pez dorado, no recuerdo nada de lo que se dijo antes 🐠
"""
    CHAT_DELETE = "🗑 Eliminar"
    CHAT_DELETE_FORBIDDEN_ERROR = """
🚨 <b>¡Espera!</b>

Este es tu único chat; no se puede eliminar.
"""
    CHAT_DELETE_SUCCESS = "Chat eliminado con éxito 🎉"

    # Eightify
    EIGHTIFY = '👀 Resumen de YouTube'
    EIGHTIFY_INFO = """
👀 Con <b>Resumen de YouTube</b>, puedes obtener un resumen breve y claro de cualquier video de YouTube.

<b>¿Cómo funciona?</b>
🔗 Envía el enlace del video de YouTube que deseas resumir.
✅ Analizaré el video y te devolveré un resumen en texto.

¡Espero tu enlace! 😊
"""
    EIGHTIFY_VALUE_ERROR = """
🧐 <b>Esto no parece un enlace de YouTube</b>

Por favor, <b>envía otro enlace</b>.
"""
    EIGHTIFY_VIDEO_ERROR = """
😢 Lamentablemente, <b>no puedo procesar este video de YouTube</b>.

Por favor, <b>envía otro enlace</b>.
"""

    # Errors
    ERROR = """
🤒 <b>He recibido un error desconocido</b>

Inténtalo de nuevo o contacta con soporte técnico:
"""
    ERROR_NETWORK = """
🤒 <b>He perdido la conexión con Telegram</b>

Inténtalo de nuevo o contacta con soporte técnico:
"""
    ERROR_PROMPT_REQUIRED = """
🚨 <b>¡Espera! ¿Dónde está el prompt?</b>

Una solicitud sin prompt es como un té sin azúcar: no sabe bien ☕️

Escribe algo y la magia comenzará 🪄
"""
    ERROR_PROMPT_TOO_LONG = """
🚨 <b>¡Vaya! Esto no es un prompt, ¡es una novela completa!</b>

Intenta acortar el texto; de lo contrario, el modelo se tomará unas vacaciones 🌴

Espero un nuevo y más compacto prompt ✨
"""
    ERROR_REQUEST_FORBIDDEN = """
🚨 <b>¡Ups! Tu solicitud no pasó la verificación</b>

Mi guardián de seguridad encontró algo sospechoso 🛑

Revisa el texto/la foto en busca de contenido prohibido e inténtalo de nuevo 😌
"""
    ERROR_PHOTO_FORBIDDEN = """
⚠️ <b>El envío de fotos solo está disponible en los siguientes modelos:</b>

🔤 <b>Modelos de texto:</b>
    ┣ ChatGPT 4.0 Omni Mini ✉️
    ┣ ChatGPT 4.0 Omni 💥
    ┣ ChatGPT o1 🧪
    ┣ Claude 3.5 Sonnet 💫
    ┣ Claude 3.0 Opus 🚀
    ┣ Gemini 2.0 Flash 🏎
    ┣ Gemini 1.5 Pro 💼
    ┣ Gemini 1.0 Ultra 🛡️
    ┗ Grok 2.0 🐦

🖼 <b>Modelos gráficos:</b>
    ┣ 🎨 Midjourney
    ┣ 🦄 Stable Diffusion XL
    ┣ 🧑‍🚀 Stable Diffusion 3.5
    ┣ 🌲 Flux 1.0 Dev
    ┣ 🏔 Flux 1.1 Pro
    ┣ 🌌 Luma Photon
    ┣ 📷 FaceSwap
    ┗ 🪄 Photoshop IA

📹 <b>Modelos de video:</b>
    ┣ 🎬 Kling
    ┣ 🎥 Runway
    ┣ 🔆 Luma Ray
    ┗ 🐇 Pika

Para cambiar a un modelo con soporte para lectura de imágenes, utiliza el botón de abajo 👇
"""
    ERROR_PHOTO_REQUIRED = """
⚠️ <b>La foto es obligatoria en este modelo</b>

Por favor, envía una foto junto con el prompt.
"""
    ERROR_ALBUM_FORBIDDEN = """
⚠️ <b>En el modelo actual no puedo procesar varias fotos a la vez</b>

Por favor, envía solo 1 foto.
"""
    ERROR_VIDEO_FORBIDDEN = "⚠️ Aún no puedo trabajar con videos en este modelo."
    ERROR_DOCUMENT_FORBIDDEN = "⚠️ Aún no puedo trabajar con este tipo de documentos."
    ERROR_STICKER_FORBIDDEN = "⚠️ Aún no puedo trabajar con stickers."
    ERROR_SERVER_OVERLOADED = """
🫨 <b>El servidor está bajo mucha carga en este momento</b>

Inténtalo de nuevo más tarde o espera un momento.
"""
    ERROR_FILE_TOO_BIG = """
🚧 <b>¡El archivo es demasiado grande!</b>

Solo puedo procesar archivos de menos de 20 MB.

Inténtalo de nuevo con un archivo más pequeño 😉
"""
    ERROR_IS_NOT_NUMBER = """
🚧 <b>¡Eso no es un número!</b>

Por favor, inténtalo de nuevo con un valor numérico 🔢
"""

    # Examples
    EXAMPLE_INFO = "Para acceder a esta red neuronal, presiona el botón de abajo:"

    @staticmethod
    def example_text_model(model: str):
        return f"👇 Así respondería a tu solicitud *{model}*"

    @staticmethod
    def example_image_model(model: str):
        return f"☝️ Así dibujaría {model} en respuesta a tu solicitud"

    # FaceSwap
    FACE_SWAP_INFO = """
📷 <b>FaceSwap: Elige una de las 3 opciones</b>

👤 <b>Enviar foto</b> — Reemplazaré la cara en tu imagen

✍️ <b>Escribir un prompt</b> — Crearé una imagen con tu cara según la descripción

🤹‍♂️ <b>Elegir un paquete predefinido</b> — Reemplazaré las caras en imágenes listas
"""
    FACE_SWAP_CHOOSE_PHOTO = "👤 Enviar foto"
    FACE_SWAP_CHOOSE_PHOTO_INFO = """
👤 <b>Envía una foto</b>

1️⃣ Envía una foto donde tu rostro sea claramente visible
2️⃣ Reemplazaré la cara en tu foto manteniendo el resto igual

💡 ¡Cuanto mejor sea la calidad, mejor será el resultado!
"""
    FACE_SWAP_CHOOSE_PROMPT = "✍️ Escribir un prompt"
    FACE_SWAP_CHOOSE_PROMPT_INFO = """
✍️ <b>Escribe un prompt</b>

1️⃣ Describe en detalle la imagen que quieres obtener
2️⃣ Crearé una imagen con tu cara basada en tu descripción

💡 ¡Cuantos más detalles, más preciso será el resultado!
"""
    FACE_SWAP_CHOOSE_PACKAGE = "🤹‍♂️ Elegir un paquete"
    FACE_SWAP_CHOOSE_PACKAGE_INFO = """
🤹‍♂️ <b>Elige un paquete</b>

1️⃣ Selecciona uno de los paquetes de imágenes predefinidos
2️⃣ Reemplazaré las caras en todas las imágenes a la vez

💡 ¡Rápido y fácil!
"""
    FACE_SWAP_GENERATIONS_IN_PACKAGES_ENDED = """
📷 <b>¡Vaya! ¡Se han usado todas las generaciones en los paquetes!</b>

<b>¿Qué sigue?</b>
👤 Envía una foto con un rostro — lo reemplazaré con el tuyo
✍️ Escribe un prompt — crearé una imagen con tu cara
"""
    FACE_SWAP_MIN_ERROR = """
🤨 <b>¡Espera!</b>

Estás intentando solicitar menos de 1 imagen, eso no funcionará.

<b>Introduce un número mayor que 0</b>
"""
    FACE_SWAP_MAX_ERROR = """
🤨 <b>¡Espera!</b>

Estás pidiendo más imágenes de las que tenemos disponibles.

<b>Introduce un número menor</b>
"""
    FACE_SWAP_NO_FACE_FOUND_ERROR = """
🚫 <b>Problema al procesar la foto</b>

Lamentablemente, no pude detectar un rostro en la foto. Por favor, carga una nueva foto en buena calidad donde tu rostro sea claramente visible.

Después de cargar una nueva foto, inténtalo de nuevo 🔄
"""

    @staticmethod
    def face_swap_choose_package(name: str, available_images: int, total_images: int, used_images: int) -> str:
        remain_images = total_images - used_images
        footer_text = f'<b>Escribe</b> cuántos cambios de rostro quieres realizar, o <b>elige</b> abajo 👇' if remain_images > 0 else ''

        return f"""
<b>{name}</b>

El paquete incluye: <b>{total_images} imágenes</b>

🌠 <b>Generaciones Disponibles</b>: {available_images} imágenes
<i>Si necesitas más, revisa /buy o /bonus</i>

🔍 <b>Usadas</b>: {used_images} imágenes
🚀 <b>Restantes</b>: {remain_images} imágenes

{footer_text}
"""

    @staticmethod
    def face_swap_package_forbidden_error(available_images: int) -> str:
        return f"""
🚧 <b>¡No hay suficientes generaciones!</b>

Solo te quedan <b>{available_images} generaciones</b> en tu arsenal

💡 <b>Consejo:</b> Prueba con un número menor o utiliza /buy para obtener posibilidades ilimitadas
"""

    # Feedback
    FEEDBACK_INFO = """
📡 <b>Comentarios</b>

Ayúdame a mejorar compartiendo tu opinión:
• <b>¿Qué te gusta?</b> Cuéntamelo
• <b>¿Tienes sugerencias?</b> Compártelas
• <b>¿Encontraste problemas?</b> Infórmame

Espero tus comentarios 💌
"""
    FEEDBACK_SUCCESS = """
🌟 <b>¡Comentarios recibidos!</b>

Tu opinión es el ingrediente secreto del éxito. Ya estoy preparando mejoras 🍳

Recibirás <b>25 créditos</b> después de que mis creadores revisen el contenido de tus comentarios.
"""
    FEEDBACK_APPROVED = """
🌟 <b>¡Comentarios aprobados!</b>

Gracias por ayudarme a mejorar.

Tu recompensa: <b>+25 créditos</b> 🪙
"""
    FEEDBACK_APPROVED_WITH_LIMIT_ERROR = """
🌟 <b>¡Comentarios aprobados!</b>

Gracias por ayudarme a mejorar.

Lamentablemente, no puedo otorgarte una recompensa porque se ha alcanzado el límite.
"""
    FEEDBACK_DENIED = """
🌟 <b>¡Comentarios rechazados!</b>

Tus comentarios no fueron lo suficientemente constructivos y no puedo aumentar tu saldo de bonificación 😢
"""

    # Flux
    FLUX_STRICT_SAFETY_TOLERANCE = "🔒 Estricta"
    FLUX_MIDDLE_SAFETY_TOLERANCE = "🔏 Media"
    FLUX_PERMISSIVE_SAFETY_TOLERANCE = "🔓 Baja"

    # Gemini Video
    GEMINI_VIDEO = "📼 Resumen de Video"
    GEMINI_VIDEO_INFO = """
📼 Con <b>Resumen de Video</b>, puedes obtener un breve resumen textual de cualquier video.

<b>¿Cómo funciona?</b> Hay 2 opciones:
1.
🔗 Envía el enlace del video que deseas resumir.
⚠️ El video debe durar menos de 1 hora.
✅ Analizaré el video y te devolveré un resumen en texto.

2.
🔗 Envía el video directamente aquí en Telegram.
⚠️ El video debe durar menos de 1 hora y tener un tamaño inferior a 20 MB.
✅ Analizaré el video y te devolveré un resumen en texto.

¡Espero tu enlace/video! 😊
"""
    GEMINI_VIDEO_TOO_LONG_ERROR = """
⚠️ <b>La duración del video debe ser menor a 60 minutos</b>

Por favor, <b>envía otro video</b>
"""
    GEMINI_VIDEO_VALUE_ERROR = """
⚠️ <b>Esto no parece un enlace de video</b>

Por favor, <b>envía otro enlace</b>
"""

    @staticmethod
    def gemini_video_prompt(
        focus: VideoSummaryFocus,
        format: VideoSummaryFormat,
        amount: VideoSummaryAmount,
    ) -> str:
        if focus == VideoSummaryFocus.INSIGHTFUL:
            focus = Spanish.VIDEO_SUMMARY_FOCUS_INSIGHTFUL
        elif focus == VideoSummaryFocus.FUNNY:
            focus = Spanish.VIDEO_SUMMARY_FOCUS_FUNNY
        elif focus == VideoSummaryFocus.ACTIONABLE:
            focus = Spanish.VIDEO_SUMMARY_FOCUS_ACTIONABLE
        elif focus == VideoSummaryFocus.CONTROVERSIAL:
            focus = Spanish.VIDEO_SUMMARY_FOCUS_CONTROVERSIAL

        if format == VideoSummaryFormat.LIST:
            format = "1. <Emoji> Descripción"
        elif format == VideoSummaryFormat.FAQ:
            format = "❔ _Pregunta_: <Pregunta>.\n❕ _Respuesta_: <Respuesta>"

        if amount == VideoSummaryAmount.AUTO:
            amount = Spanish.VIDEO_SUMMARY_AMOUNT_AUTO
        elif amount == VideoSummaryAmount.SHORT:
            amount = Spanish.VIDEO_SUMMARY_AMOUNT_SHORT
        elif amount == VideoSummaryAmount.DETAILED:
            amount = Spanish.VIDEO_SUMMARY_AMOUNT_DETAILED

        return f"""
Por favor, crea un resumen bonito y estructurado del video proporcionado usando formato Markdown de la siguiente manera:
- Divide el resumen en bloques temáticos en el formato: **<Emoji> Título del bloque temático**.
- En cada bloque, enumera varios puntos clave en el formato: {format}.
- Concluye cada punto con una idea clara e informativa.
- Evita usar el símbolo "-" en la estructura.
- No uses etiquetas HTML.
- Destaca las palabras clave con el formato: **Palabras clave**.
- Estructura el resumen de forma interesante, visualmente atractiva y organizada.
- Enfoque del resumen: {focus}.
- Longitud de la respuesta: {amount}. Donde Breve: 2-3 bloques temáticos. Automático: 4-5 bloques temáticos. Detallado: 6-10 bloques temáticos. Por bloques temáticos se entiende encabezados temáticos, no puntos, aunque el número de puntos puede variar según la longitud.
- Proporciona la respuesta en español.

Usa emojis únicos para resaltar cada punto. La respuesta debe ser visualmente atractiva y estrictamente estructurada en el formato especificado, sin introducciones ni comentarios adicionales.
"""

    # Gender
    GENDER_CHOOSE = "🚹🚺 Seleccionar género"
    GENDER_CHANGE = "🚹🚺 Cambiar género"
    GENDER_UNSPECIFIED = "🤷 No especificado"
    GENDER_MALE = "👕 Masculino"
    GENDER_FEMALE = "👚 Femenino"

    # Generation
    GENERATION_IMAGE_SUCCESS = "✨ Aquí está tu imagen generada 🎨"
    GENERATION_VIDEO_SUCCESS = "✨ Aquí está tu video generado 🎞"

    # Help
    HELP_INFO = """
🛟 <b>Ayuda y Comandos</b>

─────────────

👋 <b>Comandos Generales:</b>
/start — Acerca de mí
/profile — Tu perfil
/language — Cambiar idioma
/buy — Comprar suscripciones/paquetes
/bonus — Información sobre bonificaciones
/promo_code — Activar un código promocional
/feedback — Enviar comentarios
/terms — Términos de servicio

─────────────

🤖 <b>Redes Neuronales:</b>
/model — Seleccionar red neuronal
/info — Información sobre redes neuronales
/catalog — Catálogo de roles y prompts
/settings — Configuración de modelos

─────────────

🔤 <b>Redes Neuronales de Texto:</b>
/chatgpt — Seleccionar ChatGPT
/claude — Seleccionar Claude
/gemini — Seleccionar Gemini
/grok — Seleccionar Grok
/perplexity — Seleccionar Perplexity

─────────────

📝 <b>Resúmenes con Redes Neuronales:</b>
/youtube_summary — Seleccionar Resumen de YouTube
/video_summary — Seleccionar Resumen de Video

─────────────

🖼 <b>Redes Neuronales Gráficas:</b>
/dalle — Seleccionar DALL-E
/midjourney — Seleccionar MidJourney
/stable_diffusion — Seleccionar Stable Diffusion
/flux — Seleccionar Flux
/luma_photon — Seleccionar Luma Photon
/recraft — Seleccionar Recraft
/face_swap — Seleccionar FaceSwap
/photoshop — Seleccionar Photoshop AI

─────────────

🎵 <b>Redes Neuronales Musicales:</b>
/music_gen — Seleccionar MusicGen
/suno — Seleccionar Suno

─────────────

📹 <b>Redes Neuronales de Video:</b>
/kling — Seleccionar Kling
/runway — Seleccionar Runway
/luma_ray — Seleccionar Luma Ray
/pika — Seleccionar Pika

─────────────

Para cualquier consulta también puedes contactar al soporte técnico:
"""

    # Info
    INFO = "🤖 <b>Elige el tipo de modelos sobre los que deseas obtener información:</b>"
    INFO_TEXT_MODELS = "🤖 <b>Elige el modelo de texto sobre el que deseas obtener información:</b>"
    INFO_IMAGE_MODELS = "🤖 <b>Elige el modelo gráfico sobre el que deseas obtener información:</b>"
    INFO_MUSIC_MODELS = "🤖 <b>Elige el modelo musical sobre el que deseas obtener información:</b>"
    INFO_VIDEO_MODELS = "🤖 <b>Elige el modelo de video sobre el que deseas obtener información:</b>"
    INFO_CHAT_GPT = "🤖 <b>Selecciona el modelo ChatGPT</b> sobre el cual deseas obtener información:"
    INFO_CHAT_GPT_4_OMNI_MINI = f"""
<b>{Texts.CHAT_GPT_4_OMNI_MINI}</b>

<b>Creador:</b> OpenAI

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Por encima del promedio 🟢
• Velocidad de respuesta: Alta 🟢

📊 <b>Pruebas:</b>
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

<b>Creador:</b> OpenAI

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Por encima del promedio 🟢

📊 <b>Pruebas:</b>
• MMLU: 88.7%
• GPQA: 53.6%
• DROP: 83.4%
• MGSM: 90.5%
• MATH: 76.6%
• HumanEval: 90.2%
• MMMU: 69.1%
• MathVista: 63.8%
"""
    INFO_CHAT_GPT_O_1_MINI = f"""
<b>{Texts.CHAT_GPT_O_1_MINI}</b>

<b>Creador:</b> OpenAI

💡<b>Usos:</b>
• Generación de contenido
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: No 🔴
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Media 🟡

📊 <b>Pruebas:</b>
• MMLU: 85.2%
• GPQA: 60.0%
• MATH: 90.0%
• HumanEval: 92.4%
"""
    INFO_CHAT_GPT_O_1 = f"""
<b>{Texts.CHAT_GPT_O_1}</b>

<b>Creador:</b> OpenAI

💡<b>Usos:</b>
• Generación de contenido
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Media 🟡

📊 <b>Pruebas:</b>
• MMLU: 92.3%
• GPQA: 75.7%
• MGSM: 89.3%
• MATH: 96.4%
• HumanEval: 92.4%
• MMMU: 78.2%
• MathVista: 73.9%
"""
    INFO_CLAUDE = "🤖 <b>Selecciona el modelo Claude</b> sobre el cual deseas obtener información:"
    INFO_CLAUDE_3_HAIKU = f"""
<b>{Texts.CLAUDE_3_HAIKU}</b>

<b>Creador:</b> Anthropic

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: No 🔴
• Calidad de respuestas: Por encima del promedio 🟢
• Velocidad de respuesta: Alta 🟢

📊 <b>Pruebas:</b>
• MMLU: 80.9%
• GPQA: 41.6%
• DROP: 83.1%
• MGSM: 85.6%
• MATH: 69.2%
• HumanEval: 88.1%
"""
    INFO_CLAUDE_3_SONNET = f"""
<b>{Texts.CLAUDE_3_SONNET}</b>

<b>Creador:</b> Anthropic

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Por encima del promedio 🟢

📊 <b>Pruebas:</b>
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

<b>Creador:</b> Anthropic

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Por encima del promedio 🟢
• Velocidad de respuesta: Media 🟡

📊 <b>Pruebas:</b>
• MMLU: 88.2%
• GPQA: 50.4%
• DROP: 83.1%
• MGSM: 90.7%
• MATH: 60.1%
• HumanEval: 84.9%
• MMMU: 59.4%
• MathVista: 50.5%
"""
    INFO_GEMINI = "🤖 <b>Selecciona el modelo Gemini</b> sobre el cual deseas obtener información:"
    INFO_GEMINI_2_FLASH = f"""
<b>{Texts.GEMINI_2_FLASH}</b>

<b>Creador:</b> Google

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Por encima del promedio 🟢
• Velocidad de respuesta: Alta 🟢

📊 <b>Pruebas:</b>
• MMLU: 76.4%
• GPQA: 62.1%
• MATH: 89.7%
• MMMU: 70.7%
"""
    INFO_GEMINI_1_PRO = f"""
<b>{Texts.GEMINI_1_PRO}</b>

<b>Creador:</b> Google

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Media 🟡

📊 <b>Pruebas:</b>
• MMLU: 75.8%
• GPQA: 59.1%
• MATH: 86.5%
• MMMU: 65.9%
"""
    INFO_GEMINI_1_ULTRA = f"""
<b>{Texts.GEMINI_1_ULTRA}</b>

<b>Creador:</b> Google

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Media 🟡

📊 <b>Pruebas:</b>
• MMLU: 90.0%
• DROP: 82.4%
• HumanEval: 74.4%
• MATH: 53.2%
• MMMU: 59.4%
"""
    INFO_GROK = f"""
<b>{Texts.GROK}</b>

<b>Creador:</b> X (Twitter)

💡<b>Usos:</b>
• Generación de contenido
• Generación de ideas
• Redacción
• Comunicación y soporte
• Explicación de conceptos complejos
• Respuesta a preguntas
• Traducción entre idiomas
• Asistencia en aprendizaje
• Resolución de problemas
• Procesamiento de texto
• Trabajo con código
• Recomendaciones

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: Sí 🟢
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Por encima del promedio 🟢

📊 <b>Pruebas:</b>
• MMLU: 87.5%
• GPQA: 56.0%
• MATH: 76.1%
• HumanEval: 88.4%
• MMMU: 66.1%
• MathVista: 69.0%
"""
    INFO_PERPLEXITY = f"""
<b>{Texts.PERPLEXITY}</b>

💡<b>Usos:</b>
• Búsqueda de información actualizada en tiempo real
• Respuesta a preguntas que requieren datos recientes
• Monitoreo de eventos actuales
• Búsqueda de fuentes para verificar información
• Comparación de datos de diferentes fuentes
• Asistencia en la redacción de artículos científicos con datos actualizados
• Búsqueda de enlaces a investigaciones, informes y estadísticas
• Búsqueda rápida de definiciones y explicaciones de términos
• Creación de listas de referencias bibliográficas
• Búsqueda de ejemplos para materiales educativos
• Análisis de tendencias actuales del mercado
• Búsqueda de competidores y sus productos
• Monitoreo de reseñas y menciones sobre una empresa o producto
• Recopilación de datos para campañas publicitarias
• Evaluación de los intereses de la audiencia objetivo según las consultas de búsqueda
• Búsqueda de ideas para contenido
• Respuesta a solicitudes específicas en tiempo real

🚦 <b>Evaluaciones:</b>
• Trabajo con imágenes: No 🔴
• Calidad de respuestas: Alta 🟢
• Velocidad de respuesta: Media 🟡
"""
    INFO_DALL_E = f"""
<b>{Texts.DALL_E}</b>

• <i>Arte a pedido</i>: Generación de imágenes únicas basadas en descripciones, ideal para ilustradores o quienes buscan inspiración.
• <i>Creador publicitario</i>: Creación de imágenes atractivas para publicidad o contenido en redes sociales.
• <i>Herramienta educativa</i>: Visualización de conceptos complejos para mejorar la comprensión en la enseñanza.
• <i>Diseño de interiores</i>: Obtención de ideas para la distribución de espacios o temas decorativos.
• <i>Diseño de moda</i>: Creación de diseños de ropa o ilustraciones de moda.
"""
    INFO_MIDJOURNEY = f"""
<b>{Texts.MIDJOURNEY}</b>

• <i>Diseño artístico</i>: Creación de obras maestras visuales y abstracciones, ideal para artistas y diseñadores que buscan un estilo único.
• <i>Modelado arquitectónico</i>: Generación de proyectos conceptuales de edificios y planificación de espacios.
• <i>Asistente educativo</i>: Ilustraciones para materiales de aprendizaje que mejoran la comprensión de temas complejos.
• <i>Diseño de interiores</i>: Visualización de soluciones de interiores, desde estilos clásicos hasta tendencias modernas.
• <i>Moda y estilo</i>: Desarrollo de looks de moda y accesorios, experimentando con colores y formas.
"""
    INFO_STABLE_DIFFUSION = "🤖 <b>Selecciona el modelo Stable Diffusion</b> sobre el cual deseas obtener más información:"
    INFO_STABLE_DIFFUSION_XL = f"""
<b>{Texts.STABLE_DIFFUSION_XL}</b>

• <i>Ilustración creativa</i>: Generación de imágenes únicas basadas en solicitudes de texto, perfecta para artistas, diseñadores y escritores.
• <i>Arte conceptual y bocetos</i>: Creación de imágenes conceptuales para videojuegos, películas y otros proyectos, ayudando a visualizar ideas.
• <i>Estilización de imágenes</i>: Transformación de imágenes existentes en diversos estilos artísticos, desde cómics hasta corrientes pictóricas clásicas.
• <i>Prototipado de diseño</i>: Generación rápida de conceptos visuales para logotipos, pósters o diseño web.
• <i>Experimentos con estilos artísticos</i>: Posibilidad de explorar colores, formas y texturas para desarrollar nuevas soluciones visuales.
"""
    INFO_STABLE_DIFFUSION_3 = f"""
<b>{Texts.STABLE_DIFFUSION_3}</b>

• <i>Ilustración creativa</i>: Generación de imágenes únicas basadas en solicitudes de texto, perfecta para artistas, diseñadores y escritores.
• <i>Arte conceptual y bocetos</i>: Creación de imágenes conceptuales para videojuegos, películas y otros proyectos, ayudando a visualizar ideas.
• <i>Estilización de imágenes</i>: Transformación de imágenes existentes en diversos estilos artísticos, desde cómics hasta corrientes pictóricas clásicas.
• <i>Prototipado de diseño</i>: Generación rápida de conceptos visuales para logotipos, pósters o diseño web.
• <i>Experimentos con estilos artísticos</i>: Posibilidad de explorar colores, formas y texturas para desarrollar nuevas soluciones visuales.
"""
    INFO_FLUX = "🤖 <b>Selecciona el modelo Flux</b> sobre el cual deseas obtener más información:"
    INFO_FLUX_1_DEV = f"""
<b>{Texts.FLUX_1_DEV}</b>

• <i>Variaciones infinitas</i>: Generación de imágenes diversas basadas en una sola solicitud, cada resultado es único.
• <i>Ajuste preciso de parámetros</i>: Controla el proceso de creación para obtener un resultado exacto que se adapte a tus necesidades.
• <i>Generación con elementos aleatorios</i>: Introduce elementos de azar para soluciones creativas inesperadas.
• <i>Diversidad de conceptos visuales</i>: Explora una amplia gama de estilos y enfoques artísticos, adaptando el proceso a tus objetivos.
• <i>Experimentos visuales rápidos</i>: Prueba múltiples conceptos y estilos sin restricciones, descubriendo nuevos horizontes creativos.
"""
    INFO_FLUX_1_PRO = f"""
<b>{Texts.FLUX_1_PRO}</b>

• <i>Variaciones infinitas</i>: Generación de imágenes diversas basadas en una sola solicitud, cada resultado es único.
• <i>Ajuste preciso de parámetros</i>: Controla el proceso de creación para obtener un resultado exacto que se adapte a tus necesidades.
• <i>Generación con elementos aleatorios</i>: Introduce elementos de azar para soluciones creativas inesperadas.
• <i>Diversidad de conceptos visuales</i>: Explora una amplia gama de estilos y enfoques artísticos, adaptando el proceso a tus objetivos.
• <i>Experimentos visuales rápidos</i>: Prueba múltiples conceptos y estilos sin restricciones, descubriendo nuevos horizontes creativos.
"""
    INFO_LUMA_PHOTON = f"""
<b>{Texts.LUMA_PHOTON}</b>

• <i>Imágenes fotorrealistas</i>: Creación de visualizaciones de alta calidad para arquitectura, diseño y marketing.
• <i>Modelado tridimensional</i>: Generación de conceptos 3D y visualizaciones, ideal para presentaciones y proyectos.
• <i>Efectos de luz y texturas</i>: Control avanzado de efectos de luz y texturas para lograr imágenes realistas.
• <i>Renderizado creativo</i>: Experimenta con composiciones y estilos para crear visualizaciones artísticas únicas.
• <i>Eficiencia en el trabajo</i>: Óptimo para profesionales que buscan resultados rápidos y de alta calidad para sus proyectos.
"""
    INFO_RECRAFT = f"""
<b>{Texts.RECRAFT}</b>

• <i>Imágenes fotorrealistas</i>: Crea imágenes detalladas, ideales para arquitectura, diseño y marketing
• <i>Trabajo con texturas</i>: Añade texturas complejas y crea superficies realistas para mejorar el impacto visual
• <i>Visualizaciones estilizadas</i>: Experimenta con estilos artísticos únicos y composiciones creativas
• <i>Alta velocidad de renderizado</i>: Genera imágenes rápidamente sin perder calidad
• <i>Fácil de usar</i>: Perfecto para diseñadores, artistas y profesionales que buscan ahorrar tiempo
"""
    INFO_FACE_SWAP = f"""
<b>{Texts.FACE_SWAP}</b>

• <i>Redescubrimientos divertidos</i>: Mira cómo te verías en diferentes épocas históricas o como personajes icónicos del cine.
• <i>Felicitaciones personalizadas</i>: Crea tarjetas únicas o invitaciones con imágenes personalizadas.
• <i>Memes y creación de contenido</i>: Dale vida a tus redes sociales con fotos graciosas o imaginativas usando cambio de rostro.
• <i>Transformaciones digitales</i>: Experimenta con nuevos cortes de cabello o estilos de maquillaje.
• <i>Fusiona tu rostro con celebridades</i>: Combina tu cara con la de famosos para comparaciones divertidas.
"""
    INFO_PHOTOSHOP_AI = f"""
<b>{Texts.PHOTOSHOP_AI}</b>

• <i>Mejora de calidad</i>: Aumenta la resolución de la imagen, mejora la claridad y elimina ruidos, haciendo que la foto sea más detallada y brillante.
• <i>Restauración de fotos</i>: Recupera fotografías antiguas o dañadas devolviéndoles su aspecto original.
• <i>Transformación de blanco y negro a color</i>: Da vida a fotos monocromáticas añadiendo colores vibrantes y naturales.
• <i>Eliminación de fondos</i>: Elimina fácilmente el fondo de las imágenes, dejando solo el objeto principal.
"""
    INFO_MUSIC_GEN = f"""
<b>{Texts.MUSIC_GEN}</b>

• <i>Creación de melodías únicas</i>: Convierte tus ideas en obras musicales de cualquier género, desde clásico hasta pop.
• <i>Pistas de audio personalizadas</i>: Crea la banda sonora perfecta para tu próximo proyecto de video, juego o presentación.
• <i>Exploración de estilos musicales</i>: Experimenta con diferentes géneros y sonidos para encontrar tu propio estilo único.
• <i>Educación e inspiración musical</i>: Aprende sobre teoría musical e historia de géneros mientras creas música.
• <i>Generación instantánea de melodías</i>: Solo describe tu idea o estado de ánimo, y MusicGen lo transformará en música al instante.
"""
    INFO_SUNO = f"""
<b>{Texts.SUNO}</b>

• <i>Transformación de texto en canciones</i>: Suno convierte tus letras en canciones, ajustando la melodía y el ritmo a tu estilo.
• <i>Canciones personalizadas</i>: Crea canciones únicas para momentos especiales, desde un regalo personal hasta la banda sonora de tu evento.
• <i>Explora la diversidad de géneros musicales</i>: Descubre nuevos horizontes musicales experimentando con estilos y sonidos diversos.
• <i>Educación e inspiración musical</i>: Aprende teoría musical e historia de los géneros practicando composición.
• <i>Creación rápida de música</i>: Describe tus emociones o una historia, y Suno convertirá tu descripción en una canción al instante.
"""
    INFO_KLING = f"""
<b>{Texts.KLING}</b>

• <i>Generación de videos a partir de descripciones</i>: Describe tu idea y Kling creará un video impresionante.
• <i>Trabajo con estilos únicos</i>: Explora diversos estilos para resaltar la singularidad de tu video.
• <i>Transiciones dinámicas</i>: Añade automáticamente transiciones fluidas y efectivas entre escenas.
• <i>Efectos visuales creativos</i>: Genera videos con efectos modernos para tus proyectos.
• <i>Contenido en minutos</i>: Crea videos impactantes rápidamente sin necesidad de experiencia en edición de video.
"""
    INFO_RUNWAY = f"""
<b>{Texts.RUNWAY}</b>

• <i>Creación de clips cortos</i>: Describe una idea o guion, agrega una foto, y Runway generará un videoclip único.
• <i>Generación de videos a partir de foto + texto</i>: Transforma una imagen y una descripción en un video dinámico.
• <i>Animaciones y efectos visuales</i>: Crea animaciones atractivas y creativas basadas en tus ideas.
• <i>Contenido IA para redes sociales</i>: Genera rápidamente videos llamativos para plataformas y proyectos.
• <i>Exploración de formatos de video</i>: Experimenta con el poder del IA para desarrollar nuevos estilos y contenidos visuales.
"""
    INFO_LUMA_RAY = f"""
<b>{Texts.LUMA_RAY}</b>

• <i>Videos de alta calidad</i>: Genera videos realistas y dinámicos a partir de descripciones.
• <i>Animación 3D</i>: Crea animaciones tridimensionales impresionantes para tus proyectos.
• <i>Estilo cinematográfico</i>: Aplica efectos y composiciones dignos del cine profesional.
• <i>Magia visual</i>: Utiliza tecnología avanzada para producir contenido de alta calidad.
• <i>Formatos innovadores de video</i>: Experimenta con nuevos estilos y enfoques en la creación de contenido visual.
"""
    INFO_PIKA = f"""
<b>{Texts.PIKA}</b>

• <i>Generación de video</i>: Describe tu idea y Pika creará un video único en cuestión de minutos
• <i>Estilización de video</i>: Aplica estilos artísticos para hacer que tu video sea original y memorable
• <i>Adición de animaciones</i>: Convierte elementos estáticos en escenas dinámicas con movimientos fluidos
• <i>Contenido interactivo</i>: Crea videos que capturen la atención y mantengan a los espectadores comprometidos
• <i>Contenido sin esfuerzo</i>: Genera videos profesionales con facilidad, incluso si eres principiante
"""

    # Kling
    KLING_MODE_STANDARD = "🔸 Estándar"
    KLING_MODE_PRO = "🔹 Pro"

    # Language
    LANGUAGE = "Idioma:"
    LANGUAGE_CHOSEN = "Idioma seleccionado: Español 🇪🇸"

    # Maintenance Mode
    MAINTENANCE_MODE = "🤖 Estoy en modo de mantenimiento. Por favor, espera un poco 🛠"

    # Midjourney
    MIDJOURNEY_ALREADY_CHOSE_UPSCALE = "Ya has elegido esta imagen, intenta con una nueva 🙂"

    # Model
    MODEL = "Para <b>cambiar el modelo</b>, presiona el botón de abajo 👇"
    MODEL_CHANGE_AI = "🤖 Cambiar modelo de AI"
    MODEL_CHOOSE_CHAT_GPT = "Para seleccionar el modelo <b>ChatGPT 💭</b>, presiona el botón de abajo 👇"
    MODEL_CHOOSE_CLAUDE = "Para seleccionar el modelo <b>Claude 📄</b>, presiona el botón de abajo 👇"
    MODEL_CHOOSE_GEMINI = "Para seleccionar el modelo <b>Gemini ✨</b>, presiona el botón de abajo 👇"
    MODEL_CHOOSE_STABLE_DIFFUSION = "Para seleccionar el modelo <b>Stable Diffusion 🎆</b>, presiona el botón de abajo 👇"
    MODEL_CHOOSE_FLUX = "Para seleccionar el modelo <b>Flux 🫐</b>, presiona el botón de abajo 👇"
    MODEL_CONTINUE_GENERATING = "Continuar generando"
    MODEL_ALREADY_MAKE_REQUEST = "⚠️ Ya has hecho una solicitud. Por favor, espera."
    MODEL_READY_FOR_NEW_REQUEST = "😌 Puedes hacer la siguiente solicitud."
    MODEL_SHOW_QUOTA = "🔄 Mostrar límites de la suscripción"
    MODEL_SWITCHED_TO_AI_MANAGE = "⚙️ Gestión"
    MODEL_SWITCHED_TO_AI_MANAGE_INFO = "Selecciona lo que deseas hacer con el modelo:"
    MODEL_SWITCHED_TO_AI_SETTINGS = "🛠️ Ir a configuración"
    MODEL_SWITCHED_TO_AI_INFO = "ℹ️ Obtener más información"
    MODEL_SWITCHED_TO_AI_EXAMPLES = "💡 Mostrar ejemplos de solicitudes"
    MODEL_ALREADY_SWITCHED_TO_THIS_MODEL = """
🔄 <b>¡Todo sigue igual!</b>

Has seleccionado el mismo modelo que ya estás usando.
"""

    @staticmethod
    def model_switched(model_name: str, model_type: ModelType, model_info: dict):
        if model_type == ModelType.TEXT:
            model_role = model_info.get('role').split(' ')
            model_role = ' '.join(model_role[1:] + [model_role[0]])
            facts = f"""<b>Hechos y configuraciones:</b>
📅 Conocimientos hasta: {model_info.get('training_data')}
📷 Compatibilidad con fotos: {'Sí ✅' if model_info.get('support_photos', False) else 'No ❌'}
{Spanish.VOICE_MESSAGES}: {'Activadas ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Desactivadas ❌'}
🎭 Rol: {model_role}"""
        elif model_type == ModelType.SUMMARY:
            model_focus = model_info.get(UserSettings.FOCUS, VideoSummaryFocus.INSIGHTFUL)
            if model_focus == VideoSummaryFocus.INSIGHTFUL:
                model_focus = ' '.join(reversed(Spanish.VIDEO_SUMMARY_FOCUS_INSIGHTFUL.split(' ', 1)))
            elif model_focus == VideoSummaryFocus.FUNNY:
                model_focus = ' '.join(reversed(Spanish.VIDEO_SUMMARY_FOCUS_FUNNY.split(' ', 1)))
            elif model_focus == VideoSummaryFocus.ACTIONABLE:
                model_focus = ' '.join(reversed(Spanish.VIDEO_SUMMARY_FOCUS_ACTIONABLE.split(' ', 1)))
            elif model_focus == VideoSummaryFocus.CONTROVERSIAL:
                model_focus = ' '.join(reversed(Spanish.VIDEO_SUMMARY_FOCUS_CONTROVERSIAL.split(' ', 1)))

            model_format = model_info.get(UserSettings.FORMAT, VideoSummaryFormat.LIST)
            if model_format == VideoSummaryFormat.LIST:
                model_format = ' '.join(reversed(Spanish.VIDEO_SUMMARY_FORMAT_LIST.split(' ', 1)))
            elif model_format == VideoSummaryFormat.FAQ:
                model_format = ' '.join(reversed(Spanish.VIDEO_SUMMARY_FORMAT_FAQ.split(' ', 1)))

            model_amount = model_info.get(UserSettings.AMOUNT, VideoSummaryAmount.AUTO)
            if model_amount == VideoSummaryAmount.AUTO:
                model_amount = ' '.join(reversed(Spanish.VIDEO_SUMMARY_AMOUNT_AUTO.split(' ', 1)))
            elif model_amount == VideoSummaryAmount.SHORT:
                model_amount = ' '.join(reversed(Spanish.VIDEO_SUMMARY_AMOUNT_SHORT.split(' ', 1)))
            elif model_amount == VideoSummaryAmount.DETAILED:
                model_amount = ' '.join(reversed(Spanish.VIDEO_SUMMARY_AMOUNT_DETAILED.split(' ', 1)))

            facts = f"""<b>Hechos y configuraciones:</b>
{Spanish.SETTINGS_FOCUS}: {model_focus}
{Spanish.SETTINGS_FORMAT}: {model_format}
{Spanish.SETTINGS_AMOUNT}: {model_amount}
{Spanish.VOICE_MESSAGES}: {'Activadas ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Desactivadas ❌'}"""
        elif model_type == ModelType.IMAGE:
            model_version = get_model_version(model_info)
            model_version_info = f'\n{Spanish.SETTINGS_VERSION}: {model_version}' if model_version else ''
            facts = f"""<b>Hechos y configuraciones:</b>{model_version_info}
📷 Compatibilidad con fotos: {'Sí ✅' if model_info.get('support_photos', False) else 'No ❌'}
{Spanish.SETTINGS_ASPECT_RATIO}: {'Personalizado' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
{Spanish.SETTINGS_SEND_TYPE}: {'Documento 📄' if model_info.get(UserSettings.SEND_TYPE, SendType.IMAGE) == SendType.DOCUMENT else 'Imagen 🖼'}"""
        elif model_type == ModelType.MUSIC:
            model_version = get_model_version(model_info)
            model_version_info = f'\n{Spanish.SETTINGS_VERSION}: {model_version}' if model_version else ''
            facts = f"""<b>Hechos y configuraciones:</b>{model_version_info}
{Spanish.SETTINGS_SEND_TYPE}: {'Video 📺' if model_info.get(UserSettings.SEND_TYPE, SendType.AUDIO) == SendType.VIDEO else 'Audio 🎤'}"""
        elif model_type == ModelType.VIDEO:
            model_version = get_model_version(model_info)
            model_version_info = f'\n{Spanish.SETTINGS_VERSION}: {model_version}' if model_version else ''
            facts = f"""<b>Hechos y configuraciones:</b>{model_version_info}
📷 Compatibilidad con fotos: {'Sí ✅' if model_info.get('support_photos', False) else 'No ❌'}
{Spanish.SETTINGS_ASPECT_RATIO}: {'Personalizado' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
{Spanish.SETTINGS_DURATION}: {model_info.get(UserSettings.DURATION, 5)} segundos
{Spanish.SETTINGS_SEND_TYPE}: {'Documento 📄' if model_info.get(UserSettings.SEND_TYPE, SendType.VIDEO) == SendType.DOCUMENT else 'Video 📺'}"""
        else:
            facts = f"ℹ️ Hechos y configuraciones: Próximamente 🔜"

        return f"""
<b>{model_name}</b>
👆 Modelo seleccionado

{facts}

Para <b>acceder a la configuración</b>, <b>obtener más información sobre el modelo</b> y <b>ver ejemplos de solicitudes</b>, presiona el botón de abajo 👇
"""

    @staticmethod
    def model_text_processing_request() -> str:
        texts = [
            "Estoy consultando mi bola de cristal digital para encontrar la mejor respuesta... 🔮",
            "Un momento, estoy entrenando a mis hámsters para generar tu respuesta... 🐹",
            "Revisando mi biblioteca digital en busca de la respuesta perfecta. Un poco de paciencia... 📚",
            "Espera, estoy convocando a mi gurú interno de IA para responder tu pregunta... 🧘",
            "Un momento mientras consulto a los maestros de internet para encontrar tu respuesta... 👾",
            "Recolectando sabiduría ancestral... o al menos lo que puedo encontrar en internet... 🌐",
            "Un segundo, me estoy poniendo mi sombrero de pensar... Ah, mucho mejor. Ahora, veamos... 🎩",
            "Remangándome mis mangas virtuales para ponerme manos a la obra. Tu respuesta está en camino... 💪",
            "¡Trabajando al máximo! Mis engranajes de IA están girando para traerte la mejor respuesta... 🚂",
            "Sumergiéndome en un océano de datos para pescar tu respuesta. Vuelvo enseguida... 🎣",
            "Consultando a mis elfos virtuales. Ellos suelen ser excelentes encontrando respuestas... 🧝",
            "Activando el motor warp para una búsqueda rápida de tu respuesta. ¡Sujétate fuerte... 🚀",
            "Estoy en la cocina preparando un lote fresco de respuestas. ¡Este será sabroso... 🍳",
            "Haciendo un viaje rápido a la nube y de vuelta. Espero traer unas gotas de sabiduría... ☁️",
            "Plantando tu pregunta en mi jardín digital. Veamos qué florece... 🌱",
            "Fortaleciendo mis músculos virtuales para una respuesta poderosa... 💪",
            "¡Zas! Proceso de cálculo en marcha. La respuesta estará lista pronto... 🪄",
            "Mis búhos digitales están volando en busca de una respuesta sabia. Volverán pronto con algo interesante... 🦉",
            "Hay una tormenta de ideas en el ciberespacio. Atrapo rayos para crear la respuesta... ⚡",
            "Mi equipo de mapaches digitales está buscando la mejor respuesta. Son expertos en esto... 🦝",
            "Revisando la información como una ardilla con sus nueces, buscando la más valiosa... 🐿️",
            "Poniéndome mi capa digital y saliendo a buscar la respuesta... 🕵️‍♂️",
            "Cargando un nuevo paquete de ideas desde el cosmos. La respuesta aterrizará en unos segundos... 🚀",
            "Un momento, estoy desplegando cartas de datos en mi mesa virtual. Preparándome para una respuesta precisa... 🃏",
            "Mis barcos virtuales están navegando en un mar de información. La respuesta está en el horizonte... 🚢",
        ]

        return random.choice(texts)

    @staticmethod
    def model_image_processing_request() -> str:
        texts = [
            "Recolectando polvo estelar para crear tu obra maestra cósmica... 🌌",
            "Mezclando una paleta de colores digitales para tu creación... 🎨",
            "Sumergiéndome en tinta virtual para plasmar tu visión... 🖌️",
            "Invocando a las musas del arte para un dibujo inspirador... 🌠",
            "Puliendo píxeles hasta la perfección, un momento... 🎭",
            "Preparando un festín visual para tus ojos... 🍽️",
            "Consultando con el Da Vinci digital para tu solicitud artística... 🎭",
            "Limpiando el polvo de mi caballete digital para tu proyecto creativo... 🖼️️",
            "Creando un hechizo visual en el caldero de la IA... 🔮",
            "Activando el lienzo virtual. Prepárate para el arte... 🖼️",
            "Transformando tus ideas en una galería de píxeles... 👨‍🎨",
            "Explorando un safari digital para capturar tu visión artística... 🦁",
            "Encendiendo los motores artísticos de la IA, espera un momento... 🏎️",
            "Zambulléndome en la piscina de la imaginación digital... 🏊‍",
            "Cocinando una sinfonía visual en la cocina de la IA... 🍳",
            "Reuniendo nubes de creatividad para plasmar tu obra maestra visual... ☁️",
            "Recolectando pinceles y pinturas digitales para dar vida a tu visión... 🎨",
            "Invocando dragones de píxeles para crear una imagen épica... 🐉",
            "Llamando a las abejas digitales para recolectar el néctar de tu florecimiento visual... 🐝",
            "Colocándome mi sombrero digital de artista para empezar a trabajar en tu creación... 👒",
            "Sumergiendo píxeles en una solución mágica para que brillen con arte... 🧪",
            "Moldeando tu imagen con arcilla de imaginación. ¡Pronto será una obra maestra!... 🏺",
            "Mis elfos virtuales ya están pintando tu imagen... 🧝‍♂️",
            "Las tortugas virtuales están llevando tu imagen a través del mar de datos... 🐢",
            "Los gatitos digitales están pintando tu obra maestra con sus patitas... 🐱",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>La generación puede tardar hasta 3 minutos</i>"

        return text

    @staticmethod
    def model_face_swap_processing_request() -> str:
        texts = [
            "Viajando a la dimensión del intercambio de rostros... 👤",
            "Mezclando y emparejando rostros como un Picasso digital... 🧑‍🎨",
            "Cambiando rostros más rápido que un camaleón cambia de colores... 🦎",
            "Despertando la magia de la fusión de rostros... ✨",
            "Realizando alquimia facial, transformando identidades... ‍🧬",
            "Activando la máquina de cambio de rostros... 🤖",
            "Preparando una poción para la transformación facial... 👩‍🔬",
            "Creando hechizos en el mundo encantado de los rostros... 🧚‍️",
            "Dirigiendo una sinfonía de rasgos faciales... 🎼",
            "Esculpiendo nuevos rostros en mi estudio de arte digital... 🎨",
            "Cocinando en el caldero mágico del intercambio de rostros... 🔮",
            "Construyendo rostros como un gran arquitecto... 🏗️",
            "Empezando una búsqueda mística de la combinación perfecta de rostros... 🔍",
            "Lanzando un cohete hacia la aventura de intercambio de rostros... 🚀",
            "Embarcándome en un viaje galáctico de intercambio de rostros... 👽",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>La generación puede tardar hasta 5 minutos</i>"

        return text

    @staticmethod
    def model_music_processing_request() -> str:
        texts = [
            "Activando el generador musical, prepárate para disfrutar... 👂",
            "Mezclando notas como un DJ en una fiesta... 🕺",
            "El mago de las melodías está en acción, prepárate para la magia... 🧙‍",
            "Creando música que hará bailar incluso a los robots... 💃",
            "El laboratorio musical está en marcha, prepárate para algo épico... 🔥",
            "Capturando olas de inspiración y transformándolas en sonido... 🌊",
            "Subiendo a las cumbres de la música, espera algo grandioso... 🏔️",
            "Creando algo que ningún oído ha escuchado antes... 👂",
            "Es hora de sumergirse en un océano de armonía y ritmo... 🌊",
            "Abriendo la puerta a un mundo donde la música crea realidades... 🌍",
            "Descifrando los códigos de la composición para crear algo único... 🎶",
            "Cocinando melodías como un chef prepara sus mejores platos... 🍽️",
            "Organizando una fiesta en las teclas, cada nota es un invitado... 🎹",
            "Explorando un laberinto melódico para encontrar la salida perfecta... 🌀",
            "Transformando vibraciones en el aire en sonidos mágicos... 🌬️",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>La generación puede tardar hasta 10 minutos</i>"

        return text

    @staticmethod
    def model_video_processing_request() -> str:
        texts = [
            "Cargando el estreno de tu película, casi listo... 🍿",
            "¡El cohete de la creatividad en video está despegando! Abróchate el cinturón... 🚀",
            "Los fotogramas cobran vida, luces, cámara, acción... 🎬",
            "Generando obra maestra cuadro por cuadro... 🎥",
            "No es un video, es una maravilla cinematográfica en camino... 🎞️",
            "Armando el rompecabezas con los mejores fotogramas para tu WOW... 🤩",
            "Uniendo píxeles, prepárate para un video espectacular... 🎇",
            "Capturando los mejores momentos, el video está en proceso... 🎣",
            "La mesa de edición está en llamas, creando una obra maestra en video... 🔥",
            "Cargando contenido visual a tu dimensión... 🎞️",
            "Las abejas de IA trabajan en tu video-miel... ¡Prepárate para un dulce resultado! 🐝",
            "El proyector mágico ya está arrancando... ✨",
            "La pizza se cocina en el horno... ¡oh no, tu video! 🍕",
            "Creando hechizos visuales, el video será mágico... 🎩",
            "Llevando tu video por los rieles de la creatividad... 🚉",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ <i>La generación puede tardar hasta 20 minutos</i>"

        return text

    @staticmethod
    def model_wait_for_another_request(seconds: int) -> str:
        return f"⏳ Por favor, espera {seconds} segundos más antes de enviar otra solicitud"

    @staticmethod
    def model_reached_usage_limit():
        hours, minutes = get_time_until_limit_update()

        return f"""
🚨 <b>¡Cuota agotada!</b>

El límite diario se renovará en <i>{hours} horas {minutes} minutos</i> 🔄

Si no quieres esperar, tengo una solución para ti:
"""

    @staticmethod
    def model_restricted(model: str):
        return f"""
🔒 <b>¡Has entrado en la zona VIP!</b>

{model} no está incluido en tu suscripción actual.

Selecciona una acción:
"""

    MODELS_TEXT = "🔤 Modelos de texto"
    MODELS_SUMMARY = "📝 Modelos de resumen"
    MODELS_IMAGE = "🖼 Modelos gráficos"
    MODELS_MUSIC = "🎵 Modelos musicales"
    MODELS_VIDEO = "📹 Modelos de video"

    # MusicGen
    MUSIC_GEN_INFO = """
🎺 <b>Guía para MusicGen</b>

Estoy listo para transformar tus palabras y descripciones en melodías únicas 🎼

Cuéntame qué tipo de música quieres crear: <b>describe su estilo, estado de ánimo e instrumentos</b>.
"""
    MUSIC_GEN_TYPE_SECONDS = """
⏳ <b>¿Cuántos segundos durará tu sinfonía?</b>

<i>Cada 10 segundos consumen 1 generación</i> 🎼

Escribe o elige la duración de tu composición en segundos:
"""
    MUSIC_GEN_MIN_ERROR = """
🤨 <b>¡Espera!</b>

¡Estás intentando solicitar menos de 10 segundos!

Para continuar, <b>envía un número mayor o igual a 10</b>.
"""
    MUSIC_GEN_MAX_ERROR = """
🤨 <b>¡Espera!</b>

¡Estás intentando solicitar más de 10 minutos, y todavía no puedo crear algo tan largo!

Para comenzar la magia, <b>introduce un número menor a 600</b>.
"""
    MUSIC_GEN_SECONDS_10 = "🔹 10 segundos"
    MUSIC_GEN_SECONDS_30 = "🔹 30 segundos"
    MUSIC_GEN_SECONDS_60 = "🔹 60 segundos (1 minuto)"
    MUSIC_GEN_SECONDS_180 = "🔹 180 segundos (3 minutos)"
    MUSIC_GEN_SECONDS_300 = "🔹 300 segundos (5 minutos)"
    MUSIC_GEN_SECONDS_600 = "🔹 600 segundos (10 minutos)"

    @staticmethod
    def music_gen_forbidden_error(available_seconds: int) -> str:
        return f"""
🔔 <b>Ups, ¡un pequeño problema!</b> 🚧

Parece que solo te quedan <b>{available_seconds} segundos</b> disponibles en tu arsenal

Introduce un número menor o utiliza /buy para obtener posibilidades ilimitadas
"""

    # Notify about Quota
    @staticmethod
    def notify_about_quota(
        subscription_limits: dict,
    ) -> str:
        texts = [
            f"""
🤖 <b>¡Hola, soy yo! ¿Me recuerdas?</b>

🤓 Estoy aquí para <b>recordarte</b> tus cuotas diarias:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto</b> esperando para transformarse en tus obras maestras
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} resúmenes de video</b> para entender rápidamente el contenido
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} oportunidades gráficas</b> listas para dar vida a tus ideas

🔥 No dejes que se desperdicien, <b>¡empieza ahora mismo!</b>
""",
            f"""
🤖 <b>¡Hola! Soy Fusee, tu asistente personal</b>.

😢 Me di cuenta de que hace tiempo no usas tus cuotas, así que <b>te recuerdo</b> que cada día tienes:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto</b> para tus ideas
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} resúmenes de video</b> para ahorrar tiempo
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} imágenes</b> para dar vida a tus pensamientos

✨ <b>¡Empecemos a crear!</b> Estoy listo para ayudarte ahora mismo.
""",
            f"""
🤖 <b>Soy Fusee, tu empleado digital personal, con un recordatorio importante.</b>

🤨 ¿Sabías que tienes:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto</b> para tus brillantes ideas
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} resúmenes de video</b> para captar lo esencial
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} imágenes</b> para visualizar ideas

🔋 Estoy completamente cargado, solo falta que <b>empieces a crear</b>.
""",
            f"""
🤖 <b>¡Soy yo de nuevo! Te extrañé...</b>

😢 Estaba pensando... <b>tus cuotas también te extrañan</b>:
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto inspiradoras</b> esperando su momento
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} resúmenes de video</b> para convertirlos en ideas rápidas
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} ideas visuales</b> listas para cobrar vida

💡 Dame la oportunidad de ayudarte a <b>crear algo increíble</b>.
""",
            f"""
🤖 <b>¡Hola, soy Fusee!</b> Tus cuotas no se usarán solas, ¿verdad?

🫤 <b>Te recuerdo que tienes:</b>
• <b>{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto</b>, que pueden ser el inicio del éxito
• <b>{format_number(subscription_limits[Quota.EIGHTIFY])} resúmenes de video</b> para descubrir la esencia en segundos
• <b>{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])} imágenes</b> que dibujarán tus fantasías

✨ <b>Es hora de crear</b>, y estoy aquí para ayudarte. ¡Empecemos!
""",
        ]

        return random.choice(texts)

    NOTIFY_ABOUT_QUOTA_TURN_OFF = "🔕 Desactivar notificaciones"
    NOTIFY_ABOUT_QUOTA_TURN_OFF_SUCCESS = "🎉 Notificaciones desactivadas con éxito"

    # Open
    OPEN_SETTINGS = "⚙️ Ir a configuración"
    OPEN_BONUS_INFO = "🎁 Consultar saldo de bonificación"
    OPEN_BUY_SUBSCRIPTIONS_INFO = "💎 Suscribirse"
    OPEN_BUY_PACKAGES_INFO = "🛍 Comprar paquetes"

    # Package
    PACKAGE = "🛍 Paquete"
    PACKAGE_SUCCESS = """
🎉 <b>¡Pago realizado con éxito!</b>

Has desbloqueado con éxito el poder del paquete seleccionado 🎢

¡Vamos a crear maravillas! ✨
"""
    PACKAGE_QUANTITY_MIN_ERROR = """
🚨 <b>¡Oops!</b>

El monto es menor al mínimo requerido.

Selecciona una cantidad de paquetes que cumpla o supere el monto mínimo requerido 🔄
"""
    PACKAGE_QUANTITY_MAX_ERROR = """
🚨 <b>¡Oops!</b>

El número ingresado supera lo que puedes adquirir.

<b>Introduce un valor menor o que corresponda a tu saldo</b> 🔄
"""

    @staticmethod
    def package_info(currency: Currency, cost: str, gift_packages: list[Product]) -> str:
        if currency == Currency.USD:
            cost = f"{Currency.SYMBOLS[currency]}{cost}"
            gift_packages_sum = f"{Currency.SYMBOLS[currency]}5"
        else:
            cost = f"{cost}{Currency.SYMBOLS[currency]}"
            gift_packages_sum = f"500{Currency.SYMBOLS[currency]}"

        gift_packages_info = f"\n\n🎁 <i>Gasta {gift_packages_sum} o más — recibe estos paquetes de regalo:</i>"
        for gift_package in gift_packages:
            gift_packages_info += f"\n<i>{gift_package.names.get(LanguageCode.ES)}</i>"

        return f"""
🛍 <b>Paquetes</b>

<b>1 moneda 🪙 = {cost}</b>{gift_packages_info if len(gift_packages) > 0 else ''}

Para seleccionar un paquete, presiona el botón:
"""

    @staticmethod
    def package_choose_min(name: str) -> str:
        return f"""
Has seleccionado el paquete <b>{name}</b>

<b>Elige o ingresa la cantidad</b> que deseas comprar
"""

    @staticmethod
    def package_confirmation(package_name: str, package_quantity: int, currency: Currency, price: str) -> str:
        left_price_part = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_price_part = '' if currency == Currency.USD else Currency.SYMBOLS[currency]
        return f"Estás a punto de comprar {package_quantity} paquete(s) de <b>{package_name}</b> por {left_price_part}{price}{right_price_part}"

    @staticmethod
    def payment_package_description(user_id: str, package_name: str, package_quantity: int):
        return f"Pago de {package_quantity} paquete(s) de {package_name} para el usuario: {user_id}"

    PACKAGES = "🛍 Paquetes"
    PACKAGES_SUCCESS = """
🎉 <b>¡Pago realizado con éxito!</b>

Has desbloqueado con éxito el poder de los paquetes seleccionados 🎢

¡Vamos a crear maravillas! ✨
"""
    PACKAGES_END = """
🕒 <b>Oh-oh</b>

¡El tiempo de uno o varios paquetes ha expirado! ⌛

Para continuar, revisa mis ofertas presionando el botón de abajo:
"""

    @staticmethod
    def packages_description(user_id: str):
        return f"Pago de paquetes del carrito para el usuario: {user_id}"

    # Payment
    PAYMENT_BUY = """
🛒 <b>Tienda</b>

💳 <b>Suscripciones</b>
Obtén acceso completo a todas las redes neuronales y herramientas. Comunicación, imágenes, música, videos y mucho más, ¡todo incluido!

🛍 <b>Paquetes</b>
¡Solo lo que necesitas! Elige una cantidad específica de solicitudes y paga solo por lo que usas.

Selecciona presionando el botón de abajo 👇
"""
    PAYMENT_CHANGE_CURRENCY = "💱 Cambiar moneda"
    PAYMENT_YOOKASSA_PAYMENT_METHOD = "🪆 YooKassa"
    PAYMENT_STRIPE_PAYMENT_METHOD = "🌍 Stripe"
    PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD = "⭐️ Telegram Stars"
    PAYMENT_CHOOSE_PAYMENT_METHOD = """
<b>Elige tu método de pago:</b>

🪆 <b>YooKassa (Tarjetas Rusas)</b>

🌍 <b>Stripe (Tarjetas Internacionales)</b>

⭐️ <b>Telegram Stars (Moneda en Telegram)</b>
"""
    PAYMENT_PROCEED_TO_PAY = "🌐 Proceder al pago"
    PAYMENT_PROCEED_TO_CHECKOUT = "💳 Proceder a la compra"
    PAYMENT_DISCOUNT = "💸 Descuento"
    PAYMENT_NO_DISCOUNT = "Sin descuento"

    @staticmethod
    def payment_purchase_minimal_price(currency: Currency, current_price: str):
        left_part_price = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_part_price = '' if currency == Currency.USD else Currency.SYMBOLS[currency]
        return f"""
<b>😕 Oh-oh...</b>

Para realizar una compra, el total debe ser igual o mayor a <b>{left_part_price}{1 if currency == Currency.USD else 50}{right_part_price}</b>

Actualmente, el total de tu compra es: <b>{left_part_price}{current_price}{right_part_price}</b>
"""

    # Photoshop AI
    PHOTOSHOP_AI_INFO = """
🪄 <b>Photoshop IA</b>

Esta herramienta reúne funcionalidades de IA para la edición y estilización de imágenes.

Selecciona una acción presionando el botón de abajo 👇
"""
    PHOTOSHOP_AI_UPSCALE = "⬆️ Mejora de calidad"
    PHOTOSHOP_AI_UPSCALE_INFO = """
⬆️ <b>Esta herramienta mejora la calidad de la imagen original</b>

Para mejorar la calidad de tu imagen, envíamela
"""
    PHOTOSHOP_AI_RESTORATION = "🖌 Restauración"
    PHOTOSHOP_AI_RESTORATION_INFO = """
🖌 <b>Esta herramienta detecta y elimina arañazos o cortes en la imagen original</b>

Para eliminar arañazos o cortes, envíame tu imagen
"""
    PHOTOSHOP_AI_COLORIZATION = "🌈 Coloreado"
    PHOTOSHOP_AI_COLORIZATION_INFO = """
🌈 <b>Esta herramienta añade color a imágenes en blanco y negro</b>

Para convertir una foto en blanco y negro en color, envíame tu imagen
"""
    PHOTOSHOP_AI_REMOVE_BACKGROUND = "🗑 Eliminación de fondo"
    PHOTOSHOP_AI_REMOVE_BACKGROUND_INFO = """
🗑 <b>Esta herramienta elimina el fondo de una imagen</b>

Para eliminar el fondo, envíame tu imagen
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
            subscription_info = f"📫 <b>Estado de suscripción:</b> Cancelada. Válida hasta {renewal_date}"
        elif subscription_status == SubscriptionStatus.TRIAL:
            subscription_info = f"📫 <b>Estado de suscripción:</b> Período de prueba gratuito"
        else:
            subscription_info = "📫 <b>Estado de suscripción:</b> Activa"

        return f"""
👤 <b>Perfil</b>

---------------------------

🤖 <b>Modelo actual: {current_model}</b>

💳 <b>Tipo de suscripción:</b> {subscription_name}
🗓 <b>Fecha de renovación de suscripción:</b> {f'{renewal_date}' if subscription_name != '🆓' else 'N/A'}
{subscription_info}

---------------------------

Seleccione una acción 👇
"""

    @staticmethod
    def profile_quota(
        subscription_limits: dict,
        daily_limits,
        additional_usage_quota,
    ) -> str:
        hours, minutes = get_time_until_limit_update()

        return f"""
🤖 <b>Cuotas:</b>

─────────────

🔤 <b>Modelos de Texto</b>:
<b>Básicos</b>:
    ┣ ✉️ ChatGPT 4.0 Omni Mini{f': adicional {additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI] > 0 else ''}
    ┣ 📜 Claude 3.5 Haiku{f': adicional {additional_usage_quota[Quota.CLAUDE_3_HAIKU]}' if additional_usage_quota[Quota.CLAUDE_3_HAIKU] > 0 else ''}
    ┣ 🏎 Gemini 2.0 Flash{f': adicional {additional_usage_quota[Quota.GEMINI_2_FLASH]}' if additional_usage_quota[Quota.GEMINI_2_FLASH] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI_MINI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])}

<b>Avanzados</b>:
    ┣ 💥 ChatGPT 4.0 Omni{f': adicional {additional_usage_quota[Quota.CHAT_GPT4_OMNI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI] > 0 else ''}
    ┣ 🧩 ChatGPT o1-mini{f': adicional {additional_usage_quota[Quota.CHAT_GPT_O_1_MINI]}' if additional_usage_quota[Quota.CHAT_GPT_O_1_MINI] > 0 else ''}
    ┣ 💫 Claude 3.5 Sonnet{f': adicional {additional_usage_quota[Quota.CLAUDE_3_SONNET]}' if additional_usage_quota[Quota.CLAUDE_3_SONNET] > 0 else ''}
    ┣ 💼 Gemini 1.5 Pro{f': adicional {additional_usage_quota[Quota.GEMINI_1_PRO]}' if additional_usage_quota[Quota.GEMINI_1_PRO] > 0 else ''}
    ┣ 🐦 Grok 2.0{f': adicional {additional_usage_quota[Quota.GROK_2]}' if additional_usage_quota[Quota.GROK_2] > 0 else ''}
    ┣ 🌐 Perplexity{f': adicional {additional_usage_quota[Quota.PERPLEXITY]}' if additional_usage_quota[Quota.PERPLEXITY] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI])}

<b>Premium</b>:
    ┣ 🧪 ChatGPT o1{f': adicional {additional_usage_quota[Quota.CHAT_GPT_O_1]}' if additional_usage_quota[Quota.CHAT_GPT_O_1] > 0 else ''}
    ┣ 🚀 Claude 3.0 Opus{f': adicional {additional_usage_quota[Quota.CLAUDE_3_OPUS]}' if additional_usage_quota[Quota.CLAUDE_3_OPUS] > 0 else ''}
    ┣ 🛡️ Gemini 1.0 Ultra{f': adicional {additional_usage_quota[Quota.GEMINI_1_ULTRA]}' if additional_usage_quota[Quota.GEMINI_1_ULTRA] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.CHAT_GPT_O_1])}/{format_number(subscription_limits[Quota.CHAT_GPT_O_1])}

─────────────

📝 <b>Modelos de Resumen</b>:
    ┣ 👀 YouTube{f': adicional {additional_usage_quota[Quota.EIGHTIFY]}' if additional_usage_quota[Quota.EIGHTIFY] > 0 else ''}
    ┣ 📼 Vídeo{f': adicional {additional_usage_quota[Quota.GEMINI_VIDEO]}' if additional_usage_quota[Quota.GEMINI_VIDEO] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.EIGHTIFY])}/{format_number(subscription_limits[Quota.EIGHTIFY])}

─────────────

🖼 <b>Modelos Gráficos</b>:
<b>Básicos</b>:
    ┣ 🦄 Stable Diffusion XL{f': adicional {additional_usage_quota[Quota.STABLE_DIFFUSION_XL]}' if additional_usage_quota[Quota.STABLE_DIFFUSION_XL] > 0 else ''}
    ┣ 🌲 Flux 1.0 Dev{f': adicional {additional_usage_quota[Quota.FLUX_1_DEV]}' if additional_usage_quota[Quota.FLUX_1_DEV] > 0 else ''}
    ┣ 🌌 Luma Photon{f': adicional {additional_usage_quota[Quota.LUMA_PHOTON]}' if additional_usage_quota[Quota.LUMA_PHOTON] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.STABLE_DIFFUSION_XL])}/{format_number(subscription_limits[Quota.STABLE_DIFFUSION_XL])}

<b>Avanzados</b>:
    ┣ 👨‍🎨 DALL-E 3{f': adicional {additional_usage_quota[Quota.DALL_E]}' if additional_usage_quota[Quota.DALL_E] > 0 else ''}
    ┣ 🎨 Midjourney 6.1{f': adicional {additional_usage_quota[Quota.MIDJOURNEY]}' if additional_usage_quota[Quota.MIDJOURNEY] > 0 else ''}
    ┣ 🧑‍🚀 Stable Diffusion 3.5{f': adicional {additional_usage_quota[Quota.STABLE_DIFFUSION_3]}' if additional_usage_quota[Quota.STABLE_DIFFUSION_3] > 0 else ''}
    ┣ 🏔 Flux 1.1 Pro{f': adicional {additional_usage_quota[Quota.FLUX_1_PRO]}' if additional_usage_quota[Quota.FLUX_1_PRO] > 0 else ''}
    ┣ 🐼 Recraft 3{f': adicional {additional_usage_quota[Quota.RECRAFT]}' if additional_usage_quota[Quota.RECRAFT] > 0 else ''}
    ┣ 📷 FaceSwap{f': adicional {additional_usage_quota[Quota.FACE_SWAP]}' if additional_usage_quota[Quota.FACE_SWAP] > 0 else ''}
    ┣ 🪄 Photoshop AI{f': adicional {additional_usage_quota[Quota.PHOTOSHOP_AI]}' if additional_usage_quota[Quota.PHOTOSHOP_AI] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.DALL_E])}/{format_number(subscription_limits[Quota.DALL_E])}

─────────────

🎵 <b>Modelos de Música</b>:
    ┣ 🎺 MusicGen{f': adicional {additional_usage_quota[Quota.MUSIC_GEN]}' if additional_usage_quota[Quota.MUSIC_GEN] > 0 else ''}
    ┣ 🎸 Suno{f': adicional {additional_usage_quota[Quota.SUNO]}' if additional_usage_quota[Quota.SUNO] > 0 else ''}
    ┗ Límite diario: {format_number(daily_limits[Quota.SUNO])}/{format_number(subscription_limits[Quota.SUNO])}

─────────────

📹 <b>Modelos de Vídeo</b>:
    ┣ 🎬 Kling{f': adicional {additional_usage_quota[Quota.KLING]}' if additional_usage_quota[Quota.KLING] > 0 else ''}
    ┣ 🎥 Runway{f': adicional {additional_usage_quota[Quota.RUNWAY]}' if additional_usage_quota[Quota.RUNWAY] > 0 else ''}
    ┣ 🔆 Luma Ray{f': adicional {additional_usage_quota[Quota.LUMA_RAY]}' if additional_usage_quota[Quota.LUMA_RAY] > 0 else ''}
    ┗ 🐇 Pika{f': adicional {additional_usage_quota[Quota.PIKA]}' if additional_usage_quota[Quota.PIKA] > 0 else ''}

─────────────

📷 <b>Trabajo con fotos/documentos</b>: {'✅' if daily_limits[Quota.WORK_WITH_FILES] or additional_usage_quota[Quota.WORK_WITH_FILES] else '❌'}
🎭 <b>Acceso al catálogo de empleados digitales</b>: {'✅' if daily_limits[Quota.ACCESS_TO_CATALOG] or additional_usage_quota[Quota.ACCESS_TO_CATALOG] else '❌'}
🎙 <b>Mensajes de voz</b>: {'✅' if daily_limits[Quota.VOICE_MESSAGES] or additional_usage_quota[Quota.VOICE_MESSAGES] else '❌'}
⚡ <b>Respuestas rápidas</b>: {'✅' if daily_limits[Quota.FAST_MESSAGES] or additional_usage_quota[Quota.FAST_MESSAGES] else '❌'}

─────────────

🔄 <i>El límite se actualizará en: {hours} h. {minutes} min.</i>
"""

    PROFILE_SHOW_QUOTA = "🔄 Mostrar cuota"
    PROFILE_TELL_ME_YOUR_GENDER = "Indique su género:"
    PROFILE_YOUR_GENDER = "Su género:"
    PROFILE_SEND_ME_YOUR_PICTURE = """
📸 <b>Envíame tu foto</b>

👍 <b>Recomendaciones para una foto perfecta:</b>
• Un selfie claro y de buena calidad.
• El selfie debe incluir solo a una persona.

👎 <b>Por favor, evita las siguientes fotos:</b>
• Fotos grupales.
• Animales.
• Niños menores de 18 años.
• Fotos de cuerpo completo.
• Fotos inapropiadas o desnudos.
• Gafas de sol u objetos que cubran la cara.
• Imágenes borrosas o fuera de foco.
• Videos y animaciones.
• Imágenes comprimidas o alteradas.

Una vez que tengas la foto ideal, <b>súbela</b> y deja que la magia comience 🌟
"""
    PROFILE_UPLOAD_PHOTO = "📷 Subir foto"
    PROFILE_UPLOADING_PHOTO = "Subiendo foto..."
    PROFILE_CHANGE_PHOTO = "📷 Cambiar foto"
    PROFILE_CHANGE_PHOTO_SUCCESS = "📸 ¡Foto subida exitosamente!"
    PROFILE_RENEW_SUBSCRIPTION = "♻️ Renovar suscripción"
    PROFILE_RENEW_SUBSCRIPTION_SUCCESS = "✅ La suscripción se ha renovado con éxito"
    PROFILE_CANCEL_SUBSCRIPTION = "❌ Cancelar suscripción"
    PROFILE_CANCEL_SUBSCRIPTION_CONFIRMATION = "❗¿Está seguro de que desea cancelar su suscripción?"
    PROFILE_CANCEL_SUBSCRIPTION_SUCCESS = "💸 La suscripción se ha cancelado con éxito"
    PROFILE_NO_ACTIVE_SUBSCRIPTION = "💸 No tienes una suscripción activa"

    # Promo Code
    PROMO_CODE_ACTIVATE = "🔑 Activar código promocional"
    PROMO_CODE_INFO = """
🔓 <b>Activación de código promocional</b>

Si tienes un código promocional, simplemente envíamelo para desbloquear funciones ocultas y sorpresas especiales 🔑
"""
    PROMO_CODE_SUCCESS = """
🎉 <b>¡Tu código promocional ha sido activado con éxito!</b>

¡Disfruta explorando! 🚀
"""
    PROMO_CODE_ALREADY_HAVE_SUBSCRIPTION = """
🚫 <b>¡Ups!</b>

¡Ya formas parte de nuestro exclusivo club de suscriptores! 🌟
"""
    PROMO_CODE_EXPIRED_ERROR = """
🕒 <b>¡Este código promocional ha expirado!</b>

Envíame otro código promocional o simplemente selecciona una acción de abajo:
"""
    PROMO_CODE_NOT_FOUND_ERROR = """
🔍 <b>¡Código promocional no encontrado!</b>

Parece que el código que ingresaste está jugando a las escondidas porque no pude encontrarlo en el sistema 🕵️‍♂️

🤔 <b>Verifica que no haya errores y vuelve a intentarlo</b>. Si aún no funciona, quizá deberías buscar otro código o revisar las ofertas en /buy. ¡Hay ofertas interesantes allí! 🛍️
"""
    PROMO_CODE_ALREADY_USED_ERROR = """
🚫 <b>¡Deja-vu!</b>

Ya has usado este código promocional. Es magia de un solo uso, y ya la utilizaste 🧙

¡Pero no te preocupes! Puedes explorar mis ofertas presionando el botón de abajo:
"""

    # Remove Restriction
    REMOVE_RESTRICTION = "⛔️ Eliminar restricción"
    REMOVE_RESTRICTION_INFO = "Para eliminar la restricción, selecciona una de las acciones de abajo 👇"

    # Settings
    @staticmethod
    def settings_info(human_model: str, current_model: Model, generation_cost=1) -> str:
        if current_model == Model.DALL_E:
            additional_text = f"\nCon la configuración actual, 1 solicitud cuesta: {generation_cost} 🖼"
        elif current_model == Model.KLING or current_model == Model.RUNWAY:
            additional_text = f"\nCon la configuración actual, 1 solicitud cuesta: {generation_cost} 📹"
        else:
            additional_text = ""

        return f"""
⚙️ <b>Configuración para el modelo:</b> {human_model}

Aquí puedes personalizar el modelo seleccionado para adaptarlo a tus necesidades y preferencias
{additional_text}
"""

    SETTINGS_CHOOSE_MODEL_TYPE = """
⚙️ <b>Configuración</b>

🌍 Para cambiar el idioma de la interfaz, utiliza el comando /language
🤖 Para cambiar de modelo, utiliza el comando /model

Selecciona abajo el tipo de modelo que deseas personalizar 👇
"""
    SETTINGS_CHOOSE_MODEL = """
⚙️ <b>Configuración</b>

Selecciona abajo el modelo que deseas personalizar 👇
"""
    SETTINGS_VOICE_MESSAGES = """
⚙️ <b>Configuración</b>

A continuación, encontrarás la configuración para respuestas de voz en todos los modelos de texto 🎙
"""
    SETTINGS_VERSION = "🤖 Versión"
    SETTINGS_FOCUS = "🎯 Enfoque"
    SETTINGS_FORMAT = "🎛 Formato"
    SETTINGS_AMOUNT = "📏 Longitud de la Respuesta"
    SETTINGS_SEND_TYPE = "🗯 Tipo de Envío"
    SETTINGS_SEND_TYPE_IMAGE = "🖼 Imagen"
    SETTINGS_SEND_TYPE_DOCUMENT = "📄 Documento"
    SETTINGS_SEND_TYPE_AUDIO = "🎤 Audio"
    SETTINGS_SEND_TYPE_VIDEO = "📺 Video"
    SETTINGS_ASPECT_RATIO = "📐 Relación de Aspecto"
    SETTINGS_QUALITY = "✨ Calidad"
    SETTINGS_PROMPT_SAFETY = "🔐 Protección de Prompt"
    SETTINGS_GENDER = "👕/👚 Género"
    SETTINGS_DURATION = "📏 Duración en Segundos"
    SETTINGS_MODE = "🤖 Modo"
    SETTINGS_SHOW_THE_NAME_OF_THE_CHATS = "Nombres de los chats en los mensajes"
    SETTINGS_SHOW_THE_NAME_OF_THE_ROLES = "Nombres de los roles en los mensajes"
    SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES = "Cuota en mensajes"
    SETTINGS_TURN_ON_VOICE_MESSAGES = "Activar respuestas de voz"
    SETTINGS_LISTEN_VOICES = "Escuchar voces"

    # Shopping cart
    SHOPPING_CART = "🛒 Carrito"
    SHOPPING_CART_ADD = "➕ Agregar al carrito"

    @staticmethod
    def shopping_cart_add_or_buy_now(
        product: Product,
        product_quantity: int,
        product_price: float,
        currency: Currency,
    ):
        return f"""
<b>{product_quantity} paquete(s) {product.names.get(LanguageCode.ES)} – {format_number(product_price)}{Currency.SYMBOLS[currency]}</b>
"""

    SHOPPING_CART_BUY_NOW = "🛍 Comprar ahora"
    SHOPPING_CART_REMOVE = "➖ Eliminar del carrito"
    SHOPPING_CART_GO_TO = "🛒 Ir al carrito"
    SHOPPING_CART_GO_TO_OR_CONTINUE_SHOPPING = "¿Ir al carrito o seguir comprando?"
    SHOPPING_CART_CONTINUE_SHOPPING = "🛍 Seguir comprando"
    SHOPPING_CART_CLEAR = "🗑 Vaciar carrito"

    @staticmethod
    async def shopping_cart_info(currency: Currency, cart_items: list[dict], discount: int):
        text = ""
        total_sum = 0
        left_price_part = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
        right_price_part = '' if currency == Currency.USD else Currency.SYMBOLS[currency]

        for index, cart_item in enumerate(cart_items):
            product_id, product_quantity = cart_item.get("product_id", ''), cart_item.get("quantity", 0)

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
            text += f"{index + 1}. {product.names.get(LanguageCode.ES)}: {product_quantity} ({left_price_part}{price}{right_price_part}){right_part}"

        if not text:
            text = "Tu carrito está vacío"

        return f"""
🛒 <b>Carrito</b>

{text}

💳 <b>Total a pagar:</b> {left_price_part}{round(total_sum, 2)}{right_price_part}
"""

    @staticmethod
    async def shopping_cart_confirmation(cart_items: list[dict], currency: Currency, price: float) -> str:
        text = ""
        for index, cart_item in enumerate(cart_items):
            product_id, product_quantity = cart_item.get("product_id", ''), cart_item.get("quantity", 0)

            product = await get_product(product_id)

            text += f"{index + 1}. {product.names.get(LanguageCode.ES)}: {product_quantity}\n"

        if currency == Currency.USD:
            total_sum = f"{Currency.SYMBOLS[currency]}{price}"
        else:
            total_sum = f"{price}{Currency.SYMBOLS[currency]}"

        return f"""
Estás a punto de comprar los siguientes paquetes de tu carrito:
{text}

Total a pagar: {total_sum}
"""

    # Start
    START_INFO = """
👋 <b>¡Hola!</b>

🤓 <b>Soy tu asistente en el mundo de las redes neuronales</b>

<b>Conmigo puedes crear:</b>
💭 Texto /text
📝 Resúmenes /summary
🖼 Imágenes /image
🎵 Música /music
📹 Videos /video

🏆 <b>Mi misión es proporcionar a todos acceso a las mejores redes neuronales</b>

🤖 Puedes ver todos los modelos disponibles en /model

ℹ️ Aprende más sobre las redes neuronales y lo que pueden hacer en /info

✨ <b>¡Empieza a crear ahora mismo!</b>
"""
    START_QUICK_GUIDE = "📖 Guía rápida"
    START_QUICK_GUIDE_INFO = """
📖 <b>Guía rápida</b>

─────────────

💭 <b>Respuestas de texto</b>:
1️⃣ Ingresa el comando /text
2️⃣ Selecciona un modelo
3️⃣ Escribe tus solicitudes en el chat

<i>Adicionalmente</i>

📷 Si me envías una foto, puedo:
• Responder cualquier pregunta sobre ella
• Reconocer texto
• Resolver una tarea

🌐 Puedes obtener información de Internet en <b>Perplexity</b> con /perplexity

─────────────

📝 <b>Resúmenes</b>:
1️⃣ Ingresa el comando /summary
2️⃣ Selecciona un modelo
3️⃣ Envía un video o un enlace al mismo

─────────────

🖼 <b>Creación de imágenes</b>:
1️⃣ Ingresa el comando /image
2️⃣ Selecciona un modelo
3️⃣ Escribe tus solicitudes en el chat

<i>Adicionalmente</i>
📷 Si me envías una foto, puedo:
• Completar/modificar detalles
• Cambiar el estilo de la imagen
• Visualizar algo nuevo

─────────────

📷️ <b>Cambio de caras en fotos</b>:
1️⃣ Ingresa el comando /face_swap
2️⃣ Sigue las instrucciones

─────────────

🪄 <b>Edición de imágenes</b>:
1️⃣ Ingresa el comando /photoshop
2️⃣ Sigue las instrucciones

─────────────

🎵 <b>Creación de música</b>:
1️⃣ Ingresa el comando /music
2️⃣ Selecciona un modelo
3️⃣ Sigue las instrucciones

─────────────

📹 <b>Creación de videos</b>:
1️⃣ Ingresa el comando /video
2️⃣ Selecciona un modelo
3️⃣ Sigue las instrucciones
"""

    # Subscription
    SUBSCRIPTION = "💳 Suscripción"
    SUBSCRIPTIONS = "💳 Suscripciones"
    SUBSCRIPTION_MONTH_1 = "1 mes"
    SUBSCRIPTION_MONTHS_3 = "3 meses"
    SUBSCRIPTION_MONTHS_6 = "6 meses"
    SUBSCRIPTION_MONTHS_12 = "12 meses"
    SUBSCRIPTION_SUCCESS = """
🎉 <b>¡Tu suscripción ha sido activada!</b>

Esto es lo que te espera a continuación:
• Un mundo de posibilidades se ha abierto ante ti 🌍
• Los amigos de IA están listos para ayudarte 🤖
• Prepárate para sumergirte en un mar de funciones y diversión 🌊

¡Hagamos maravillas juntos! 🪄
"""
    SUBSCRIPTION_RESET = """
🚀 <b>¡Suscripción renovada!</b>

¡Hola, viajero en el mundo de las redes neuronales! 👋

Tu suscripción ha sido renovada con éxito. ¡Hagamos que este mes sea aún mejor! 💪
"""
    SUBSCRIPTION_RETRY = """
❗️ <b>No se pudo renovar la suscripción</b>

El pago de hoy no se realizó con éxito. Se intentará nuevamente mañana

Si vuelve a fallar, la suscripción finalizará
"""
    SUBSCRIPTION_END = """
🛑 <b>¡Tu suscripción ha expirado!</b>

Tu suscripción ha terminado, pero no te preocupes, el viaje por el mundo de las redes neuronales aún no ha terminado 🚀

Puedes continuar explorando el universo de las redes neuronales y reactivar tu acceso presionando el botón de abajo:
"""
    SUBSCRIPTION_MONTHLY = "Mensual"
    SUBSCRIPTION_YEARLY = "Anual"

    @staticmethod
    def subscription_description(user_id: str, name: str):
        return f"Pago de suscripción {name} para el usuario: {user_id}"

    @staticmethod
    def subscription_renew_description(user_id: str, name: str):
        return f"Renovación de suscripción {name} para el usuario: {user_id}"

    @staticmethod
    def subscribe(
        subscriptions: list[Product],
        currency: Currency,
        user_discount: int,
        is_trial=False,
    ) -> str:
        text_subscriptions = ''
        for subscription in subscriptions:
            subscription_name = subscription.names.get(LanguageCode.ES)
            subscription_price = subscription.prices.get(currency)
            left_part_price = Currency.SYMBOLS[currency] if currency == Currency.USD else ''
            right_part_price = Currency.SYMBOLS[currency] if currency != Currency.USD else ''
            if subscription_name and subscription_price:
                is_trial_info = ''

                if is_trial and currency == Currency.RUB:
                    is_trial_info = '1₽ los primeros 3 días, luego '
                elif is_trial and currency == Currency.USD:
                    is_trial_info = 'Gratis los primeros 3 días, luego '

                text_subscriptions += f'<b>{subscription_name}</b>: '
                per_period = 'por mes' if subscription.category == ProductCategory.MONTHLY else 'por año'

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
💳 <b>Suscripciones</b>

{text_subscriptions}
Selecciona tu opción y presiona el botón de abajo para suscribirte:
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
        period = 'mes' if category == ProductCategory.MONTHLY else 'año'

        trial_info = ''
        if is_trial:
            trial_info = ' con un periodo de prueba de los primeros 3 días'

        return f"""
Estás a punto de activar la suscripción {name} por {left_price_part}{price}{right_price_part}/{period}{trial_info}

❗️Puedes cancelar la suscripción en cualquier momento desde la sección <b>Perfil 👤</b>
"""

    # Suno
    SUNO_INFO = """
🤖 <b>Elige el estilo para crear tu canción:</b>

🎹 En el <b>modo simple</b>, solo necesitas describir de qué se tratará la canción y en qué género.
🎸 En el <b>modo avanzado</b>, puedes usar tu propia letra y experimentar con géneros.

<b>Suno</b> creará 2 pistas, de hasta 4 minutos cada una 🎧
"""
    SUNO_SIMPLE_MODE = "🎹 Simple"
    SUNO_CUSTOM_MODE = "🎸 Avanzado"
    SUNO_SIMPLE_MODE_PROMPT = """
🎶 <b>Descripción de la canción</b>

En el modo simple, crearé una canción utilizando tus preferencias y tu gusto musical.

<b>Envíame tus preferencias</b> 📝
"""
    SUNO_CUSTOM_MODE_LYRICS = """
🎤 <b>Letra de la canción</b>

En el modo avanzado, crearé una canción utilizando la letra que me proporciones.

<b>Envíame la letra de tu canción</b> ✍️
"""
    SUNO_CUSTOM_MODE_GENRES = """
🎵 <b>Selección de género</b>

Para que tu canción en el modo avanzado se ajuste exactamente a tus preferencias, indícame los géneros que te gustaría incluir. La selección del género afecta significativamente el estilo y el ambiente de la composición, así que elígelo con cuidado.

<b>Enumera los géneros deseados separados por comas</b> en tu próximo mensaje, y comenzaré a crear una canción única 🔍
"""
    SUNO_START_AGAIN = "🔄 Empezar de nuevo"
    SUNO_TOO_MANY_WORDS_ERROR = """
🚧 <b>¡Uy!</b>

En alguna etapa, enviaste un texto demasiado largo 📝

Inténtalo nuevamente, pero con un texto más corto.
"""
    SUNO_VALUE_ERROR = """
🧐 <b>Esto no parece un prompt válido</b>

Por favor, envíame un valor diferente.
"""
    SUNO_SKIP = "⏩️ Saltar"

    # Tech Support
    TECH_SUPPORT = "👨‍💻 Soporte Técnico"

    # Terms Link
    TERMS_LINK = "https://telegra.ph/Terms-of-Service-in-GPTsTurboBot-05-07"

    # Video Summary
    VIDEO_SUMMARY_FOCUS_INSIGHTFUL = "💡 Profundo"
    VIDEO_SUMMARY_FOCUS_FUNNY = "😄 Divertido"
    VIDEO_SUMMARY_FOCUS_ACTIONABLE = "🛠 Útil"
    VIDEO_SUMMARY_FOCUS_CONTROVERSIAL = "🔥 Controversial"
    VIDEO_SUMMARY_FORMAT_LIST = "📋 Lista"
    VIDEO_SUMMARY_FORMAT_FAQ = "🗯 Preg/Resp"
    VIDEO_SUMMARY_AMOUNT_AUTO = "⚙️ Automático"
    VIDEO_SUMMARY_AMOUNT_SHORT = "✂️ Breve"
    VIDEO_SUMMARY_AMOUNT_DETAILED = "📚 Detallado"

    # Voice
    VOICE_MESSAGES = "🎙 Respuestas de voz"
    VOICE_MESSAGES_FORBIDDEN_ERROR = """
🎙 <b>¡Ups!</b>

¡Tu voz se ha perdido en el espacio de la IA!

Para <b>desbloquear la magia de la conversión de voz a texto</b>, simplemente utiliza la magia de los botones a continuación:
"""

    # Work with files
    WORK_WITH_FILES = "📷 Trabajo con fotos/documentos"
    WORK_WITH_FILES_FORBIDDEN_ERROR = """
🔒 <b>¡Has ingresado a la zona VIP!</b>

Por ahora, no tienes acceso para trabajar con fotos y documentos.

Puedes obtener acceso haciendo clic en el botón de abajo:
"""
