#!/bin/bash
set -x

url=$1

user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

html_content=$(curl -s -A "$user_agent" "$url")

song_name=$(echo "$html_content" | perl -ne 'if (/<span id="SongName" style="display:none;">(.*?)<\/span>/) { print $1 }')
artist_name=$(echo "$html_content" | perl -ne 'if (/<span id="Singer" style="display:none;">(.*?)<\/span>/) { print $1 }')

if [[ -z "$song_name" ]]; then
  exit 1
fi

converted_content=$(echo "$html_content" | grep -Po '(?<=<span class="LyricsYomi notranslate").*?(?=</span>)' | perl -pe 's/(.*?>)//; s/$/<br\/>/' | sed -e '1s/.*/<lyric>/' -e '$ a\<\/lyric>' -e '1i# '"$song_name"'\n---')

mkdir -p "./docs/$artist_name"

echo "$converted_content" > "./docs/$artist_name/$song_name.md"
echo $song_name - $artist_name
./update.sh