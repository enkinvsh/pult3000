from src.bot.keyboards import player_keyboard, volume_keyboard


class TestPlayerKeyboard:
    def test_player_keyboard_has_media_buttons(self):
        kb = player_keyboard()
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        callbacks = {btn.callback_data for btn in buttons}
        assert "prev" in callbacks
        assert "playpause" in callbacks
        assert "next" in callbacks

    def test_player_keyboard_has_extra_row(self):
        kb = player_keyboard()
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        callbacks = {btn.callback_data for btn in buttons}
        assert "shuffle" in callbacks
        assert "like" in callbacks
        assert "vol" in callbacks
        assert "info" in callbacks

    def test_volume_keyboard(self):
        kb = volume_keyboard()
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        callbacks = {btn.callback_data for btn in buttons}
        assert "vol_down" in callbacks
        assert "vol_up" in callbacks
        assert "vol_back" in callbacks
