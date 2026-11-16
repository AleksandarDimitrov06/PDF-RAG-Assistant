from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

_histories: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id:str)->BaseChatMessageHistory:
    if session_id not in _histories:
        _histories[session_id] = InMemoryChatMessageHistory()
    return _histories[session_id]