#!/bin/bash
# Weekly beets library maintenance script
set -e

BEETS_CMD="beet -c /app/config.yaml"

$BEETS_CMD update
$BEETS_CMD lyrics
$BEETS_CMD fetchart
$BEETS_CMD mbupdate
$BEETS_CMD mbsync
$BEETS_CMD acousticbrainz
$BEETS_CMD fingerprint
$BEETS_CMD lastgenre
$BEETS_CMD splupdate
$BEETS_CMD submit
