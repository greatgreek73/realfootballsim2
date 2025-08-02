import { TablePagination, TablePaginationProps } from "@mui/material";
import MuiPagination from "@mui/material/Pagination";
import { gridPageCountSelector, useGridApiContext, useGridSelector } from "@mui/x-data-grid-pro";

import NiChevronDownSmall from "@/icons/nexture/ni-chevron-down-small";

function Pagination({
  page,
  onPageChange,
  className,
}: Pick<TablePaginationProps, "page" | "onPageChange" | "className">) {
  const apiRef = useGridApiContext();
  const pageCount = useGridSelector(apiRef, gridPageCountSelector);

  return (
    <MuiPagination
      variant="text"
      size="small"
      className={className}
      count={pageCount as number}
      page={page + 1}
      onChange={(event, newPage) => {
        onPageChange(event as never, newPage - 1);
      }}
    />
  );
}

export default function DataGridPagination(props: any) {
  return (
    <TablePagination
      {...props}
      component="div"
      ActionsComponent={Pagination}
      slotProps={{
        displayedRows: { className: "hidden!" },
        spacer: { className: "flex-none" },
        toolbar: { className: "px-0 flex justify-end" },
        selectLabel: {
          className: "hidden!",
        },
        select: {
          IconComponent: () => {
            return (
              <NiChevronDownSmall size="medium" className="pointer-events-none absolute right-1"></NiChevronDownSmall>
            );
          },
          className: "hidden!",
        },
      }}
    />
  );
}

function PaginationFullPage({
  page,
  onPageChange,
  className,
}: Pick<TablePaginationProps, "page" | "onPageChange" | "className">) {
  const apiRef = useGridApiContext();
  const pageCount = useGridSelector(apiRef, gridPageCountSelector);

  return (
    <MuiPagination
      variant="text"
      size="medium"
      className={className}
      count={pageCount as number}
      page={page + 1}
      onChange={(event, newPage) => {
        onPageChange(event as never, newPage - 1);
      }}
    />
  );
}

export function DataGridPaginationFullPage(props: any) {
  return (
    <TablePagination
      {...props}
      component="div"
      ActionsComponent={(props) => {
        return <PaginationFullPage {...props} className="surface-standard" />;
      }}
      slotProps={{
        displayedRows: { className: "hidden!" },
        spacer: { className: "flex-none" },
        toolbar: { className: "px-0 flex justify-end" },
        select: {
          IconComponent: () => {
            return (
              <NiChevronDownSmall size="medium" className="pointer-events-none absolute right-1"></NiChevronDownSmall>
            );
          },
        },
      }}
    />
  );
}
