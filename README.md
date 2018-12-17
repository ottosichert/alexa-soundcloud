# alexa-soundcloud
Making accessing SoundCloud easier for Alexa

This public endpoint allows playing music from SoundCloud via a generated RSS feed.

- Install https://mypodapp.com Alexa skill
- Create new playlist
- Add link to playlist
  - Name: `Favourites`
  - Link: [`https://alexa-soundcloud.now.sh`](https://alexa-soundcloud.now.sh)
  - **Advanced**
    - Username: `your-soundcloud-name`
    - Password: `your-client-id`
    - Disable resume: `[X]`
    - Save
- Say `Alexa, play favourites on my pod`
- Enjoy the finest music in the world, i.e. your favourites

_Note_: To get your SoundCloud `client_id` go to https://soundcloud.com/stream and check the network tab of your developer tools for any requests containing the `client_id` as HTTP GET query parameter.
