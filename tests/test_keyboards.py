from src.bot.keyboards import reply_keyboard, search_results_keyboard


class TestReplyKeyboard:
    def test_has_media_buttons(self):
        kb = reply_keyboard()
        buttons = [btn.text for row in kb.keyboard for btn in row]
        assert "⏮" in buttons
        assert "⏯" in buttons
        assert "⏭" in buttons

    def test_has_extra_buttons(self):
        kb = reply_keyboard()
        buttons = [btn.text for row in kb.keyboard for btn in row]
        assert "🔀" in buttons
        assert "❤️" in buttons
        assert "🔇" in buttons
        assert "ℹ️" in buttons

    def test_has_volume_presets(self):
        kb = reply_keyboard()
        buttons = [btn.text for row in kb.keyboard for btn in row]
        assert "15%" in buttons
        assert "50%" in buttons
        assert "100%" in buttons


class TestSearchResultsKeyboard:
    def test_has_play_buttons(self):
        results = [("abc123", "Artist — Song")]
        kb = search_results_keyboard(results, total=1)
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert buttons[0].callback_data == "play:abc123"

    def test_pagination(self):
        results = [("abc", "Song")]
        kb = search_results_keyboard(results, page=0, per_page=5, total=10)
        nav = kb.inline_keyboard[-1]
        callbacks = {btn.callback_data for btn in nav}
        assert "page:1" in callbacks
