import { NextureIconsProps, sizeHelper, strokeSizeHelper } from "../nexture-icons";

export default function NiPinPlus({
  className,
  variant = "outlined",
  size = "medium",
  oneTone = false,
}: NextureIconsProps) {
  const iconSize = sizeHelper(size);
  const iconStrokeWidth = strokeSizeHelper(iconSize);

  if (variant === "outlined") {
    return (
      <svg
        width={iconSize}
        height={iconSize}
        className={className}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M4 10.1387C4 -0.712954 20 -0.712873 20 10.1387C20 14.6372 16.6052 18.7326 14.2386 21.0411C12.9735 22.2751 11.0269 22.2752 9.76181 21.0412C7.39504 18.7327 4 14.6373 4 10.1387Z"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M9.49952 9.99982H14.4995M11.9999 7.49951L11.9999 12.4995"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
      </svg>
    );
  } else {
    return (
      <svg
        width={iconSize}
        height={iconSize}
        className={className}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M12 1.25C14.1633 1.25001 16.3492 1.98303 18.0029 3.47852C19.6695 4.9856 20.75 7.22674 20.75 10.1387C20.75 12.5743 19.8325 14.8591 18.6465 16.8018C17.4583 18.7479 15.9724 20.3982 14.7627 21.5781C13.2063 23.0962 10.7947 23.0961 9.23828 21.5781C8.02851 20.3981 6.5418 18.748 5.35352 16.8018C4.16745 14.8591 3.25 12.5743 3.25 10.1387C3.25002 7.22672 4.3305 4.9856 5.99707 3.47852C7.65082 1.98303 9.83667 1.25 12 1.25ZM12 6.75C11.586 6.7502 11.25 7.08591 11.25 7.5V9.25H9.5C9.08589 9.25 8.75016 9.58593 8.75 10C8.75 10.4142 9.08579 10.75 9.5 10.75H11.25V12.5C11.25 12.9141 11.5859 13.2498 12 13.25C12.414 13.2498 12.75 12.9141 12.75 12.5V10.75H14.5C14.914 10.7497 15.25 10.4141 15.25 10C15.2498 9.58609 14.9139 9.25026 14.5 9.25H12.75V7.5C12.75 7.08595 12.414 6.75027 12 6.75Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 0 : 0.4}
          d="M11.2495 12.5L11.2495 10.75H9.49953C9.08532 10.75 8.74953 10.4142 8.74953 10C8.74969 9.58593 9.08541 9.25 9.49952 9.25H11.2495L11.2495 7.5C11.2495 7.08591 11.5855 6.7502 11.9995 6.75C12.4137 6.75 12.7495 7.08579 12.7495 7.5L12.7495 9.25H14.4995C14.9136 9.25 15.2494 9.58593 15.2495 10C15.2495 10.4142 14.9137 10.75 14.4995 10.75H12.7495L12.7495 12.5C12.7495 12.9142 12.4138 13.25 11.9995 13.25C11.5855 13.2498 11.2495 12.9141 11.2495 12.5Z"
          fill="currentColor"
        />
      </svg>
    );
  }
}
