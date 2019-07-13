from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
from functools import partial
from html import unescape
from urllib.parse import unquote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os, re, time
from lib import utils

class ArtStationAPI:

    threads = cpu_count() * 3
    download_chunk_size = 1048576

    def __init__(self):
        self.session = requests.Session()
        # retry when exceed the max request number
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def request(self, method, url, **kwargs):
        if method == "GET":
            res = self.session.get(url, **kwargs)
        elif method == "POST":
            res = self.session.post(url, **kwargs)
        res.raise_for_status()
        return res

    def artist(self, artist_id):
        res = self.request("GET", f"https://{artist_id}.artstation.com")
        html = unescape(res.text)
        data = {
            "url": res.url,
            "name": re.search(r"\"og:title\" content=\"(.+)\"", html)[1],
            "description": re.search(r"\"og:description\" content=\"(.+)\"", html)[1],
            "projects": re.findall(r"href=\"/projects/(.+?)\"", html)
        }
        return data
    
    def artwork(self, artwork_id):
        res = self.request("GET", f"https://www.artstation.com/projects/{artwork_id}.json")
        return res.json()

    def artist_artworks(self, artist_id, dir_path):
        artist = self.artist(artist_id)
        artworks = []
        file_names = utils.file_names(dir_path, pattern=r"-(\d+)\.(.+)$")
        with ThreadPool(self.threads) as pool:
            for artwork in pool.imap(self.artwork, artist["projects"]):
                for a in artwork["assets"]:
                    if str(a["id"]) in file_names:
                        pool.terminate()
                        break
                else:
                    artworks.append(artwork)
                    continue
                break
        return artworks

    def save_artwork(self, dir_path, artwork):
        file = {
            "id": [artwork["hash_id"]],
            "title": [artwork["title"]],
            "urls": [],
            "names": [],
            "count": 0,
            "size": 0
        }
        for a in artwork["assets"]:
            file["urls"].append(a["image_url"])
            res = self.request("GET", a["image_url"], stream=True)
            file_name = re.match(r".+/(.+)\?\d+", a["image_url"])[1]
            file_name = unquote(file_name)
            file_name = re.sub(r"\.(.+)$", rf"-{a['id']}.\1", file_name)
            file["names"].append(file_name)
            with open(os.path.join(dir_path, file_name), "wb") as f:
                for chunk in res.iter_content(chunk_size=self.download_chunk_size):
                    f.write(chunk)
                    file["size"] += len(chunk)
                file["count"] += 1
            print(f"download image: {artwork['title']} ({file_name})")
        return file

    def save_artist(self, artist_id, dir_path):
        artist_name = self.artist(artist_id)["name"]
        print(f"download for artist {artist_name} begins\n")
        dir_path = utils.make_dir(dir_path, artist_id)
        artworks = self.artist_artworks(artist_id, dir_path)
        if not artworks:
            print(f"artist {artist_name} is up-to-date\n")
            return
        with ThreadPool(self.threads) as pool:
            files = pool.map(partial(self.save_artwork, dir_path), artworks)
        print(f"\ndownload for artist {artist_name} completed\n")
        combined_files = utils.counter(files)
        utils.file_mtimes(combined_files["names"], dir_path)
        return combined_files

    def save_artists(self, artist_ids, dir_path):
        print(f"\nthere are {len(artist_ids)} artists\n")
        result = []
        for id in artist_ids:
            files = self.save_artist(id, dir_path)
            if not files:
                continue
            result.append(files)
        return utils.counter(result)