import { useState } from "react";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { TreeViewBaseItem } from "@mui/x-tree-view/models";
import { RichTreeViewPro, RichTreeViewProProps } from "@mui/x-tree-view-pro/RichTreeViewPro";

import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";

const MUI_X_PRODUCTS: TreeViewBaseItem[] = [
  {
    id: "grid",
    label: "Data Grid",
    children: [
      { id: "grid-community", label: "@mui/x-data-grid" },
      { id: "grid-pro", label: "@mui/x-data-grid-pro" },
      { id: "grid-premium", label: "@mui/x-data-grid-premium" },
    ],
  },
  {
    id: "pickers",
    label: "Date and Time Pickers",
    children: [
      { id: "pickers-community", label: "@mui/x-date-pickers" },
      { id: "pickers-pro", label: "@mui/x-date-pickers-pro" },
    ],
  },
  {
    id: "charts",
    label: "Charts",
    children: [{ id: "charts-community", label: "@mui/x-charts" }],
  },
  {
    id: "tree-view",
    label: "Tree View",
    children: [{ id: "tree-view-community", label: "@mui/x-tree-view" }],
  },
];

export default function ItemPositionChange() {
  const [lastReorder, setLastReorder] = useState<
    Parameters<NonNullable<RichTreeViewProProps<any, any>["onItemPositionChange"]>>[0] | null
  >(null);

  return (
    <Box className="flex flex-col gap-4">
      {lastReorder == null ? (
        <Typography>No reorder registered yet</Typography>
      ) : (
        <Typography>
          Last reordered item: {lastReorder.itemId}
          <br />
          Position before: {lastReorder.oldPosition.parentId ?? "root"} (index {lastReorder.oldPosition.index})<br />F
          Position after: {lastReorder.newPosition.parentId ?? "root"} (index {lastReorder.newPosition.index})
        </Typography>
      )}
      <Box className="min-w-72">
        <RichTreeViewPro
          items={MUI_X_PRODUCTS}
          itemsReordering
          defaultExpandedItems={["grid", "pickers"]}
          onItemPositionChange={(params) => setLastReorder(params)}
          slots={{
            collapseIcon: () => {
              return <NiChevronDownSmall size={"small"}></NiChevronDownSmall>;
            },
            expandIcon: () => {
              return <NiChevronRightSmall size={"small"}></NiChevronRightSmall>;
            },
          }}
        />
      </Box>
    </Box>
  );
}

