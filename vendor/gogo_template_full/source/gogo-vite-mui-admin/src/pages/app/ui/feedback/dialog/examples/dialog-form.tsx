import { FormEvent, useState } from "react";

import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
} from "@mui/material";

export default function DialogForm() {
  const [openForm, setOpenForm] = useState(false);
  const handleClickOpenForm = () => {
    setOpenForm(true);
  };
  const handleCloseForm = () => {
    setOpenForm(false);
  };
  return (
    <Box>
      <Button variant="outlined" onClick={handleClickOpenForm}>
        Open Form Dialog
      </Button>
      <Dialog
        open={openForm}
        onClose={handleCloseForm}
        slotProps={{
          paper: {
            component: "form",
            onSubmit: (event: FormEvent<HTMLFormElement>) => {
              event.preventDefault();
              const formData = new FormData(event.currentTarget);
              const formJson = Object.fromEntries((formData as any).entries());
              const email = formJson.email;
              console.log(email);
              handleCloseForm();
            },
          },
        }}
      >
        <DialogTitle>Subscribe</DialogTitle>
        <DialogContent>
          <DialogContentText className="mb-4">
            To subscribe to this website, please enter your email address here. We will send updates occasionally.
          </DialogContentText>
          <TextField
            required
            margin="dense"
            id="name"
            name="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseForm}>Cancel</Button>
          <Button type="submit">Subscribe</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
