#!/bin/bash
set -e

cd /root/evolution-api/IHJ || exit

echo "🔁 Enviando modificações do VPS para o GitHub..."

# Força uso da chave SSH correta
export GIT_SSH_COMMAND="ssh -i ~/.ssh/github -o IdentitiesOnly=yes"

# Adiciona mudanças
git add .

# Commit com data e hora
COMMIT_MSG="Atualização do VPS em $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG" || echo "⚠️ Nenhuma mudança nova para commitar."

# Envia para o GitHub
git push origin main

echo "✅ Atualização enviada para o GitHub com sucesso!"
