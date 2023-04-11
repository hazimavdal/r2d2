import os
import requests
from tqdm import tqdm


class ZoomClient:
    def __init__(self, root, account_id, client_id, client_secret):
        self.root = root
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret

        try:
            with open(self.token_filename(), "r") as f:
                self.token = f.read()
                self.validate_token(self.token)
        except Exception as e:
            print(f"token check failed: {e}")
            self.token = None

        if self.token is None:
            self.token = self.get_token()
            with open(self.token_filename(), "w") as f:
                f.write(self.token)

    def token_filename(self) -> str:
        return os.path.join(self.root, ".zoom_token")

    def get(self, path, headers={}, params={}):
        endpoint = f"https://api.zoom.us/v2/{path.lstrip('/')}"
        headers = {'Authorization': f'Bearer {self.token}', **headers}
        response = requests.get(endpoint, headers=headers, params=params)

        if not response.ok:
            raise IOError(f"{response.status_code}: {response.text}")

        return response.json()

    def download(self, download_url, output_file_path):
        try:
            headers = {"Authorization": "Bearer " + self.token}
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type')
            if not content_type or 'application/octet-stream' not in content_type:
                raise ValueError(f"Invalid content type: {content_type}")

            total_size = int(response.headers.get('Content-Length', 0))
            block_size = 8192
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
            with open(output_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    progress_bar.update(len(chunk))

            progress_bar.close()

        except (requests.RequestException, ValueError) as err:
            print(f"Error downloading recording: {err}")

    def validate_token(self, access_token):
        url = 'https://api.zoom.us/oauth/check_token'
        params = {'token': access_token}
        auth = (self.client_id, self.client_secret)
        response = requests.post(url, params=params, auth=auth)

        if not response.ok:
            raise IOError(f"{response.status_code}: {response.text}")

    def get_token(self):
        url = "https://zoom.us/oauth/token"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        params = {
            "grant_type": "account_credentials",
            "account_id": self.account_id
        }

        auth = (self.client_id, self.client_secret)

        response = requests.post(url, headers=headers, params=params, auth=auth)

        access_token = response.json()["access_token"]

        return access_token

    def meeting_recordings(self, meeting_id):
        return self.get(f"meetings/{meeting_id}/recordings")
