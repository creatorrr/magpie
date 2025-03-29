import unittest

from magpie.prepare_dataset import get_host, pluck


class TestUtils(unittest.TestCase):
    """Test utility functions from the magpie package."""

    def test_pluck(self):
        """Test the pluck lambda function."""
        test_dict = {"a": 1, "b": 2, "c": 3, "d": 4}
        result = pluck(test_dict, ["a", "c"])
        assert result == {"a": 1, "c": 3}

        # Test with keys that don't exist
        result = pluck(test_dict, ["a", "e"])
        assert result == {"a": 1}

        # Test with empty keys
        result = pluck(test_dict, [])
        assert result == {}

        # Test with empty dict
        result = pluck({}, ["a", "b"])
        assert result == {}

    def test_get_host(self):
        """Test the get_host lambda function."""
        # Test with standard URL
        url = "https://example.com/path/to/resource"
        assert get_host(url) == "example.com"

        # Test with subdomain
        url = "https://subdomain.example.com/path"
        assert get_host(url) == "subdomain.example.com"

        # Test with port
        url = "http://example.com:8080/path"
        assert get_host(url) == "example.com:8080"

        # Test with no protocol
        url = "example.com/path"
        assert get_host(url) == ""

        # Test empty string
        url = ""
        assert get_host(url) == ""


if __name__ == "__main__":
    unittest.main()
