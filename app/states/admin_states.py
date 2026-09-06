from aiogram.fsm.state import State, StatesGroup


class AddAnimeStates(StatesGroup):
    title = State()
    description = State()
    genres = State()
    studio = State()
    rating = State()
    kind = State()
    poster = State()
    confirm = State()


class UploadVideoStates(StatesGroup):
    choose_anime = State()
    episode_number = State()
    video_360 = State()
    video_480 = State()
    video_720 = State()
    video_1080 = State()
    preview = State()


class BroadcastStates(StatesGroup):
    content = State()
    confirm = State()


class BannerStates(StatesGroup):
    waiting_media = State()


class StartTextStates(StatesGroup):
    waiting_text = State()


class RequiredChannelStates(StatesGroup):
    waiting_channel = State()
