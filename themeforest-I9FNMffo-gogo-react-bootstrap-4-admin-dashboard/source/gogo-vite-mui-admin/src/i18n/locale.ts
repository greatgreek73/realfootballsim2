import Cookies from "js-cookie";

import { DEFAULTS } from "@/config";
import { COOKIE_KEYS, LocaleOption } from "@/constants";
import i18n from "@/i18n/i18n";

// Get client locale from cookie
export function getClientLocale(): LocaleOption {
  return (Cookies.get(COOKIE_KEYS.locale) as LocaleOption) || DEFAULTS.locale;
}

// Set client locale in cookie
export function setClientLocale(locale: LocaleOption) {
  i18n.changeLanguage(locale);
  Cookies.set(COOKIE_KEYS.locale, locale, { sameSite: "lax" });
}
