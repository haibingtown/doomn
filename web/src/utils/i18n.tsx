// src/i18n.ts
import React, { createContext, useContext, useEffect, useState } from "react";
import i18n from 'i18next';
import { I18nextProvider, initReactI18next, Trans, useTranslation } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';
import Cookies from 'js-cookie';
import { parse } from 'tldts';

const getCookieDomain = (): string => {
  const parsed = parse(window.location.hostname);
  return parsed.domain ? `.${parsed.domain}` : window.location.hostname;
};

i18n
  .use(HttpBackend) // 加载翻译文件
  .use(LanguageDetector) // 自动语言检测
  .use(initReactI18next) // React 绑定
  .init({
    fallbackLng: 'en', // 默认语言
    debug: true,
    interpolation: {
      escapeValue: false, // 防止 XSS（i18next 已处理）
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json', // 翻译文件路径
    },
    // 配置命名空间
    defaultNS: 'common', // 默认命名空间
  });

export { i18n, Trans, useTranslation };

export const translate = (key: string) => {
  return i18n.t(key);
}

export interface I18nContextProps {
  currentLanguage: string;
  changeLanguage: (language: string) => void;
}

// 创建上下文
const I18nContext = createContext<I18nContextProps | undefined>(undefined);

// 封装 I18nProvider
export const I18nProvider: React.FC<{ children: React.ReactNode, ns?:string[] }> = ({ children, ns = ['common'] }) => {
  const [currentLanguage, setCurrentLanguage] = useState<string>(() => {
    // 从 cookie 加载语言，默认是 'en'
    return Cookies.get('locale') || 'en';
  });

  useEffect(() => {
    if (i18n.language !== currentLanguage) {
      i18n.changeLanguage(currentLanguage);
    }
  }, [currentLanguage]);

  useEffect(() => {
    const loadNamespaces = async () => {
      const unloadedNamespaces = (ns ?? []).filter((namespace) => 
        !i18n.hasResourceBundle(i18n.language, namespace)
      );
  
      if (unloadedNamespaces.length > 0) {
        try {
          await i18n.loadNamespaces(unloadedNamespaces);
        } catch (error) {
          console.error(`Failed to load namespaces: ${unloadedNamespaces.join(', ')}`, error);
        }
      }
    };
  
    loadNamespaces();
  }, [ns]);

  const changeLanguage = (language: string) => {
    setCurrentLanguage(language);
    i18n.changeLanguage(language);
    // 将语言设置到根域名的 cookie 中，设置 1 年过期时间
    Cookies.set('locale', language, { domain: getCookieDomain(), path: '/', expires: 365 });
  };

  return (
    <I18nextProvider i18n={i18n}>
      <I18nContext.Provider value={{ currentLanguage, changeLanguage}}>
        {children}
      </I18nContext.Provider>
    </I18nextProvider>
  );
};

// 自定义 Hook 用于消费 I18nContext
export const useI18n = (): I18nContextProps => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};