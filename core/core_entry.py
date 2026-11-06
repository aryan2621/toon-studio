"""Entry point for the bundled Toon Studio core (built into one executable by scripts/build-core.sh)."""

import truststore

# The bundled Python's OpenSSL looks for CA certificates at a path that doesn't exist on macOS, so
# against the macOS keychain instead, which also picks up any certificates an organisation installs.
truststore.inject_into_ssl()

from toon_core.ipc import main

if __name__ == "__main__":
    main()
