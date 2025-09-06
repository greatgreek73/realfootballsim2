import base from "../../tailwind.config";
import type { Config } from "tailwindcss";

const config: Config = {
  // используем базовый конфиг проекта
  ...(base as Config),
  // гарантируем, что сканируются и файлы внутри template_full
  content: [
    ...(Array.isArray((base as any).content) ? (base as any).content : []),
    "./**/*.{ts,tsx,js,jsx,css,html,mdx}",
  ],
};

export default config;
