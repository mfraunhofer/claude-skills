#!/usr/bin/env bash
# UserPromptSubmit hook: "box <project>" = enter PM mode for that project.
#
# Typing "box myapp" in any session makes Claude act as the PM for that project.
# It reads the project's .scratch/pm-state.md and all active .scratch/pm-inbox/*.md
# reports and answers with a compact status plus the ONE next step.
# A bare "box" infers the project from the running conversation and asks if unclear.
#
# Setup:
#   1. Copy to ~/.claude/hooks/box-pm.sh and chmod +x it.
#   2. Edit the PROJECTS map below (one "name:path" pair per line).
#   3. Register it in ~/.claude/settings.json (see the SKILL.md of the pm skill).
#
# Fires ONLY on exactly "box" or "box <known-project>" (trimmed, case-insensitive,
# spaces/brackets/dots ignored). "boxing" / "box status" / "the box" do NOT fire.
# Requires jq.

set -euo pipefail

# name:path map. Extend with your projects.
PROJECTS="
myapp:$HOME/projects/myapp
website:$HOME/projects/website
"

input=$(cat)
prompt=$(printf '%s' "$input" | jq -r '.prompt // ""')
norm=$(printf '%s' "$prompt" | tr -d '[:space:]().' | tr '[:upper:]' '[:lower:]')

emit() {
  jq -n --arg c "$1" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit",additionalContext:$c}}'
  exit 0
}

if [ "$norm" = "box" ]; then
  names=$(printf '%s' "$PROJECTS" | awk -F: 'NF {printf "%s ", $1}')
  emit "The user typed a bare 'box' = PM mode without a project name. This is a fixed convention, do NOT ask what 'box' means. Infer the intended project from the RUNNING conversation (usually the project discussed last) and become its PM: read its .scratch/pm-state.md AND the active .scratch/pm-inbox/*.md reports (NOT _archive). Answer compactly: a one-sentence verdict, one line per report/slice (date/topic/status/blocker), and close with exactly ONE next step as a paste-ready line. Say which project you picked. Known projects: ${names}. If the conversation does not make the project obvious, ask briefly which one instead of guessing."
fi

target=""
while IFS=: read -r name path; do
  [ -z "$name" ] && continue
  key=$(printf 'box%s' "$name" | tr -d '[:space:]().' | tr '[:upper:]' '[:lower:]')
  if [ "$norm" = "$key" ]; then
    target="$path"
    break
  fi
done <<EOF
$PROJECTS
EOF

[ -z "$target" ] && exit 0

if [ -d "$target/.scratch/pm-inbox" ]; then
  emit "The user invoked PM mode for the project at ${target} (the 'box' convention). Become the PM for THIS project: read ${target}/.scratch/pm-state.md (if present) for the current state AND all active reports under ${target}/.scratch/pm-inbox/*.md (NOT _archive unless asked). Answer compactly in PM format: one-sentence verdict, one line per report/slice with date/topic/status/blocker, and close with exactly ONE concrete next step as a paste-ready line. Also say which project/workspace this is. Do NOT ask what 'box' means, it is this convention."
else
  emit "The user invoked the 'box' PM convention for ${target}, but there is no .scratch/pm-inbox directory there yet. Say so openly and ask whether to create it."
fi
