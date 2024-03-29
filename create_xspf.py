from _datetime import datetime
import json
import os
import shutil
import sys
import urllib.request as req
import xml.etree.ElementTree as ET


class Playlist:
    """Build xml playlist."""

    def __init__(self):
        # Defines basic tree structure.
        self.playlist = ET.Element('playlist')
        self.tree = ET.ElementTree(self.playlist)
        self.playlist.set('xmlns', 'http://xspf.org/ns/0/')
        self.playlist.set('xmlns:vlc', 'http://www.videolan.org/vlc/playlist/ns/0/')
        self.playlist.set('version', '1')

        self.title = ET.Element('title')
        self.playlist.append(self.title)
        self.title.text = 'Playlist'

        self.trackList = ET.Element('trackList')
        self.playlist.append(self.trackList)

    def add_track(self, path, title_='', album_='', image_url_='', genre_='', share_url_=''):
        # Add tracks to xml tree (within trackList).
        track = ET.Element('track')
        location = ET.SubElement(track, 'location')
        location.text = path
        # track.append(location)
        if title_ != '':
            title = ET.SubElement(track, 'title')
            title.text = title_
        if album_ != '':
            album = ET.SubElement(track, 'album')
            album.text = album_
        if image_url_ != '':
            image_url = ET.SubElement(track, 'image')
            image_url.text = image_url_
        if genre_ != '':
            genre_str = genre_
            genre = ET.SubElement(track, 'annotation')
            genre.text = genre_str
        if share_url_ != '':
            share_url = ET.SubElement(track, 'info')
            share_url.text = share_url_
        self.trackList.append(track)

    def get_playlist(self):
        # Return complete playlist with tracks.
        return self.playlist


def create_pl(outfile):
    playlist = Playlist()
    url = 'https://radiorecord.ru/api/stations'
    # we will work as Mozilla, because user-agent python 3.x caused error 403
    headers = {'User-Agent': 'Mozilla/5.0'}
    reg_val = req.Request(url, headers=headers)
    with req.urlopen(reg_val) as url:
        data = json.loads(url.read().decode())
        for station in data['result']['stations']:
            icon_url = station['icon_fill_colored'].split('?')[0]
            genres = []
            for genre in station['genre']:
                genres.append(genre['name'])
            genres_str = ', '.join(genres)
            playlist.add_track(station['stream_320'], station['title'], station['tooltip'],
                               icon_url, genres_str, station['shareUrl'])
    ET.indent(playlist.tree, "\t", level=0)
    playlist_xml = playlist.get_playlist()
    playlist.tree.write(outfile,
                        xml_declaration=True, encoding='utf-8',
                        method='xml')


def copy_rename_file(file_path):
    if os.path.exists(file_path):
        filename, file_extension = os.path.splitext(file_path)
        current_time = datetime.now().strftime('%Y%m%d')
        file_number = 0
        for file_number in range(100):
            if file_number == 0:
                new_file_name = f'{filename}_{current_time}{file_extension}.bak'
            else:
                new_file_name = f'{filename}_{current_time}({file_number}){file_extension}.bak'
            if not os.path.exists(new_file_name):
                shutil.copy(file_path, new_file_name)
                print(f'Old playlist saved as: {new_file_name}')
                return 1
            else:
                file_number += 1

        print('We already create 100 backups of playlists: to continue delete some old backups or try again tomorrow.')
        return -1
    else:
        # print('The file does not exist')
        return 0


def parse_file(file_path):
    try:
        root = ET.parse(file_path).getroot()
        titles = []
        for track in root.iter():
            if 'title' in track.tag:
                titles.append(track.text)
        return titles
    except FileNotFoundError:
        # print(f'File {file_path} not found')
        return []
    except Exception as e:
        print(f'An error occurred while parsing the file: {str(e)}')
        return []


def compare_lists(old_list, new_list):
    added_items = [item for item in new_list if item not in old_list]
    removes_items = [item for item in old_list if item not in new_list]
    return added_items, removes_items


def print_stations(old_list, new_list):
    added, removed = compare_lists(old_list, new_list)
    if not added and not removed:
        print('No new stations found')
    else:
        if added:
            print('New stations:')
            for station in added:
                print('\t', station)
        if removed:
            print('Removed stations:')
            for station in removed:
                print('\t', station)


def main():
    outfile = 'rr_stations.xspf'
    if len(sys.argv) > 1:
        if sys.argv[1] != '':
            outfile = sys.argv[1]

    result = copy_rename_file(outfile)
    if result == -1:
        return -1
    old_list = parse_file(outfile)
    create_pl(outfile)
    new_list = parse_file(outfile)
    print('Playlist created in file ' + outfile)
    print_stations(old_list, new_list)


if __name__ == '__main__':
    main()

