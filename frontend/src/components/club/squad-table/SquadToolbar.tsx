import { Toolbar, Box, FilledInput, InputAdornment } from "@mui/material";
import {
  QuickFilter,
  QuickFilterClear,
  QuickFilterControl,
  GridToolbarColumnsButton,
  GridToolbarFilterButton,
  GridToolbarExport,
} from "@mui/x-data-grid";

import NiSearch from "@/icons/nexture/ni-search";
import NiCross from "@/icons/nexture/ni-cross";
import { cn } from "@/lib/utils";

type SquadToolbarProps = {};

export default function SquadToolbar(_: SquadToolbarProps) {
  return (
    <Toolbar className="px-3 py-2">
      <Box className="flex w-full flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <Box className="w-full md:max-w-[320px]">
          <QuickFilter size="medium" debounceMs={200}>
            <QuickFilterControl
              render={({ ref, ...controlProps }, state) => (
                <FilledInput
                  {...controlProps}
                  inputRef={ref}
                  placeholder="Search players..."
                  size="small"
                  startAdornment={
                    <InputAdornment position="start">
                      <NiSearch size="medium" className="text-text-disabled" />
                    </InputAdornment>
                  }
                  endAdornment={
                    <InputAdornment position="end" className={cn(state.value === "" && "hidden")}>
                      <QuickFilterClear edge="end">
                        <NiCross size="medium" className="text-text-disabled" />
                      </QuickFilterClear>
                    </InputAdornment>
                  }
                />
              )}
            />
          </QuickFilter>
        </Box>

        <Box className="flex flex-wrap items-center gap-1.5">
          <GridToolbarColumnsButton />
          <GridToolbarFilterButton />
          <GridToolbarExport csvOptions={{ fileName: "squad" }} printOptions={{ hideFooter: true, hideToolbar: true }} />
        </Box>
      </Box>
    </Toolbar>
  );
}
