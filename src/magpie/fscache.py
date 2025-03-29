import os
import time
from urllib.parse import urlparse


class FSCache:
    def __init__(self):
        pass

    def path(self, url: str, cache_dir: str = ".fscache") -> str:
        """
        Generate a file path for caching the URL content.

        Args:
            url: The URL to cache
            cache_dir: The cache directory to use

        Returns:
            The full path where the cached file should be stored
        """
        # Parse URL components
        parsed = urlparse(url)

        # Create path components
        scheme = parsed.scheme
        netloc = parsed.netloc
        path = parsed.path

        # Handle query parameters if they exist
        if parsed.query:
            # Encode query params in the path
            path = f"{path}_{parsed.query}"

        # Create the cache path
        components = [cache_dir, scheme, netloc]

        # Add path components, removing leading slash
        if path:
            components.extend(path.strip("/").split("/"))

        # Ensure the path is clean and has proper extension
        return os.path.join(*components)

    def valid(self, cache_path: str, lifetime: int = 3600) -> bool:
        """
        Check if a cached file exists and is still valid based on lifetime.

        Args:
            cache_path: Path to the cached file
            lifetime: Cache lifetime in seconds

        Returns:
            True if cache is valid, False otherwise
        """
        if not os.path.exists(cache_path):
            return False

        # Check if cache is expired
        modified_time = os.path.getmtime(cache_path)
        current_time = time.time()

        return (current_time - modified_time) < lifetime

    def load(self, cache_path: str) -> str:
        """
        Load content from a cached file.

        Args:
            cache_path: Path to the cached file

        Returns:
            The cached content as a string
        """
        with open(cache_path, encoding="utf-8") as f:
            return f.read()

    def save(self, cache_path: str, content: str) -> None:
        """
        Save content to a cache file.

        Args:
            cache_path: Path to the cached file
            content: Content to save
        """
        # Create directory structure if it doesn't exist
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(content)


# Create a singleton instance
fscache = FSCache()
