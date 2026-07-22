#!/usr/bin/env bash
set -euo pipefail

urls=(
   "https://www.youtube.com/watch?v=iuCp-TC_HsI" 
)

for url in "${urls[@]}"; do
  echo "=============================="
  echo "下載：$url"

  downloaded_file="$(
    yt-dlp \
      -f ba \
      --audio-format m4a \
      -o "%(title)s.%(ext)s" \
      --print after_move:filepath \
      "$url"
  )"

  if [[ -z "$downloaded_file" ]]; then
    echo "錯誤：沒有取得下載檔名" >&2
    continue
  fi

  if [[ ! -f "$downloaded_file" ]]; then
    echo "錯誤：找不到檔案：$downloaded_file" >&2
    continue
  fi

  echo "轉錄：$downloaded_file"

  python direct_m4a_to_text.py "$downloaded_file" zh

  echo "完成：$downloaded_file"
done

echo "=============================="
echo "全部下載與轉錄完成"
