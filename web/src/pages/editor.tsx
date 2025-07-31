import Fabritor from '@/fabritor';
import { EditorContextProvider } from '@/context';

export default function Editor() {

  return (
      <EditorContextProvider>
        <Fabritor />
      </EditorContextProvider>
  )
}