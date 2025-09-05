import { useLayoutContext } from "@/components/layout/layout-context";

export default function MenuBackdrop() {
  const { resetLeftMenu, leftShowBackdrop } = useLayoutContext();

  const handleOnClick = () => {
    if (leftShowBackdrop) {
      resetLeftMenu();
    }
  };

  return (
    <>{leftShowBackdrop && <div className="absolute inset-0 top-0 left-0 z-0" onClick={() => handleOnClick()}></div>}</>
  );
}
