#!/usr/bin/env bash
# DBNT Learning Extraction Hook (Stop)
# Extracts learnings from session transcript, stores in ~/.dbnt/learnings.db

set -euo pipefail

INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null || echo "")

[ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ] && echo '{"result":"continue"}' && exit 0

# Find python with dbnt installed
PYTHON=""
for p in python3 python; do
    if command -v "$p" >/dev/null 2>&1 && "$p" -c "import dbnt" 2>/dev/null; then
        PYTHON="$p"
        break
    fi
done

# Check common venv locations
if [ -z "$PYTHON" ]; then
    for venv in "$HOME/.dbnt/.venv/bin/python" "$HOME/.local/bin/python3"; do
        if [ -x "$venv" ] && "$venv" -c "import dbnt" 2>/dev/null; then
            PYTHON="$venv"
            break
        fi
    done
fi

[ -z "$PYTHON" ] && echo '{"result":"continue"}' && exit 0

# Run extraction in background (fire-and-forget)
nohup "$PYTHON" -c "
import sys
from pathlib import Path
from dbnt.extract import extract_from_transcript
from dbnt.learning import LearningStore

transcript = Path('$TRANSCRIPT_PATH').read_text()
learnings = extract_from_transcript(transcript)

if learnings:
    with LearningStore() as store:
        for l in learnings:
            store.add(
                text=l.text,
                source='session',
                domain=l.type.value,
                importance=l.importance,
                session_id='$SESSION_ID',
            )
" > /dev/null 2>&1 &
disown

echo '{"result":"continue"}'
exit 0
