import { Button, Card, CardContent, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

import ClubPlayersTable from "@/components/club/ClubPlayersTable";
import HeroBar from "@/components/ui/HeroBar";
import PageShell from "@/components/ui/PageShell";

export default function PlayersPage() {
  const hero = (
    <HeroBar
      title="Squad"
      subtitle="Manage your roster composition and depth chart"
      tone="green"
      kpis={[
        { label: "Roster size", value: "—" },
        { label: "Average OVR", value: "—" },
        { label: "Players on loan", value: "—" },
        { label: "Foreign quota", value: "—" },
      ]}
      actions={
        <Button component={RouterLink} to="/transfers" size="small" variant="outlined">
          Go to transfers
        </Button>
      }
    />
  );

  const top = (
    <Typography variant="body2" color="text.secondary">
      Use filters in the table to manage positions, contracts and depth. Click a player name to open the detailed profile.
    </Typography>
  );

  const mainContent = (
    <Card>
      <CardContent sx={{ p: 0 }}>
        <ClubPlayersTable />
      </CardContent>
    </Card>
  );

  const asideContent = (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Squad tips
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Keep at least two players per position and track fatigue before each matchday. Use the transfers page to offload surplus players
          or sign short-term replacements.
        </Typography>
      </CardContent>
    </Card>
  );

  return <PageShell hero={hero} top={top} main={mainContent} aside={asideContent} bottomSplit="67-33" />;
}
