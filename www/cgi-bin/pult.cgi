#!/bin/bash

# IFS='=&' read -ra query <<< "$QUERY_STRING"
IFS='=&' read -ra query
declare -A query_var
for ((i = 0; i < ${#query[@]}; i += 2)); do
  query_var[${query[i]}]=${query[i + 1]}
done

channel=$(basename "$0" | egrep -o "\-[0-9]+\.cgi\$" | egrep -o "[0-9]+")
channels="$(ls /usr/local/etc/pult/pult-*.conf | egrep -o '[0-9]+')"

start_text="start"
stop_text="stop"
hide_text="hide"
show_text="show"
min_text="min"
max_text="max"

lock_file="/usr/local/var/run/pult/pultd-$channel.lock"
status_file="/usr/local/var/run/pult/pult-status-$channel"
declare -A module_status
declare -A module_info

. "/usr/local/etc/pult/pult.conf"

invoke_module ()
{
  local m="$1"
  local d="$2"
  shift 2
  local driver="$module_directory/$d.module"
  if [ -x "$driver" ]; then
    export PULT_MODULE_NAME="$m"
    export PULT_CHANNEL="$channel"
    "$driver" "$@"
  fi
}

module ()
{
  local m="$1"
  local d="$2"
  mcmd=${query_var["$m"]}
  case "$mcmd" in
    "start"|"stop")
      echo "$m $mcmd" | nc localhost "$pultd_port"
      sleep 0.2
      while [ -e "$lock_file" ]; do
        sleep 0.1
      done
      ;;
    "min"|"max"|"hide")
      echo "$m $mcmd" | nc localhost "$pultd_port"
      ;;
  esac
  shift 2
  local show_buttons=true
  local module_name="$m"
  for opt in $defaults "$@"; do
    case "$opt" in
      "nobuttons")
        show_buttons=false
        ;;
      "module_name="*)
        module_name="$(echo $opt | sed -e 's/^module_name=//')"
        ;;
    esac
  done
  if $show_buttons; then
    local module_class
    . "$status_file"
    case "${module_status[$m]}" in
      "")        module_class="module_stopped" ;;
      "running") module_class="module_running" ;;
      *)         module_class="module_transient" ;;
    esac
    echo -e "      <tr>"
    echo -e "        <td><div class=\"module_name\"><div class=\"$module_class\">$module_name</div></div></td>"
    echo -e "        <td><form action=\"pult-$channel.cgi\" method=\"post\"><input type=\"hidden\" name=\"$m\" value=\"start\"><button class=\"channel\" type=\"submit\" style=\"$start_style\">$start_text</button></form></td>"
    echo -e "        <td><form action=\"pult-$channel.cgi\" method=\"post\"><input type=\"hidden\" name=\"$m\" value=\"stop\"><button class=\"channel\" type=\"submit\" style=\"$stop_style\">$stop_text</button></form></td>"
    echo -e "        <td><form action=\"pult-$channel.cgi\" method=\"post\"><input type=\"hidden\" name=\"$m\" value=\"hide\"><button class=\"channel\" type=\"submit\" style=\"$hide_style\">$hide_text</button></form></td>"
    local min=false
    local defaults=$(invoke_module "$m" "$d" "defaults")
    for opt in $defaults "$@"; do
      case "$opt" in
        "min="*)
          eval "$opt"
          if "$min"; then
            echo -e "        <td><form action=\"pult-$channel.cgi\" method=\"post\"><input type=\"hidden\" name=\"$m\" value=\"min\"><button class=\"channel\" type=\"submit\" style=\"$min_style\">$min_text</button></form></td>"
          fi
          ;;
        "invitation="*)
          local invitation=$(echo "$opt" | sed -e 's/^invitation=//' -e "s/@INFO@/${module_info[$m]}/g")
          local status="${module_status[$m]}"
          if [ -n "$status" -a "$status" != "running" ]; then
            print_invitation="$print_invitation<center><strong>$module_name:</strong> $invitation</center>"
          fi
          ;;
        "persistent_invitation="*)
          local invitation=$(echo "$opt" | sed -e 's/^persistent_invitation=//' -e "s/@INFO@/${module_info[$m]}/g")
          local status="${module_status[$m]}"
          if [ -n "$status" ]; then
            print_invitation="$print_invitation<center><strong>$module_name:</strong> $invitation</center>"
          fi
          ;;
      esac
    done
    local max_or_show_text="$show_text"
    local max_or_show_style="$show_style"
    if "$min"; then
      max_or_show_text="$max_text"
      max_or_show_style="$max_style"
    fi
    echo -e "        <td><form action=\"pult-$channel.cgi\" method=\"post\"><input type=\"hidden\" name=\"$m\" value=\"max\"><button class=\"channel\" type=\"submit\" style=\"$max_or_show_style\">$max_or_show_text</button></form></td>"
    echo -e "      </tr>"
  fi
}

generate_pult ()
{
  cat << EOF | sed -e 's/^    //'
    Content-type: text/html

    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf8"/>
        <meta http-equiv="refresh" content="10"/>
        <link rel="stylesheet" href="/pult/stylesheets/default.css" type="text/css"/>
        <title>PULT-Kanal $channel</title>
      </head>
      <body class="panel">
        <div style="text-align: center; float: right">
          <strong style="font-size: large;">Kanal $channel</strong><br/>
          <a href="pult.cgi">
            <img src="/pult/pult-logo-192x74.png"
                 alt="PULT ULTimate Learning/Teaching Tool"/>
          </a>
        </div>
        <table>
EOF

  print_invitation=""
  . "/usr/local/var/run/pult/pult-status-$channel"
  . "/usr/local/etc/pult/pult-$channel.conf"  

  cat << EOF | sed -e 's/^    //'
        </table>
        $print_invitation
      </body>
    </html>
EOF
}

generate_chooser ()
{
  cat << EOF | sed -e 's/^    //'
    Content-type: text/html

    <!doctype html public "-//W3C//DTD HTML 4.0 Strict//EN">
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf8">
        <link rel="stylesheet" href="/pult/stylesheets/default.css" type="text/css">
        <title>PULT-Kanalauswahl</title>
      </head>
      <body class="text">
        <img src="/pult/pult-logo-192x74.png"
             alt="PULT ULTimate Learning/Teaching Tool"
             class="logo" align="right"/>
        <h1>
          PULT-Kanäle
        </h1>
        </p>
        <p>
          Bitte wählen Sie Ihren PULT-Kanal:
        </p>
        <table><tr>
          $(for i in $channels; do
              echo -e "<td><form action=\"pult-$i.cgi\"><button class=\"channel\" type=\"submit\">$i</button></form></td>"
            done)
        </tr></table>
        <p>
          Wenn Sie dieses System nutzen möchten, wenden Sie sich bitte an:<br/>
          <a href="mailto:peter.gerwinski@hs-bochum.de">Prof. Dr. Peter Gerwinski</a>.
        </p>
      </body>
    </html>
      </body>
    </html>
EOF
}

pult_generated=false
for i in $channels; do
  if [ "$channel" = "$i" ]; then
    generate_pult
    pult_generated=true
  fi
done
if ! $pult_generated; then
  generate_chooser
fi
