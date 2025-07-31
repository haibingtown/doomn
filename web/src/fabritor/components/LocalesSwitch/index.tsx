import { useI18n } from '@/utils/i18n';
import { Button } from 'antd';
import { useSearchParams } from 'react-router-dom';

export default function LocalesSwitch () {

  const { currentLanguage, changeLanguage } = useI18n()

  const switchLocale = () => {
    changeLanguage(currentLanguage === 'en' ? 'zh' : 'en');
  }

  return (
    <Button
      shape="circle"
      style={{
        backgroundColor: '#fff', 
        width: 40, 
        height: 40,
        border: 'none',
        // boxShadow: '0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
        fontSize: 16,
        fontWeight: 'bold'
      }}
      onClick={switchLocale}
    >
      { currentLanguage === 'en' ? 'En' : '中' }
    </Button>
  )
}