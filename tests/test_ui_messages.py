from bot_ui import bot_ui_messages as msg

def test_get_help_text():
    help_text = msg.get_help_text()
    assert isinstance(help_text, str)
    assert "помощ" in help_text.lower()
