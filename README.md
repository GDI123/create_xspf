Create VLC playlist for all [**RadioRecord**](https://radiorecord.ru) stations. Script will get stations list directly from RadioRecord website and fill Title, Album (as station description), Logo image, Stream URL for 320 bps and URL to station web page.

Running script without arguments will create **rr_stations.xspf** in current folder.

You can add full path for output file.

    $ create_xspf.py new_stations.xspf

I recommend to open resulted XSPF file in VLC and then save it again from VLC. In this case all station logos will be saved locally.

I use https://github.com/chitraanshpopli/create-vlc-playlist as starting point.

More info about XSPF format [here](https://www.xspf.org/xspf-v1.html) and [here](https://wiki.videolan.org/XSPF)
