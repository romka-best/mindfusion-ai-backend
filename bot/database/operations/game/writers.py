from bot.database.main import firebase
from bot.database.models.game import Game, GameStatus, GameType
from bot.database.operations.game.helpers import create_game_object


async def write_game(
    user_id: str, type: GameType, status: GameStatus, reward: int
) -> Game:
    game = await create_game_object(user_id, type, status, reward)
    await (
        firebase.db.collection(Game.COLLECTION_NAME)
        .document(game.id)
        .set(game.to_dict())
    )

    return game
