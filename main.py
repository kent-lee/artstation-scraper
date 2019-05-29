from argparse import ArgumentParser
import sys, os, time
from lib.artstation import ArtStationAPI
from lib.config import Config
from lib import utils

def download_artists(api, config):
    start_time = time.time()
    result = api.save_artists(config.artists, config.save_dir)
    duration = time.time() - start_time
    size_mb = result["size"] / 1048576
    print("\nSUMMARY")
    print("---------------------------------")
    print(f"time elapsed:\t{duration:.4f} seconds")
    print(f"total size:\t{size_mb:.4f} MB")
    print(f"total artworks:\t{result['count']} artworks")
    print(f"download speed:\t{(size_mb / duration):.4f} MB/s")

def commands():
    parser = ArgumentParser()
    parser.add_argument("-f", dest="file", default=os.path.join("data", "config.json"), help="set config file")
    parser.add_argument("-l", action="store_true", dest="list", help="list current settings")
    parser.add_argument("-s", dest="save_dir", help="set save directory path")
    parser.add_argument("-a", nargs="+", dest="add", metavar=("", "ID"), help="add artist ids")
    parser.add_argument("-d", nargs="+", dest="delete", metavar=("all", "ID"), help="delete artist ids and their directories")
    parser.add_argument("-c", nargs="+", dest="clear", metavar=("all", "ID"), help="clear artists directories")
    parser.add_argument("-t", dest="threads", type=int, help="set the number of threads")
    parser.add_argument("-r", action="store_true", dest="run", help="run program")
    return parser.parse_args()

def main():
    args = commands()
    api = ArtStationAPI()
    config = Config(args.file)

    if args.list:
        config.print()
    if args.save_dir:
        config.save_dir = args.save_dir
    if args.add:
        config.add_artists(args.add)
    if args.delete:
        config.delete_artists(args.delete)
    if args.clear:
        config.clear_artists(args.clear)
    if args.threads:
        api.threads = args.threads
    if len(sys.argv) == 1 or args.run:
        download_artists(api, config)
    config.update()

if __name__ == "__main__":
    main()