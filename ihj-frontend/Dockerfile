# Use a imagem oficial do Node.js para construir a aplicação React
FROM node:20-slim as build

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar os arquivos de configuração do projeto
COPY package.json pnpm-lock.yaml ./ 

# Instalar as dependências
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile

# Copiar o restante do código da aplicação
COPY . .

# Construir a aplicação React para produção
RUN pnpm run build

# Use uma imagem Nginx leve para servir a aplicação
FROM nginx:alpine

# Copiar a configuração do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar os arquivos de build da aplicação React para o diretório de serviço do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expor a porta 80 do Nginx
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]

