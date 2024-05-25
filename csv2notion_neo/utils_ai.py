import shutil, os
import logging
from tqdm import tqdm
from icecream import ic
import requests

logger = logging.getLogger(__name__)

class AI:

    def __init__(self,ai_data:dict) -> None:
        self.ai_data = ai_data
    
    def out(self,row) -> str:
        
        if 'caption' in self.ai_data:
            data = self.ai_data['caption']
            try:
                row[data['caption_column']] = self._img2caption(data['hftoken'],str(data['image_path']))
                return row
            except Exception as e:
                logger.error(f"Error during AI process : {e}")


    def _img2caption(self,token,image_url:str) -> str:
        try:
            sess = requests.session()
            file = open(image_url,'rb')
            filename = os.path.basename(image_url)
            tqdm.write(f"AI generating caption for image {filename}")

            caption = sess.post(
            'https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning',
            json='None',
            data=file,
            headers={'authorization': f'Bearer {token}'},
            cookies=None,
            timeout=None,
            stream=False
            )

            tqdm.write(f"Caption generated for image {filename} : {caption.json()[0]['generated_text']}")
            return caption.json()[0]['generated_text']
        except Exception as e:
            tqdm.write(f"Error generating caption for {filename}")
            logger.error(e,exc_info=1)




        
