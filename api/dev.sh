watchmedo shell-command \
 --patterns="*.py" \
 --command='python "${watch_src_path}"' \
 .