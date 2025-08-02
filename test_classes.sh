#!/bin/bash

# CONFIGURAÇÕES
API_BASE="https://ihj.jmedeiros.com.br/api"
USUARIO="gilberto"         # Substitua pelo seu nome de usuário real
SENHA="secret"           # Substitua pela sua senha real

# 1. Obter token
echo "🔐 Solicitando token..."
RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USUARIO\", \"password\":\"$SENHA\"}")

TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')

if [[ "$TOKEN" == "null" || -z "$TOKEN" ]]; then
  echo "❌ Falha ao obter token!"
  echo "Resposta da API:"
  echo "$RESPONSE"
  exit 1
fi

echo "✅ Token recebido com sucesso."

# 2. Fazer requisição autenticada
echo "📦 Chamando /equipamentos/classes com token..."
curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/equipamentos/classes" | jq
