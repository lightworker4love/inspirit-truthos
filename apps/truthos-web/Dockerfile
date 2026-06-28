FROM node:20-alpine AS base
WORKDIR /app
COPY apps/truthos-web/package*.json ./
RUN npm ci
COPY apps/truthos-web/ .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=base /app/.next/standalone ./
COPY --from=base /app/.next/static ./.next/static
COPY --from=base /app/public ./public
EXPOSE 3000
CMD ["sh", "-c", "exec node server.js"]
