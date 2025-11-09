import { useMemo } from "react";
import { Link as RouterLink } from "react-router-dom";

import {
  Card,
  CardContent,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import PaidIcon from "@mui/icons-material/Paid";
import SavingsIcon from "@mui/icons-material/Savings";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import AssessmentIcon from "@mui/icons-material/Assessment";

import PageShell from "@/components/ui/PageShell";
import HeroBar from "@/components/ui/HeroBar";

type CashFlowItem = {
  label: string;
  amount: number;
  type: "income" | "expense";
  category: string;
  due?: string;
};

const CASH_FLOW: CashFlowItem[] = [
  { label: "Broadcasting", amount: 18.4, type: "income", category: "Media" },
  { label: "Sponsorship", amount: 12.2, type: "income", category: "Commercial" },
  { label: "Matchday Revenue", amount: 4.8, type: "income", category: "Tickets" },
  { label: "Player Salaries", amount: 14.6, type: "expense", category: "Wages" },
  { label: "Youth Academy", amount: 2.1, type: "expense", category: "Development" },
  { label: "Stadium Maintenance", amount: 1.7, type: "expense", category: "Operations" },
];

const UPCOMING_PAYMENTS: CashFlowItem[] = [
  { label: "Training Facilities Upgrade", amount: 3.2, type: "expense", category: "Infrastructure", due: "Nov 18" },
  { label: "Sponsor Bonus", amount: 1.1, type: "income", category: "Commercial", due: "Nov 22" },
  { label: "Signing Fee (Youth GK)", amount: 0.6, type: "expense", category: "Transfers", due: "Nov 27" },
];

export default function FinancePage() {
  const totals = useMemo(() => {
    return CASH_FLOW.reduce(
      (acc, item) => {
        if (item.type === "income") {
          acc.income += item.amount;
        } else {
          acc.expense += item.amount;
        }
        return acc;
      },
      { income: 0, expense: 0 }
    );
  }, []);

  const netBalance = totals.income - totals.expense;
  const wageBudgetUsed = 72; // %
  const transferBudget = 38.4;

  const hero = (
    <HeroBar
      title="Club Finance"
      subtitle="Monitor budgets, cash flow and upcoming obligations"
      tone="green"
      kpis={[
        { label: "Net balance", value: `$${netBalance.toFixed(1)}M`, icon: <PaidIcon fontSize="small" /> },
        { label: "Income (30d)", value: `$${totals.income.toFixed(1)}M`, icon: <SavingsIcon fontSize="small" /> },
        { label: "Expenses (30d)", value: `$${totals.expense.toFixed(1)}M`, icon: <TrendingDownIcon fontSize="small" /> },
        { label: "Transfer budget", value: `$${transferBudget.toFixed(1)}M`, icon: <AssessmentIcon fontSize="small" /> },
      ]}
      accent={
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Chip label={`Wage budget used: ${wageBudgetUsed}%`} size="small" sx={{ color: "white", bgcolor: "rgba(255,255,255,0.12)" }} />
          <Chip label="Financial fair play: compliant" size="small" sx={{ color: "white", bgcolor: "rgba(255,255,255,0.12)" }} />
        </Stack>
      }
      actions={
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Chip component={RouterLink} clickable to="/transfers" label="Go to Transfers" color="secondary" />
          <Chip component={RouterLink} clickable to="/my-club/players" label="Review Squad Costs" color="secondary" variant="outlined" />
        </Stack>
      }
    />
  );

  const topSection = (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="subtitle1" fontWeight={600}>
            Financial overview
          </Typography>
          <Typography variant="body2" color="text.secondary">
            All amounts are reported in millions of credits. Net balance reflects the last 30 days of activity and
            automatically syncs with transfer/salary operations.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );

  const mainSection = (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Cash flow
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Item</TableCell>
                <TableCell>Category</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {CASH_FLOW.map((row) => (
                <TableRow key={row.label}>
                  <TableCell>{row.label}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      color={row.type === "income" ? "success" : "error"}
                      label={row.category}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right" style={{ color: row.type === "income" ? "#14b8a6" : "#e11d48" }}>
                    {row.type === "income" ? "+" : "-"}${row.amount.toFixed(1)}M
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Divider sx={{ my: 2 }} />
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Typography variant="body2" flex={1}>
              Income total: <strong>${totals.income.toFixed(1)}M</strong>
            </Typography>
            <Typography variant="body2" flex={1}>
              Expense total: <strong>${totals.expense.toFixed(1)}M</strong>
            </Typography>
            <Typography variant="body2" flex={1}>
              Net 30d balance: <strong>${netBalance.toFixed(1)}M</strong>
            </Typography>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Wage budget usage
          </Typography>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Wages committed
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {wageBudgetUsed}%
              </Typography>
            </Stack>
            <LinearProgress value={wageBudgetUsed} variant="determinate" />
            <Typography variant="caption" color="text.secondary">
              Target is to stay below 85% before mid-season review.
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );

  const asideSection = (
    <Stack spacing={3}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upcoming payments
          </Typography>
          <Stack spacing={1.5}>
            {UPCOMING_PAYMENTS.map((item) => (
              <Stack key={item.label} spacing={0.3}>
                <Typography variant="body2" fontWeight={600}>
                  {item.label}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Due {item.due} · {item.category}
                </Typography>
                <Typography variant="body2" color={item.type === "income" ? "success.main" : "error.main"}>
                  {item.type === "income" ? "+" : "-"}${item.amount.toFixed(1)}M
                </Typography>
                <Divider />
              </Stack>
            ))}
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              • Consider refinancing stadium loan to free up ${Math.abs(netBalance).toFixed(1)}M buffer.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Sponsorship tier upgrade available next month if average attendance ≥ 90%.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Review performance bonuses before winter break to avoid overspend.
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );

  return <PageShell hero={hero} top={topSection} main={mainSection} aside={asideSection} />;
}
