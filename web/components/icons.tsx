"use client";

import type { ReactNode, SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function Base({ size = 24, children, ...props }: IconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export const HomeIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z" />
  </Base>
);

export const FeedIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M4 6h16M4 12h16M4 18h10" />
  </Base>
);

export const ChartIcon = (props: IconProps) => (
  <Base {...props} strokeWidth={2}>
    <path d="M5 20V10M12 20V4M19 20v-7" />
  </Base>
);

export const ClockIcon = (props: IconProps) => (
  <Base {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 7.5V12l3 2" />
  </Base>
);

export const SettingsIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M4 7h5M13 7h7M4 17h7M15 17h5" />
    <circle cx="11" cy="7" r="2.2" fill="currentColor" stroke="none" />
    <circle cx="13" cy="17" r="2.2" fill="currentColor" stroke="none" />
  </Base>
);

export const LockIcon = (props: IconProps) => (
  <Base {...props}>
    <rect x="5" y="10" width="14" height="10" rx="2.5" />
    <path d="M8.5 10V7.5a3.5 3.5 0 0 1 7 0V10" />
  </Base>
);

export const PinIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11z" />
    <circle cx="12" cy="10" r="2.5" />
  </Base>
);

export const HeartIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M20.8 8.6a5 5 0 0 0-8.8-3.2A5 5 0 0 0 3.2 8.6c0 5.4 8.8 10.4 8.8 10.4s8.8-5 8.8-10.4z" />
  </Base>
);

export const ChevronRightIcon = (props: IconProps) => (
  <Base {...props} size={props.size ?? 18}>
    <path d="m9 5 7 7-7 7" />
  </Base>
);

export const PlusIcon = (props: IconProps) => (
  <Base {...props} size={props.size ?? 18}>
    <path d="M12 5v14M5 12h14" />
  </Base>
);

export const SparkIcon = (props: IconProps) => (
  <Base {...props}>
    <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z" />
  </Base>
);

export const DownloadIcon = (props: IconProps) => (
  <Base {...props} size={props.size ?? 18}>
    <path d="M12 4v10m0 0 4-4m-4 4-4-4M5 20h14" />
  </Base>
);

export const TrashIcon = (props: IconProps) => (
  <Base {...props} size={props.size ?? 18}>
    <path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5" />
  </Base>
);

export const RefreshIcon = (props: IconProps) => (
  <Base {...props} size={props.size ?? 18}>
    <path d="M20 11a8 8 0 1 0-2.3 6.3M20 4v7h-7" />
  </Base>
);

export const XIcon = (props: IconProps) => (
  <Base {...props} size={props.size ?? 18}>
    <path d="M6 6l12 12M18 6 6 18" />
  </Base>
);
