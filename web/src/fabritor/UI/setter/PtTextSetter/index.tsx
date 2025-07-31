import { useContext, useEffect, useState } from 'react';
import { fabric } from 'fabric';
import { Form, Select } from 'antd';
import { FONT_PRESET_FAMILY_LIST } from '@/utils/constants';
import { GloablStateContext } from '@/context';
import FontStyleSetter from './FontStyleSetter';
import AlignSetter from './AlignSetter';
import ColorSetter from '../ColorSetter';
import { loadFont, transformColors2Fill, transformFill2Colors } from '@/utils';
import { FunctionOutlined, RightOutlined } from '@ant-design/icons';
import SliderInputNumber from '@/fabritor/components/SliderInputNumber';
import { Switch,Input,Typography } from "antd";
import { useTranslation } from '@/utils/i18n';
import PicTransSetter from './PicTransSetter';
import Divider from 'antd/lib/divider';

const { Item: FormItem } = Form;
const { TextArea } = Input;
const { Title } = Typography;

export default function PtTextSetter () {
  const { object, editor }= useContext(GloablStateContext);
  const [form] = Form.useForm();
  const [openFx, setOpenFx] = useState(false);
  const { t } = useTranslation();
  const [ ptText, setPtText] = useState(null);
  const [ transable, setTransable] = useState(true);

  const TEXT_ADVANCE_CONFIG = [
    {
      icon: <FunctionOutlined style={{ fontSize: 22 }} />,
      label: t('setter.text.fx.title'),
      key: 'fx',
      onClick: () => { setOpenFx(true) }
    }
  ]

  // const handleTransable = (_transable) => {
  //   setTransable(_transable);
  //   object.setTransable(_transable)
  // }
    

  const handleFontStyles = (styles) => {
    ptText.set({
      fontWeight: styles?.bold ? 'bold' : 'normal',
      fontStyle: styles?.italic ? 'italic' : 'normal',
      underline: !!styles.underline,
      linethrough: !!styles.linethrough
    });
  }

  const handleFill = (_fill) => {
    let fill = transformColors2Fill(_fill);
    // text gradient nor support percentage https://github.com/fabricjs/fabric.js/issues/8168  
    if (typeof fill !== 'string') {
      fill.gradientUnits = 'pixels';
      const { coords } = fill;
      fill.coords = {
        x1: coords.x1 === 1 ? ptText.width : 0,
        y1: coords.y1 === 1 ? ptText.height : 0,
        x2: coords.x2 === 1 ? ptText.width : 0,
        y2: coords.y2 === 1 ? ptText.height : 0,
        r1: 0,
        r2: ptText.width > ptText.height ? ptText.width / 2  : ptText.height
      }
    }
    if (typeof fill !== 'string') {
      fill = new fabric.Gradient(fill);
    }
    ptText.set({ fill });
  }

  const handleValuesChange = async (values) => {
    const keys = Object.keys(values);
    if (!keys?.length) return;

    for (let key of keys) {
      if (key === 'fontStyles') {
        handleFontStyles(values[key]);
      } else if (key === 'transable'){
        setTransable(values[key])
        object.set('transable', values[key])
      }else if (key === 'fontFamily') {
        try {
          await loadFont(values[key]);
        } finally {
          ptText.set(key, values[key]);
        }
      } else if (key === 'fill') {
        handleFill(values[key]);
      } else {
        const selectedText = ptText.getSelectedText();
        if (selectedText && key === 'fill') {
          ptText.setSelectionStyles({ fill: values[key] });
        } else {
          ptText.set('styles', {});
          ptText.set(key, values[key]);
        }
      }

      if (key !== 'fontSize' && key !== 'lineHeight' && key !== 'charSpacing') {
        editor.fireCustomModifiedEvent();
      }
    }
   
    editor.canvas.requestRenderAll();
  }

  useEffect(() => {
    const dptt = (object as fabric.DPtText)
    const ptText = dptt.getTextLayer()
    setPtText(ptText)
    setTransable(dptt.transable)

    form.setFieldsValue({
      transable: dptt.transable,
      text: ptText.text,
      origin_text: ptText.extra.from_text,
      fontFamily: ptText.fontFamily,
      fontSize: ptText.fontSize,
      fill: transformFill2Colors(ptText.fill),
      textAlign: ptText.textAlign,
      lineHeight: ptText.lineHeight,
      charSpacing: ptText.charSpacing,
      fontStyles: {
        bold: ptText.fontWeight === 'bold',
        italic: ptText.fontStyle === 'italic',
        underline: ptText.underline,
        linethrough: ptText.linethrough
      }
    });
  }, [object]);

  return (
    <>
      <Form
          form={form}
          onValuesChange={handleValuesChange}
          colon={false}
        >
      <FormItem name="transable" label={t('setter.text.is_traslate')}>
        <Switch checked={transable} defaultChecked/>
      </FormItem>

      <FormItem name="origin_text" label={t('setter.text.origin')}>
        <Title level={5}>{ptText?.extra?.from_text}</Title>
      </FormItem>

      <FormItem name="text" label={t('setter.text.translate')}>
        <TextArea disabled={!transable}></TextArea>
      </FormItem>
      {transable?(
          <>
          <Divider />
          
          <FormItem
            name="fontFamily"
            label={t('setter.text.font_family')}
          >
            <Select
              options={FONT_PRESET_FAMILY_LIST} />
          </FormItem><FormItem
            name="fontSize"
            label={t('setter.text.font_size')}
          >
              <SliderInputNumber max={400} onChangeComplete={() => { editor.fireCustomModifiedEvent(); } } />
            </FormItem><FormItem
              name="fill"
              label={t('setter.text.fill')}
            >
              <ColorSetter type="fontColor" defaultColor="#000000" />
            </FormItem><FormItem
              name="textAlign"
              label={t('setter.text.text_align')}
            >
              <AlignSetter />
            </FormItem><FormItem
              name="fontStyles"
              label={t('setter.text.font_styles')}
            >
              <FontStyleSetter />
            </FormItem><FormItem
              name="charSpacing"
              label={t('setter.text.char_spacing')}
            >
              <SliderInputNumber
                min={-200}
                max={800}
                onChangeComplete={() => { editor.fireCustomModifiedEvent(); } } />
            </FormItem><FormItem
              name="lineHeight"
              label={t('setter.text.line_height')}
            >
              <SliderInputNumber
                min={0.5}
                max={2.5}
                step={0.01}
                onChangeComplete={() => { editor.fireCustomModifiedEvent(); } } />
            </FormItem></>
      ):null}
      </Form>
    </>
  )
}