import { createFTextClass } from './FText';
import { createFImageClass } from './FImage';
import { createFLineClass } from './FLine';
import { createFArrowClass, createFTriArrowClass } from './FArrow';
import { createPicTransTextClass } from './DPtText'
import { createFSVGClass } from './FSvg';

export default function () {
  createFTextClass();
  createFImageClass();
  createFLineClass();
  createFArrowClass();
  createFTriArrowClass();
  createPicTransTextClass();
  createFSVGClass();
}