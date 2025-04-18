from bot.database.main import firebase
from bot.database.models.game import Game, GameStatus, GameType


async def create_game_object(
    user_id: str, type: GameType, status: GameStatus, reward: int
) -> Game:
    game_ref = firebase.db.collection(Game.COLLECTION_NAME).document()

    return Game(
        id=game_ref.id,
        user_id=user_id,
        type=type,
        status=status,
        reward=reward,
    )
