import { Card, CardContent, CardHeader, Divider, Skeleton, Stack, Typography } from "@mui/material";

export type ClubActivityItem = {
  id: string | number;
  title: string;
  description?: string;
  time?: string;
};

export type ClubActivityProps = {
  loading: boolean;
  items?: ClubActivityItem[];
};

export default function ClubActivity({ loading, items = [] }: ClubActivityProps) {
  return (
    <Card className="h-full">
      <CardHeader title="Recent Activity" subheader="Latest updates around your club" />
      <CardContent>
        {loading ? (
          <Stack spacing={2}>
            <Skeleton height={20} />
            <Skeleton height={20} />
            <Skeleton height={20} />
          </Stack>
        ) : items.length ? (
          <Stack divider={<Divider flexItem />} spacing={2}>
            {items.map((item) => (
              <Stack key={item.id} spacing={0.5}>
                <Typography variant="body1">{item.title}</Typography>
                {item.description && (
                  <Typography variant="body2" color="text.secondary">
                    {item.description}
                  </Typography>
                )}
                {item.time && (
                  <Typography variant="caption" color="text.disabled">
                    {item.time}
                  </Typography>
                )}
              </Stack>
            ))}
          </Stack>
        ) : (
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              No recent activity yet.
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Transfer news, training updates and match events will appear here.
            </Typography>
          </Stack>
        )}
      </CardContent>
    </Card>
  );
}
