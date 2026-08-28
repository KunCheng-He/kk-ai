import { readFileSync } from "node:fs";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const NAMESPACE = "ext.pi-agent-switcher";

type Bundle = {
  version: 1;
  namespace: string;
  locale: string;
  messages: Record<string, string>;
};

type I18nApi = {
  t(key: string, params?: Record<string, string | number>): string;
};

function loadBundle(locale: string): Bundle {
  return JSON.parse(
    readFileSync(new URL(`./locales/${locale}.json`, import.meta.url), "utf-8"),
  ) as Bundle;
}

function format(text: string, params?: Record<string, string | number>): string {
  return text.replace(/\{(\w+)\}/g, (_, key: string) =>
    params?.[key] === undefined ? `{${key}}` : String(params[key]),
  );
}

export function createTranslator(
  pi: Pick<ExtensionAPI, "events">,
): (key: string, params?: Record<string, string | number>) => string {
  const bundles = [loadBundle("en"), loadBundle("fr")];
  const english = bundles[0]!.messages;
  let i18n: I18nApi | undefined;

  pi.events.emit("pi-i18n/requestApi", {
    reply: (api: I18nApi) => {
      i18n = api;
    },
  });

  if (i18n) {
    for (const bundle of bundles) pi.events.emit("pi-i18n/registerBundle", bundle);
  }

  return (key, params) =>
    i18n ? i18n.t(`${NAMESPACE}.${key}`, params) : format(english[key] ?? key, params);
}
