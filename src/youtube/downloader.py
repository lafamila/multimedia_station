import json
import yt_dlp
import os
import ffmpeg
import pymysql
from urllib.parse import urlparse, parse_qs
from datetime import datetime


def download(url: str):
    ydl_opts = {
        'format': 'bestvideo*+bestaudio/best',
        # 'paths': {"*" : os.path.abspath("./files/")}
    }
    conn = pymysql.connect(host='localhost', user='root', password='P@ssw0rd', db='multimedia')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    
    query = parse_qs(urlparse(url).query)
    if not query.get('v', []):
        raise Exception(f"Invalid url '{url}'")
    
    row = {"display_id" : query['v'][0]}
    raw = curs.execute("SELECT * FROM youtube WHERE display_id=%(display_id)s", row)
    if not raw:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # json_path = os.path.join("./files/", datetime.now().strftime("%Y%m%d_%H%M%S.json"))
            json_path = datetime.now().strftime("%Y%m%d_%H%M%S.json")
            row['url'] = url
            row['json_path'] = json_path
            row['status_code'] = 'JSON'
            row['output_path'] = ''
            row['title'] = ''
            with open(json_path, "w") as f:
                json.dump(info, f)
            curs.execute("INSERT INTO youtube VALUES (%(display_id)s, %(url)s, %(json_path)s, %(status_code)s, %(output_path)s, %(title)s)", row)
            conn.commit()
    else:
        row = curs.fetchone()
    
    if row['status_code'] == 'JSON':
        with open(row['json_path'], "r") as f:
            data = json.load(f)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                row.update({"status_code" : "DOWNLOADING"})
                curs.execute("UPDATE youtube SET status_code=%(status_code)s WHERE display_id=%(display_id)s", row)
                conn.commit()
                error_code = ydl.download_with_info_file(row['json_path'])
                row.update({"status_code": "DOWNLOADED"})
                curs.execute("UPDATE youtube SET status_code=%(status_code)s WHERE display_id=%(display_id)s", row)
                conn.commit()
            if data['ext'] == 'webm':
                row.update({"status_code": "CONVERTING"})
                curs.execute("UPDATE youtube SET status_code=%(status_code)s WHERE display_id=%(display_id)s", row)
                conn.commit()
                filename = f"{data['fulltitle']} [{data['display_id']}].{data['ext']}"
                _filename = f"{data['fulltitle']} [{data['display_id']}].mp4"
                ffmpeg.input(filename).output(_filename).run()
                output_path = datetime.now().strftime("%Y%m%d_%H%M%S.mp4")
                os.rename(_filename, output_path)
                row.update({"status_code": "DONE", "output_path" : output_path, "title": _filename})
                curs.execute("UPDATE youtube SET status_code=%(status_code)s, output_path=%(output_path)s, title=%(title)s WHERE display_id=%(display_id)s", row)
                conn.commit()
            else:
                filename = f"{data['fulltitle']} [{data['display_id']}].{data['ext']}"
                output_path = datetime.now().strftime(f"%Y%m%d_%H%M%S.{data['ext']}")
                os.rename(filename, output_path)
                row.update({"status_code": "DONE", "output_path" : output_path, "title": filename})
                curs.execute("UPDATE youtube SET status_code=%(status_code)s, output_path=%(output_path)s, title=%(title)s WHERE display_id=%(display_id)s", row)
                conn.commit()
    
