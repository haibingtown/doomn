// import { LOGO_ICON } from '@/assets/icon';
import { CenterV } from '@/fabritor/components/Center';
import { PANEL_WIDTH } from '@/config';
import { useTranslation } from '@/utils/i18n'

export default function Logo () {
  const { t } = useTranslation();
  return (
    <CenterV gap={5} style={{ width: PANEL_WIDTH, paddingLeft: 16 }}>
      <img src='/doomn.png' style={{ width: 56 }} />
      <span style={{ fontWeight: 'bold', fontSize: 14 }}>
        | {t('header.logo_desc')}
      </span>
    </CenterV>
  )
}