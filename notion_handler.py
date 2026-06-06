import os
from notion_client import Client

class NotionHandler:
    def __init__(self):
        # .envからNotionの設定を読み込む
        notion_api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        # Notionクライアントの初期化
        self.notion = Client(auth=notion_api_key)

    def add_record(self, menu_name, calories):
        """Notionのデータベースに食事記録を追加する"""
        try:
            self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "メニュー名": {
                        "title": [
                            {
                                "text": {
                                    "content": menu_name
                                }
                            }
                        ]
                    },
                    "カロリー (kcal)": {
                        "number": int(calories) 
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Notion書き込みエラー: {e}")
            return False