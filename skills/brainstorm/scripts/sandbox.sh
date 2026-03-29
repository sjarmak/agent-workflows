#!/usr/bin/env bash
set -euo pipefail

BRAINSTORM_DIR="$(pwd)/.brainstorm"

cmd="${1:-help}"
session="${2:-}"
idea_num="${3:-}"

case "$cmd" in
    create)
        if [[ -z "$session" || -z "$idea_num" ]]; then
            echo "Usage: sandbox.sh create <session> <idea-number>"
            exit 1
        fi

        sandbox_dir="$BRAINSTORM_DIR/$session/sandboxes/idea-$(printf '%03d' "$idea_num")"
        mkdir -p "$sandbox_dir"

        echo "Sandbox: $sandbox_dir"
        echo "Prototype idea #$idea_num here."
        ;;

    list)
        if [[ -z "$session" ]]; then
            echo "Usage: sandbox.sh list <session>"
            exit 1
        fi

        sandbox_base="$BRAINSTORM_DIR/$session/sandboxes"
        if [[ -d "$sandbox_base" ]]; then
            found=$(ls -d "$sandbox_base"/idea-* 2>/dev/null || true)
            if [[ -z "$found" ]]; then
                echo "No sandboxes yet."
            else
                echo "$found"
            fi
        else
            echo "No sandboxes yet."
        fi
        ;;

    clean)
        if [[ -z "$session" ]]; then
            echo "Usage: sandbox.sh clean <session>"
            exit 1
        fi

        sandbox_base="$BRAINSTORM_DIR/$session/sandboxes"
        if [[ -d "$sandbox_base" ]]; then
            rm -rf "${sandbox_base:?}"/idea-*
            echo "Sandboxes cleaned."
        else
            echo "No sandboxes to clean."
        fi
        ;;

    *)
        echo "Usage: sandbox.sh {create|list|clean} <session> [idea-number]"
        ;;
esac
