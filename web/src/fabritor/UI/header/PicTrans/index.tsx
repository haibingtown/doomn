import { Dropdown, Button, message, FloatButton, Modal, Select, Upload } from 'antd';
import { ExportOutlined, FileOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { downloadFile, base64ToBlob } from '@/utils';
import { useContext, useRef, useState } from 'react';
import { GloablStateContext, useEditorContext } from '@/context';
import LocalFileSelector from '@/fabritor/components/LocalFileSelector';
import { CenterV } from '@/fabritor/components/Center';
import { LOCALE_CHANGE_ENABLE, SETTER_WIDTH } from '@/config';
import { Trans, translate, useTranslation } from '@/utils/i18n';
import LocalesSwitch from '@/fabritor/components/LocalesSwitch';
import { saveDesign, uploadImage, translateImage, BASE_URL } from '@/utils/api';
import { convert } from '@/utils/parser';
import { fabric } from 'fabric';

const i18nKeySuffix = 'header.trans';

const items: MenuProps['items'] = [
  'jpg', 
  'png',
  'divider', 
  'clipboard',
  'cloud'].map(
  item => item === 'divider' ? ({ type: 'divider' }) : ({ key: item, label: <Trans i18nKey={`${i18nKeySuffix}.${item}`} /> })
)

export default function PicTrans () {
  const { editor, setReady, setActiveObject } = useContext(GloablStateContext);
  const { design_uid } = useEditorContext()
  const localFileSelectorRef = useRef<any>();
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sourceLang, setSourceLang] = useState('zh');
  const [targetLang, setTargetLang] = useState('en');
  const [uploading, setUploading] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);

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

  const handleOk = async () => {
    if (!imageFile) {
      message.warning(t(`${i18nKeySuffix}.uploadWarning`));
      return;
    }

    setUploading(true);
    try {
      // First upload the image
      const uploadResponse = await uploadImage(imageFile);
      // Then translate the image
      const translateResponse = await translateImage({
        from_lan: sourceLang,
        to_lan: targetLang,
        image_url: uploadResponse.image_url
      });

      if (translateResponse?.content) {
        const fabricJson = JSON.stringify(translateResponse.content);
        localStorage.setItem('fabritor_web_json', fabricJson);
        window.location.reload()
        message.success(t(`${i18nKeySuffix}.success`));
      }
    } catch (error) {
      message.error(t(`${i18nKeySuffix}.error`));
    } finally {
      setUploading(false);
      setIsModalOpen(false);
    }
  };

  const beforeUpload = (file: File) => {
    setImageFile(file);
    return false;
  };

  return (
    <>
      <CenterV
        justify="flex-end"
        gap={16}
        style={{
          width: SETTER_WIDTH,
          paddingRight: 16
        }}
      >
        <Button 
          type="primary" 
          icon={<ExportOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          {t(`${i18nKeySuffix}.export`)}
        </Button>
      </CenterV>

      <Modal
        title={t(`${i18nKeySuffix}.modalTitle`)}
        open={isModalOpen}
        onOk={handleOk}
        confirmLoading={uploading}
        onCancel={() => setIsModalOpen(false)}
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>{t(`${i18nKeySuffix}.sourceLang`)}</div>
          <Select
            style={{ width: '100%' }}
            value={sourceLang}
            onChange={setSourceLang}
            options={[
              { value: 'en', label: 'English' },
              { value: 'zh', label: '中文' }
            ]}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>{t(`${i18nKeySuffix}.targetLang`)}</div>
          <Select
            style={{ width: '100%' }}
            value={targetLang}
            onChange={setTargetLang}
            options={[
              { value: 'en', label: 'English' },
              { value: 'zh', label: '中文' }
            ]}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>{t(`${i18nKeySuffix}.uploadImage`)}</div>
          <Upload
            accept="image/*"
            beforeUpload={beforeUpload}
            showUploadList={false}
          >
            <Button block>
              {imageFile ? imageFile.name : t(`${i18nKeySuffix}.selectImage`)}
            </Button>
          </Upload>
        </div>
      </Modal>
    </>
  )
}
