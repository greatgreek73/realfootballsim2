import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import { ChampionshipStanding } from "@/types/tournaments";

interface ChampionshipStandingsTableProps {
  standings: ChampionshipStanding[];
}

export function ChampionshipStandingsTable({ standings }: ChampionshipStandingsTableProps) {
  if (standings.length === 0) {
    return <Typography variant="body2">Standings are not available yet.</Typography>;
  }

  return (
    <TableContainer component={Paper}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>#</TableCell>
            <TableCell>Team</TableCell>
            <TableCell align="right">P</TableCell>
            <TableCell align="right">W</TableCell>
            <TableCell align="right">D</TableCell>
            <TableCell align="right">L</TableCell>
            <TableCell align="right">Goals</TableCell>
            <TableCell align="right">+/-</TableCell>
            <TableCell align="right">Очки</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {standings.map((row) => {
            const promotion = row.is_promotion_zone;
            const relegation = row.is_relegation_zone;
            return (
              <TableRow
                key={row.team.id}
                hover
                sx={{
                  bgcolor: promotion
                    ? "success.light"
                    : relegation
                    ? "error.light"
                    : "inherit",
                  "&:hover": {
                    bgcolor: promotion
                      ? "success.light"
                      : relegation
                      ? "error.light"
                      : "action.hover",
                  },
                }}
              >
                <TableCell>{row.position}</TableCell>
                <TableCell>{row.team.name}</TableCell>
                <TableCell align="right">{row.matches_played}</TableCell>
                <TableCell align="right">{row.wins}</TableCell>
                <TableCell align="right">{row.draws}</TableCell>
                <TableCell align="right">{row.losses}</TableCell>
                <TableCell align="right">
                  {row.goals_for}:{row.goals_against}
                </TableCell>
                <TableCell align="right">{row.goal_diff}</TableCell>
                <TableCell align="right">{row.points}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
