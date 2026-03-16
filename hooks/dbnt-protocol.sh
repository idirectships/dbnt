#!/usr/bin/env bash
# DBNT Protocol Detection Hook (UserPromptSubmit)
# Detects DB/DBN/DBNM/DBYC commands and tracks score

set -euo pipefail

INPUT=$(cat)
MESSAGE=$(echo "$INPUT" | jq -r '.user_prompt // .prompt // ""' 2>/dev/null || echo "")
[ -z "$MESSAGE" ] && echo '{"result":"continue"}' && exit 0

# Normalize
MSG_LOWER=$(echo "$MESSAGE" | tr '[:upper:]' '[:lower:]' | sed 's/^[[:space:]]*//')

# Protocol commands (must be at start of message)
POINTS=0
CMD=""
if echo "$MSG_LOWER" | /usr/bin/grep -qE "^dbyc(\s|$|[.!])"; then
    CMD="DBYC"; POINTS=-2
elif echo "$MSG_LOWER" | /usr/bin/grep -qE "^dbnm(\s|$|[.!])"; then
    CMD="DBNM"; POINTS=-1
elif echo "$MSG_LOWER" | /usr/bin/grep -qE "^dbn(\s|$|[.!])"; then
    CMD="DBN"; POINTS=-1
elif echo "$MSG_LOWER" | /usr/bin/grep -qE "^db(\s|$|[.!])"; then
    CMD="DB"; POINTS=-1
elif echo "$MSG_LOWER" | /usr/bin/grep -qE "^(fixed|ship it|nailed it)(\s|$|[.!])"; then
    CMD="GOOD"; POINTS=3
elif echo "$MSG_LOWER" | /usr/bin/grep -qE "^tweak(\s|$|[.!])"; then
    CMD="TWEAK"; POINTS=0
fi

[ -z "$CMD" ] && echo '{"result":"continue"}' && exit 0

# Log to score file
SCORE_DIR="$HOME/.dbnt"
mkdir -p "$SCORE_DIR"
SCORE_FILE="$SCORE_DIR/score.json"

if [ -f "$SCORE_FILE" ]; then
    TOTAL=$(jq -r '.total_points // 0' "$SCORE_FILE" 2>/dev/null || echo 0)
else
    TOTAL=0
fi

NEW_TOTAL=$(echo "$TOTAL + $POINTS" | bc)

# Append event
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EVENT="{\"command\":\"$(echo $CMD | tr '[:upper:]' '[:lower:]')\",\"points\":$POINTS,\"timestamp\":\"$TIMESTAMP\"}"

if [ -f "$SCORE_FILE" ]; then
    jq --argjson evt "$EVENT" '.total_points = '"$NEW_TOTAL"' | .events += [$evt] | .last_updated = "'"$TIMESTAMP"'"' "$SCORE_FILE" > "${SCORE_FILE}.tmp" && mv "${SCORE_FILE}.tmp" "$SCORE_FILE"
else
    echo "{\"total_points\":$NEW_TOTAL,\"events\":[$EVENT],\"tweak_count\":0,\"last_updated\":\"$TIMESTAMP\"}" | jq . > "$SCORE_FILE"
fi

echo '{"result":"continue"}'
exit 0
