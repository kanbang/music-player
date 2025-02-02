import os

from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from src.entity.music_list import MusicList
from src.service.MP3Parser import MP3

from src.entity.music import Music
from src.service.music_service import MusicService


class SearchLocalMusic(QObject):
    begin_search = QtCore.pyqtSignal()
    end_search = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

    @staticmethod
    # 全盘搜索
    @DeprecationWarning
    def search():
        # 以 .mp3结尾, 大于100kb的文件
        paths = set()
        # 合法的mp3文件
        musics_table = []
        pans = SearchLocalMusic.__get_exist_pan()
        for pan in pans:
            paths = SearchLocalMusic.__loop_all(pan, paths)
        musics_table = SearchLocalMusic.__get_mp3_info(paths, musics_table)
        print(len(musics_table), "  ", musics_table)
        SearchLocalMusic.__to_database(musics_table)

    def search_in_path(self, search_paths: list):
        self.begin_search.emit()
        # 以 .mp3结尾, 大于100kb的文件
        paths = set()
        # 合法的mp3文件
        musics_table = []
        for search_path in search_paths:
            paths = SearchLocalMusic.__loop_all(search_path, paths)
        musics_table = SearchLocalMusic.__get_mp3_info(list(paths), musics_table)
        self.__to_database(musics_table)
        self.end_search.emit()

    @staticmethod
    # 把搜索结果存入数据库
    def __to_database(musics_table: list):
        music_service = MusicService()
        music_service.batch_insert(musics_table)

    @staticmethod
    def __get_exist_pan():
        pan_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        exist_pan = []
        for pan in pan_list:
            if os.path.isdir(pan + ":/"):
                exist_pan.append(pan + ":/")
        return exist_pan

    @staticmethod
    # 递归遍历path下的文件, 把符合规则的文件路径加入到paths
    def __loop_all(path: str, paths: set):
        try:
            listdir = os.listdir(path)
            for f in listdir:
                if not path.endswith("/"):
                    p = path + "/" + f
                else:
                    p = path + f
                if (f.endswith("mp3") or f.endswith("MP3")) and os.path.getsize(p) > 100 * 1024:
                    paths.add(p)
                if os.path.isdir(p):
                    SearchLocalMusic.__loop_all(p, paths)
            return paths
        except PermissionError as e:
            pass

    @staticmethod
    # paths: 文件路径列表
    # musics_table: Music列表
    def __get_mp3_info(paths: list, musics_table: list):
        for path in paths:
            try:
                mp3 = MP3(path)
                if mp3.ret["has-ID3V2"] and mp3.duration >= 30:
                    size = os.path.getsize(path)
                    if size < 1024 * 1024:
                        size = str(int(size / 1024)) + "KB"
                    else:
                        size = str(round(size / 1024 / 1024, 1)) + "MB"

                    title = mp3.title
                    if title == "":
                        title = os.path.basename(path)

                    artist = mp3.artist
                    if artist == "":
                        artist = "未知歌手"

                    album = mp3.album
                    if album == "":
                        album = "未知专辑"

                    duration = mp3.duration
                    music = Music()
                    music.mid = MusicList.DEFAULT_ID
                    music.path = path
                    music.title = title
                    music.artist = artist
                    music.album = album
                    music.duration = duration
                    music.size = size
                    musics_table.append(music)
            except IndexError as e:
                pass
            except UnicodeDecodeError as e1:
                pass
        return musics_table


if __name__ == "__main__":
    pass
