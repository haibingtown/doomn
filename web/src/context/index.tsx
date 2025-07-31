import { createContext, useContext, useEffect, useState } from 'react';
import { fabric } from 'fabric';
import Editor from '@/editor';
import { useTranslation, useI18n } from '@/utils/i18n';
import { ConfigProvider, Spin } from 'antd';
import dayjs from 'dayjs';
import enUS from 'antd/locale/en_US';
import zhCN from 'antd/locale/zh_CN';
import type { Locale } from 'antd/es/locale';
import { useSearchParams } from 'react-router-dom';
import { convert } from '@/utils/parser';
import { loadDesign } from '@/utils/api';


export interface IGloablStateContext {
  object?: fabric.Object | null | undefined;
  setActiveObject?: (o: fabric.Object) => void;
  isReady?: boolean;
  setReady?: (o: boolean) => void;
  editor?: Editor;
  roughSvg?: any;
}

export const GloablStateContext = createContext<IGloablStateContext>(null);

export interface EditorContextType {
    // profile: Profile,
    design_uid?: string,
}

// 创建AppContext
export const EditorContext = createContext<EditorContextType | undefined>(undefined);


// 获取 AppContext 的 Hook
export const useEditorContext = (): EditorContextType => {
    const context = useContext(EditorContext);
    if (!context) {
        throw new Error("useAppContext must be used within an AppProvider");
    }
    return context;
};

interface EditorContextProviderProps {
  children: React.ReactNode;
}

export const EditorContextProvider: React.FC<EditorContextProviderProps> = ({ children }) => {
  const { currentLanguage } = useI18n()
  // const {profile, loading} = useAuthContext()
  const { i18n } = useTranslation();
  const [searchParams] = useSearchParams();
  const json_url = searchParams.get('f');
  const source = searchParams.get('s');
  const design_uid = searchParams.get('d');

  
  const [antDLocale, setAntDLocale] = useState<Locale>(undefined);
  const [isTaskLoaded, setIsTaskLoaded] = useState(false); // 用于跟踪任务是否加载

  const loadJsonFile = async (json_url) => {
    try{
      // Fetch JSON data from the URL
      const jsonResponse = await fetch(json_url);
      if (!jsonResponse.ok) {
        throw new Error(`JSON API response not OK: ${jsonResponse.status}`);
      }
      const json = await jsonResponse.json();

      var _json = convert(json, source)

      const fabricJson = JSON.stringify(_json);
      localStorage.setItem('fabritor_web_json', fabricJson);
      
    } catch (error) {
      console.error('Error fetching task or JSON:', error);
    } finally{
      setIsTaskLoaded(true);
    }
  }

  const loadD = async (id) => {      
    try {
      const design = await loadDesign(id)
      const fabricJson = JSON.stringify(design);
      localStorage.setItem('fabritor_web_json', fabricJson);
    } catch (error) {
      console.error('Error fetching task or JSON:', error);
    } finally {
      setIsTaskLoaded(true);
    }
  }

  useEffect(() => {
    handleLanguageChange(currentLanguage)
  }, [currentLanguage])

  useEffect(() => {
    if (design_uid) {
      loadD(design_uid);
    } else if (json_url) {
      loadJsonFile(json_url);
    }
  }, [design_uid, json_url]);

  const handleLanguageChange = (lng: string) => {
    dayjs.locale(lng);
    if (lng === 'en-US') {
      setAntDLocale(enUS);
    } else {
      setAntDLocale(zhCN);
    }
  };

  useEffect(() => {
    i18n.on('languageChanged', handleLanguageChange);
    handleLanguageChange(i18n.language)
    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, []);

  // 仅在任务加载完成后渲染配置
  if ( (design_uid || json_url) && !isTaskLoaded) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="Loading task data..." />
      </div>
    );
  }

  return (
    <EditorContext.Provider value={{ design_uid }}>
      <ConfigProvider locale={antDLocale}>
        {children}
      </ConfigProvider>
    </EditorContext.Provider>
  );
};
