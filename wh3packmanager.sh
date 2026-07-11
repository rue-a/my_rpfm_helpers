#!/bin/bash

WORKSHOP="$HOME/.local/share/Steam/steamapps/workshop/content/1142710"
GAME_DATA="$HOME/.local/share/Steam/steamapps/common/Total War WARHAMMER III/data"
SCHEMA="$HOME/WH3-Mods/rpfm-schemas/schema_wh3.ron"

#################################################
# Command descriptions
#################################################

cmd_browse_workshop_desc="Browse Steam Workshop packs and extract one"
cmd_browse_data_desc="Browse base game packs and extract one"
cmd_repack_desc="Repack a folder into a .pack file"
cmd_list_desc="List available pack files"

#################################################
# Help system
#################################################

show_help() {

    if [ -z "$1" ]; then
        echo
        echo "wh3packmanager — Total War Warhammer III pack helper"
        echo
        echo "Usage:"
        echo "  wh3packmanager <command> [args]"
        echo
        echo "Commands:"
        printf "  %-18s %s\n" "browse_workshop" "$cmd_browse_workshop_desc"
        printf "  %-18s %s\n" "browse_data" "$cmd_browse_data_desc"
        printf "  %-18s %s\n" "repack <folder>" "$cmd_repack_desc"
        printf "  %-18s %s\n" "list <data|workshop>" "$cmd_list_desc"
        echo
        echo "Run 'wh3packmanager help <command>' for details."
        echo
        return
    fi

    case "$1" in

        browse_workshop)
            echo
            echo "wh3packmanager browse_workshop"
            echo
            echo "Browse Steam Workshop .pack files using fzf and extract one."
            echo
            echo "WH3 workshop path:"
            echo "  $WORKSHOP"
            echo
            ;;

        browse_data)
            echo
            echo "wh3packmanager browse_data"
            echo
            echo "Browse base game .pack files using fzf and extract one."
            echo
            echo "WH3 game data path:"
            echo "  $GAME_DATA"
            echo
            ;;

        repack)
            echo
            echo "wh3packmanager repack <folder>"
            echo
            echo "Create a .pack file from a folder."
            echo
            echo "Send pack to (and overwrite existing):"
            echo "  $GAME_DATA/<folder>.pack"
            echo
            echo "Example:"
            echo "  wh3packmanager repack my_mod"
            echo "  (creates|overwrites my_mod.pack at $GAME_DATA)"
            echo
            ;;

        list)
            echo
            echo "wh3packmanager list <data|workshop>"
            echo
            echo "List available .pack files."
            echo
            echo "Examples:"
            echo "  wh3packmanager list data"
            echo "  wh3packmanager list workshop"
            echo
            ;;

        *)
            echo "Unknown command: $1"
            ;;
    esac
}

#################################################
# Extract helper
#################################################

extract_pack() {

    PACK_PATH="$1"
    PACK_NAME=$(basename "$PACK_PATH" .pack)

    echo
    echo "Selected:"
    echo "$PACK_NAME"
    echo "$PACK_PATH"
    echo

    read -p "Extract this pack? [y/N] " confirm
    [[ ! "$confirm" =~ ^[Yy]$ ]] && return

    OUT_DIR="$PACK_NAME"
    OUT_FILTER="/;./$PACK_NAME"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    rpfm_cli --game warhammer_3 pack extract \
        -p "$PACK_PATH" \
        -F "$OUT_FILTER" \
        -t "$SCHEMA"

    echo
    echo "Extracted → ./$OUT_DIR"
}

#################################################
# Commands
#################################################

browse_workshop() {

    PACK_PATH=$(find "$WORKSHOP" -name "*.pack" \
        | sort \
        | fzf --height=40% --reverse --border \
        --prompt="Workshop Packs > ")

    [ -z "$PACK_PATH" ] && return

    extract_pack "$PACK_PATH"
}

browse_data() {

    PACK_PATH=$(find "$GAME_DATA" -maxdepth 1 -name "*.pack" \
        | sort \
        | fzf --height=40% --reverse --border \
        --prompt="Game Packs > ")

    [ -z "$PACK_PATH" ] && return

    extract_pack "$PACK_PATH"
}

repack() {

    if [ -z "$1" ]; then
        show_help repack
        return 1
    fi

    PACK="$1"
    SOURCE_FOLDER="$(pwd)/$PACK"
    PACK_FILE="$GAME_DATA/$PACK.pack"

    if [ ! -d "$SOURCE_FOLDER" ]; then
        echo "ERROR: Folder '$SOURCE_FOLDER' does not exist."
        return 1
    fi

    if [ -f "$PACK_FILE" ]; then
        echo
        echo "Removing existing pack:"
        echo "$PACK_FILE"
        rm -f "$PACK_FILE"
    fi

    echo
    echo "Creating pack:"
    echo "$PACK_FILE"

    rpfm_cli --game warhammer_3 pack create -p "$PACK_FILE" || return 1

    echo
    echo "Adding contents..."

    rpfm_cli --game warhammer_3 pack add \
        -p "$PACK_FILE" \
        -t "$SCHEMA" \
        -F "$SOURCE_FOLDER" || return 1

    echo
    echo "Done → $PACK_FILE"
}


list() {

    case "$1" in

        workshop)
            find "$WORKSHOP" -name "*.pack" -printf "%f\n" \
            | awk '
                {
                    name=$0
                    # count leading ! characters
                    n = match(name, /[^!]/) - 1
                    if (n < 0) { n=length(name) }   # in case all !s
                    # get first non-! char
                    first=substr(name,n+1,1)
                    # assign secondary priority
                    if(first=="@") p=1
                    else if(first=="_") p=2
                    else if(first ~ /[0-9]/) p=3
                    else if(first ~ /[A-Z]/) p=4
                    else if(first ~ /[a-z]/) p=5
                    else p=6
                    # we use -n so that more !s appear first
                    print -n*n "\t" p "\t" name
                }' \
            | sort -k1,1n -k2,2n -k3 \
            | cut -f3-
            ;;

        data)
            find "$GAME_DATA" -maxdepth 1 -name "*.pack" \
                -printf "%f\n" \
                | sort 
            ;;

        *)
            echo
            echo "Usage:"
            echo "  wh3packmanager list workshop"
            echo "  wh3packmanager list data"
            echo
            return 1
            ;;
    esac
}

#################################################
# Dispatcher
#################################################

case "$1" in

    help|-h|--help)
        shift
        show_help "$@"
        ;;

    browse_workshop)
        shift
        browse_workshop "$@"
        ;;

    browse_data)
        shift
        browse_data "$@"
        ;;

    repack)
        shift
        repack "$@"
        ;;

    list)
        shift
        list "$@"
        ;;

    *)
        show_help
        ;;
esac