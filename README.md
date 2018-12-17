# alexa-soundcloud
Making accessing SoundCloud easier for Alexa

This public endpoint allows playing music from SoundCloud via a generated RSS feed.

## Installation

Enable any Alexa skill capable of playing music from RSS. I found https://mypodapp.com which has a minimal but ad-free option for users.

## Options

All options can be passed as HTTP Basic authentication `username` in form of a query string, e.g. `foo=1&bar=2`

| Name | Default | Description |
|------|---------|-------------|
| **shuffle** | `False` | After retrieving the desired list, randomly shuffle the output |

## Examples

- Create new playlist
- Add link to playlist
  - Name: `Favourites`
  - Link: `https://alexa-soundcloud.now.sh/resolve?url=https://soundcloud.com/<name>/likes`
  - **Advanced**
    - Username: `shuffle=1`
    - Password: `<client_id>`
    - Disable resume: `[X]`
    - Save
- Say `Alexa, play favourites on my pod`
- Enjoy the finest music in the world, i.e. your favourites

_Note_: To get your SoundCloud `client_id` go to https://soundcloud.com/stream and check the network tab of your developer tools for any requests containing the `client_id` as HTTP GET query parameter.
