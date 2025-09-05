import { forwardRef, Ref, useState } from "react";

import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import {
  TreeItem,
  TreeItemLabelInput,
  TreeItemProps,
  UseTreeItemLabelInputSlotOwnProps,
  useTreeItemUtils,
} from "@mui/x-tree-view";
import { TreeViewBaseItem } from "@mui/x-tree-view/models";
import { RichTreeView } from "@mui/x-tree-view/RichTreeView";

import NiCheckSquare from "@/template_full/icons/nexture/ni-check-square";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronRightSmall from "@/template_full/icons/nexture/ni-chevron-right-small";
import NiCrossHexagon from "@/template_full/icons/nexture/ni-cross-hexagon";

type ExtendedTreeItemProps = {
  editable?: boolean;
  id: string;
  label: string;
};

const MUI_X_PRODUCTS: TreeViewBaseItem<ExtendedTreeItemProps>[] = [
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

const ERRORS = {
  REQUIRED: "The label cannot be empty",
  INVALID: "The label cannot contain digits",
};

interface CustomLabelInputProps extends UseTreeItemLabelInputSlotOwnProps {
  error: null | keyof typeof ERRORS;
}

function CustomLabelInput(props: Omit<CustomLabelInputProps, "ref">) {
  const { error, ...other } = props;

  return (
    <>
      <TreeItemLabelInput {...other} />
      {error ? (
        <Tooltip title={ERRORS[error]}>
          <NiCrossHexagon className="text-error" />
        </Tooltip>
      ) : (
        <Tooltip title="All good!">
          <NiCheckSquare className="text-success" />
        </Tooltip>
      )}
    </>
  );
}

const CustomTreeItem2 = forwardRef(function CustomTreeItem2(props: TreeItemProps, ref: Ref<HTMLLIElement>) {
  const [error, setError] = useState<null | keyof typeof ERRORS>(null);
  const { interactions } = useTreeItemUtils({
    itemId: props.itemId,
    children: props.children,
  });
  const validateLabel = (label: string) => {
    if (!label) {
      setError("REQUIRED");
    } else if (/\d/.test(label)) {
      setError("INVALID");
    } else {
      setError(null);
    }
  };

  const handleInputBlur: UseTreeItemLabelInputSlotOwnProps["onBlur"] = (event) => {
    if (error) {
      event.defaultMuiPrevented = true;
    }
  };

  const handleInputKeyDown: UseTreeItemLabelInputSlotOwnProps["onKeyDown"] = (event) => {
    event.defaultMuiPrevented = true;
    const target = event.target as HTMLInputElement;

    if (event.key === "Enter" && target.value) {
      if (error) {
        return;
      }
      setError(null);
      interactions.handleSaveItemLabel(event, target.value);
    } else if (event.key === "Escape") {
      setError(null);
      interactions.handleCancelItemLabelEditing(event);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    validateLabel(event.target.value);
  };

  return (
    <TreeItem
      {...props}
      ref={ref}
      slots={{ labelInput: CustomLabelInput }}
      slotProps={{
        labelInput: {
          onBlur: handleInputBlur,
          onKeyDown: handleInputKeyDown,
          onChange: handleInputChange,
          error,
        } as CustomLabelInputProps,
      }}
    />
  );
});

export default function EditingValidation() {
  return (
    <Box className="min-w-72">
      <RichTreeView
        items={MUI_X_PRODUCTS}
        isItemEditable
        defaultExpandedItems={["grid", "pickers"]}
        slots={{
          item: CustomTreeItem2,
          collapseIcon: () => {
            return <NiChevronDownSmall size={"small"}></NiChevronDownSmall>;
          },
          expandIcon: () => {
            return <NiChevronRightSmall size={"small"}></NiChevronRightSmall>;
          },
        }}
      />
    </Box>
  );
}

