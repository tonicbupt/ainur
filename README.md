# Ainur

Web UI for Eru.

# Run

## Dependencies

### Redis

Optional for caching project or app config data.

Mandatory for user session management or when building images. Base images should be pushed to `base_images` key, e.g.

    LPUSH base_images ubuntu:binary-2015.09.06 ubuntu:python-2015.09.06 ubuntu:java-2015.07.20
