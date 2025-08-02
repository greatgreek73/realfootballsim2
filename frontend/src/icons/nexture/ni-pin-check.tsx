import { NextureIconsProps, sizeHelper, strokeSizeHelper } from "../nexture-icons";

export default function NiPinCheck({
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
          d="M15 8.5L11.8423 12.0979C11.6514 12.3154 11.3162 12.3259 11.112 12.1206L9.5 10.5"
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
          d="M12 1.25C14.1633 1.25001 16.3492 1.98303 18.0029 3.47852C19.6695 4.9856 20.75 7.22674 20.75 10.1387C20.75 12.5743 19.8325 14.8591 18.6465 16.8018C17.4583 18.7479 15.9724 20.3982 14.7627 21.5781C13.2063 23.0962 10.7947 23.0961 9.23828 21.5781C8.02851 20.3981 6.5418 18.748 5.35352 16.8018C4.16745 14.8591 3.25 12.5743 3.25 10.1387C3.25002 7.22672 4.3305 4.9856 5.99707 3.47852C7.65082 1.98303 9.83667 1.25 12 1.25ZM15.4951 7.93652C15.2033 7.68044 14.7686 7.69149 14.4902 7.9502L14.4365 8.00488L11.4551 11.4014L10.0322 9.9707C9.74013 9.67705 9.26438 9.67571 8.9707 9.96777C8.67713 10.2599 8.67574 10.7356 8.96777 11.0293L10.5801 12.6494C11.0904 13.1623 11.9289 13.1365 12.4062 12.5928L15.5635 8.99512L15.6113 8.93457C15.8318 8.62515 15.7866 8.19274 15.4951 7.93652Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 0 : 0.4}
          d="M15.4951 7.93632C15.7867 8.19252 15.8318 8.6249 15.6113 8.93437L15.5634 8.99491L12.4062 12.5926C11.9289 13.1365 11.0904 13.1623 10.58 12.6492L8.96774 11.0291C8.67568 10.7354 8.67702 10.2597 8.97067 9.96757C9.26435 9.67551 9.7401 9.67684 10.0322 9.9705L11.455 11.4012L14.4365 8.00468L14.4902 7.94999C14.7685 7.69129 15.2033 7.68024 15.4951 7.93632Z"
          fill="currentColor"
        />
      </svg>
    );
  }
}
