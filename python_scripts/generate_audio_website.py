import os
from ffxiv_aku import convert_png_to_webp

template = """<div class="container2">
    <h1>Audio Library</h1>
    <input type='text' id='search' class='search-bar' placeholder='Search for a song...' onkeyup='filterAlbums()'>
    <div class='innercontainer'>
        {content}
    </div>
</div>
<style>
    .container2 { display: block; text-align: center;}
    .search-bar { margin: 20px; padding: 10px; width: 80%; max-width: 400px; border-radius: 5px; border: none; }
    .innercontainer { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; color: #ffffff; }
    @media screen and (max-width: 1024px) { .innercontainer > .album { width: 45% !important; height: auto !important; max-height: 500px !important} .innercontainer > .album > img { height: 300px !important; }}
    @media screen and (max-width: 768px)  { .innercontainer > .album { width: 90% !important; height: auto !important; max-height: 500px !important} .innercontainer > .album > img { height: 250px !important; }}
    .innercontainer > .album { width: 22%; min-width: 200px; max-width: 500px; height: 800px; background: #1e1e1e; border-radius: 8px; box-shadow: 0 0 10px rgba(255,255,255,0.1); padding: 10px; display: flex; flex-direction: column; align-items: center; }
    .innercontainer > .album > img { width: auto; height: 350px; object-fit: cover; border-radius: 25px; margin-bottom: 10px; }
    .innercontainer > .album > .track-container { overflow-y: auto; width: 100%; flex-grow: 1; }
    .innercontainer > .album > .track-container > ul { list-style: none; padding: 0; width: 100%; }
    .innercontainer > .album > .track-container > ul > li { text-align: left; display: block; }
    .innercontainer > .album > .track-container > h4 { text-align: left; font-size: 1.1em; text-decoration: underline; margin: 10px 0 5px; }
    .innercontainer > .album > ::-webkit-scrollbar { width: 5px; }
    .innercontainer > .album > ::-webkit-scrollbar-track { background: #958686; border-radius: 25px;}
    .innercontainer > .album > ::-webkit-scrollbar-thumb { background: #912020; border-radius: 25px; }
    .innercontainer > .album > ::-webkit-scrollbar-thumb:hover { background: #dd0505; }
    .innercontainer > .album > h3 { font-size: 1.4rem; }
</style>
<script>
    function filterAlbums() {
        let input = document.getElementById('search').value.toLowerCase();
        let albums = document.getElementsByClassName('album');

        for (let album of albums) {
            let tracks = album.getElementsByTagName('li');
            let found = false;
            for (let track of tracks) {
                if (track.innerText.toLowerCase().includes(input)) {
                    track.style.display = 'block';
                    found = true;
                } else {
                    track.style.display = 'none';
                }
            }
            album.style.display = found || input === '' ? 'block' : 'none';
        }
    }
</script>
"""

def scan_directory(base_dir: str) -> str:
    albums = []
    for entry in os.listdir(base_dir):
        entry_path = os.path.join(base_dir, entry)
        if os.path.isdir(entry_path):
            cover_path: str = os.path.join(entry_path, "cover.jpg")
            new_cover_path: str = f"..\\assets\\img\\music\\{entry}.webp"
            if not os.path.exists(new_cover_path):
                convert_png_to_webp(cover_path, new_cover_path)
            cover_path = new_cover_path
            tracks = []
            subfolders = [f for f in os.listdir(entry_path) if os.path.isdir(os.path.join(entry_path, f))]

            if subfolders:
                folder_tracks = {}
                for subfolder in subfolders:
                    sub_path = os.path.join(entry_path, subfolder)
                    folder_tracks[subfolder] = [f for f in os.listdir(sub_path) if f.endswith('.mp3')]
                albums.append((entry, cover_path if os.path.exists(cover_path) else None, folder_tracks))
            else:
                tracks = [f for f in os.listdir(entry_path) if f.endswith('.mp3')]
                if tracks:
                    albums.append((entry, cover_path if os.path.exists(cover_path) else None, {None: tracks}))

    return generate_html(albums)

def generate_html(albums: list) -> str:
    content = ""
    for album, cover, folder_tracks in albums:
        cover_img = f"<img src='{cover}' alt='{album} Cover'>" if cover else ""
        track_list = "<div class='track-container'>\n"
        for subfolder, tracks in folder_tracks.items():
            if subfolder:
                track_list += f"<h4>{subfolder}</h4>"
            track_list += "<ul>\n" + "".join(f"        <li>{track.replace('.mp3', '')}</li>\n" for track in tracks) + "</ul>"
        track_list += "</div>"
        content += f"<div class='album'><h3>{album.replace(' - ', '</br>')}</h3>{cover_img}{track_list}</div>"

    return template.replace("{content}", content)

if __name__ == "__main__":
    base_dir = os.path.dirname("W:\\Musik\\Game OST\\FFXIV (MP3)\\")
    html_content = scan_directory(base_dir)
    file = os.path.join("..", "_includes", "single_pages", "music.html")
    with open(file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"{file} has been generated successfully!")
