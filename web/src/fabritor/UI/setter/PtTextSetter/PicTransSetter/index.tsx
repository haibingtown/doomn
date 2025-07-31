import { useContext, useEffect, useState } from 'react';
import { GloablStateContext } from '@/context';
import { LockOutlined, UnlockOutlined, CopyOutlined, DeleteOutlined, PicCenterOutlined, AlignLeftOutlined, AlignCenterOutlined, AlignRightOutlined, VerticalAlignTopOutlined, VerticalAlignMiddleOutlined, VerticalAlignBottomOutlined } from '@ant-design/icons';
import { SKETCH_ID } from '@/utils/constants';
import { CenterV } from '@/fabritor/components/Center';
import { copyObject, pasteObject, removeObject } from '@/utils/helper';
import { Divider } from 'antd';
import { useTranslation, Trans } from '@/utils/i18n';
import { Form, Radio } from 'antd';

const { Item: FormItem } = Form;

export default function PicTransSetter () {
  const { object, editor } = useContext(GloablStateContext);
  const { t } = useTranslation();
  const [form] = Form.useForm();

  const handleValuesChange = (values) => {
    
    const keys = Object.keys(values);
    if (!keys?.length) return;

    for (let key of keys) {

        if (key == 'picTrans'){
          const isTransable = values[key] === 1;
          object.setTransable(isTransable); // 使用方法更新状态
        }
    }
    
    editor.canvas.requestRenderAll();
    editor.fireCustomModifiedEvent();
  }

  useEffect(() => {
    if (object) {
      form.setFieldsValue({
        picTrans: object.transable ? 1 : 2,
      });
    }
  }, [object]);

  if (!object || object.id === SKETCH_ID) return null;

  return (
    <>
    <Form
      colon={false}
      form={form}
      onValuesChange={handleValuesChange}
    >
      {/* <span style={{ fontWeight: 'bold', margin: '0, 0, 0, 32px'}}>翻译设置</span> */}
      <FormItem
          name="picTrans"
          label="是否翻译"
        >
          <Radio.Group>
            <Radio value={1}>是</Radio>
            <Radio value={2}>否</Radio>
          </Radio.Group>
        </FormItem>
      {/* <Divider style={{ margin: '16px 0' }} /> */}
    </Form>
    </>
  )
}