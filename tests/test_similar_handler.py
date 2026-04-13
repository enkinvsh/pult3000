from src.deezer import DeezerRecommender, SimilarTrack


class TestSimilarTrack:
    def test_dataclass_fields(self):
        track = SimilarTrack(name="Test Song", artist="Test Artist")
        assert track.name == "Test Song"
        assert track.artist == "Test Artist"


class TestDeezerRecommender:
    def test_can_instantiate(self):
        recommender = DeezerRecommender()
        assert recommender is not None
