import { Dropdown, Button, message, FloatButton } from 'antd';
import { ExportOutlined, FileOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { downloadFile, base64ToBlob } from '@/utils';
import { useContext, useRef } from 'react';
import { GloablStateContext, useEditorContext } from '@/context';
import LocalFileSelector from '@/fabritor/components/LocalFileSelector';
import { CenterV } from '@/fabritor/components/Center';
import { LOCALE_CHANGE_ENABLE, SETTER_WIDTH } from '@/config';
import { Trans, translate, useTranslation } from '@/utils/i18n';
import LocalesSwitch from '@/fabritor/components/LocalesSwitch';
import { saveDesign } from '@/utils/api';

const i18nKeySuffix = 'header.export';

const items: MenuProps['items'] = [
  'jpg', 
  'png',
  'divider', 
  'clipboard',
  'cloud'].map(
  item => item === 'divider' ? ({ type: 'divider' }) : ({ key: item, label: <Trans i18nKey={`${i18nKeySuffix}.${item}`} /> })
)

export default function Export () {
  const { editor, setReady, setActiveObject } = useContext(GloablStateContext);
  // const { workspace } = useContext(AuthStateContext)
  const { design_uid } = useEditorContext()
  const localFileSelectorRef = useRef<any>();
  const { t } = useTranslation();

  const selectJsonFile = () => {
    localFileSelectorRef.current?.start?.();
  }

  const handleFileChange = (file) => {
    setReady(false);
    const reader = new FileReader();
    reader.onload = (async (evt) => {
      const json = evt.target?.result as string;
      if (json) {
        await editor.loadFromJSON(json, true);
        editor.fhistory.reset();
        setReady(true);
        setActiveObject(null);
        editor.fireCustomModifiedEvent();
      }
    });
    reader.readAsText(file);
  }

  // const save2Cloud = async () => {
  //   try{
  //     const jpg = editor.export2Img({ format: 'jpg' });
  //     const blob = await base64ToBlob(jpg);
  //     // const {savedImages} = await saveImagesToOss({prefix: "editorX/previews", images:[blob]}).then()
  //     const json = editor.canvas2Json();
  //     await saveDesign(design_uid?? "", savedImages[0], json)
  //     message.success(translate(`${i18nKeySuffix}.save_success`));
  //   } catch(e) {
  //     message.error(translate(`${i18nKeySuffix}.save_fail`));
  //   }
  // }

  const copyImage = async () => {
    try {
      const png = editor.export2Img({ format: 'png' });
      const blob = await base64ToBlob(png);
      await navigator.clipboard.write([
        new ClipboardItem({
          'image/png': blob
        })
      ]);
      message.success(translate(`${i18nKeySuffix}.copy_success`));
    } catch(e) {
      message.error(translate(`${i18nKeySuffix}.copy_fail`));
    }
  }

  const handleClick = async ({ key }) => {
    const { sketch } = editor;
    // @ts-ignore
    const name = sketch.fabritor_desc;
    switch (key) {
      case 'png':
        const png = editor.export2Img({ format: 'png' });
        downloadFile(png, 'png', name);
        break;
      case 'jpg':
        const jpg = editor.export2Img({ format: 'jpg' });
        downloadFile(jpg, 'jpg', name);
        break;
      case 'svg':
        const svg = editor.export2Svg();
        downloadFile(svg, 'svg', name);
        break;
      // case 'json':
      //   // const json = editor.canvas2Json();
      //   const json_str = JSON.stringify(editor.canvas2Json(), null, 2)
      //   const preview = editor.export2Img({ format: 'jpg' });
      //   const { width, height } = editor.sketch
      //   await createTemplate({ params: {json: json_str, preview, width, height} })
      //   message.success('保存成功');
      //   break;
      case 'clipboard':
        copyImage();
        break;
      default:
        break;
    }
  }

  return (
    <CenterV
      justify="flex-end"
      gap={16}
      style={{
        width: SETTER_WIDTH,
        paddingRight: 16
      }}
    >
      {/* <Button onClick={selectJsonFile} icon={<FileOutlined />}>
        {t(`${i18nKeySuffix}.load`)}
      </Button> */}

      <Dropdown 
        menu={{ items, onClick: handleClick }} 
        arrow={{ pointAtCenter: true }}
        placement="bottom"
      >
        <Button type="primary" icon={<ExportOutlined />}>{t(`${i18nKeySuffix}.export`)}</Button>
      </Dropdown>
      <LocalFileSelector accept="application/json" ref={localFileSelectorRef} onChange={handleFileChange} />

      {LOCALE_CHANGE_ENABLE? <LocalesSwitch /> : ''}
    </CenterV>
  )
}