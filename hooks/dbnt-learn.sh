#!/usr/bin/env bash
# DBNT Learning Extraction Hook (Stop)
# Extracts learnings from session transcript, stores in ~/.dbnt/learnings.db
# Uses Ollama (llama3.2:3b) when available, falls back to regex extraction.

set -euo pipefail

DBNT_DIR="$HOME/DEV/dbnt"
LOG="$HOME/.dbnt/learn-hook.log"
mkdir -p "$HOME/.dbnt"

INPUT=$(cat)
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null || echo "")

# No transcript or file missing → skip
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo '{"result":"continue"}'
    exit 0
fi

# Need uv and the dbnt project
if ! command -v uv >/dev/null 2>&1 || [ ! -d "$DBNT_DIR" ]; then
    echo '{"result":"continue"}'
    exit 0
fi

# Fire-and-forget: spawn extraction detached so the hook returns fast
nohup uv run --directory "$DBNT_DIR" python3 -c "
import sys, logging
from pathlib import Path

logging.basicConfig(
    filename='$LOG',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
)
log = logging.getLogger('dbnt-learn')

try:
    from dbnt.extract import format_transcript, extract_with_ollama, extract_from_text
    from dbnt.learning import LearningStore

    transcript_path = Path('$TRANSCRIPT_PATH')
    session_id = '$SESSION_ID'

    raw = transcript_path.read_text()
    log.info(f'Transcript: {transcript_path.name} ({len(raw)} bytes)')

    # Format the JSONL transcript into readable text
    text = format_transcript(raw, max_chars=8000)
    log.info(f'Formatted transcript: {len(text)} chars')

    if len(text.strip()) < 50:
        log.info('Transcript too short, skipping')
        sys.exit(0)

    # Try Ollama first (llama3.2:3b is running locally), fall back to regex
    learnings = extract_with_ollama(text, model='llama3.2:3b')
    source = 'ollama'

    if not learnings:
        learnings = extract_from_text(text)
        source = 'regex'

    log.info(f'Extracted {len(learnings)} learning(s) via {source}')

    if learnings:
        with LearningStore() as store:
            for l in learnings:
                lid = store.add(
                    text=l.text,
                    source=source,
                    domain=l.type.value,
                    importance=l.importance,
                    session_id=session_id,
                )
                log.info(f'  Stored #{lid}: [{l.type.value}] {l.text[:80]}')
    else:
        log.info('No learnings extracted')

except Exception as e:
    log.error(f'Extraction failed: {e}', exc_info=True)
" >> "$LOG" 2>&1 &
disown

echo '{"result":"continue"}'
exit 0
