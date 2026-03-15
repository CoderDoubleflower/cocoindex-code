# Repo Notes

## GitHub SSH Key

For this repository, use the GitHub SSH key:

```bash
~/.ssh/id_ed25519_huangdada1126@gmail
```

This key authenticates as GitHub user `CoderDoubleflower`.

Do not assume the default `~/.ssh/id_ed25519` is the correct key for pushes to this fork.

## Push Command

If normal SSH push does not pick the right key, use:

```bash
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_huangdada1126@gmail -o IdentitiesOnly=yes' git push origin main
```

If the environment can reach GitHub only through the local HTTP proxy, use the repo-local proxy helper pattern that was validated in this workspace:

```bash
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_huangdada1126@gmail -o IdentitiesOnly=yes -o ProxyCommand="/tmp/http_connect_proxy.py 192.168.11.128 7890 %h %p"' git push origin main
```
