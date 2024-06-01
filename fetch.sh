#!/bin/bash
set -x

url=$1

user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

html_content=$(curl -s -A "$user_agent" "$url")

hiragana_content=$(echo "$html_content" | xmllint --html --xpath '//*[@class="hiragana"]' - 2>/dev/null)

song_name=$(echo "$html_content" | grep -oP 'cf_page_song = "\K[^"]*')
artist_name=$(echo "$html_content" | grep -oP 'cf_page_artist = "\K[^"]*')

if [[ -z "$song_name" ]]; then
  exit 1
fi

converted_content=$(echo "$hiragana_content" | 
        sed -e 's|<span class="ruby"><span class="rb">|<ruby>|g' \
            -e 's|</span><span class="rt">|<rt>|g' \
            -e 's|</span></span>|</rt></ruby>|g' \
            -e 's|<div class="hiragana">||' -e 's|</div>||' \
            -e 's/^[ \t]*//;s/[ \t]*$//' \
            -e '1s/.*/<lyric>/' -e '$ a\<\/lyric>' \
            -e '/^$/d' \
            -e '1i# '"$song_name"'\n---'
            -e 's/&#13;//g' )

mkdir -p "./docs/$artist_name"
echo "$converted_content" > "./docs/$artist_name/$song_name.md"
echo $song_name - $artist_name
./update.sh