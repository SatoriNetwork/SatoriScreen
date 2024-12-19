import urequests
import os

class GitHubUpdater:
    def __init__(self, libraries):
        """
        Initializes the GitHubUpdater with the required libraries.
        :param libraries: Dictionary of library names and their GitHub raw URLs.
        """
        self.libraries = libraries

    def download_library(self, lib_name, url):
        """
        Downloads a library from the given URL.
        :param lib_name: Name of the library to save locally.
        :param url: URL to download the library from.
        """
        try:
            print(f"Downloading library '{lib_name}' from {url}...")
            response = urequests.get(url)
            
            # Check if the response was successful and has data
            if response.status_code == 200 and response.content:
                
                    temp_filename = f"{lib_name}.tmp"

                    # Write to a temporary file first
                    with open(temp_filename, "wb") as f:
                        f.write(response.content)
                    
                    # Rename the temporary file to the target file
                    os.rename(temp_filename, f"{lib_name}.py")
                    print(f"Library '{lib_name}' downloaded successfully.")
                
            else:
                print(f"Failed to download '{lib_name}'. HTTP Status Code: {response.status_code} or no content received.")
        except Exception as e:
            print(f"Error downloading '{lib_name}': {e}")
        finally:
            # Close the response to free resources
            if 'response' in locals() and response:
                response.close()

    def check_and_download_libraries(self):
        """
        Checks if libraries are installed. If not, downloads them.
        """
        for lib, url in self.libraries.items():
            
            
                print(f"Library '{lib}' Downloading...")
                self.download_library(lib, url)
                try:
                    __import__(lib)  # Attempt to import the library after downloading
                    print(f"Library '{lib}' imported successfully after downloading.")
                except ImportError:
                    print(f"Failed to import '{lib}' even after downloading.")


