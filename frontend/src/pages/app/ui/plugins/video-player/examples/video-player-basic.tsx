import "@vidstack/react/player/styles/base.css";
import "@vidstack/react/player/styles/plyr/theme.css";

import { Card, CardContent, Typography } from "@mui/material";

import { plyrLayoutIcons } from "@/components/plugins/video-player-controls";
import { MediaPlayer, MediaProvider, Poster } from "@vidstack/react";
import { PlyrLayout } from "@vidstack/react/player/layouts/plyr";

export default function VideoPlayerBasic() {
  return (
    <Card>
      <CardContent>
        <Typography component={"h5"} variant="h5" className="card-title">
          Basic
        </Typography>
        <MediaPlayer
          title="Sprite Fight"
          src="https://files.vidstack.io/sprite-fight/720p.mp4"
          className="media-player mb-0! rounded-lg!"
        >
          <MediaProvider>
            <Poster className="media-poster rounded-lg!" src="https://files.vidstack.io/sprite-fight/poster.webp" />
          </MediaProvider>
          <PlyrLayout thumbnails="https://files.vidstack.io/sprite-fight/thumbnails.vtt" icons={plyrLayoutIcons} />
        </MediaPlayer>
      </CardContent>
    </Card>
  );
}
