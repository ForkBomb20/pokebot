import pytest
from unittest.mock import patch, MagicMock
import os
from PIL import Image
import tempfile

from utils.image_utils import merge_images_vert, create_type_image


@pytest.fixture
def temp_images(tmp_path):
    img1 = Image.new("RGB", (100, 50), color="red")
    img2 = Image.new("RGB", (80, 60), color="blue")
    path1 = tmp_path / "img1.png"
    path2 = tmp_path / "img2.png"
    img1.save(path1)
    img2.save(path2)
    return str(path1), str(path2)


class TestMergeImagesVert:
    def test_returns_image(self, temp_images):
        result = merge_images_vert(temp_images[0], temp_images[1])
        assert isinstance(result, Image.Image)

    def test_width_is_max_of_inputs(self, temp_images):
        result = merge_images_vert(temp_images[0], temp_images[1])
        # Result is 2x scaled: max(100, 80) * 2 = 200
        assert result.size[0] == 200

    def test_height_is_sum_of_inputs_scaled(self, temp_images):
        result = merge_images_vert(temp_images[0], temp_images[1])
        # (50 + 60) * 2 = 220
        assert result.size[1] == 220

    def test_same_size_images(self, tmp_path):
        img1 = Image.new("RGB", (100, 100), color="red")
        img2 = Image.new("RGB", (100, 100), color="blue")
        path1 = tmp_path / "same1.png"
        path2 = tmp_path / "same2.png"
        img1.save(path1)
        img2.save(path2)

        result = merge_images_vert(str(path1), str(path2))
        assert result.size == (200, 400)  # (100*2, (100+100)*2)


class TestCreateTypeImage:
    @pytest.fixture(autouse=True)
    def setup_cwd(self, monkeypatch):
        monkeypatch.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def test_single_type_returns_discord_file(self):
        result = create_type_image(["fire"])
        assert result is not None
        assert hasattr(result, "filename")
        assert result.filename == "fire.png"

    def test_dual_type_returns_discord_file(self):
        result = create_type_image(["fire", "flying"])
        assert result is not None
        assert result.filename == "fire_flying.png"

    def test_single_type_creates_file_on_disk(self):
        create_type_image(["water"])
        assert os.path.exists("assets/generated/water.png")

    def test_dual_type_creates_file_on_disk(self):
        create_type_image(["grass", "poison"])
        assert os.path.exists("assets/generated/grass_poison.png")

    def test_all_single_types_work(self):
        all_types = [
            "normal", "fire", "water", "electric", "grass", "ice",
            "fighting", "poison", "ground", "flying", "psychic",
            "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"
        ]
        for type_name in all_types:
            result = create_type_image([type_name])
            assert result.filename == f"{type_name}.png"
