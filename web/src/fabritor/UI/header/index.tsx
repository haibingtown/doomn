import { FloatButton, Layout } from 'antd';
import Toolbar from './Toolbar';
import Export from './Export';
import Logo from './Logo';
import BaseInfo from './BaseInfo';
import { CenterV } from '@/fabritor/components/Center';
import { LOCALE_CHANGE_ENABLE } from '@/config';
import LocalesSwitch from '@/fabritor/components/LocalesSwitch';
import PicTrans from './PicTrans';

const { Header} = Layout;

const headerStyle: React.CSSProperties = {
  padding: 0,
  height: 50,
  backgroundColor: '#fff',
  display: 'flex',
  alignItems: 'center',
  borderBottom: '1px solid #e8e8e8'
};

export default function () {
  return (
    <Header style={headerStyle}>
      <Logo />
      <CenterV
        justify="space-between"
        style={{ flex: 1 }}
      >
        {/* <BaseInfo /> */}
        <Toolbar />
      </CenterV>
      <PicTrans />
      <Export />
    </Header>
  )
}