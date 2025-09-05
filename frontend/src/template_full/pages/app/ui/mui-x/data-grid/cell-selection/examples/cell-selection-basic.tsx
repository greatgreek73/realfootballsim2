import { Box, Button, FormControl, InputLabel, Select, SelectProps } from "@mui/material";
import { useDemoData } from "@mui/x-data-grid-generator";
import { DataGridPremium, GridAiAssistantPanel } from "@mui/x-data-grid-premium";

import NiAI from "@/template_full/icons/nexture/ni-ai";
import NiArrowDown from "@/template_full/icons/nexture/ni-arrow-down";
import NiArrowInDown from "@/template_full/icons/nexture/ni-arrow-in-down";
import NiArrowUp from "@/template_full/icons/nexture/ni-arrow-up";
import NiBinEmpty from "@/template_full/icons/nexture/ni-bin-empty";
import NiCheck from "@/template_full/icons/nexture/ni-check";
import NiChevronDownSmall from "@/template_full/icons/nexture/ni-chevron-down-small";
import NiChevronLeftRightSmall from "@/template_full/icons/nexture/ni-chevron-left-right-small";
import NiChevronUpSmall from "@/template_full/icons/nexture/ni-chevron-up-small";
import NiClock from "@/template_full/icons/nexture/ni-clock";
import NiCols from "@/template_full/icons/nexture/ni-cols";
import NiCross from "@/template_full/icons/nexture/ni-cross";
import NiEllipsisVertical from "@/template_full/icons/nexture/ni-ellipsis-vertical";
import NiEndDownSmall from "@/template_full/icons/nexture/ni-end-down-small";
import NiEndUpSmall from "@/template_full/icons/nexture/ni-end-up-small";
import NiEyeInactive from "@/template_full/icons/nexture/ni-eye-inactive";
import NiFilter from "@/template_full/icons/nexture/ni-filter";
import NiFilterPlus from "@/template_full/icons/nexture/ni-filter-plus";
import NiGroup from "@/template_full/icons/nexture/ni-group";
import NiMicrophone from "@/template_full/icons/nexture/ni-microphone";
import NiPivot from "@/template_full/icons/nexture/ni-pivot";
import NiPlus from "@/template_full/icons/nexture/ni-plus";
import NiPushPinLeft from "@/template_full/icons/nexture/ni-push-pin-left";
import NiPushPinRight from "@/template_full/icons/nexture/ni-push-pin-right";
import NiSearch from "@/template_full/icons/nexture/ni-search";
import NiSendUpRight from "@/template_full/icons/nexture/ni-send-up-right";
import NiSum from "@/template_full/icons/nexture/ni-sum";
import NiUngroup from "@/template_full/icons/nexture/ni-ungroup";

export default function CellSelectionBasic() {
  const { data } = useDemoData({
    dataSet: "Commodity",
    rowLength: 10,
    maxColumns: 6,
  });

  return (
    <Box className="h-[500px] w-full">
      <DataGridPremium
        disableRowSelectionOnClick
        cellSelection
        {...data}
        className="border-none"
        hideFooter
        slots={{
          aiAssistantPanel: GridAiAssistantPanel,
          columnSortedDescendingIcon: () => {
            return <NiArrowDown size={"small"}></NiArrowDown>;
          },
          columnSortedAscendingIcon: () => {
            return <NiArrowUp size={"small"}></NiArrowUp>;
          },
          columnFilteredIcon: () => {
            return <NiFilterPlus size={"small"}></NiFilterPlus>;
          },
          columnReorderIcon: () => {
            return <NiChevronLeftRightSmall size={"small"}></NiChevronLeftRightSmall>;
          },
          columnMenuIcon: () => {
            return <NiEllipsisVertical size={"small"}></NiEllipsisVertical>;
          },
          columnMenuSortAscendingIcon: NiArrowUp,
          columnMenuSortDescendingIcon: NiArrowDown,
          columnMenuFilterIcon: NiFilter,
          columnMenuHideIcon: NiEyeInactive,
          columnMenuClearIcon: NiCross,
          columnMenuManageColumnsIcon: NiCols,
          columnMenuPinLeftIcon: NiPushPinLeft,
          columnMenuPinRightIcon: NiPushPinRight,
          columnMenuAggregationIcon: NiSum,
          columnMenuGroupIcon: NiGroup,
          columnMenuUngroupIcon: NiUngroup,
          filterPanelDeleteIcon: NiCross,
          filterPanelAddIcon: NiPlus,
          filterPanelRemoveAllIcon: NiBinEmpty,
          pivotIcon: NiPivot,
          columnSelectorIcon: NiCols,
          exportIcon: NiArrowInDown,
          openFilterButtonIcon: NiFilter,
          collapsibleIcon: NiChevronDownSmall,
          aiAssistantIcon: NiAI,
          aiAssistantPanelCloseIcon: NiCross,
          aiAssistantPanelHistoryIcon: NiClock,
          aiAssistantPanelNewConversationIcon: NiPlus,
          promptSendIcon: NiSendUpRight,
          promptSpeechRecognitionIcon: NiMicrophone,
          pivotMenuAddIcon: () => {
            return <NiPlus size={"small"}></NiPlus>;
          },
          pivotMenuCheckIcon: () => {
            return <NiCheck size={"small"}></NiCheck>;
          },
          pivotMenuMoveDownIcon: () => {
            return <NiChevronDownSmall size={"small"}></NiChevronDownSmall>;
          },
          pivotMenuMoveUpIcon: () => {
            return <NiChevronUpSmall size={"small"}></NiChevronUpSmall>;
          },
          pivotMenuMoveToBottomIcon: () => {
            return <NiEndDownSmall size={"small"}></NiEndDownSmall>;
          },
          pivotMenuMoveToTopIcon: () => {
            return <NiEndUpSmall size={"small"}></NiEndUpSmall>;
          },
          pivotMenuRemoveIcon: () => {
            return <NiCross size={"small"}></NiCross>;
          },
          pivotSearchIcon: () => {
            return <NiSearch size={"small"}></NiSearch>;
          },
          pivotSearchClearIcon: () => {
            return <NiCross size={"medium"} />;
          },
          baseSelect: (props) => {
            const propsCasted = props as SelectProps;
            return (
              <FormControl size="small" variant="outlined">
                <InputLabel>{props.label}</InputLabel>
                <Select {...propsCasted} IconComponent={NiChevronDownSmall} MenuProps={{ className: "outlined" }} />
              </FormControl>
            );
          },
          quickFilterIcon: () => {
            return <NiSearch size={"medium"} />;
          },
          quickFilterClearIcon: () => {
            return <NiCross size={"medium"} />;
          },
          baseButton: (props) => {
            return <Button {...props} variant="pastel" color="grey"></Button>;
          },
        }}
      />
    </Box>
  );
}

