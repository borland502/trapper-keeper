# Trapper Keeper
## Overview
Trapper Keeper aims to be a thin wrapper over KeePassXC using PyKeepass for the niche goal of packing various
environment variables, ssh keys, and other sensitive artifacts into the password manager to then unpack at a 
destination vm/lxc/docker image.     

### Chezmoi Adjacent
I love [chezmoi](https://www.chezmoi.io), which handles this goal with more encryption options and with better 
instructions.  If you are really industrious, you can integrate with 1password or self-hosted bitwarden instances.
But simplicity in secrets management is key for me. Most TK operations are straight from the [PyKeepass](https://pykeepass.readthedocs.io/en/latest/) 
library and the wrapped TK database binary will be accessible from the various KeePassXC [clients](https://github.com/lgg/awesome-keepass).  
TK does not aim to alter any object it stores or the location where that object is expected

## Commands

![Allied MCV](./img/RA3_Allied_MCV_land.webp)
![Allied Construction Yard](./img/Allied_Conyard.webp)

### Pack

This will create any files which are missing as well as the Keepass database itself.  The user is expected to supply
only a password token `~/.local/state/keepass_token` and a key `~/.config/trapper_keeper/key.txt`.  The key can be 
anything at all so long as it never changes.

```shell
python -m trapper_keeper pack
```

### Repack

Artifacts are gathered up from well-known locations (mostly [XDG_*](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)) 
and attached as binaries in an existing KeepPass database.

```shell
python -m trapper_keeper repack
```

Takes the artifacts and unpacks them back to where they were originally.

```shell
python -m trapper_keeper unpack
```

### SQLite commands

A sqlite db is automatically created and embedded into the Keepass database.  For now, it functions as a key/value
store located at `~/.cache/trapper_keeper/kv_store.sqlite` after unpacking. This houses the few values unique 
to Trapper Keeper.  Like all artifacts though, it is accessible through any sqlite client you care to use.

## Links
* [KeePassXC](https://keepassxc.org)
* [PyKeepass](https://pykeepass.readthedocs.io/en/latest/)
* [XDG Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
* [xdg-base-dirs library](https://github.com/srstevenson/xdg-base-dirs)