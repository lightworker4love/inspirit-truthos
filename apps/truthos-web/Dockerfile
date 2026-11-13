FROM node:20-alpine AS base
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_HERMES_AGENT_URL
ARG NEXT_PUBLIC_TRUTH_API_URL
ARG NEXT_PUBLIC_MIXPANEL_TOKEN
ENV NEXT_PUBLIC_HERMES_AGENT_URL=$NEXT_PUBLIC_HERMES_AGENT_URL
ENV NEXT_PUBLIC_TRUTH_API_URL=$NEXT_PUBLIC_TRUTH_API_URL
ENV NEXT_PUBLIC_MIXPANEL_TOKEN=$NEXT_PUBLIC_MIXPANEL_TOKEN
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
