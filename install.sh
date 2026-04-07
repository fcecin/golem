#!/usr/bin/env bash
set -euo pipefail

# install.sh — make golem available system-wide
# Creates a 'golem' command in ~/.local/bin/ that dispatches to golem tools.

GOLEM_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/golem" << SCRIPT
#!/usr/bin/env bash
set -euo pipefail

GOLEM_DIR="$GOLEM_DIR"

cmd="\${1:-help}"
shift || true

case "\$cmd" in
  run)
    # Launch claude in the current work directory
    exec "\$GOLEM_DIR/golem-claude.sh" "\$@"
    ;;
  fetch)
    # Fetch a cartridge
    exec "\$GOLEM_DIR/tools/cart-fetch" "\$@"
    ;;
  boot)
    # Print the boot phrase
    exec "\$GOLEM_DIR/boot.sh"
    ;;
  init)
    # Create a work directory with a starter task.md
    dir="\${1:?Usage: golem init <dir>}"
    mkdir -p "\$dir/material" "\$dir/workspace"
    if [ ! -f "\$dir/task.md" ]; then
      cat > "\$dir/task.md" << 'TASK'
# Task

cartridge:

## Setup

## Output
TASK
      echo "Created \$dir/task.md — edit it to set your cartridge and task."
    else
      echo "task.md already exists in \$dir"
    fi
    ;;
  cart-init)
    # Run a cartridge's golem-cart-init.sh in a work directory
    pattern="\${1:?Usage: golem cart-init <cart-pattern> <dir>}"
    dir="\${2:?Usage: golem cart-init <cart-pattern> <dir>}"
    shift 2

    # Search for matching carts
    if [ -d "\$pattern" ]; then
      # Absolute or relative path given directly
      matches=("\$pattern")
    else
      # Search cartridges/ for dirs matching the pattern
      matches=()
      while IFS= read -r d; do
        [ -f "\$d/manifest.md" ] && matches+=("\$d")
      done < <(find "\$GOLEM_DIR/cartridges" -type d -name "*\$pattern*" 2>/dev/null | sort)
    fi

    if [ \${#matches[@]} -eq 0 ]; then
      echo "ERROR: No cart matching '\$pattern' found in \$GOLEM_DIR/cartridges/" >&2
      exit 1
    elif [ \${#matches[@]} -gt 1 ]; then
      echo "Multiple carts match '\$pattern':" >&2
      for m in "\${matches[@]}"; do
        echo "  \$(realpath --relative-to="\$GOLEM_DIR/cartridges" "\$m")" >&2
      done
      echo "Be more specific." >&2
      exit 1
    fi

    CART_DIR="\${matches[0]}"

    # Check work dir is a golem work dir
    if [ ! -f "\$dir/task.md" ]; then
      echo "ERROR: \$dir does not look like a golem work directory (no task.md)." >&2
      echo "Run 'golem init \$dir' first." >&2
      exit 1
    fi

    # Check cart has the init script
    if [ ! -f "\$CART_DIR/tools/golem-cart-init.sh" ]; then
      echo "Cart \$(basename "\$CART_DIR") does not have a tools/golem-cart-init.sh"
      exit 0
    fi

    echo "Running cart-init for \$(basename "\$CART_DIR") in \$dir..."
    (cd "\$dir" && bash "\$CART_DIR/tools/golem-cart-init.sh" "\$CART_DIR" "\$@")
    ;;
  cart-list)
    # List all installed cartridges with cart-init status
    if [ ! -d "\$GOLEM_DIR/cartridges" ]; then
      echo "No cartridges installed."
      exit 0
    fi
    found=0
    while IFS= read -r manifest; do
      cart_dir=\$(dirname "\$manifest")
      cart_name=\$(basename "\$cart_dir")
      rel_path=\$(realpath --relative-to="\$GOLEM_DIR/cartridges" "\$cart_dir")
      echo "\$rel_path"
      if [ -f "\$cart_dir/tools/golem-cart-init.sh" ]; then
        desc=\$(sed -n '2s/^# *//p' "\$cart_dir/tools/golem-cart-init.sh")
        echo "  cart-init: \${desc:-available (no description)}"
      else
        echo "  cart-init: not available"
      fi
    done < <(find "\$GOLEM_DIR/cartridges" -name "manifest.md" -not -path "*/.git/*" | sort)
    ;;
  help|*)
    echo "golem — context scheduler for LLMs"
    echo ""
    echo "Usage: golem <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  init <dir>            Create a work directory (use . for current dir)"
    echo "  fetch <url>           Clone a cart repo (fetches entire repo, including monorepos)"
    echo "  cart-list             List installed cartridges and cart-init availability"
    echo "  cart-init <cart> <dir> Run a cartridge's init in a work directory"
    echo "  run [args]            Launch claude in the current work directory"
    echo "  boot                  Print the bootstrap phrase"
    echo ""
    echo "Cart matching examples:"
    echo "  golem cart-init styler ~/work        # matches 'cart-logos-delivery-styler'"
    echo "  golem cart-init code-processor ~/work # matches 'cart-code-processor'"
    echo "  golem cart-init fcecin/carts/cart-logos-delivery-styler ~/work  # full path"
    echo ""
    echo "To run unattended (no permission prompts, THIS IS DANGEROUS):"
    echo "  golem run --dangerously-skip-permissions"
    echo ""
    echo "Golem dir: \$GOLEM_DIR"
    ;;
esac
SCRIPT

chmod +x "$BIN_DIR/golem"

echo "Installed 'golem' to $BIN_DIR/golem"

# Add ~/.local/bin to PATH in shell profile unless --no-path was used
if [ "${GOLEM_NO_PATH:-}" = "1" ]; then
  echo ""
  echo "Skipping PATH setup. Add manually if needed:"
  echo "  export PATH=\"$BIN_DIR:\$PATH\""
elif [[ ":$PATH:" == *":$BIN_DIR:"* ]]; then
  echo "PATH already includes $BIN_DIR"
else
  # Find the right profile file
  PROFILE=""
  if [ -f "$HOME/.zshrc" ]; then
    PROFILE="$HOME/.zshrc"
  elif [ -f "$HOME/.bashrc" ]; then
    PROFILE="$HOME/.bashrc"
  elif [ -f "$HOME/.bash_profile" ]; then
    PROFILE="$HOME/.bash_profile"
  elif [ -f "$HOME/.profile" ]; then
    PROFILE="$HOME/.profile"
  fi

  if [ -n "$PROFILE" ]; then
    if grep -q "$BIN_DIR" "$PROFILE" 2>/dev/null; then
      echo "PATH entry already in $PROFILE — restart your shell or run:"
      echo "  source $PROFILE"
    else
      echo "" >> "$PROFILE"
      echo "# Added by golem installer" >> "$PROFILE"
      echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$PROFILE"
      echo "Added $BIN_DIR to PATH in $PROFILE"
      echo "Run: source $PROFILE"
    fi
  else
    echo "Could not find shell profile. Add manually:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
  fi
fi
