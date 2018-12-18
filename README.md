# alexa-soundcloud

This public endpoint allows playing music from SoundCloud via a generated RSS feed. This endpoint acts as an convenience wrapper around SoundCloud's public API linked below. It works by calling the same URL path after `https://alexa-soundcloud.now.sh` appended to `https://api.soundcloud.com`.

## Installation

Enable any Alexa skill capable of playing music from RSS. I found https://mypodapp.com which has a minimal but ad-free option for users.

## SoundCloud API

The documentation of SoundCloud's public API (not the https://api-v2.soundcloud.com used on the live site) can be found here: https://developers.soundcloud.com/docs/api/guide

To get your SoundCloud `client_id` log in and go to https://soundcloud.com/stream and check the network tab of your developer tools for any requests containing the `client_id` as HTTP GET query parameter.

## alexa-soundcloud API

Additional options can be passed as HTTP Basic authentication `username` in form of a query string, e.g.:

```
simple=foo&shorthand&nested.key=bar
```

| Name | Usage | Description |
|------|---------|-------------|
| **shuffle** | `shuffle` | Set to any value to randomly shuffle the output after retrieving the desired list |
| **relative** | `relative.created.to=P10Y` | Today's date subtracted of the duration parsed by [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Durations) will be added to the key path after `relative` |

## Examples

- Create new playlist on https://mypodapp.com
- Add link to playlist
  - Name: `Favourites`
  - Link: `https://alexa-soundcloud.now.sh/resolve?url=https://soundcloud.com/<name>/likes`
  - **Advanced**
    - Username: `shuffle`
    - Password: `<client_id>`
    - Disable resume: `[X]`
    - Save
  - Say `Alexa, play Favourites on MyPod`
  - _Enjoy the finest music in the world, i.e. your favourites_
- Add link to playlist
  - Name: `Feed`
  - Link: `https://alexa-soundcloud.now.sh/tracks?q=dub+techno&duration.from=1800000`
  - **Advanced**
    - Username: `shuffle&relative.created_at.from=P1W`
    - Password: `<client_id>`
    - Disable resume: `[X]`
    - Save
  - Say `Alexa, play Feed on MyPod`
  - _Enjoy the freshest\* music in the world, i.e. last week's new sets of sweet dub techno (\*taste may differ)_
