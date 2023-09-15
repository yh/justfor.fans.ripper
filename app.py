import base64
import datetime
import glob
import json
import os
import re
import shutil
import sys
import urllib.parse

import bs4
import requests
from yt_dlp import YoutubeDL

import config


class Post:
    def __init__(self, post_soup: bs4.Tag):
        self.post_soup = post_soup

        ptext = post_soup.select("div.fr-view")
        classvals = post_soup.attrs["class"]

        self.uploader_id: str = re.fullmatch(
            r"""location\.href=['"]/?(.+?)['"]""",
            post_soup.select("h5.mbsc-card-title.mbsc-bold span")[0].get("onclick"),
        ).group(1)
        self.post_date_str = post_soup.select("div.mbsc-card-subtitle")[0].text.strip()
        # Stripping "burning post" alert
        self.post_date_str = self.post_date_str.split("This post will disappear")[
            0
        ].strip()
        self.post_id = base64.b64decode(post_soup.attrs["data-pid"]).decode()
        self.full_text = ptext[0].text.strip() if ptext else ""
        self.tags = list(
            x.text.strip().strip("#") for x in post_soup.select("div.postTags a")
        )
        self.access_control = next(
            (
                x[len("AccessControl-") :]
                for x in classvals
                if x.startswith("AccessControl-")
            ),
            None,
        )

        self.store_url = None

        self.type = None
        if "shoutout" in classvals:
            self.type = "shoutout"
        elif "video" in classvals:
            self.type = "video"
        elif "photo" in classvals:
            self.type = "photo"
        elif "text" in classvals:
            self.type = "text"

        store_button = post_soup.select("div.storeItemWidget button")
        if len(store_button) > 0:
            store_url = re.fullmatch(
                r"""location\.href=['"]/?(.+?)['"]""", store_button[0].get("onclick")
            ).group(1)
            self.store_url = urllib.parse.urljoin("https://justfor.fans/", store_url)

        dt_format = "%B %d, %Y, %I:%M %p"
        dt = datetime.datetime.strptime(self.post_date_str, dt_format)
        self.post_date = dt.strftime("%Y-%m-%d")
        self.post_date_iso = dt.isoformat()
        self.excerpt = self.full_text
        self.excerpt = re.sub(r'[\\\/:*?"<>|\s]', " ", self.excerpt)
        self.excerpt = re.sub(r"\s{2,}", " ", self.excerpt).strip()

        basename = (
            config.file_name_format.replace("{name}", self.uploader_id)
            .replace("{post_date}", self.post_date)
            .replace("{post_id}", self.post_id)
            .replace("{desc}", self.excerpt)
        )
        basename = basename.strip().encode('utf-8')

        if len(basename) >= 140:
            i = basename.rfind(b' ', 0, 140)
            if i == -1:
                i = 140
            basename = basename[:i] + b'...'

        self.basename = basename.decode('utf-8')


def create_folder(post: Post) -> str:
    fpath = os.path.join(config.save_path, post.uploader_id, post.type)
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    return fpath


def photo_save(post: Post):
    photos_url = []

    photos_img = post.post_soup.select("div.imageGallery.galleryLarge img.expandable")

    if len(photos_img) == 0:
        photos_img.append(post.post_soup.select("img.expandable")[0])

    for i, img in enumerate(photos_img):
        if "src" in img.attrs:
            imgsrc = img.attrs["src"]
        elif "data-lazy" in img.attrs:
            imgsrc = img.attrs["data-lazy"]
        else:
            # print("no image source, skipping")
            continue
        ext = imgsrc.split(".")[-1]

        folder = create_folder(post)
        ppath = ".".join(
            [os.path.join(folder, "{}.{:02}".format(post.basename, i)), ext]
        )

        exists = len(glob.glob(os.path.join(folder, post.basename[:50]) + '*.{:02}.{}'.format(i, ext))) > 0
        if not config.overwrite_existing and exists:
            # print(f'p: <<exists skip>>: {ppath}')
            continue

        photos_url.append((ppath, imgsrc))

    for img in photos_url:
        ppath, imgsrc = img
        tmp_ppath = ppath + ".tmp"

        try:
            response = requests.get(imgsrc, stream=True)
            # print("Downloading " + str(round(int(response.headers.get('content-length'))/1024/1024, 2)) + " MB")
            with open(tmp_ppath, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            os.rename(tmp_ppath, ppath)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            import traceback

            print(traceback.format_exc())


def video_save(post: Post):
    folder = create_folder(post)
    vpath = os.path.join(folder, post.basename) + ".mp4"

    exists = len(glob.glob(os.path.join(folder, post.basename[:50]) + '*.ytdl')) == 0 and len(glob.glob(os.path.join(folder, post.basename[:50]) + '*.mp4')) > 0
    if not config.overwrite_existing and exists:
        return

    try:
        videoBlock = post.post_soup.select("div.videoBlock a")
        if len(videoBlock) == 0:
            if post.store_url is None:
                print("Get video URL failed: %s" % post.basename[:30])
            else:
                print("Store post: %s" % post.basename[:30])
            return
        vidurljumble = videoBlock[0].attrs["onclick"]
        vidurl = json.loads(vidurljumble.split(", ")[1])

        url = vidurl.get("1080p", "")
        url = vidurl.get("540p", "") if url == "" else url

        # print(f'v: {vpath}')
        # print(url)

        print("Downloading %s" % post.basename[:30])
        ydl_opts = {
            'retries': 10,
            'updatetime': True,
            'noprogress': True,
            'concurrent_fragment_downloads': 3,
            'outtmpl': vpath,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        import traceback

        print(traceback.format_exc())


def text_save(post: Post):
    folder = create_folder(post)
    tpath = os.path.join(folder, post.basename) + ".txt"

    exists = len(glob.glob(os.path.join(folder, post.basename[:50]) + '*.txt')) > 0
    if not config.overwrite_existing and exists:
        return

    # print(f't: {tpath}')

    with open(tpath, "w", encoding="utf-8") as file:
        file.write("---\n")
        file.write("id: %s\n" % post.post_id)
        file.write("date: %s\n" % post.post_date_iso)
        file.write("tags: %s\n" % ", ".join(post.tags))
        if post.access_control is not None:
            file.write("access_control: %s\n" % post.access_control)
        if post.store_url is not None:
            file.write("store_url: %s\n" % post.store_url)
        file.write("---\n\n")
        file.write(post.full_text)

        file.close()


def parse_and_get(html_text: str):
    soup = bs4.BeautifulSoup(html_text, "html.parser")

    for pp in soup.select("div.mbsc-card.jffPostClass"):
        try:
            if "donotremove" in pp.get("class"):
                # Skip "Whom To Follow"
                continue

            post = Post(pp)

            if post.type == "shoutout":
                # Skip "Shoutout Post"
                continue
            elif post.type == "video":
                video_save(post)
                if config.save_full_text:
                    text_save(post)
            elif post.type == "photo":
                photo_save(post)
                if config.save_full_text:
                    text_save(post)
            elif post.type == "text":
                if config.save_full_text:
                    text_save(post)

        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            import traceback

            print(traceback.format_exc())
            # print(pp.prettify())


def get_html(loopct: int) -> str:
    geturl = config.api_url.format(
        userid=uid, poster_id=poster_id, seq=loopct, hash=hsh
    )
    html_text = requests.get(geturl).text
    return html_text


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        uid = sys.argv[1]
        hsh = sys.argv[2]
        print("(%s) Using uid and hash from command line parameters" % uid)

    if len(sys.argv) >= 4:
        poster_id = sys.argv[3]
    else:
        uid = config.uid
        hsh = config.hsh
        if uid == "" or hsh == "":
            print(
                "Specify UserID and UserHash4 in the config file or in the command line parameters and restart program. Aborted."
            )
            sys.exit(0)
        else:
            print("(%s) Using uid and hash from config file..." % uid)

    loopit = True
    loopct: int = 0
    while loopit:
        html_text = get_html(loopct)

        if "as sad as you are" in html_text:
            print("(%s) No more posts to parse. Exiting." % uid)
            print(
                "If program is not downloaded any files, your token is expired or invalid. Get a new one."
            )
            loopit = False
        else:
            parse_and_get(html_text)
            loopct += 10
