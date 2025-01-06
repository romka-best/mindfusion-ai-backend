import random
from typing import Union

from bot.database.models.product import Product, ProductType, ProductCategory
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


class Spanish(Texts):
    # Action
    ACTION_BACK = "Atrás ◀️"
    ACTION_CLOSE = "Cerrar 🚪"
    ACTION_CANCEL = "Cancelar ❌"
    ACTION_APPROVE = "Aprobar ✅"
    ACTION_DENY = "Rechazar ❌"

    # Bonus
    @staticmethod
    def bonus_info(user_id: str, balance: float, referred_count: int, feedback_count: int, play_count: int) -> str:
        return f"""
🎁 <b>Tu saldo de bonificación</b>

💰 Saldo actual: {int(balance)} 🪙

Para aumentar tu saldo de bonificación, puedes:
━ 1️⃣ <b>Invitar a amigos:</b>
    ┣ 💸 Por cada amigo que invites, tú y tu amigo reciben 25 créditos 🪙
    ┣ 🌟 Tu enlace de invitación personal: {Texts.bonus_referral_link(user_id, False)}
    ┗ 👤 Has invitado a: {referred_count}

━ 2️⃣ <b>Dejar un comentario:</b>
    ┣ 💸 Por cada comentario constructivo recibes 25 créditos 🪙
    ┣ 📡 Para dejar tu comentario, usa el comando /feedback
    ┗ 💭 Has dejado: {feedback_count}

━ 3️⃣ <b>Probar suerte en un juego:</b>
    ┣ 🎳 Juega a los bolos y gana tantos créditos como pines derribes: entre 1 y 6 créditos 🪙
    ┣ ⚽️ Marca un gol y recibe 5 créditos 🪙
    ┣ 🏀 Encesta y recibe 10 créditos 🪙
    ┣ 🎯 Da en el blanco y recibe 15 créditos 🪙
    ┣ 🎲 Adivina el número del dado y gana 20 créditos 🪙
    ┣ 🎰 Consigue el Jackpot y gana entre 50 y 100 créditos 🪙
    ┗ 🎮 Has jugado: {play_count}

¡Elige una opción!
"""

    BONUS_ACTIVATED_SUCCESSFUL = """
🌟 <b>¡Bonificación activada!</b> 🌟

¡Felicidades! Has utilizado tu saldo de bonificación con éxito. Ahora puedes sumergirte aún más en el mundo de la inteligencia artificial.

¡Empieza a usar tus créditos ahora y descubre nuevos horizontes con las redes neuronales! 🚀
"""
    BONUS_CHOOSE_PACKAGE = "Elige cómo gastar tus créditos ganados:"
    BONUS_INVITE_FRIEND = "👥 Invitar a un amigo"
    BONUS_REFERRAL_SUCCESS = """
🌟 <b>¡Felicidades! ¡Tu magia de referidos ha funcionado!</b> 🌟

Gracias a ti, un nuevo usuario se ha unido, y como recompensa, tú y tu amigo han recibido 25 créditos 🪙. Úsalos para acceder a funciones exclusivas o aumentar tus generadores de IA 💸.

Para usar tu bonificación, escribe el comando /bonus y sigue las instrucciones. ¡Que cada invitación te traiga felicidad y beneficios!
"""
    BONUS_REFERRAL_LIMIT_ERROR = """
🌟 <b>¡Felicidades! ¡Tu magia de referidos ha funcionado!</b> 🌟

Gracias a tus esfuerzos, un nuevo usuario se ha unido. Pero, lamentablemente, no puedo otorgarte más recompensas, ya que has alcanzado el límite de bonificaciones por invitaciones.

Usa el comando /bonus para explorar otras formas de ganar créditos de bonificación. ¡Sigue compartiendo y disfrutando de cada momento aquí! 🎉
"""
    BONUS_LEAVE_FEEDBACK = "📡 Dejar un comentario"
    BONUS_CASH_OUT = "🛍 Retirar créditos"
    BONUS_PLAY = "🎮 Jugar"
    BONUS_PLAY_GAME = "🎮 Probar suerte"
    BONUS_PLAY_GAME_CHOOSE = """
🎮 <b>Elige tu juego:</b>

━ 🎳 <b>Bolos:</b>
Derriba los pines. ¡Tu resultado será la cantidad de créditos que ganes, entre 1 y 6!

━ ⚽️ <b>Fútbol:</b>
¡Desafío de fútbol! Marca un gol y gana 5 créditos garantizados.

━ 🏀 <b>Baloncesto:</b>
¡Tiro decisivo! Si encestas, ganas 10 créditos.

━ 🎯 <b>Dardos:</b>
¡Acierta en el blanco y gana 15 créditos!

━ 🎲 <b>Dado:</b>
El dado de la suerte. Adivina el número y gana 20 créditos.

━ 🎰 <b>Casino:</b>
🍋 Número ganador. Si consigues tres números iguales, ganas 50 créditos.
🎰 ¡Jackpot! Consigue tres 7️⃣ y gana 100 créditos.

✨ Recuerda: solo tienes una oportunidad al día, ¡elige sabiamente y buena suerte! 😊
"""
    BONUS_PLAY_BOWLING_GAME = "🎳 Jugar a los bolos"
    BONUS_PLAY_BOWLING_GAME_INFO = """
🎳 <b>Bolos: ¿Listo para lanzar?</b>

Cuando presiones "Jugar", lanzaré la bola automáticamente. ¡Siempre ganas! Los créditos dependerán de cuántos pines derribes: entre 1 y 6.

Cada lanzamiento es una victoria, pero ¿cuánto ganarás?
"""
    BONUS_PLAY_SOCCER_GAME = "⚽️ Jugar al fútbol"
    BONUS_PLAY_SOCCER_GAME_INFO = """
⚽️ <b>Desafío de fútbol: ¿Listo para anotar?</b>

Presiona "Jugar", y yo tomaré el balón. Lo lanzaré hacia la portería, pero la suerte decide: tienes un 60% de probabilidad de marcar.

Si anoto, recibirás 5 créditos. ¿Listo para el gol decisivo?
"""
    BONUS_PLAY_BASKETBALL_GAME = "🏀 Jugar al baloncesto"
    BONUS_PLAY_BASKETBALL_GAME_INFO = """
🏀 <b>Tiro decisivo: ¡Es hora de lanzar!</b>

Presiona "Jugar", y lanzaré el balón al aro. Tienes un 40% de probabilidad de anotar y, si lo consigues, ¡ganarás 10 créditos!

¿Será un tiro digno de un profesional? ¡Descúbrelo ahora!
"""
    BONUS_PLAY_DARTS_GAME = "🎯 Jugar a los dardos"
    BONUS_PLAY_DARTS_GAME_INFO = """
🎯 <b>Tiro preciso: ¿Darás en el blanco?</b>

Presiona "Jugar", y lanzaré el dardo hacia el centro de la diana. ¡Tienes un 16.67% de probabilidad de acertar y ganar 15 créditos!

¿Te arriesgas a probar tu puntería?
"""
    BONUS_PLAY_DICE_GAME = "🎲 Lanzar el dado"
    BONUS_PLAY_DICE_GAME_INFO = """
🎲 <b>Dado de la suerte: ¡Adivina el número!</b>

Elige un número del 1 al 6, y yo lanzaré el dado. Si aciertas, ¡ganas 20 créditos! La probabilidad es de 1 entre 6.

¿Podrás confiar en tu intuición y adivinar el número ganador?
"""
    BONUS_PLAY_CASINO_GAME = "🎰 Jugar al casino"
    BONUS_PLAY_CASINO_GAME_INFO = """
🎰 <b>Casino: ¡Prueba tu suerte al máximo!</b>

Presiona "Jugar", y giraré los rodillos del casino. Si aparecen tres números iguales, ¡felicidades, ganas! La probabilidad de conseguir tres iguales es de un 5% y ganarás 50 créditos. Pero hay algo especial: si obtienes tres 7️⃣, ¡te llevarás el Jackpot de 100 créditos! La probabilidad de este superpremio es un poco más del 1%.

¡Gira los rodillos y descubre qué te depara la suerte!
"""
    BONUS_PLAY_GAME_WON = """
🎉 <b>¡Felicidades!</b>

¡La suerte está de tu lado! Has ganado. Tu premio ya está disponible en /bonus.

Vuelve mañana para más victorias. ¡La suerte ama a jugadores como tú! 🎊
"""
    BONUS_PLAY_GAME_LOST = """
😔 <b>Hoy no fue tu día...</b>

La suerte es cuestión de tiempo. ¡No te desanimes, que yo estoy contigo!

Inténtalo mañana, y quizás la fortuna te sonría más ampliamente. 🍀
"""

    @staticmethod
    def bonus_play_game_reached_limit():
        hours, minutes = get_time_until_limit_update(hours=0)
        return f"""
⏳ <b>Oh, parece que ya jugaste hoy.</b>

¡Pero no te preocupes! Mañana tendrás una nueva oportunidad de probar suerte.

Vuelve en <i>{hours} h {minutes} min</i> y demuestra de qué eres capaz. 👏
"""

    # Catalog
    CATALOG_INFO = """
📁 <b>¡Bienvenido al catálogo de posibilidades!</b>

Aquí encontrarás una colección de roles de empleados digitales y un catálogo de prompts para inspirarte.

Todo está en tus manos: simplemente presiona el botón 👇
"""
    CATALOG_MANAGE = "Gestionar catálogo 🎭"
    CATALOG_DIGITAL_EMPLOYEES = "Catálogo de roles 🎭"
    CATALOG_DIGITAL_EMPLOYEES_INFO = """
🎭 <b>¡Bienvenido a mi catálogo de roles!</b>

Elige entre una variedad de empleados digitales, cada uno con sus propias habilidades y conocimientos 🎩

Simplemente presiona el botón a continuación 👇
"""
    CATALOG_DIGITAL_EMPLOYEES_FORBIDDEN_ERROR = """
🔒 <b>¡Ups! Parece que has ingresado a una zona VIP exclusiva.</b> 🌟

Estás a un clic de desbloquear mi tesoro de roles IA, pero parece que aún no tienes la llave dorada.

¡No te preocupes! Puedes obtenerla fácilmente haciendo clic en el botón de abajo:
"""
    CATALOG_PROMPTS = "Catálogo de prompts 🗯"
    CATALOG_PROMPTS_CHOOSE_MODEL_TYPE = """
🗯 <b>¡Bienvenido al catálogo de prompts!</b>

Modelos de texto, gráficos y música están listos para inspirarte.

Simplemente elige el tipo que necesitas presionando el botón a continuación 👇
"""
    CATALOG_PROMPTS_CHOOSE_CATEGORY = """
🗯 <b>Catálogo de prompts</b>

Selecciona una <b>categoría</b> que necesites presionando el botón a continuación 👇
"""
    CATALOG_PROMPTS_CHOOSE_SUBCATEGORY = """
🗯 <b>Catálogo de prompts</b>

Selecciona una <b>subcategoría</b> que necesites presionando el botón a continuación 👇
"""

    @staticmethod
    def catalog_prompts_choose_prompt(prompts: list[Prompt]):
        prompt_info = ''
        for index, prompt in enumerate(prompts):
            is_last = index == len(prompts) - 1
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            prompt_info += f'    {left_part} <b>{index + 1}</b>: {prompt.names.get(LanguageCode.ES)}{right_part}'

        return f"""
🗯 <b>Catálogo de prompts</b>

Prompts:
{prompt_info}

Selecciona el <b>número del prompt</b> para obtener el prompt completo presionando el botón a continuación 👇
"""

    @staticmethod
    def catalog_prompts_info_prompt(prompt: Prompt, products: list[Product]):
        model_info = ''
        for index, product in enumerate(products):
            is_last = index == len(products) - 1
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            model_info += f'    {left_part} <b>{product.names.get(LanguageCode.ES)}</b>{right_part}'

        return f"""
🗯 <b>Catálogo de prompts</b>

Has seleccionado el prompt: <b>{prompt.names.get(LanguageCode.ES)}</b>
Este prompt es adecuado para los modelos:
{model_info}

Elige lo que deseas hacer presionando el botón a continuación 👇
"""

    @staticmethod
    def catalog_prompts_examples(products: list[Product]):
        prompt_examples_info = ''
        for index, product in enumerate(products):
            is_last = index == len(products) - 1
            is_first = index == 0
            left_part = '┣' if not is_last else '┗'
            right_part = '\n' if not is_last else ''
            prompt_examples_info += f'{left_part if not is_first else "┏"} <b>{index + 1}</b>: {product.names.get(LanguageCode.ES)}{right_part}'

        return prompt_examples_info

    CATALOG_PROMPTS_GET_SHORT_PROMPT = "Obtener prompt corto ⚡️"
    CATALOG_PROMPTS_GET_LONG_PROMPT = "Obtener prompt largo 📜"
    CATALOG_PROMPTS_GET_EXAMPLES = "Obtener ejemplos del prompt 👀"
    CATALOG_PROMPTS_COPY = "Copiar prompt 📋"

    # Chats
    @staticmethod
    def chat_info(current_chat_name: str, total_chats: int) -> str:
        return f"""
🗨️ <b>Chat actual: {current_chat_name}</b>

¡Bienvenido al dinámico mundo de los chats gestionados por IA! Esto es lo que puedes hacer:

- Crear nuevos chats temáticos: Sumérgete en conversaciones enfocadas en tus intereses.
- Cambiar entre chats: Navega fácilmente entre tus diferentes chats.
- Limpiar chats: Borraré todo lo que hemos hablado, como si nunca hubiera existido.
- Eliminar chats: Libera espacio eliminando los chats que ya no necesitas.

📈 Total de chats: <b>{total_chats}</b>

¿Listo para personalizar tu experiencia de chat? Explora las opciones a continuación y comienza a chatear. 👇
"""

    CHAT_DEFAULT_TITLE = "Nuevo chat"
    CHAT_MANAGE = "Gestionar chats 💬"
    CHAT_SHOW = "Mostrar chats 👁️"
    CHAT_CREATE = "Crear un nuevo chat 💬"
    CHAT_CREATE_SUCCESS = "💬 ¡Chat creado! 🎉\n👌 No olvides cambiar a él en /settings"
    CHAT_TYPE_TITLE = "Escribe el título del chat"
    CHAT_SWITCH = "Cambiar entre chats 🔄"
    CHAT_SWITCH_FORBIDDEN_ERROR = """
🔄 <b>¿Quieres cambiar? ¡Espera un momento!</b> ⚙️

Actualmente estás en tu único chat. Un lugar acogedor, pero ¿por qué no ampliar tus horizontes? 🌌

Para moverte entre diferentes chats temáticos, simplemente obtén acceso haciendo clic en uno de los botones de abajo:
"""
    CHAT_SWITCH_SUCCESS = "¡Chat cambiado con éxito! 🎉"
    CHAT_RESET = "Limpiar chat ♻️"
    CHAT_RESET_WARNING = """
🧹 <b>¡Advertencia de limpieza de chat!</b> 🚨

Estás a punto de borrar todos los mensajes y limpiar el contexto de este chat. Esta acción no se puede deshacer, y todos tus mensajes desaparecerán en el polvo virtual. ¿Estás seguro de que deseas continuar?

✅ <b>Confirmar</b> - ¡Sí, empecemos desde cero!
❌ <b>Cancelar</b> - No, aún tengo algo que decir.
"""
    CHAT_RESET_SUCCESS = """
🧹<b>¡Chat limpiado con éxito!</b> ✨

Ahora soy como un pez dorado, ya no recuerdo nada de lo que se dijo antes 🐠
"""
    CHAT_DELETE = "Eliminar chat 🗑"
    CHAT_DELETE_FORBIDDEN_ERROR = """
🗑️ <b>¿Eliminar este chat? ¡Eso suena a quedarse hablando solo!</b> 💬

Este es tu único reino-chat, ¡y todo reino necesita su rey o reina! Eliminarlo es como cancelar tu propia fiesta 🎈

¿Qué tal si en lugar de eso, añades más chats a tu reino? Mira las opciones haciendo clic en uno de los botones de abajo:
"""
    CHAT_DELETE_SUCCESS = "🗑️ ¡Chat eliminado con éxito! 🎉"

    # Eightify
    EIGHTIFY = '👀 Resumen de YouTube'
    EIGHTIFY_INFO = """
Con <b>Resumen de YouTube</b>, puedes obtener un resumen breve y claro de cualquier video de YouTube.

<b>¿Cómo funciona?</b>
🔗 Envía el enlace del video de YouTube que deseas resumir.
✅ Analizaré el video y te devolveré un resumen en texto.

¡Espero tu enlace! 😊
"""
    EIGHTIFY_VALUE_ERROR = "Esto no parece ser un enlace de YouTube 🧐\n\nPor favor, envía otro enlace"
    EIGHTIFY_VIDEO_ERROR = "Lo siento, pero no puedo procesar este video de YouTube 😢\n\nPor favor, envía otro enlace"

    # Errors
    ERROR = """
He encontrado un error desconocido 🤒

Por favor, intenta de nuevo o contacta con el soporte técnico:
"""
    ERROR_NETWORK = """
He perdido la conexión con Telegram 🤒

Por favor, inténtalo de nuevo 🥺
"""
    ERROR_PROMPT_REQUIRED = """
🚨 <b>¡Espera! ¿Dónde está el prompt?</b> 🧐

Parece que falta el prompt, como un té sin azúcar — sin sabor ☕️

Vamos, escribe algo — ¡y la magia comenzará! 🪄
"""
    ERROR_PROMPT_TOO_LONG = """
🚨 <b>¡Vaya! Esto no es un prompt, ¡es toda una novela!</b> 😅

Intenta acortar un poco el texto para que el modelo no se tome unas vacaciones 🌴

Hazlo más breve, ¡y creará una obra maestra! ✨
"""
    ERROR_REQUEST_FORBIDDEN = """
<b>¡Ups! Parece que tu solicitud se topó con una barrera de seguridad.</b> 🚨

Algo en tu solicitud activó mis defensas contra contenido no permitido 🛑

Por favor, revisa el texto o la imagen por posibles elementos prohibidos e inténtalo de nuevo. 🌟
"""
    ERROR_PHOTO_FORBIDDEN = """
⚠️ El envío de fotos solo está disponible en los siguientes modelos:

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
    ┣ 🎆 Stable Diffusion
    ┣ 🫐 Flux
    ┣ 🌌 Luma Photon
    ┣ 📷 FaceSwap
    ┗ 🪄 Photoshop IA

📹 <b>Modelos de video:</b>
    ┣ 🎬 Kling
    ┣ 🎥 Runway
    ┗ 🔆 Luma Ray

Usa el botón de abajo para cambiar a un modelo que soporte el procesamiento de imágenes 👀
"""
    ERROR_PHOTO_REQUIRED = "Se requiere una foto para este modelo ⚠️\n\nPor favor, envía una foto junto con el prompt."
    ERROR_ALBUM_FORBIDDEN = "El modelo IA actual no puede procesar varias fotos a la vez. Por favor, envía solo una 🙂"
    ERROR_VIDEO_FORBIDDEN = "Todavía no puedo trabajar con videos en este modelo IA 👀"
    ERROR_DOCUMENT_FORBIDDEN = "Todavía no sé cómo trabajar con documentos de este tipo 👀"
    ERROR_STICKER_FORBIDDEN = "Aún no puedo trabajar con stickers 👀"
    ERROR_SERVER_OVERLOADED = "Actualmente tengo una gran carga en el servidor 🫨\n\nPor favor, inténtalo de nuevo más tarde."
    ERROR_FILE_TOO_BIG = """
🚧 <b>¡Ups!</b>

El archivo enviado es demasiado grande. Solo puedo procesar archivos de menos de 20 MB.

Por favor, intenta de nuevo con un archivo más pequeño. 😊
"""
    ERROR_IS_NOT_NUMBER = """
🚧 <b>¡Ups!</b>

Parece que esto no es un número 🤔

Por favor, envíame un valor numérico 🔢
"""

    # Examples
    EXAMPLE_INFO = "Aquí está lo que puedes hacer para acceder a esta red neuronal:"

    @staticmethod
    def example_text_model(model: str):
        return f"👇 Así respondería a tu solicitud *{model}*"

    @staticmethod
    def example_image_model(model: str):
        return f"☝️ Así dibujaría {model} las imágenes según tu solicitud"

    # FaceSwap
    FACE_SWAP_INFO = """
🌟 <b>¡Vamos a crear con tus fotos!</b>

¿Listo? ¡Sumérgete en el mundo de la imaginación! 🚀

- 📷 <b>Envíame una foto con tu rostro</b> para reemplazarlo con FaceSwap.
- ✍️ <b>Escríbeme cualquier prompt</b> y generaré una imagen reemplazando tu rostro.
- 🔄 O simplemente <b>elige un paquete</b> abajo y comienza tu aventura fotográfica 👇
"""
    FACE_SWAP_GENERATIONS_IN_PACKAGES_ENDED = """
🎨 <b>¡Wow, has usado todas las generaciones en nuestros paquetes! ¡Tu creatividad es impresionante!</b> 🌟

¿Qué sigue?
- 📷 Envíame una foto con tu rostro para reemplazarlo con FaceSwap.
- ✍️ Escríbeme cualquier prompt y generaré una imagen reemplazando tu rostro.
- 🔄 O cambia el modelo con /model para seguir creando con otras herramientas de IA.
"""
    FACE_SWAP_MIN_ERROR = """
🤨 <b>¡Un momento, amigo!</b>

Parece que intentas solicitar menos de una imagen. ¡En el mundo de la creatividad, necesito al menos una para comenzar!

🌟 <b>Consejo:</b> Ingresa un número mayor a 0 para empezar con la magia. ¡Dejemos volar las ideas creativas!
"""
    FACE_SWAP_MAX_ERROR = """
🚀 <b>¡Wow, apuntamos alto, lo veo! Pero, ups...</b>

Estás pidiendo más imágenes de las que tenemos disponibles.

🧐 <b>¿Qué tal esto?</b> Intenta con un número dentro del límite de tu paquete.
"""
    FACE_SWAP_NO_FACE_FOUND_ERROR = """
🚫 <b>Problema al procesar la foto</b>

Lamentablemente, no pude identificar claramente un rostro en la foto. Por favor, sube una nueva imagen donde tu rostro sea visible y esté en buena calidad.

🔄 Después de cargar una nueva foto, intenta nuevamente, ¡por favor!
"""

    @staticmethod
    def face_swap_choose_package(name: str, available_images: int, total_images: int, used_images: int) -> str:
        remain_images = total_images - used_images
        return f"""
<b>{name}</b>

¡Tienes un tesoro de <b>{total_images} imágenes</b> en tu paquete, listo para desatar tu creatividad! 🌟

🌠 <b>Generaciones disponibles</b>: {available_images} imágenes. ¿Necesitas más? Consulta /buy o /bonus.
🔍 <b>Usadas</b>: {used_images} imágenes. {'¡Impresionante, estás en racha!' if used_images > 0 else ''}
🚀 <b>Restantes</b>: {remain_images} imágenes. {'¡Ya las has usado todas!' if remain_images == 0 else '¡Aún tienes muchas oportunidades!'}.

📝 <b>Escribe cuántos cambios de rostro deseas hacer o selecciona una opción rápida de los botones a continuación</b>. ¡El mundo de las transformaciones faciales te espera! 🎭🔄
"""

    @staticmethod
    def face_swap_package_forbidden_error(available_images: int) -> str:
        return f"""
🔔 <b>¡Ups, un pequeño problema!</b> 🚧

Parece que solo te quedan <b>{available_images} generaciones</b> en tu paquete.

💡 <b>Consejo</b>: ¡A veces menos es más! Intenta con un número menor o usa /buy para desbloquear posibilidades ilimitadas.
"""

    # Feedback
    FEEDBACK_INFO = """
🌟 <b>¡Tu opinión importa!</b> 🌟

Siempre busco mejorar, y tu feedback es como oro para mí ✨

- ¿Algo te ha gustado especialmente? ¡Cuéntamelo! 😊
- ¿Tienes sugerencias para nuevas funciones? Estoy aquí para escucharlas 🦻
- ¿Algo te preocupa? Estoy listo para resolverlo 🐞

Y recuerda, cada comentario que compartes es un paso hacia un mejor servicio. ¡Espero con ansias tus pensamientos! 💌
"""
    FEEDBACK_SUCCESS = """
🌟 <b>¡Feedback recibido!</b> 🌟

Tu opinión es el ingrediente secreto del éxito. Estoy trabajando en mejoras, y tu comentario es una pieza clave 🍳🔑
Te agregaré 25 créditos a tu saldo una vez que mis creadores revisen el contenido de tu feedback. ¡Mientras tanto, disfruta de la experiencia!

¡Tu opinión es muy valiosa para mí! 💌
"""
    FEEDBACK_APPROVED = """
🌟 <b>¡Feedback aprobado!</b> 🌟

Como muestra de agradecimiento, tu saldo ha aumentado en 25 créditos 🪙. ¡Úsalos para acceder a funciones exclusivas o para aumentar el número de generaciones en las redes neuronales! 💸

Para utilizar el bono, escribe el comando /bonus y sigue las instrucciones.
"""
    FEEDBACK_APPROVED_WITH_LIMIT_ERROR = """
🌟 <b>¡Feedback aprobado!</b> 🌟

¡Gracias a tu contribución, seguiré mejorando! Pero, lamentablemente, no puedo acreditarte más créditos ya que has alcanzado el límite de recompensas por feedback.

Escribe el comando /bonus para descubrir otras formas de obtener créditos de bonificación. ¡Sigue compartiendo y disfrutando de cada momento aquí! 🎉
"""
    FEEDBACK_DENIED = """
🌟 <b>¡Feedback rechazado!</b> 🌟

Lamentablemente, tu feedback no fue lo suficientemente constructivo, y no puedo aumentar tu saldo de bonificación 😢

¡No te preocupes! Puedes escribir el comando /bonus para explorar otras formas de aumentar tu saldo de bonificación.
"""

    # Flux
    FLUX_STRICT_SAFETY_TOLERANCE = "🔒 Estricta"
    FLUX_MIDDLE_SAFETY_TOLERANCE = "🔏 Media"
    FLUX_PERMISSIVE_SAFETY_TOLERANCE = "🔓 Baja"

    # Gemini Video
    GEMINI_VIDEO = "📼 Resumen de Video"
    GEMINI_VIDEO_INFO = """
Con <b>Resumen de Video</b>, puedes obtener un breve resumen textual de cualquier video.

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
    GEMINI_VIDEO_TOO_LONG_ERROR = "La duración del video debe ser menor a 60 minutos ⚠️\n\nPor favor, envía otro video."
    GEMINI_VIDEO_VALUE_ERROR = "Esto no parece ser un enlace de video 🧐\n\nPor favor, envía otro enlace."

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
    GENDER_UNSPECIFIED = "No especificado 🤷"
    GENDER_MALE = "Masculino 👕"
    GENDER_FEMALE = "Femenino 👚"

    # Generation
    GENERATION_IMAGE_SUCCESS = "✨ Aquí está tu imagen generada 🎨"
    GENERATION_VIDEO_SUCCESS = "✨ Aquí está tu video generado 🎞"

    # Help
    HELP_INFO = """
🤖 <b>Esto es lo que puedes hacer:</b>

━ Comandos generales:
    ┣ 👋 /start - <b>Sobre mí</b>: Descubre lo que puedo hacer por ti
    ┣ 👤 /profile - <b>Tu perfil</b>: Revisa tu cuota de uso o los detalles de tu suscripción y mucho más
    ┣ 🌍 /language - <b>Cambiar idioma</b>: Elige tu idioma preferido para los mensajes
    ┣ 💳 /buy - <b>Comprar suscripción o paquetes</b>: Consigue un nuevo nivel
    ┣ 🎁 /bonus - Consulta tu saldo de bonos y <b>canjea tus bonos por paquetes de generaciones</b>
    ┣ 🔑 /promo_code - <b>Activar código promocional</b>, si tienes uno
    ┣ 📡 /feedback - <b>Comentarios</b>: Ayúdame a mejorar
    ┗ 📄 /terms - <b>Condiciones del servicio</b>

━ Comandos de IA:
    ┣ 🤖 /model - <b>Cambiar entre redes neuronales</b> en cualquier momento — todas las modelos disponibles allí
    ┣ ℹ️ /info - <b>Obtener información sobre las redes neuronales</b>: Descubre para qué sirven y cómo funcionan
    ┣ 📁 /catalog - <b>Catálogo de roles y prompts</b>: Mejora la eficiencia al interactuar conmigo
    ┣ 💥 /chatgpt - <b>Conversar con ChatGPT</b>: Comienza un diálogo de texto y recibe respuestas avanzadas de la IA
    ┣ 🚀 /claude - <b>Conversar con Claude</b>: Inicia una conversación y explora respuestas profundas de Claude
    ┣ ✨ /gemini - <b>Conversar con Gemini</b>: Comienza a chatear y adéntrate en las respuestas avanzadas de esta nueva IA
    ┣ 🐦 /grok - <b>Conversar con Grok</b>: Experimenta con las avanzadas capacidades analíticas de la IA de X
    ┣ 🌐 /perplexity - <b>Conversar con Perplexity</b>: Obtén respuestas a preguntas complejas usando la búsqueda de internet en Perplexity
    ┣ 👀 /youtube_summary - <b>Resumen de YouTube</b>: Envía un enlace de video y recibe un resumen
    ┣ 📼 /video_summary - <b>Resumen de cualquier video</b>: Envía un enlace de video o carga el tuyo y recibe un resumen
    ┣ 👨‍🎨 /dalle - <b>Crear imágenes con DALL-E</b>: Convierte tus ideas en dibujos
    ┣ 🎨 /midjourney - <b>Crea con Midjourney</b>: Transforma tus pensamientos en imágenes
    ┣ 🎆 /stable_diffusion - <b>Originalidad con Stable Diffusion</b>: Crea imágenes únicas
    ┣ 🫐 /flux - <b>Experimentar con Flux</b>: Explora variaciones infinitas de imágenes sin limitaciones
    ┣ 🌌 /luma_photon - <b>Crear arte con Luma Photon</b>: Desarrolla tus ideas en impresionantes proyectos visuales
    ┣ 📷️ /face_swap - <b>Diviértete con FaceSwap</b>: Cambia de rostro en las fotos
    ┣ 🪄 /photoshop - <b>Magia con Photoshop IA</b>: Retoque y edición de fotos con un solo toque
    ┣ 🎺 /music_gen - <b>Componer con MusicGen</b>: Crea música sin derechos de autor
    ┣ 🎸 /suno - <b>Crear canciones con Suno</b>: Compón tu propia canción con letras y géneros variados
    ┣ 🎬 /kling - <b>Crear videos con Kling</b>: Genera videos de alta calidad
    ┣ 🎥 /runway - <b>Generación de videos con Runway</b>: Crea videos creativos a partir de fotos
    ┣ 🔆 /luma_ray - <b>Crear videos con Luma Ray</b>: Convierte tus ideas en videoclips con precisión innovadora
    ┗ 🔧 /settings - <b>Configurar modelos a tu medida</b>: Ajusta los modelos según tus necesidades. También puedes <b>elegir un asistente digital</b> y <b>gestionar chats temáticos</b>

Solo escribe el comando. Para cualquier duda, también puedes contactar con soporte técnico:
"""

    # Info
    INFO = "🤖 <b>Elige el tipo de modelos sobre los que deseas obtener información:</b>"
    INFO_TEXT_MODELS = "🤖 <b>Elige el modelo de texto sobre el que deseas obtener información:</b>"
    INFO_IMAGE_MODELS = "🤖 <b>Elige el modelo gráfico sobre el que deseas obtener información:</b>"
    INFO_MUSIC_MODELS = "🤖 <b>Elige el modelo musical sobre el que deseas obtener información:</b>"
    INFO_VIDEO_MODELS = "🤖 <b>Elige el modelo de video sobre el que deseas obtener información:</b>"
    INFO_CHAT_GPT = """
🤖 <b>Esto es lo que cada modelo puede hacer por ti:</b>

✉️ <b>ChatGPT 4.0 Omni Mini: El comunicador versátil</b>
- <i>Desde charlas cotidianas hasta conversaciones profundas</i>: Ideal para chatear sobre cualquier tema, desde la vida diaria hasta bromas.
- <i>Asistente educativo</i>: Ayuda con tareas escolares, aprendizaje de idiomas o temas complejos como programación.
- <i>Entrenador personal</i>: Motivación, consejos de fitness o incluso guías de meditación.
- <i>Escritor creativo</i>: ¿Necesitas un post, una historia o incluso una canción? ChatGPT 4.0 Omni Mini lo crea en segundos.
- <i>Guía de viajes</i>: Pide consejos de viaje, gastronomía local o datos históricos de tu próximo destino.
- <i>Asistente empresarial</i>: Redacción de correos electrónicos, planes de negocio o ideas de marketing.

💥 <b>ChatGPT 4.0 Omni: Inteligencia de nueva generación</b>
- <i>Análisis detallado</i>: Ideal para investigaciones profundas, explicaciones técnicas complejas o análisis de escenarios virtuales.
- <i>Resolución de problemas avanzados</i>: Desde cálculos matemáticos hasta diagnósticos de errores en software y respuestas a preguntas científicas.
- <i>Dominio del lenguaje</i>: Traducciones de alto nivel y mejora de habilidades conversacionales en diferentes idiomas.
- <i>Mentor creativo</i>: Ideas inspiradoras para blogs, guiones o investigaciones en el ámbito artístico.
- <i>Recomendaciones personalizadas</i>: Selección de libros, películas o itinerarios de viaje basados en tus preferencias.

🧩 <b>ChatGPT o1-mini: El mini-experto en resolución de problemas</b>
- <i>Análisis profundo</i>: Ayuda con razonamiento lógico y resolución de problemas complejos.
- <i>Pensamiento crítico</i>: Perfecto para tareas que requieren atención al detalle y conclusiones fundamentadas.
- <i>Asistente educativo</i>: Ayuda con programación, matemáticas o investigaciones científicas.
- <i>Eficiencia</i>: Respuestas rápidas y precisas a preguntas prácticas y teóricas.

🧪 <b>ChatGPT o1: Revolución en el razonamiento</b>
- <i>Análisis avanzado de datos</i>: Ideal para procesar y analizar grandes cantidades de información.
- <i>Resolución fundamentada</i>: Perfecto para tareas que requieren conclusiones argumentadas y lógica compleja.
- <i>Generación de hipótesis</i>: Ideal para investigaciones científicas y experimentos.
- <i>Desarrollo de estrategias</i>: Ayuda en la creación de estrategias complejas, tanto en negocios como en proyectos personales.
"""
    INFO_CLAUDE = """
🤖 <b>Esto es lo que cada modelo puede hacer por ti:</b>

📜 <b>Claude 3.5 Haiku: El arte de la brevedad y la sabiduría</b>
- <i>Respuestas profundas y concisas</i>: Ideal para reflexiones y consejos que van directo al punto.
- <i>Resolución rápida de problemas</i>: Proporciona soluciones inmediatas para preguntas cotidianas y técnicas.
- <i>Precisión lingüística</i>: Capacidad para expresar la esencia en pocas palabras, ya sea con traducciones o explicaciones.
- <i>Creatividad en el minimalismo</i>: Ayuda a crear contenido breve, desde poemas hasta ideas condensadas.

💫 <b>Claude 3.5 Sonnet: El equilibrio entre velocidad y sabiduría</b>
- <i>Análisis multifuncional</i>: Eficaz para investigaciones integrales y explicaciones técnicas.
- <i>Resolución de problemas</i>: Soporte en matemáticas, errores de programación o enigmas científicos.
- <i>Experto lingüístico</i>: Un aliado confiable para traducir textos y mejorar habilidades conversacionales en diferentes idiomas.
- <i>Asesor creativo</i>: Desarrollo de ideas innovadoras para contenido y proyectos artísticos.
- <i>Guía personal</i>: Recomendaciones de contenido cultural y planificación de viajes adaptadas a tus intereses.

🚀 <b>Claude 3.0 Opus: El máximo poder y profundidad</b>
- <i>Análisis avanzado</i>: Ideal para manejar investigaciones complejas y escenarios hipotéticos.
- <i>Experto en resolución de problemas</i>: Responde preguntas científicas avanzadas, problemas técnicos y desafíos matemáticos.
- <i>Nivel supremo de dominio lingüístico</i>: Traducciones y práctica de idiomas a nivel profesional.
- <i>Consultor creativo</i>: Apoyo en el desarrollo de ideas únicas para guiones y proyectos artísticos.
- <i>Conserje de recomendaciones</i>: Consejos expertos sobre libros, películas y organización de viajes según tus preferencias.
"""
    INFO_GEMINI = """
🤖 <b>Esto es lo que cada modelo puede hacer por ti:</b>

🏎 <b>Gemini 2.0 Flash: Velocidad y eficiencia</b>
- <i>Análisis rápido de datos</i>: Ideal para tareas que requieren análisis instantáneo y generación de respuestas rápidas.
- <i>Resultados inmediatos</i>: Perfecto para búsquedas de información y soluciones rápidas.
- <i>Resolución simplificada de problemas</i>: Ayuda con cálculos simples, tareas cotidianas y solicitudes rápidas.
- <i>Interacción fluida</i>: Proporciona información precisa en el menor tiempo posible, manteniendo un alto nivel de exactitud.

💼 <b>Gemini 1.5 Pro: Potencia profesional</b>
- <i>Análisis profundo</i>: Destaca en investigaciones complejas, análisis de datos avanzados y explicaciones técnicas detalladas.
- <i>Soluciones integrales</i>: Ideal para resolver tareas de alta complejidad, preguntas científicas y problemas matemáticos.
- <i>Flexibilidad lingüística</i>: Ayuda en traducciones, edición de textos y soporte multilingüe a nivel profesional.
- <i>Pensamiento creativo</i>: Facilita el desarrollo de ideas para proyectos creativos, escritura y otras tareas innovadoras.
- <i>Recomendaciones personalizadas</i>: Ofrece consejos profesionales sobre contenido y planificación de actividades según tus preferencias.

🛡 <b>Gemini 1.0 Ultra: Potencia y precisión</b>
- <i>Analítica ilimitada</i>: Maneja con excelencia tareas complejas, análisis profundos y grandes volúmenes de datos.
- <i>Soluciones precisas</i>: Ideal para cálculos avanzados e investigaciones científicas.
- <i>Erudición lingüística</i>: Experto en traducciones y soporte lingüístico al más alto nivel.
- <i>Inspiración creativa</i>: Asistente en la creación y desarrollo de proyectos creativos e ideas complejas.
- <i>Interacción personalizada</i>: Ajusta sus respuestas según tus necesidades y preferencias específicas.
"""
    INFO_GROK = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🐦 <b>Grok 2.0: El maestro del contexto</b>
- <i>Análisis adaptativo</i>: Perfecto para una comprensión profunda del contexto y el análisis de datos complejos.
- <i>Procesamiento de textos largos</i>: Capaz de trabajar eficazmente con grandes volúmenes de información mientras conserva los puntos clave.
- <i>Mentor creativo</i>: Ayuda a generar ideas para proyectos, artículos o investigaciones científicas.
- <i>Educación y tutoría</i>: Proporciona explicaciones claras de temas complejos, ayudando en tareas educativas y profesionales.
- <i>Desarrollo de estrategias</i>: Apoyo en la creación de estrategias para negocios o metas personales basadas en análisis profundos.
"""
    INFO_PERPLEXITY = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🌐 <b>Perplexity: Respuestas instantáneas con alcance global</b>
- <i>Información global</i>: Capacidad excepcional para proporcionar datos precisos y enlaces a fuentes confiables.
- <i>Navegación por temas complejos</i>: Ayuda a entender cualquier cuestión, desde las más simples hasta las más complicadas.
- <i>Resolución de problemas reales</i>: Recomendaciones rápidas para negocios, educación y la vida cotidiana.
- <i>Búsqueda por consulta</i>: Excelente para solicitudes específicas, ofreciendo respuestas precisas.
- <i>Interfaz amigable</i>: Se integra fácilmente en tus tareas y proyectos para un uso conveniente.
"""
    INFO_DALL_E = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

👨‍🎨 <b>DALL-E: El genio creativo</b>
- <i>Arte a pedido</i>: Generación de imágenes únicas basadas en descripciones, ideal para ilustradores o quienes buscan inspiración.
- <i>Creador publicitario</i>: Creación de imágenes atractivas para publicidad o contenido en redes sociales.
- <i>Herramienta educativa</i>: Visualización de conceptos complejos para mejorar la comprensión en la enseñanza.
- <i>Diseño de interiores</i>: Obtención de ideas para la distribución de espacios o temas decorativos.
- <i>Diseño de moda</i>: Creación de diseños de ropa o ilustraciones de moda.
"""
    INFO_MIDJOURNEY = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🎨 <b>Midjourney: El navegante de la creatividad</b>
- <i>Diseño artístico</i>: Creación de obras maestras visuales y abstracciones, ideal para artistas y diseñadores que buscan un estilo único.
- <i>Modelado arquitectónico</i>: Generación de proyectos conceptuales de edificios y planificación de espacios.
- <i>Asistente educativo</i>: Ilustraciones para materiales de aprendizaje que mejoran la comprensión de temas complejos.
- <i>Diseño de interiores</i>: Visualización de soluciones de interiores, desde estilos clásicos hasta tendencias modernas.
- <i>Moda y estilo</i>: Desarrollo de looks de moda y accesorios, experimentando con colores y formas.
"""
    INFO_STABLE_DIFFUSION = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🎆 <b>Stable Diffusion: La herramienta para generar imágenes</b>
- <i>Ilustración creativa</i>: Generación de imágenes únicas basadas en solicitudes de texto, perfecta para artistas, diseñadores y escritores.
- <i>Arte conceptual y bocetos</i>: Creación de imágenes conceptuales para videojuegos, películas y otros proyectos, ayudando a visualizar ideas.
- <i>Estilización de imágenes</i>: Transformación de imágenes existentes en diversos estilos artísticos, desde cómics hasta corrientes pictóricas clásicas.
- <i>Prototipado de diseño</i>: Generación rápida de conceptos visuales para logotipos, pósters o diseño web.
- <i>Experimentos con estilos artísticos</i>: Posibilidad de explorar colores, formas y texturas para desarrollar nuevas soluciones visuales.
"""
    INFO_FLUX = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🫐 <b>Flux: Experimentos con Flux</b>
- <i>Variaciones infinitas</i>: Generación de imágenes diversas basadas en una sola solicitud, cada resultado es único.
- <i>Ajuste preciso de parámetros</i>: Controla el proceso de creación para obtener un resultado exacto que se adapte a tus necesidades.
- <i>Generación con elementos aleatorios</i>: Introduce elementos de azar para soluciones creativas inesperadas.
- <i>Diversidad de conceptos visuales</i>: Explora una amplia gama de estilos y enfoques artísticos, adaptando el proceso a tus objetivos.
- <i>Experimentos visuales rápidos</i>: Prueba múltiples conceptos y estilos sin restricciones, descubriendo nuevos horizontes creativos.
"""
    INFO_LUMA_PHOTON = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🌌 <b>Luma Photon: Visualización profesional</b>
- <i>Imágenes fotorrealistas</i>: Creación de visualizaciones de alta calidad para arquitectura, diseño y marketing.
- <i>Modelado tridimensional</i>: Generación de conceptos 3D y visualizaciones, ideal para presentaciones y proyectos.
- <i>Efectos de luz y texturas</i>: Control avanzado de efectos de luz y texturas para lograr imágenes realistas.
- <i>Renderizado creativo</i>: Experimenta con composiciones y estilos para crear visualizaciones artísticas únicas.
- <i>Eficiencia en el trabajo</i>: Óptimo para profesionales que buscan resultados rápidos y de alta calidad para sus proyectos.
"""
    INFO_FACE_SWAP = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

📷️ <b>FaceSwap: El maestro de la diversión</b>
- <i>Redescubrimientos divertidos</i>: Mira cómo te verías en diferentes épocas históricas o como personajes icónicos del cine.
- <i>Felicitaciones personalizadas</i>: Crea tarjetas únicas o invitaciones con imágenes personalizadas.
- <i>Memes y creación de contenido</i>: Dale vida a tus redes sociales con fotos graciosas o imaginativas usando cambio de rostro.
- <i>Transformaciones digitales</i>: Experimenta con nuevos cortes de cabello o estilos de maquillaje.
- <i>Fusiona tu rostro con celebridades</i>: Combina tu cara con la de famosos para comparaciones divertidas.
"""
    INFO_PHOTOSHOP_AI = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🪄 <b>Photoshop IA: Magia en fotografía</b>
- <i>Restauración de fotos</i>: Recupera fotografías antiguas o dañadas devolviéndoles su aspecto original.
- <i>Transformación de blanco y negro a color</i>: Da vida a fotos monocromáticas añadiendo colores vibrantes y naturales.
- <i>Eliminación de fondos</i>: Elimina fácilmente el fondo de las imágenes, dejando solo el objeto principal.
"""
    INFO_MUSIC_GEN = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🎺 <b>MusicGen: Tu compositor personal</b>
- <i>Creación de melodías únicas</i>: Convierte tus ideas en obras musicales de cualquier género, desde clásico hasta pop.
- <i>Pistas de audio personalizadas</i>: Crea la banda sonora perfecta para tu próximo proyecto de video, juego o presentación.
- <i>Exploración de estilos musicales</i>: Experimenta con diferentes géneros y sonidos para encontrar tu propio estilo único.
- <i>Educación e inspiración musical</i>: Aprende sobre teoría musical e historia de géneros mientras creas música.
- <i>Generación instantánea de melodías</i>: Solo describe tu idea o estado de ánimo, y MusicGen lo transformará en música al instante.
"""
    INFO_SUNO = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🎸 <b>Suno: El profesional de la creación de canciones</b>
- <i>Transformación de texto en canciones</i>: Suno convierte tus letras en canciones, ajustando la melodía y el ritmo a tu estilo.
- <i>Canciones personalizadas</i>: Crea canciones únicas para momentos especiales, desde un regalo personal hasta la banda sonora de tu evento.
- <i>Explora la diversidad de géneros musicales</i>: Descubre nuevos horizontes musicales experimentando con estilos y sonidos diversos.
- <i>Educación e inspiración musical</i>: Aprende teoría musical e historia de los géneros practicando composición.
- <i>Creación rápida de música</i>: Describe tus emociones o una historia, y Suno convertirá tu descripción en una canción al instante.
"""
    INFO_KLING = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🎬 <b>Kling: Creación de videos de alta calidad</b>
- <i>Generación de videos a partir de descripciones</i>: Describe tu idea y Kling creará un video impresionante.
- <i>Trabajo con estilos únicos</i>: Explora diversos estilos para resaltar la singularidad de tu video.
- <i>Transiciones dinámicas</i>: Añade automáticamente transiciones fluidas y efectivas entre escenas.
- <i>Efectos visuales creativos</i>: Genera videos con efectos modernos para tus proyectos.
- <i>Contenido en minutos</i>: Crea videos impactantes rápidamente sin necesidad de experiencia en edición de video.
"""
    INFO_RUNWAY = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🎥 <b>Runway: Generación de videos</b>
- <i>Creación de clips cortos</i>: Describe una idea o guion, agrega una foto, y Runway generará un videoclip único.
- <i>Generación de videos a partir de foto + texto</i>: Transforma una imagen y una descripción en un video dinámico.
- <i>Animaciones y efectos visuales</i>: Crea animaciones atractivas y creativas basadas en tus ideas.
- <i>Contenido IA para redes sociales</i>: Genera rápidamente videos llamativos para plataformas y proyectos.
- <i>Exploración de formatos de video</i>: Experimenta con el poder del IA para desarrollar nuevos estilos y contenidos visuales.
"""
    INFO_LUMA_RAY = """
🤖 <b>Esto es lo que este modelo puede hacer por ti:</b>

🔆 <b>Luma Ray: Creatividad en video</b>
- <i>Videos de alta calidad</i>: Genera videos realistas y dinámicos a partir de descripciones.
- <i>Animación 3D</i>: Crea animaciones tridimensionales impresionantes para tus proyectos.
- <i>Estilo cinematográfico</i>: Aplica efectos y composiciones dignos del cine profesional.
- <i>Magia visual</i>: Utiliza tecnología avanzada para producir contenido de alta calidad.
- <i>Formatos innovadores de video</i>: Experimenta con nuevos estilos y enfoques en la creación de contenido visual.
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
    MODEL = "Para cambiar el modelo, presiona el botón de abajo 👇"
    MODEL_CHANGE_AI = "🤖 Cambiar modelo de IA"
    MODEL_CHOOSE_CHAT_GPT = "Para seleccionar el modelo <b>ChatGPT 💭</b>, presiona el botón de abajo 👇"
    MODEL_CHOOSE_CLAUDE = "Para seleccionar el modelo <b>Claude 📄</b>, presiona el botón de abajo 👇"
    MODEL_CHOOSE_GEMINI = "Para seleccionar el modelo <b>Gemini ✨</b>, presiona el botón de abajo 👇"
    MODEL_CONTINUE_GENERATING = "Continuar generando"
    MODEL_ALREADY_MAKE_REQUEST = "Ya has hecho una solicitud. Por favor, espera ⚠️"
    MODEL_READY_FOR_NEW_REQUEST = "Puedes hacer la siguiente solicitud 😌"
    MODEL_SWITCHED_TO_AI_SETTINGS = "⚙️ Configuración del modelo"
    MODEL_SWITCHED_TO_AI_INFO = "ℹ️ Más información sobre el modelo"
    MODEL_SWITCHED_TO_AI_EXAMPLES = "💡 Mostrar ejemplos"
    MODEL_ALREADY_SWITCHED_TO_THIS_MODEL = """
🔄 <b>¡Oops, parece que nada ha cambiado!</b>

Has seleccionado el mismo modelo que ya tienes activo. No te preocupes, tu universo digital permanece intacto. Puedes continuar con tus consultas o creaciones como de costumbre. Si deseas cambiar algo, simplemente selecciona otro modelo a través de /model

De cualquier manera, ¡estoy aquí para ayudarte! 🛟
"""

    @staticmethod
    def model_switched(model_name: str, model_type: ModelType, model_info: dict):
        if model_type == ModelType.TEXT:
            facts = f"""⚙️ Hechos y configuraciones:
    ┣ 📅 Conocimientos hasta: {model_info.get('training_data')}
    ┣ 📷 Compatibilidad con fotos: {'Sí ✅' if model_info.get('support_photos', False) else 'No ❌'}
    ┣ 🎙 Respuestas de voz: {'Activadas ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Desactivadas ❌'}
    ┗ 🎭 Rol: {model_info.get('role')}"""
        elif model_type == ModelType.SUMMARY:
            model_focus = model_info.get(UserSettings.FOCUS, VideoSummaryFocus.INSIGHTFUL)
            if model_focus == VideoSummaryFocus.INSIGHTFUL:
                model_focus = Spanish.VIDEO_SUMMARY_FOCUS_INSIGHTFUL
            elif model_focus == VideoSummaryFocus.FUNNY:
                model_focus = Spanish.VIDEO_SUMMARY_FOCUS_FUNNY
            elif model_focus == VideoSummaryFocus.ACTIONABLE:
                model_focus = Spanish.VIDEO_SUMMARY_FOCUS_ACTIONABLE
            elif model_focus == VideoSummaryFocus.CONTROVERSIAL:
                model_focus = Spanish.VIDEO_SUMMARY_FOCUS_CONTROVERSIAL

            model_format = model_info.get(UserSettings.FORMAT, VideoSummaryFormat.LIST)
            if model_format == VideoSummaryFormat.LIST:
                model_format = Spanish.VIDEO_SUMMARY_FORMAT_LIST
            elif model_format == VideoSummaryFormat.FAQ:
                model_format = Spanish.VIDEO_SUMMARY_FORMAT_FAQ

            model_amount = model_info.get(UserSettings.AMOUNT, VideoSummaryAmount.AUTO)
            if model_amount == VideoSummaryAmount.AUTO:
                model_amount = Spanish.VIDEO_SUMMARY_AMOUNT_AUTO
            elif model_amount == VideoSummaryAmount.SHORT:
                model_amount = Spanish.VIDEO_SUMMARY_AMOUNT_SHORT
            elif model_amount == VideoSummaryAmount.DETAILED:
                model_amount = Spanish.VIDEO_SUMMARY_AMOUNT_DETAILED

            facts = f"""⚙️ Configuraciones:
    ┣ 🎯 Enfoque: {model_focus}
    ┣ 🎛 Formato: {model_format}
    ┣ 📏 Longitud del resultado: {model_amount}
    ┗ 🎙 Respuestas de voz: {'Activadas ✅' if model_info.get(UserSettings.TURN_ON_VOICE_MESSAGES, False) else 'Desactivadas ❌'}"""
        elif model_type == ModelType.IMAGE:
            facts = f"""⚙️ Hechos y configuraciones:
    ┣ 📷 Compatibilidad con fotos: {'Sí ✅' if model_info.get('support_photos', False) else 'No ❌'}
    ┣ 📐 Relación de aspecto: {'Personalizado' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
    ┗ 🗯 Tipo de envío: {Spanish.SETTINGS_SEND_TYPE_DOCUMENT if model_info.get(UserSettings.SEND_TYPE, SendType.IMAGE) == SendType.DOCUMENT else Spanish.SETTINGS_SEND_TYPE_IMAGE}"""
        elif model_type == ModelType.MUSIC:
            facts = f"""⚙️ Configuraciones:
    ┗ 🗯 Tipo de envío: {Spanish.SETTINGS_SEND_TYPE_VIDEO if model_info.get(UserSettings.SEND_TYPE, SendType.AUDIO) == SendType.VIDEO else Spanish.SETTINGS_SEND_TYPE_AUDIO}"""
        elif model_type == ModelType.VIDEO:
            facts = f"""⚙️ Hechos y configuraciones:
    ┣ 📷 Compatibilidad con fotos: {'Sí ✅' if model_info.get('support_photos', False) else 'No ❌'}
    ┣ 📐 Relación de aspecto: {'Personalizado' if model_info.get(UserSettings.ASPECT_RATIO, AspectRatio.CUSTOM) == AspectRatio.CUSTOM else model_info.get(UserSettings.ASPECT_RATIO)}
    ┣ 📏 Duración: {model_info.get(UserSettings.DURATION, 5)} segundos
    ┗ 🗯 Tipo de envío: {Spanish.SETTINGS_SEND_TYPE_DOCUMENT if model_info.get(UserSettings.SEND_TYPE, SendType.VIDEO) == SendType.DOCUMENT else Spanish.SETTINGS_SEND_TYPE_VIDEO}"""
        else:
            facts = f"ℹ️ Hechos y configuraciones: Próximamente 🔜"

        return f"""
<b>Modelo seleccionado: {model_name}</b>

{facts}

👇 Usa los botones de abajo para explorar más:
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
            "Sumergiéndome en un océano de datos para pescar tu respuesta. Vuelvo enseguida... 🌊🎣",
            "Consultando a mis elfos virtuales. Ellos suelen ser excelentes encontrando respuestas... 🧝",
            "Activando el motor warp para una búsqueda rápida de tu respuesta. ¡Sujétate fuerte... 🚀",
            "Estoy en la cocina preparando un lote fresco de respuestas. ¡Este será sabroso... 🍳",
            "Haciendo un viaje rápido a la nube y de vuelta. Espero traer unas gotas de sabiduría... ☁️",
            "Plantando tu pregunta en mi jardín digital. Veamos qué florece... 🌱🤖",
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
            "Puliendo píxeles hasta la perfección, un momento... 👁️🎭",
            "Preparando un festín visual para tus ojos... 🍽️👀",
            "Consultando con el Da Vinci digital para tu solicitud artística... 🎭",
            "Limpiando el polvo de mi caballete digital para tu proyecto creativo... 🖼️🖌️",
            "Creando un hechizo visual en el caldero de la IA... 🧙‍🔮",
            "Activando el lienzo virtual. Prepárate para el arte... 🖼️",
            "Transformando tus ideas en una galería de píxeles... 🖼️👨‍🎨",
            "Explorando un safari digital para capturar tu visión artística... 🦁🎨",
            "Encendiendo los motores artísticos de la IA, espera un momento... 🏎️💨",
            "Zambulléndome en la piscina de la imaginación digital... 🏊‍💭",
            "Cocinando una sinfonía visual en la cocina de la IA... 🍳🎼",
            "Reuniendo nubes de creatividad para plasmar tu obra maestra visual... ☁️🎨",
            "Recolectando pinceles y pinturas digitales para dar vida a tu visión... 🎨🖌️",
            "Invocando dragones de píxeles para crear una imagen épica... 🐉",
            "Llamando a las abejas digitales para recolectar el néctar de tu florecimiento visual... 🐝",
            "Colocándome mi sombrero digital de artista para empezar a trabajar en tu creación... 👒",
            "Sumergiendo píxeles en una solución mágica para que brillen con arte... 🧪✨",
            "Moldeando tu imagen con arcilla de imaginación. ¡Pronto será una obra maestra!... 🏺",
            "Mis elfos virtuales ya están pintando tu imagen... 🧝‍♂️",
            "Las tortugas virtuales están llevando tu imagen a través del mar de datos... 🐢",
            "Los gatitos digitales están pintando tu obra maestra con sus patitas... 🐱",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ La generación puede tardar hasta 3 minutos"

        return text

    @staticmethod
    def model_face_swap_processing_request() -> str:
        texts = [
            "Viajando a la dimensión del intercambio de rostros... 🌌👤",
            "Mezclando y emparejando rostros como un Picasso digital... 🧑‍🎨🖼️",
            "Cambiando rostros más rápido que un camaleón cambia de colores... 🦎🌈",
            "Despertando la magia de la fusión de rostros... ✨👥",
            "Realizando alquimia facial, transformando identidades... 🧙‍🧬",
            "Activando la máquina de cambio de rostros... 🤖🔀",
            "Preparando una poción para la transformación facial... 🧪👩‍🔬",
            "Creando hechizos en el mundo encantado de los rostros... 🧚‍🎭️",
            "Dirigiendo una sinfonía de rasgos faciales... 🎼👩‍🎤👨‍🎤",
            "Esculpiendo nuevos rostros en mi estudio de arte digital... 🎨👩‍🎨",
            "Cocinando en el caldero mágico del intercambio de rostros... 🧙‍🔮",
            "Construyendo rostros como un gran arquitecto... 🏗️👷‍",
            "Empezando una búsqueda mística de la combinación perfecta de rostros... 🗺️🔍",
            "Lanzando un cohete hacia la aventura de intercambio de rostros... 🚀👨‍🚀👩‍🚀",
            "Embarcándome en un viaje galáctico de intercambio de rostros... 🌌👽",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ La generación puede tardar hasta 5 minutos"

        return text

    @staticmethod
    def model_music_processing_request() -> str:
        texts = [
            "Activando el generador musical, prepárate para disfrutar... 🎶👂",
            "Mezclando notas como un DJ en una fiesta... 🎧🕺",
            "El mago de las melodías está en acción, prepárate para la magia... 🧙‍✨",
            "Creando música que hará bailar incluso a los robots... 🤖💃",
            "El laboratorio musical está en marcha, prepárate para algo épico... 🔬🔥",
            "Capturando olas de inspiración y transformándolas en sonido... 🌊🎹",
            "Subiendo a las cumbres de la música, espera algo grandioso... 🏔️🎶",
            "Creando algo que ningún oído ha escuchado antes... 🌟👂",
            "Es hora de sumergirse en un océano de armonía y ritmo... 🌊🎶",
            "Abriendo la puerta a un mundo donde la música crea realidades... 🚪🌍",
            "Descifrando los códigos de la composición para crear algo único... 🧬🎶",
            "Cocinando melodías como un chef prepara sus mejores platos... 🍽️🎹",
            "Organizando una fiesta en las teclas, cada nota es un invitado... 🎉🎹",
            "Explorando un laberinto melódico para encontrar la salida perfecta... 🌀🎵",
            "Transformando vibraciones en el aire en sonidos mágicos... 🌬️🎼",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ La generación puede tardar hasta 10 minutos"

        return text

    @staticmethod
    def model_video_processing_request() -> str:
        texts = [
            "Cargando el estreno de tu película, casi listo... 🎬🍿",
            "¡El cohete de la creatividad en video está despegando! Abróchate el cinturón... 🚀🎥",
            "Los fotogramas cobran vida, luces, cámara, acción... 🎬💥",
            "Generando obra maestra cuadro por cuadro... 🎥✨",
            "No es un video, es una maravilla cinematográfica en camino... 🎞️🌟",
            "Armando el rompecabezas con los mejores fotogramas para tu WOW... 🤩🎞️",
            "Uniendo píxeles, prepárate para un video espectacular... 🎇🎥",
            "Capturando los mejores momentos, el video está en proceso... 🎥🎣",
            "La mesa de edición está en llamas, creando una obra maestra en video... 🔥✂️",
            "Cargando contenido visual a tu dimensión... 🖥️🎞️",
            "Las abejas de IA trabajan en tu video-miel... ¡Prepárate para un dulce resultado! 🐝🍯️",
            "El proyector mágico ya está arrancando... 🎥✨",
            "La pizza se cocina en el horno... ¡oh no, tu video! 🍕🎞️",
            "Creando hechizos visuales, el video será mágico... ✨🎩",
            "Llevando tu video por los rieles de la creatividad... 🚉🎥",
        ]

        text = random.choice(texts)
        text += "\n\n⚠️ La generación puede tardar hasta 20 minutos"

        return text

    @staticmethod
    def model_wait_for_another_request(seconds: int) -> str:
        return f"Por favor, espera {seconds} segundos más antes de enviar otra solicitud ⏳"

    @staticmethod
    def model_reached_usage_limit():
        hours, minutes = get_time_until_limit_update()

        return f"""
<b>¡Ups! 🚨</b>

¡Tu cuota diaria para usar este modelo ha desaparecido como un truco de magia! 🎩

🔄 <i>El límite se renovará en: {hours} horas y {minutes} minutos.</i>

❗️¿No quieres esperar? Tranquilo, tengo una solución para ti:
"""

    MODELS_TEXT = "🔤 Modelos de texto"
    MODELS_SUMMARY = "📝 Modelos de resumen"
    MODELS_IMAGE = "🖼 Modelos gráficos"
    MODELS_MUSIC = "🎵 Modelos musicales"
    MODELS_VIDEO = "📹 Modelos de video"

    # MusicGen
    MUSIC_GEN_INFO = """
<b>Tu taller musical 🎹</b>

¡Abre la puerta a un mundo donde cada idea tuya se convierte en música! Con <b>MusicGen</b>, tu imaginación es el único límite. Estoy listo para transformar tus palabras y descripciones en melodías únicas 🎼

Escríbeme qué tipo de música quieres crear. Usa palabras para describir su estilo, estado de ánimo e instrumentos. No necesitas ser profesional; simplemente comparte tu idea, ¡y juntos la haremos realidad! 🎤
"""
    MUSIC_GEN_TYPE_SECONDS = """
<b>¿Cuántos segundos tendrá tu sinfonía?</b> ⏳

¡Perfecto! Tu idea musical está lista para cobrar vida. Ahora viene lo interesante: ¿cuánto tiempo le damos a esta magia musical para desplegarse completamente?
<i>Cada 10 segundos consumen 1 generación</i> 🎼

Escribe o elige la duración de tu composición en segundos. Ya sea una ráfaga instantánea de inspiración o una odisea épica, ¡estamos listos para crearla juntos! ✨
"""
    MUSIC_GEN_MIN_ERROR = """
🤨 <b>Espera, compañero/a!</b>

Parece que quieres solicitar menos de 10 segundos. En el mundo de la creatividad, necesitamos al menos 10 para empezar.

🌟 <b>Consejo:</b> Ingresa un número mayor o igual a 10 para comenzar la magia.
"""
    MUSIC_GEN_MAX_ERROR = """
🤨 <b>Espera, compañero/a!</b>

Parece que quieres solicitar más de 10 minutos, y aún no puedo generar tanto tiempo.

🌟 <b>Consejo:</b> Ingresa un número menor a 600 para comenzar la magia.
"""
    MUSIC_GEN_SECONDS_30 = "🔹 30 segundos"
    MUSIC_GEN_SECONDS_60 = "🔹 60 segundos (1 minuto)"
    MUSIC_GEN_SECONDS_180 = "🔹 180 segundos (3 minutos)"
    MUSIC_GEN_SECONDS_300 = "🔹 300 segundos (5 minutos)"
    MUSIC_GEN_SECONDS_600 = "🔹 600 segundos (10 minutos)"

    @staticmethod
    def music_gen_forbidden_error(available_seconds: int) -> str:
        return f"""
🔔 <b>Ups, ¡un pequeño problema!</b> 🚧

Parece que solo te quedan <b>{available_seconds} segundos</b> disponibles en tu arsenal.

💡 <b>Consejo:</b> A veces, menos es más. Intenta ingresar una cantidad menor, o utiliza /buy para desbloquear posibilidades ilimitadas.
"""

    # Notify about Quota
    @staticmethod
    def notify_about_quota(
        subscription_limits: dict,
    ) -> str:
        texts = [
            f"""
🤖 ¡Hola! ¿Te acuerdas de mí?

🤓 Estoy aquí para recordarte tus cuotas diarias:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto listas para convertirse en tus obras maestras.
- {format_number(subscription_limits[Quota.DALL_E])} oportunidades gráficas para dar vida a tus ideas.

🔥 ¡No las dejes sin usar! ¡Empieza ahora mismo!
""",
            f"""
🤖 ¡Hola! Soy Fusy, tu asistente personal. ¡Sí, estoy de vuelta!

😢 Me di cuenta de que hace tiempo no usas tus cuotas. Por si acaso, aquí te lo recuerdo: cada día tienes:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto para dar forma a tus ideas.
- {format_number(subscription_limits[Quota.DALL_E])} imágenes listas para animar tus pensamientos.

✨ ¿Empezamos a crear? Estoy listo cuando tú lo estés.
""",
            f"""
🤖 Soy yo, Fusy, tu robot personal, con un recordatorio importante.

🤨 ¿Sabías que tienes:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto para dar vida a tus pensamientos brillantes.
- {format_number(subscription_limits[Quota.DALL_E])} imágenes para visualizar tus ideas.

🔋 Ya estoy cargado y listo. ¡Solo falta que empecemos a crear!
""",
            f"""
🤖 ¡Soy yo otra vez! Te extrañaba...

😢 Pensé en algo... Tus cuotas también te extrañan:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto inspiradoras esperan su momento.
- {format_number(subscription_limits[Quota.DALL_E])} ideas visuales listas para cobrar vida.

💡 ¡Dame la oportunidad de ayudarte a crear algo increíble!
""",
            f"""
🤖 ¡Hola, soy Fusy! Tus cuotas no se usarán solas, ¿lo sabías?

🫤 ¿Te lo recuerdo? Aquí va:
- {format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])} solicitudes de texto que podrían ser el comienzo de un gran éxito.
- {format_number(subscription_limits[Quota.DALL_E])} imágenes listas para dibujar tu imaginación.

✨ Es hora de crear, y estoy aquí para ayudarte. ¡Vamos a empezar!
""",
        ]

        return random.choice(texts)

    # Open
    OPEN_SETTINGS = "⚙️ Ir a configuración"
    OPEN_BONUS_INFO = "🎁 Consultar saldo de bonificación"
    OPEN_BUY_SUBSCRIPTIONS_INFO = "💎 Suscribirse"
    OPEN_BUY_PACKAGES_INFO = "🛍 Comprar paquetes"

    # Package
    PACKAGE = "🛍 Paquete"
    PACKAGE_SUCCESS = """
🎉 <b>¡Éxito! ¡Pago realizado con éxito!</b> 💳

Tu pago ha sido tan rápido como un superhéroe. 🦸‍ ¡Has desbloqueado el increíble poder del paquete elegido! Prepárate para aventuras emocionantes con IA. 🎢

Recuerda, con gran poder viene una gran... ya sabes cómo sigue. ¡Hagamos maravillas juntos! ✨🪄
"""
    PACKAGE_QUANTITY_MIN_ERROR = "¡Ups! Parece que la cantidad es menor al límite mínimo permitido. Por favor, elige una cantidad de paquetes que sea igual o superior al mínimo requerido. ¡Intenta de nuevo! 🔄"
    PACKAGE_QUANTITY_MAX_ERROR = "¡Ups! Parece que la cantidad ingresada supera lo que puedes comprar. Por favor, introduce un número menor o que se ajuste a tu saldo. ¡Intenta de nuevo! 🔄"

    @staticmethod
    def package_info(currency: Currency, cost: str) -> str:
        if currency == Currency.USD:
            cost = f"{Currency.SYMBOLS[currency]}{cost}"
        else:
            cost = f"{cost}{Currency.SYMBOLS[currency]}"

        return f"""
🤖 <b>¡Bienvenido a la zona de compras!</b> 🛍

<b>1 🪙 = {cost}</b>

Presiona el botón para seleccionar un paquete:
"""

    @staticmethod
    def package_choose_min(name: str) -> str:
        return f"""
🚀 ¡Genial!

Has elegido el paquete <b>{name}</b>

🌟 Por favor, <b>introduce la cantidad</b> que deseas adquirir.
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
🎉 <b>¡Éxito! ¡Pago realizado con éxito!</b> 💳

Tu pago ha sido tan rápido como un superhéroe. 🦸‍ ¡Has desbloqueado el increíble poder de los paquetes seleccionados! Prepárate para aventuras emocionantes con IA. 🎢

Recuerda, con gran poder viene una gran... ya sabes cómo sigue. ¡Hagamos maravillas juntos! ✨🪄
"""
    PACKAGES_END = """
🕒 <b>¡El tiempo de uno o más paquetes ha expirado!</b> ⌛

Oh no, parece que tu paquete de mensajes rápidos (o mensajes de voz, acceso al catálogo de roles) ha llegado a su fin. ¡Pero no te preocupes, siempre hay nuevas oportunidades en el horizonte!

🎁 ¿Quieres continuar? Consulta mis ofertas haciendo clic en el botón de abajo:
"""

    @staticmethod
    def packages_description(user_id: str):
        return f"Pago de paquetes del carrito para el usuario: {user_id}"

    # Payment
    PAYMENT_BUY = """
🚀 <b>¡Bienvenidos a la tienda de maravillas!</b> 🪄

Delante de ti se abren las puertas a un mundo de posibilidades exclusivas. ¿Qué eliges hoy?

🌟 <b>Suscripciones: ¡Todo incluido, un pase VIP que desbloquea todas las funciones de IA y más!</b>
Conversaciones, creación de imágenes, música, videos y mucho más. Todo está incluido para que disfrutes y explores cada día.

🛍 <b>Paquetes: Generaciones específicas para tus necesidades</b>
¿Necesitas generación específica para ciertas tareas? Los paquetes te permiten elegir la cantidad de solicitudes y modelos de IA que necesitas, pagando solo por lo que realmente usas.

Elige pulsando el botón de abajo 👇
"""
    PAYMENT_CHANGE_CURRENCY = "💱 Cambiar moneda"
    PAYMENT_YOOKASSA_PAYMENT_METHOD = "🪆💳 YooKassa"
    PAYMENT_STRIPE_PAYMENT_METHOD = "🌍💳 Stripe"
    PAYMENT_TELEGRAM_STARS_PAYMENT_METHOD = "✈️⭐️ Telegram Stars"
    PAYMENT_CHOOSE_PAYMENT_METHOD = """
<b>Elige tu método de pago:</b>

🪆💳 <b>YooKassa (Tarjetas Rusas)</b>

🌍💳 <b>Stripe (Tarjetas Internacionales)</b>

✈️⭐️ <b>Telegram Stars (Moneda en Telegram)</b>
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
En esta sección encontrarás herramientas de inteligencia artificial para editar y estilizar imágenes.

¡Haz clic en el botón de abajo para elegir una acción y comenzar tu viaje creativo! 👇
"""
    PHOTOSHOP_AI_RESTORATION = "Restauración 🖌"
    PHOTOSHOP_AI_RESTORATION_INFO = """
La herramienta detecta rasguños o daños en la imagen original y los elimina.

📸 Sube tu imagen al chat y deja que la magia comience ahora mismo. ¡✨!
"""
    PHOTOSHOP_AI_COLORIZATION = "Colorización 🌈"
    PHOTOSHOP_AI_COLORIZATION_INFO = """
Esta herramienta permite agregar color a imágenes en blanco y negro.

📸 Sube tu imagen al chat y deja que la magia comience ahora mismo. ¡✨!
"""
    PHOTOSHOP_AI_REMOVE_BACKGROUND = "Eliminar fondo 🗑"
    PHOTOSHOP_AI_REMOVE_BACKGROUND_INFO = """
La herramienta permite eliminar el fondo de una imagen.

📸 Sube tu imagen al chat y deja que la magia comience ahora mismo. ¡✨!
"""

    @staticmethod
    def photoshop_ai_actions() -> list[str]:
        return [
            Spanish.PHOTOSHOP_AI_RESTORATION,
            Spanish.PHOTOSHOP_AI_COLORIZATION,
            Spanish.PHOTOSHOP_AI_REMOVE_BACKGROUND,
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
            subscription_info = f"📫 <b>Estado de suscripción:</b> Cancelada. Válida hasta {renewal_date}"
        elif subscription_status == SubscriptionStatus.TRIAL:
            subscription_info = f"📫 <b>Estado de suscripción:</b> Período de prueba gratuito"
        else:
            subscription_info = "📫 <b>Estado de suscripción:</b> Activa"

        if current_currency == Currency.XTR:
            current_currency = f'Telegram Stars {Currency.SYMBOLS[current_currency]}'
        else:
            current_currency = f'{Currency.SYMBOLS[current_currency]}'

        return f"""
<b>Perfil</b> 👤

---------------------------

🤖 <b>Modelo actual: {current_model}</b>
💱 <b>Moneda actual: {current_currency}</b>
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
<b>Cuotas:</b>

🔤 <b>Modelos de Texto</b>:
━ <b>Básicos</b>:
    ┣ Límite diario: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI_MINI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI_MINI])}
    ┣ ✉️ ChatGPT 4.0 Omni Mini{f': adicional {additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI_MINI] > 0 else ''}
    ┣ 📜 Claude 3.5 Haiku{f': adicional {additional_usage_quota[Quota.CLAUDE_3_HAIKU]}' if additional_usage_quota[Quota.CLAUDE_3_HAIKU] > 0 else ''}
    ┗ 🏎 Gemini 2.0 Flash{f': adicional {additional_usage_quota[Quota.GEMINI_2_FLASH]}' if additional_usage_quota[Quota.GEMINI_2_FLASH] > 0 else ''}

━ <b>Avanzados</b>:
    ┣ Límite diario: {format_number(daily_limits[Quota.CHAT_GPT4_OMNI])}/{format_number(subscription_limits[Quota.CHAT_GPT4_OMNI])}
    ┣ 💥 ChatGPT 4.0 Omni{f': adicional {additional_usage_quota[Quota.CHAT_GPT4_OMNI]}' if additional_usage_quota[Quota.CHAT_GPT4_OMNI] > 0 else ''}
    ┣ 🧩 ChatGPT o1-mini{f': adicional {additional_usage_quota[Quota.CHAT_GPT_O_1_MINI]}' if additional_usage_quota[Quota.CHAT_GPT_O_1_MINI] > 0 else ''}
    ┣ 💫 Claude 3.5 Sonnet{f': adicional {additional_usage_quota[Quota.CLAUDE_3_SONNET]}' if additional_usage_quota[Quota.CLAUDE_3_SONNET] > 0 else ''}
    ┣ 💼 Gemini 1.5 Pro{f': adicional {additional_usage_quota[Quota.GEMINI_1_PRO]}' if additional_usage_quota[Quota.GEMINI_1_PRO] > 0 else ''}
    ┣ 🐦 Grok 2.0{f': adicional {additional_usage_quota[Quota.GROK_2]}' if additional_usage_quota[Quota.GROK_2] > 0 else ''}
    ┗ 🌐 Perplexity{f': adicional {additional_usage_quota[Quota.PERPLEXITY]}' if additional_usage_quota[Quota.PERPLEXITY] > 0 else ''}

━ <b>Premium</b>:
    ┣ Límite diario: {format_number(daily_limits[Quota.CHAT_GPT_O_1])}/{format_number(subscription_limits[Quota.CHAT_GPT_O_1])}
    ┣ 🧪 ChatGPT o1{f': adicional {additional_usage_quota[Quota.CHAT_GPT_O_1]}' if additional_usage_quota[Quota.CHAT_GPT_O_1] > 0 else ''}
    ┣ 🚀 Claude 3.0 Opus{f': adicional {additional_usage_quota[Quota.CLAUDE_3_OPUS]}' if additional_usage_quota[Quota.CLAUDE_3_OPUS] > 0 else ''}
    ┗ 🛡️ Gemini 1.0 Ultra{f': adicional {additional_usage_quota[Quota.GEMINI_1_ULTRA]}' if additional_usage_quota[Quota.GEMINI_1_ULTRA] > 0 else ''}

---------------------------

📝 <b>Modelos de Resumen</b>:
    ┣ Límite diario: {format_number(daily_limits[Quota.EIGHTIFY])}/{format_number(subscription_limits[Quota.EIGHTIFY])}
    ┣ 👀 YouTube{f': adicional {additional_usage_quota[Quota.EIGHTIFY]}' if additional_usage_quota[Quota.EIGHTIFY] > 0 else ''}
    ┗ 📼 Vídeo{f': adicional {additional_usage_quota[Quota.GEMINI_VIDEO]}' if additional_usage_quota[Quota.GEMINI_VIDEO] > 0 else ''}

---------------------------

🖼 <b>Modelos Gráficos</b>:
    ┣ Límite diario: {format_number(daily_limits[Quota.DALL_E])}/{format_number(subscription_limits[Quota.DALL_E])}
    ┣ 👨‍🎨 DALL-E{f': adicional {additional_usage_quota[Quota.DALL_E]}' if additional_usage_quota[Quota.DALL_E] > 0 else ''}
    ┣ 🎨 Midjourney{f': adicional {additional_usage_quota[Quota.MIDJOURNEY]}' if additional_usage_quota[Quota.MIDJOURNEY] > 0 else ''}
    ┣ 🎆 Stable Diffusion{f': adicional {additional_usage_quota[Quota.STABLE_DIFFUSION]}' if additional_usage_quota[Quota.STABLE_DIFFUSION] > 0 else ''}
    ┣ 🫐 Flux{f': adicional {additional_usage_quota[Quota.FLUX]}' if additional_usage_quota[Quota.FLUX] > 0 else ''}
    ┣ 🌌 Luma Photon{f': adicional {additional_usage_quota[Quota.LUMA_PHOTON]}' if additional_usage_quota[Quota.LUMA_PHOTON] > 0 else ''}
    ┣ 📷 FaceSwap{f': adicional {additional_usage_quota[Quota.FACE_SWAP]}' if additional_usage_quota[Quota.FACE_SWAP] > 0 else ''}
    ┗ 🪄 Photoshop AI{f': adicional {additional_usage_quota[Quota.PHOTOSHOP_AI]}' if additional_usage_quota[Quota.PHOTOSHOP_AI] > 0 else ''}

---------------------------

🎵 <b>Modelos de Música</b>:
    ┣ Límite diario: {format_number(daily_limits[Quota.SUNO])}/{format_number(subscription_limits[Quota.SUNO])}
    ┣ 🎺 MusicGen{f': adicional {additional_usage_quota[Quota.MUSIC_GEN]}' if additional_usage_quota[Quota.MUSIC_GEN] > 0 else ''}
    ┗ 🎸 Suno{f': adicional {additional_usage_quota[Quota.SUNO]}' if additional_usage_quota[Quota.SUNO] > 0 else ''}

---------------------------

📹 <b>Modelos de Vídeo</b>:
    ┣ 🎬 Kling{f': adicional {additional_usage_quota[Quota.KLING]}' if additional_usage_quota[Quota.KLING] > 0 else ''}
    ┣ 🎥 Runway{f': adicional {additional_usage_quota[Quota.RUNWAY]}' if additional_usage_quota[Quota.RUNWAY] > 0 else ''}
    ┗ 🔆 Luma Ray{f': adicional {additional_usage_quota[Quota.LUMA_RAY]}' if additional_usage_quota[Quota.LUMA_RAY] > 0 else ''}

---------------------------

🎭 <b>Acceso al catálogo de empleados digitales</b>: {'✅' if daily_limits[Quota.ACCESS_TO_CATALOG] or additional_usage_quota[Quota.ACCESS_TO_CATALOG] else '❌'}
🎙 <b>Mensajes de voz</b>: {'✅' if daily_limits[Quota.VOICE_MESSAGES] or additional_usage_quota[Quota.VOICE_MESSAGES] else '❌'}
⚡ <b>Respuestas rápidas</b>: {'✅' if daily_limits[Quota.FAST_MESSAGES] or additional_usage_quota[Quota.FAST_MESSAGES] else '❌'}

---------------------------

🔄 <i>El límite se actualizará en: {hours} h. {minutes} min.</i>
"""

    PROFILE_SHOW_QUOTA = "🔄 Mostrar cuota"
    PROFILE_TELL_ME_YOUR_GENDER = "Indique su género:"
    PROFILE_YOUR_GENDER = "Su género:"
    PROFILE_SEND_ME_YOUR_PICTURE = """
📸 <b>¿Listo para la transformación fotográfica? Envíame tu foto</b>

👍 <b>Recomendaciones para una foto perfecta:</b>
- Un selfie claro y de buena calidad.
- El selfie debe incluir solo a una persona.

👎 <b>Por favor, evita las siguientes fotos:</b>
- Fotos grupales.
- Animales.
- Niños menores de 18 años.
- Fotos de cuerpo completo.
- Fotos inapropiadas o desnudos.
- Gafas de sol u objetos que cubran la cara.
- Imágenes borrosas o fuera de foco.
- Videos y animaciones.
- Imágenes comprimidas o alteradas.

Una vez que tengas la foto ideal, <b>súbela</b> y deja que la magia comience 🌟
"""
    PROFILE_UPLOAD_PHOTO = "📷 Subir foto"
    PROFILE_UPLOADING_PHOTO = "Subiendo foto..."
    PROFILE_CHANGE_PHOTO = "📷 Cambiar foto"
    PROFILE_CHANGE_PHOTO_SUCCESS = "📸 ¡Foto subida exitosamente! 🌟"
    PROFILE_RENEW_SUBSCRIPTION = "♻️ Renovar suscripción"
    PROFILE_RENEW_SUBSCRIPTION_SUCCESS = "✅ La suscripción se ha renovado con éxito"
    PROFILE_CANCEL_SUBSCRIPTION = "❌ Cancelar suscripción"
    PROFILE_CANCEL_SUBSCRIPTION_CONFIRMATION = "❗¿Está seguro de que desea cancelar su suscripción?"
    PROFILE_CANCEL_SUBSCRIPTION_SUCCESS = "💸 La suscripción se ha cancelado con éxito"
    PROFILE_NO_ACTIVE_SUBSCRIPTION = "💸 No tienes una suscripción activa"

    # Promo Code
    PROMO_CODE_ACTIVATE = "🔑 Activar código promocional"
    PROMO_CODE_INFO = """
🔓 <b>¡Desbloquea el mundo mágico de la IA con tu código secreto!</b> 🌟

Si tienes un código promocional, simplemente ingrésalo para revelar funciones ocultas y sorpresas especiales 🔑

¿No tienes un código? ¡No te preocupes! Simplemente presiona 'Cancelar' para seguir explorando el universo de la IA sin él 🚀
"""
    PROMO_CODE_SUCCESS = """
🎉 <b>¡Tu código promocional se ha activado con éxito!</b> 🌟

Prepárate para sumergirte en el mundo mágico de la IA con tus nuevos beneficios

¡Que disfrutes explorando! 🚀
"""
    PROMO_CODE_ALREADY_HAVE_SUBSCRIPTION = """
🚫 <b>Ups</b>

¡Parece que ya formas parte de nuestro exclusivo club de suscriptores! 🌟
"""
    PROMO_CODE_EXPIRED_ERROR = """
🕒 <b>Oh, este código promocional ha expirado.</b>

Parece que este código promocional ya no es válido. Es como el cuento de Cenicienta, pero sin el zapato de cristal 🥿

¡Pero no te preocupes! Todavía puedes explorar otras ofertas mágicas. Simplemente selecciona una acción a continuación:
"""
    PROMO_CODE_NOT_FOUND_ERROR = """
🔍 <b>Oh, no se encontró el código promocional.</b>

Parece que el código ingresado está jugando al escondite porque no pude encontrarlo en el sistema 🕵️‍♂️

🤔 Revisa si hay errores y vuelve a intentarlo. Si aún no funciona, quizá valga la pena buscar otro código o consultar las ofertas en /buy, ¡allí encontrarás opciones interesantes! 🛍️
"""
    PROMO_CODE_ALREADY_USED_ERROR = """
🚫 <b>¡Ups, déjà vu!</b>

Parece que ya usaste este código promocional. Es una magia de un solo uso, ¡y ya la aprovechaste! ✨🧙

Pero no te preocupes. Puedes explorar mis ofertas presionando el botón a continuación:
"""

    # Remove Restriction
    REMOVE_RESTRICTION = "⛔️ Eliminar restricción"
    REMOVE_RESTRICTION_INFO = "Para eliminar la restricción, selecciona una de las opciones a continuación 👇"

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
⚙️ <b>Bienvenido a la configuración</b>

🌍 Para cambiar el idioma de la interfaz, utiliza el comando /language
🤖 Para cambiar de modelo, utiliza el comando /model

Aquí eres el artista y la configuración es tu paleta. Selecciona abajo el tipo de modelo que quieres personalizar 👇
"""
    SETTINGS_CHOOSE_MODEL = """
⚙️ <b>Bienvenido a la configuración</b>

Selecciona abajo el modelo que deseas personalizar 👇
"""
    SETTINGS_TO_OTHER_MODELS = "A otros modelos ◀️"
    SETTINGS_TO_OTHER_TYPE_MODELS = "A otros tipos de modelos ◀️"
    SETTINGS_VOICE_MESSAGES = """
⚙️ <b>Bienvenido a la configuración</b>

A continuación, encontrarás la configuración para respuestas de voz en todos los modelos de texto 🎙
"""
    SETTINGS_VERSION = "Versión 🤖"
    SETTINGS_FOCUS = "Enfoque 🎯"
    SETTINGS_FORMAT = "Formato 🎛"
    SETTINGS_AMOUNT = "Longitud de la Respuesta 📏"
    SETTINGS_SEND_TYPE = "Tipo de Envío 🗯"
    SETTINGS_SEND_TYPE_IMAGE = "Imagen 🖼"
    SETTINGS_SEND_TYPE_DOCUMENT = "Documento 📄"
    SETTINGS_SEND_TYPE_AUDIO = "Audio 🎤"
    SETTINGS_SEND_TYPE_VIDEO = "Video 📺"
    SETTINGS_ASPECT_RATIO = "Relación de Aspecto 📐"
    SETTINGS_QUALITY = "Calidad ✨"
    SETTINGS_PROMPT_SAFETY = "Protección de Prompt 🔐"
    SETTINGS_GENDER = "Género 👕/👚"
    SETTINGS_DURATION = "Duración en Segundos 📏"
    SETTINGS_MODE = "Modo 🤖"
    SETTINGS_SHOW_THE_NAME_OF_THE_CHATS = "Nombres de los chats en los mensajes"
    SETTINGS_SHOW_THE_NAME_OF_THE_ROLES = "Nombres de los roles en los mensajes"
    SETTINGS_SHOW_USAGE_QUOTA_IN_MESSAGES = "Cuota en mensajes"
    SETTINGS_TURN_ON_VOICE_MESSAGES = "Activar respuestas de voz"
    SETTINGS_LISTEN_VOICES = "Escuchar voces"

    # Shopping cart
    SHOPPING_CART = "🛒 Carrito"
    SHOPPING_CART_ADD = "➕ Agregar al carrito"
    SHOPPING_CART_ADD_OR_BUY_NOW = "¿Comprar ahora o agregar al carrito?"
    SHOPPING_CART_ADDED = "Agregado al carrito ✅"
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

💳 Total a pagar: {left_price_part}{round(total_sum, 2)}{right_price_part}
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
🤖 <b>¡Hola!</b> 👋

Soy tu guía en el mundo de las inteligencias artificiales, ofreciéndote acceso a las mejores herramientas para crear:
━ 💭 texto /text
━ 📝 resúmenes /summary
━ 🖼 imágenes /image
━ 🎵 música /music
━ 📹 videos /video

🏆 <b>No soy solo un bot — soy tu asistente con inteligencia emocional</b>, siempre listo para inspirarte, guiarte y hacer que tu experiencia con la IA sea simple y efectiva.

🆓 <b>Gratis</b>:
━ Interactúa con:
    ┣ <b>ChatGPT 4.0 Omni Mini ✉️</b> /chatgpt
    ┣ <b>Claude 3.5 Haiku 📜</b> /claude
    ┗ <b>Gemini 2.0 Flash 🏎</b> /gemini
━ Extrae lo más importante de:
    ┣ <b>YouTube 👀</b> /youtube_summary
    ┗ <b>Videos 📼</b> /video_summary
━ Crea imágenes con:
    ┣ <b>DALL-E 3 👨‍🎨</b> /dalle
    ┣ <b>Midjourney 6.1 🎨</b> /midjourney
    ┣ <b>Stable Diffusion 3.5 🎆</b> /stable_diffusion
    ┣ <b>Flux 1.1 Pro 🫐</b> /flux
    ┗ <b>Luma Photon 🌌</b> /luma_photon
━ Cambia caras con <b>FaceSwap 📷️</b> /face_swap
━ Edita tus imágenes con <b>Photoshop IA 🪄</b> /photoshop

💡 <b>Descubre más posibilidades en /buy:</b>
━ Redes neuronales de texto avanzadas:
    ┣ <b>ChatGPT 4.0 Omni 💥</b> /chatgpt
    ┣ <b>ChatGPT o1-mini 🧩</b> /chatgpt
    ┣ <b>ChatGPT o1 🧪</b> /chatgpt
    ┣ <b>Claude 3.5 Sonnet 💫</b> /claude
    ┣ <b>Claude 3.0 Opus 🚀</b> /claude
    ┣ <b>Gemini 1.5 Pro 💼</b> /gemini
    ┣ <b>Gemini 1.0 Ultra 🛡</b> /gemini
    ┣ <b>Grok 2.0 🐦</b> /grok
    ┗ <b>Perplexity 🌐</b> /perplexity
━ Redes neuronales de música:
    ┣ Crea melodías con <b>MusicGen 🎺</b> /music_gen
    ┗ Crea canciones con <b>Suno 4.0 🎸</b> /suno
━ Creatividad en video:
    ┣ Crea videos con <b>Kling 🎬</b> /kling
    ┣ Genera videos a partir de imágenes con <b>Runway Gen-3 Alpha Turbo 🎥</b> /runway
    ┗ Explora ideas de video con <b>Luma Ray 🔆</b> /luma_ray
━ ¡Y más cuotas diarias desbloqueadas! 🔓

✨ <b>¡Comienza a crear ahora!</b>
"""
    START_QUICK_GUIDE = "📖 Guía rápida"
    START_ADDITIONAL_FEATURES = "🔮 Funciones adicionales"
    START_QUICK_GUIDE_INFO = """
📖 Aquí tienes una guía rápida para empezar:

━ 💭 <b>Respuestas de texto</b>:
    ┣ 1️⃣ Escribe el comando /text
    ┣ 2️⃣ Elige un modelo
    ┗ 3️⃣ Escribe tus solicitudes en el chat

━ 📝 <b>Resúmenes</b>:
    ┣ 1️⃣ Escribe el comando /summary
    ┣ 2️⃣ Elige un modelo
    ┗ 3️⃣ Envía un video o enlace de YouTube

━ 🖼 <b>Creación de imágenes</b>:
    ┣ 1️⃣ Escribe el comando /image
    ┣ 2️⃣ Elige un modelo
    ┗ 3️⃣ Da rienda suelta a tu imaginación enviando tus solicitudes

━ 📷️ <b>Cambio de caras en fotos</b>:
    ┣ 1️⃣ Escribe el comando /face_swap
    ┣ 2️⃣ Sigue las instrucciones para obtener los mejores resultados
    ┗ 3️⃣ Escoge imágenes de mis paquetes únicos o sube las tuyas

━ 🪄 <b>Edición de imágenes</b>:
    ┣ 1️⃣ Escribe el comando /photoshop
    ┣ 2️⃣ Elige lo que deseas hacer con la imagen
    ┗ 3️⃣ Sube una imagen para editar

━ 🎵 <b>Creación de música</b>:
    ┣ 1️⃣ Escribe el comando /music
    ┣ 2️⃣ Elige un modelo
    ┗ 3️⃣ Describe la música que deseas o envía tu propio texto

━ 📹 <b>Creación de videos</b>:
    ┣ 1️⃣ Escribe el comando /video
    ┣ 2️⃣ Elige un modelo
    ┗ 3️⃣ Describe el video que deseas
"""
    START_ADDITIONAL_FEATURES_INFO = """
🔮 <b>Funciones adicionales</b>:

━ 🔄 /model - Cambia rápidamente entre redes neuronales
━ 📊 /profile - Consulta tu perfil y cuotas
━ 🔍 /info - Información útil sobre cada modelo de IA
━ 📂 /catalog - Catálogo de asistentes digitales y prompts
━ 🎁 /bonus - Descubre cómo obtener acceso gratuito a todas las redes neuronales
━ 🔧 /settings - Personalización y configuraciones
"""

    # Subscription
    SUBSCRIPTION = "💳 Suscripción"
    SUBSCRIPTION_MONTH_1 = "1 mes"
    SUBSCRIPTION_MONTHS_3 = "3 meses"
    SUBSCRIPTION_MONTHS_6 = "6 meses"
    SUBSCRIPTION_MONTHS_12 = "12 meses"
    SUBSCRIPTION_SUCCESS = """
🎉 <b>¡Hurra! ¡Ahora eres parte de nosotros!</b> 🚀

Tu suscripción está activada, ¡como una ardilla con cafeína! 🐿️☕ Bienvenido al club de increíbles posibilidades. Esto es lo que te espera:
- Todo un mundo de oportunidades está abierto para ti 🌍✨
- Tus amigos de IA ya están listos para ayudarte 🤖👍
- Prepárate para sumergirte en un océano de funciones y diversión 🌊🎉

¡Gracias por unirte a nosotros en este emocionante viaje! ¡Vamos a crear maravillas! 🪄🌟
"""
    SUBSCRIPTION_RESET = """
🚀 <b>¡Suscripción renovada!</b>

¡Hola, explorador del mundo de la IA! 🌟
¿Adivina qué? ¡Tu suscripción acaba de ser renovada! Es como una recarga mágica, pero mejor, porque es realidad 🧙‍♂️
Te espera un mes lleno de diversión con la IA. Comunica, crea, explora — ¡no hay límites! ✨

Sigue desbloqueando el poder de la IA y recuerda, estoy aquí para hacer realidad tus sueños digitales. ¡Hagamos de este mes algo inolvidable! 🤖💥
"""
    SUBSCRIPTION_END = """
🛑 <b>¡Suscripción finalizada!</b>

Tu suscripción ha terminado. Pero no te preocupes, ¡la aventura en el mundo de la IA no ha terminado! 🚀

Puedes seguir explorando el universo de la IA y renovar tu acceso mágico haciendo clic en el botón de abajo:
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

                text_subscriptions += f'- <b>{subscription_name}</b>: '
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
🤖 ¿Listo para acelerar tu viaje digital? Aquí tienes lo que ofrezco:

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

🎹 En el <b>modo sencillo</b>, solo necesitas describir de qué trata la canción y el género musical deseado.
🎸 En el <b>modo avanzado</b>, puedes usar tus propias letras y experimentar con diferentes géneros.

<b>Suno</b> creará 2 pistas de hasta 4 minutos cada una 🎧
"""
    SUNO_SIMPLE_MODE = "🎹 Sencillo"
    SUNO_CUSTOM_MODE = "🎸 Avanzado"
    SUNO_SIMPLE_MODE_PROMPT = """
🎶 <b>Descripción de la canción</b>

Para crear tu canción en modo sencillo, por favor describe de qué tratará la canción y el género musical deseado. Esto ayudará al sistema a entender mejor tus expectativas y a crear algo único para ti.

📝 Escribe tu descripción a continuación y comencemos con el proceso creativo.
"""
    SUNO_CUSTOM_MODE_LYRICS = """
🎤 <b>Letra de la canción</b>

Para crear tu canción en modo avanzado, necesitas proporcionar la letra que se utilizará en la música. Este es un elemento importante que dará a tu composición un toque personal y un ambiente especial.

✍️ Envía la letra de tu futura canción ahora mismo y creemos juntos una obra musical.
"""
    SUNO_CUSTOM_MODE_GENRES = """
🎵 <b>Elección de género</b>

Para que tu canción en modo avanzado se ajuste completamente a tus preferencias, indica los géneros que te gustaría incluir. La elección del género influye mucho en el estilo y el ambiente de la composición, así que elige cuidadosamente.

🔍 Enumera los géneros deseados separados por comas en tu próximo mensaje, y comenzaré a crear una canción única para ti.
"""
    SUNO_START_AGAIN = "Comenzar de nuevo 🔄"
    SUNO_TOO_MANY_WORDS_ERROR = "<b>¡Uy!</b> 🚧\n\nEn alguna de las etapas enviaste un texto demasiado largo 📝\n\nPor favor, intenta de nuevo con un texto más corto."
    SUNO_VALUE_ERROR = "Eso no parece ser un prompt válido 🧐\n\nPor favor, introduce otro valor."
    SUNO_SKIP = "Saltar ⏩️"

    # Tech Support
    TECH_SUPPORT = "👨‍💻 Soporte Técnico"

    # Terms Link
    TERMS_LINK = "https://telegra.ph/Terms-of-Service-in-GPTsTurboBot-05-07"

    # Video Summary
    VIDEO_SUMMARY_FOCUS_INSIGHTFUL = "Profundo 💡"
    VIDEO_SUMMARY_FOCUS_FUNNY = "Divertido 😄"
    VIDEO_SUMMARY_FOCUS_ACTIONABLE = "Útil 🛠"
    VIDEO_SUMMARY_FOCUS_CONTROVERSIAL = "Controversial 🔥"
    VIDEO_SUMMARY_FORMAT_LIST = "Lista 📋"
    VIDEO_SUMMARY_FORMAT_FAQ = "Preg/Resp 🗯"
    VIDEO_SUMMARY_AMOUNT_AUTO = "Automático ⚙️"
    VIDEO_SUMMARY_AMOUNT_SHORT = "Breve ✂️"
    VIDEO_SUMMARY_AMOUNT_DETAILED = "Detallado 📚"

    # Voice
    VOICE_MESSAGES = "Respuestas de voz 🎙"
    VOICE_MESSAGES_FORBIDDEN_ERROR = """
🎙 <b>¡Ups! Parece que tu voz se perdió en el espacio IA!</b>

Para desbloquear la magia de la conversión de voz a texto, simplemente usa los botones mágicos a continuación:
"""
