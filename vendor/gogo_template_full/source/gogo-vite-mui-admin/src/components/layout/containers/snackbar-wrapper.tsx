import { SnackbarProvider } from "notistack";
import { PropsWithChildren } from "react";

import NiCheckSquare from "@/icons/nexture/ni-check-square";
import NiCrossSquare from "@/icons/nexture/ni-cross-square";
import NiExclamationSquare from "@/icons/nexture/ni-exclamation-square";
import NiInfoSquare from "@/icons/nexture/ni-info-square";

const iconVariants = {
  success: <NiCheckSquare className="mr-2" />,
  error: <NiCrossSquare className="mr-2" />,
  warning: <NiExclamationSquare className="mr-2" />,
  info: <NiInfoSquare className="mr-2" />,
};

export default function SnackbarWrapper({ children }: PropsWithChildren) {
  return (
    <SnackbarProvider maxSnack={4} iconVariant={iconVariants}>
      {children}
    </SnackbarProvider>
  );
}
