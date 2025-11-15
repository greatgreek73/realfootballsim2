import { Card, CardContent, CardHeader, Skeleton, Stack, Typography } from "@mui/material";

type SquadStatusData = {
  fit: number;
  injured: number;
  suspended: number;
};

type ClubSquadStatusProps = {
  loading: boolean;
  data?: SquadStatusData | null;
};

function StatusCell({
  label,
  value,
}: {
  label: string;
  value: number | string;
}) {
  return (
    <Stack spacing={0.25}>
      <Typography variant="h5" component="div">
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
    </Stack>
  );
}

export default function ClubSquadStatus({ loading, data }: ClubSquadStatusProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader title="Squad status" subheader="Availability overview" />
        <CardContent>
          <Skeleton height={48} />
        </CardContent>
      </Card>
    );
  }

  const status = data ?? { fit: "—", injured: "—", suspended: "—" };

  return (
    <Card>
      <CardHeader title="Squad status" subheader="Availability overview" />
      <CardContent>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <StatusCell label="Fit" value={status.fit} />
          <StatusCell label="Injured" value={status.injured} />
          <StatusCell label="Suspended" value={status.suspended} />
        </Stack>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5, display: "block" }}>
          Detailed availability will appear once squad data is connected.
        </Typography>
      </CardContent>
    </Card>
  );
}
