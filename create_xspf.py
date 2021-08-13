import json
import urllib.request as req
import xml.etree.ElementTree as ET
import sys


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
            genre_str = ", ".join(genre_)
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
    with req.urlopen("https://radiorecord.ru/api/stations") as url:
        data = json.loads(url.read().decode())
        for station in data['result']['stations']:
            genres = []
            for genre in station['genre']:
                genres.append(genre['name'])
            playlist.add_track(station['stream_320'], station['title'], station['tooltip'],
                               station['icon_fill_colored'], genres, station['shareUrl'])
    ET.indent(playlist.tree, "\t", level=0)
    playlist_xml = playlist.get_playlist()
    playlist.tree.write(outfile,
                        xml_declaration=True, encoding='utf-8',
                        method="xml")


def main():
    outfile = 'rr_stations.xspf'
    if len(sys.argv) > 1:
        if sys.argv[1] != '':
            outfile = sys.argv[1]
    create_pl(outfile)
    print("Playlist created in file "+outfile)
    print("Done.")


if __name__ == '__main__':
    main()
