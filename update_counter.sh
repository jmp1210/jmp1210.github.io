#!/bin/bash
# Met à jour le compteur 2026 en checkant Zimbra pour UL-DN-INFRA
cd /home/modbot/.openclaw/workspace
python3 compteur_zimbra.py check
cp compteur_2026.json counter.json
# Push si changement
if ! git diff --quiet counter.json 2>/dev/null; then
  git add counter.json
  git commit -m "Update counter $(date -u +%Y-%m-%dT%H:%M)"
  git push github deploy-clean:main
fi
