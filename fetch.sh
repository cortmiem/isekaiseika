#!/bin/bash
url=$1

user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

html_content=$(curl -s -A "$user_agent" "$url")

hiragana_content=$(echo "$html_content" | xmllint --html --xpath '//*[@class="hiragana"]' - 2>/dev/null)

artist_name=$(echo "$html_content" | grep -oP 'cf_page_artist = "\K[^"]*')
song_name=$(echo "$html_content" | grep -oP 'cf_page_song = "\K[^"]*')

converted_content=$(echo "$hiragana_content" | 
        sed -e 's|<span class="ruby"><span class="rb">|<ruby>|g' \
            -e 's|</span><span class="rt">|<rt>|g' \
            -e 's|</span></span>|</rt></ruby>|g' \
            -e 's|<div class="hiragana">||' -e 's|</div>||' \
            -e 's/^[ \t]*//;s/[ \t]*$//' \
            -e '1s/.*/<lyric>/' -e '$ a\<\/lyric>' \
            -e '/^$/d' \
            -e '1i# '"$song_name"'\n---')

mkdir -p "/mnt/c/Users/Cortmiem/Desktop/isekaiuta/$artist_name"
echo "$converted_content" > "/mnt/c/Users/Cortmiem/Desktop/isekaiuta/$artist_name/$song_name.md"
