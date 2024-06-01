#!/bin/bash

cd docs
outfile="./.vitepress/config.mts"

function list_files() {
  dirpath=$1
  prefix=$2
  result=""
  
  for f in "${dirpath}"*; do
    if [[ "${f}" != *"public"* ]] && [[ "${f}" != *"/."* ]]; then
      if [[ -d "${f}" ]]; then
        local subdir_result
        subdir_result=$(list_files "${f}/" "$prefix  ")
        result+="${prefix}{ text: '$(basename "${f}")', collapsed: false, items: [\n$subdir_result${prefix}],\n${prefix}},\n"
      elif [[ -f "${f}" ]]; then
        f_dir=$(dirname "${f}" | sed 's/^.\///' | sed 's/^docs\///')
        f_name=$(basename "${f}" .md)
        result+="${prefix}{ text: \"$f_name\", link: '/$f_dir/$f_name' },\n"
      fi
    fi
  done

  echo -e "$result"
}

echo "import { defineConfig } from 'vitepress'
export default defineConfig({
  title: \"ヰ世界製歌\",
  description: \"isekaiuta\",
  themeConfig: {
    logo: '/favicon.ico',
    nav: [
      { text: 'ヰ世界製菓', link: 'https://z46.icu/' },
    ],
    sidebar: [" > "./.vitepress/config.mts"

list_files "${dir}" "      " >> "./.vitepress/config.mts"

echo "  ],
    socialLinks: [
      { icon: 'twitter', link: 'https://github.com/vuejs/vitepress' },
    ],
    search: {
      provider: 'local',
    },
  },
})" >> "./.vitepress/config.mts"