import { NextureIconsProps, sizeHelper, strokeSizeHelper } from "../nexture-icons";

export default function NiCpu({
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
          d="M9.69863 18.6164C7.4861 18.2477 5.75232 16.5139 5.38356 14.3014V14.3014C5.12961 12.7776 5.12961 11.2224 5.38356 9.69863V9.69863C5.75232 7.4861 7.4861 5.75232 9.69863 5.38356V5.38356C11.2224 5.1296 12.7776 5.12961 14.3014 5.38356V5.38356C16.5139 5.75232 18.2477 7.4861 18.6164 9.69863V9.69863C18.8704 11.2224 18.8704 12.7776 18.6164 14.3014V14.3014C18.2477 16.5139 16.5139 18.2477 14.3014 18.6164V18.6164C12.7776 18.8704 11.2224 18.8704 9.69863 18.6164V18.6164Z"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M3 8L5 8"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M3 12L5 12"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M3 16L5 16"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M19 8L21 8"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M19 12L21 12"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M19 16L21 16"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M8 21L8 19"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M12 21L12 19"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M16 21L16 19"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M8 5L8 3"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M12 5L12 3"
          stroke="currentColor"
          strokeWidth={iconStrokeWidth}
          strokeLinecap="round"
        />
        <path
          opacity={oneTone ? 1 : 0.6}
          d="M16 5L16 3"
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
          d="M9.57467 4.64398C11.1799 4.37645 12.8191 4.37652 14.4243 4.64398C16.9528 5.0654 18.9343 7.04718 19.3559 9.57562C19.6235 11.181 19.6235 12.8199 19.3559 14.4252C18.9344 16.9538 16.9529 18.9354 14.4243 19.3569C12.8191 19.6244 11.1799 19.6244 9.57467 19.3569C7.04641 18.9352 5.06442 16.9536 4.64303 14.4252C4.37551 12.82 4.3755 11.1809 4.64303 9.57562C5.06454 7.04738 7.04648 5.06566 9.57467 4.64398Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M8 18.25C8.38817 18.25 8.70747 18.5449 8.74609 18.9229L8.75 19V21C8.75 21.4142 8.41421 21.75 8 21.75C7.58579 21.75 7.25 21.4142 7.25 21V19L7.25391 18.9229C7.29253 18.5449 7.61183 18.25 8 18.25Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M12 18.25C12.3882 18.25 12.7075 18.5449 12.7461 18.9229L12.75 19V21C12.75 21.4142 12.4142 21.75 12 21.75C11.5858 21.75 11.25 21.4142 11.25 21V19L11.2539 18.9229C11.2925 18.5449 11.6118 18.25 12 18.25Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M16 18.25C16.3882 18.25 16.7075 18.5449 16.7461 18.9229L16.75 19V21C16.75 21.4142 16.4142 21.75 16 21.75C15.5858 21.75 15.25 21.4142 15.25 21V19L15.2539 18.9229C15.2925 18.5449 15.6118 18.25 16 18.25Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M5.07715 15.2539C5.45512 15.2925 5.75 15.6118 5.75 16C5.75 16.3882 5.45512 16.7075 5.07715 16.7461L5 16.75H3C2.58579 16.75 2.25 16.4142 2.25 16C2.25 15.5858 2.58579 15.25 3 15.25H5L5.07715 15.2539Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M21.0771 15.2539C21.4551 15.2925 21.75 15.6118 21.75 16C21.75 16.3882 21.4551 16.7075 21.0771 16.7461L21 16.75H19C18.5858 16.75 18.25 16.4142 18.25 16C18.25 15.5858 18.5858 15.25 19 15.25H21L21.0771 15.2539Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M5.07715 11.2539C5.45512 11.2925 5.75 11.6118 5.75 12C5.75 12.3882 5.45512 12.7075 5.07715 12.7461L5 12.75H3C2.58579 12.75 2.25 12.4142 2.25 12C2.25 11.5858 2.58579 11.25 3 11.25H5L5.07715 11.2539Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M21.0771 11.2539C21.4551 11.2925 21.75 11.6118 21.75 12C21.75 12.3882 21.4551 12.7075 21.0771 12.7461L21 12.75H19C18.5858 12.75 18.25 12.4142 18.25 12C18.25 11.5858 18.5858 11.25 19 11.25H21L21.0771 11.2539Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M5.07715 7.25391C5.45512 7.29253 5.75 7.61183 5.75 8C5.75 8.38817 5.45512 8.70747 5.07715 8.74609L5 8.75H3C2.58579 8.75 2.25 8.41421 2.25 8C2.25 7.58579 2.58579 7.25 3 7.25H5L5.07715 7.25391Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M21.0771 7.25391C21.4551 7.29253 21.75 7.61183 21.75 8C21.75 8.38817 21.4551 8.70747 21.0771 8.74609L21 8.75H19C18.5858 8.75 18.25 8.41421 18.25 8C18.25 7.58579 18.5858 7.25 19 7.25H21L21.0771 7.25391Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M8 2.25C8.38817 2.25 8.70747 2.54488 8.74609 2.92285L8.75 3V5C8.75 5.41421 8.41421 5.75 8 5.75C7.58579 5.75 7.25 5.41421 7.25 5V3L7.25391 2.92285C7.29253 2.54488 7.61183 2.25 8 2.25Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M12 2.25C12.3882 2.25 12.7075 2.54488 12.7461 2.92285L12.75 3V5C12.75 5.41421 12.4142 5.75 12 5.75C11.5858 5.75 11.25 5.41421 11.25 5V3L11.2539 2.92285C11.2925 2.54488 11.6118 2.25 12 2.25Z"
          fill="currentColor"
        />
        <path
          opacity={oneTone ? 1 : 0.4}
          d="M16 2.25C16.3882 2.25 16.7075 2.54488 16.7461 2.92285L16.75 3V5C16.75 5.41421 16.4142 5.75 16 5.75C15.5858 5.75 15.25 5.41421 15.25 5V3L15.2539 2.92285C15.2925 2.54488 15.6118 2.25 16 2.25Z"
          fill="currentColor"
        />
      </svg>
    );
  }
}
