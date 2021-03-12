import sys
import argparse
import datetime
import distutils.spawn
import subprocess
import youtube_dl
import youtubesearchpython as ysp

def search_youtube(query=None, limit=5, search_result=None):
    if not search_result:
        search_result = ysp.VideosSearch(f"{query}", limit=limit)
    search_info = search_result.result()["result"]

    vid_infos = {result["title"]:result["link"] for result in search_info}
    return vid_infos, search_result

def get_next_results(search_result):
    search_result.next()
    return search_result

def get_video_info(url, quality):
    ydl_opts = {"format":f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(url, download=False)
    print(f"[yt-vlc] {results['format']}")
    return results

def play_media(video, audio):
    vlc_path = get_vlc_path()
    subprocess.Popen([vlc_path, video, f"--input-slave={audio}"])

def get_vlc_path():
    if sys.platform.startswith("win32"):
        return distutils.spawn.find_executable("vlc.exe")
    elif sys.platform.startswith("linux"):
        return "vlc"
    elif sys.platform.startswith("darwin"):
        return "/Applications/VLC.app/Contents/MacOS/VLC"

def print_info(to_print_info, to_print_aud_vid, results):
    if to_print_info:
        url_info = ["title", "view_count", "duration", "uploader", "upload_date", "thumbnail"]
        print()
        for item in url_info:
            description = item.upper().replace('_', ' ')
            info = results[f"{item}"]

            if item == "duration" or item == "upload_date":
                info = format_info(info, item)
            print(f"[{description}] {info}")

    if to_print_aud_vid:
        video, audio = results["requested_formats"]
        print()
        print(f"[VIDEO STREAM URL] {video['url']}")
        print()
        print(f"[AUDIO STREAM URL] {audio['url']}")

def format_info(information, format_type):
    if format_type == "duration":
        info = str(datetime.timedelta(seconds=int(information)))
        for char in info:
            if char != "0" and char != ":":
                info = info[info.index(char):]
                if len(info) == 2:
                    info = f"0:{info}"
                elif len(info) == 1:
                    info = f"0:0{info}"
                break
        return info
    elif format_type == "upload_date":
        return f"{information[:4]}/{information[4:6]}/{information[6:]}"

def add_arg_parse():
    parser = argparse.ArgumentParser(description="MAIN YT-VLC")
    parser.add_argument("url", type=str, help="Youtube URL")
    parser.add_argument("-q", metavar="quality", type=str, default="360p", 
                        help="Youtube video quality (default 360p)")
    parser.add_argument("-x", default=False, action="store_true", 
                        help="Flag to not play the Youtube stream url in VLC (for testing purposes)")
    parser.add_argument("-i", default=False, action="store_true", 
                        help="Prints information about the Youtube url")
    parser.add_argument("-av", default=False, action="store_true", 
                        help="Prints the audio and video Youtube stream url")

    return parser.parse_args()

def main():
    args = add_arg_parse()
    url = args.url
    quality = args.q.replace("p", "")
    to_unplay = args.x
    to_print_info = args.i
    to_print_aud_vid = args.av

    results = get_video_info(url, quality)
    print_info(to_print_info, to_print_aud_vid, results)

    if not to_unplay:
        video, audio = results["requested_formats"]
        play_media(video["url"], audio["url"])

if __name__ == "__main__":
    main()
