import { Box } from '@mui/material'
import ClubPlayersTable from '@/components/club/ClubPlayersTable'
// Если alias "@" не настроен, замените строку выше на:
// import { ClubPlayersTable } from '../../../components/club/ClubPlayersTable'

export default function PlayersPage() {
  return (
    <Box className="p-2 sm:p-4">
      <ClubPlayersTable />
    </Box>
  )
}
