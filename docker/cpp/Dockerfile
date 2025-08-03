# Secure C++ execution environment
FROM gcc:11-alpine

# Create non-root user
RUN adduser -D -s /bin/sh sandbox

# Remove potentially dangerous packages and commands
RUN apk del --purge \
    curl \
    wget \
    git \
    openssh \
    && rm -rf /var/cache/apk/*

# Create sandbox directory
RUN mkdir -p /sandbox && chown sandbox:sandbox /sandbox
WORKDIR /sandbox

# Switch to non-root user
USER sandbox

# Default command
CMD ["g++"]