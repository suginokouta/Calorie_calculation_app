import io
from PIL import Image, ImageOps

def resize_image(image_bytes: bytes, max_size: int = 800) -> Image.Image:
    """
    LINEから取得した画像のバイナリデータを受け取り、トークン節約のために
    リサイズ（圧縮）してGemini APIに直接渡せる形式（PIL.Image）で返す関数
    """
    
    # バイナリデータをPILのImageオブジェクトに変換
    image = Image.open(io.BytesIO(image_bytes))

    # 画像の向きを正しくする（EXIF情報に基づいて回転）
    image = ImageOps.exif_transpose(image)
    
    # 画像をリサイズして最大サイズを指定（例: 800x800）
    image.thumbnail((max_size, max_size))

    return image
