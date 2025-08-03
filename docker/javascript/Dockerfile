# Secure Node.js execution environment
FROM node:18-alpine

# Create non-root user
RUN adduser -D -s /bin/sh sandbox

# Remove potentially dangerous packages and commands
RUN apk del --purge \
    curl \
    wget \
    git \
    openssh \
    npm \
    && rm -rf /var/cache/apk/* \
    && rm -rf /usr/local/lib/node_modules/npm

# Create sandbox directory
RUN mkdir -p /sandbox && chown sandbox:sandbox /sandbox
WORKDIR /sandbox

# Switch to non-root user
USER sandbox

# Default command
CMD ["node"]