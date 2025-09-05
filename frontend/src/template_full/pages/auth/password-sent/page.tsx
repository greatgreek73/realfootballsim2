import { Link } from "react-router-dom";

import { Alert, AlertTitle, Box, Divider, Paper, Typography } from "@mui/material";

import Logo from "@/components/logo/logo";
import NiCheckSquare from "@/icons/nexture/ni-check-square";

export default function Page() {
  return (
    <Box className="flex min-h-screen w-full items-center justify-center p-4">
      <Paper elevation={3} className="bg-background-paper shadow-darker-xs w-[32rem] max-w-full rounded-4xl py-14">
        <Box className="flex flex-col gap-4 px-8 sm:px-14">
          <Box className="flex flex-col">
            <Box className="mb-14 flex justify-center">
              <Logo classNameMobile="hidden" />
            </Box>

            <Box className="flex flex-col gap-10">
              <Box className="flex flex-col">
                <Typography variant="h1" component="h1" className="mb-2">
                  Reset Password
                </Typography>
                <Typography variant="body1" className="text-text-primary">
                  Get an email about how to reset your password securely.
                </Typography>
              </Box>

              <Alert severity="success" icon={<NiCheckSquare />} className="neutral bg-background-paper/60!">
                <AlertTitle variant="subtitle2">Email Sent!</AlertTitle>
                Please check your email to reset your password.
              </Alert>

              <Divider className="text-text-secondary my-0 text-sm"></Divider>
              <Box className="flex flex-col">
                <Typography variant="h5" component="h5">
                  Sign in
                </Typography>
                <Typography variant="body1" className="text-text-secondary">
                  If you already have an account, please{" "}
                  <Link to="/auth/sign-in" className="link-primary link-underline-hover">
                    sign in
                  </Link>
                  .
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}
