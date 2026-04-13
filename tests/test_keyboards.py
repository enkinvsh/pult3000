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
        assert "📻" in buttons

    def test_has_volume_presets(self):
        kb = reply_keyboard()
        buttons = [btn.text for row in kb.keyboard for btn in row]
        assert "15%" in buttons
        assert "50%" in buttons
        assert "100%" in buttons

    def test_similar_button_present(self):
        kb = reply_keyboard()
        all_texts = [btn.text for row in kb.keyboard for btn in row]
        assert "📻" in all_texts


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

    def test_default_page_prefix(self):
        results = [("v1", "Track 1"), ("v2", "Track 2")]
        kb = search_results_keyboard(results, page=0, per_page=2, total=5)
        nav_row = kb.inline_keyboard[-1]
        assert nav_row[0].callback_data == "page:1"

    def test_custom_page_prefix(self):
        results = [("v1", "Track 1"), ("v2", "Track 2")]
        kb = search_results_keyboard(
            results, page=0, per_page=2, total=5, page_prefix="sp"
        )
        nav_row = kb.inline_keyboard[-1]
        assert nav_row[0].callback_data == "sp:1"

    def test_prev_button_custom_prefix(self):
        results = [("v1", "Track 1")]
        kb = search_results_keyboard(
            results, page=1, per_page=1, total=3, page_prefix="sp"
        )
        nav_row = kb.inline_keyboard[-1]
        assert nav_row[0].callback_data == "sp:0"

    def test_play_prefix_unchanged(self):
        results = [("vid123", "Track 1")]
        kb = search_results_keyboard(
            results, page=0, per_page=5, total=1, page_prefix="sp"
        )
        assert kb.inline_keyboard[0][0].callback_data == "play:vid123"
