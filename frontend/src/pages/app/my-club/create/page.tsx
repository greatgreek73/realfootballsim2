import { useFormik } from "formik";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";

import {
  Alert,
  AlertTitle,
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { postJSON } from "@/lib/apiClient";
import { COUNTRY_OPTIONS } from "@/constants/countries";

const validationSchema = yup.object({
  name: yup.string().required("Club name is required").min(3, "Should be at least 3 characters"),
  country: yup.string().required("Country is required"),
});

export default function CreateClubPage() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const formik = useFormik({
    initialValues: {
      name: "",
      country: COUNTRY_OPTIONS[0].code,
    },
    validationSchema,
    onSubmit: async (values) => {
      setServerError(null);
      setLoading(true);
      try {
        await postJSON("/api/clubs/create/", {
          name: values.name.trim(),
          country: values.country,
        });
        navigate("/my-club", { replace: true });
      } catch (err: any) {
        setServerError(err?.message ?? "Failed to create club");
      } finally {
        setLoading(false);
      }
    },
  });

  return (
    <Box className="flex min-h-screen items-start justify-center bg-background-default p-4">
      <Paper elevation={3} className="w-full max-w-xl rounded-4xl p-8">
        <Stack spacing={3}>
          <Box>
            <Typography variant="h1" component="h1" className="mb-1">
              Create your club
            </Typography>
            <Typography variant="body1" className="text-text-secondary">
              Choose a name and country to start building your squad.
            </Typography>
          </Box>

          {serverError && (
            <Alert severity="error">
              <AlertTitle>Error</AlertTitle>
              {serverError}
            </Alert>
          )}

          <Stack
            component="form"
            spacing={3}
            onSubmit={(event) => {
              event.preventDefault();
              formik.handleSubmit();
            }}
          >
            <TextField
              id="club-name"
              name="name"
              label="Club name"
              variant="outlined"
              value={formik.values.name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.name && Boolean(formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
              fullWidth
              autoFocus
            />

            <TextField
              id="club-country"
              name="country"
              label="Country"
              select
              variant="outlined"
              value={formik.values.country}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.country && Boolean(formik.errors.country)}
              helperText={formik.touched.country && formik.errors.country}
              fullWidth
            >
              {COUNTRY_OPTIONS.map((option) => (
                <MenuItem key={option.code} value={option.code}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>

            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? "Creating…" : "Create club"}
            </Button>
          </Stack>
        </Stack>
      </Paper>
    </Box>
  );
}
