Current steps to getting docker container running:

1. Ensuring you're in the `documentation` subdir, build container with docker compose:

```bash
docker compose up
```

2. Once the container is built, it still needs the Material for Mkdocs Insiders extras installed. To do this, first start the container running:

```bash
docker run -it -p 8001:8001 documentation-mkdocs
```

3. Now, within the context of the container, using either `docker exec` or VSCode 'Attach shell':

```bash
pip install git+URL_FOR_INSIDERS
```

4. Finally,  within the context of the container, using either `docker exec` or VSCode 'Attach shell':

```bash
mkdocs serve
```
