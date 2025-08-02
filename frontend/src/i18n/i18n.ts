import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import { getClientLocale } from "@/i18n/locale";
import de from "@/i18n/messages/de.json";
import en from "@/i18n/messages/en.json";
import es from "@/i18n/messages/es.json";
import fr from "@/i18n/messages/fr.json";

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    de: { translation: de },
    es: { translation: es },
    fr: { translation: fr },
  },
  lng: getClientLocale(),
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
