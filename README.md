# alexa-soundcloud
Making accessing SoundCloud easier for Alexa

This public endpoint allows playing music from SoundCloud via a generated RSS feed.

## Installation

Enable any Alexa skill capable of playing music from RSS. I found https://mypodapp.com which has a minimal but ad-free option for users.

## Options

All options can be passed as HTTP Basic authentication `username` in form of a query string, e.g. `foo=1&bar`

| Name | Default | Description |
|------|---------|-------------|
| **shuffle** | `None` | Set to any value to randomly shuffle the output after retrieving the desired list |

## Examples

- Create new playlist
- Add link to playlist
  - Name: `Favourites`
  - Link: `https://alexa-soundcloud.now.sh/resolve?url=https://soundcloud.com/<name>/likes`
  - **Advanced**
    - Username: `shuffle`
    - Password: `<client_id>`
    - Disable resume: `[X]`
    - Save
- Say `Alexa, play Favourites on MyPod`
- Enjoy the finest music in the world, i.e. your favourites

_Note_: To get your SoundCloud `client_id` go to https://soundcloud.com/stream and check the network tab of your developer tools for any requests containing the `client_id` as HTTP GET query parameter.
