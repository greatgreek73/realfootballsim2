import { Box, Paper, Typography } from "@mui/material";

export default function Page() {
  return (
    <Box className="p-6">
      <Typography variant="h5" className="mb-4">My Club</Typography>
      <Paper className="p-4">
        <Typography>Заглушка страницы клуба. Страница подключена и работает.</Typography>
      </Paper>
    </Box>
  );
}
