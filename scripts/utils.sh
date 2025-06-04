# These are meant to be sourced by other scripts

ensure_sudo() {
    if [ "$EUID" != 0 ]; then
        echo "This script requires sudo!"
        exit $?
    fi
}

