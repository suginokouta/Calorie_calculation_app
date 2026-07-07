import os
from notion_client import Client
from datetime import datetime, timezone, timedelta

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
                    "カロリー(kcal)": {
                        "number": int(calories) 
                    },
                    "記録日時": {
                        "date": {
                            "start": self.__get_current_date()
                        }
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Notion書き込みエラー: {e}")
            return False
    
    def __get_current_date(self):
        """現在の日付を取得する"""
        jst = timezone(timedelta(hours=9))  # 日本標準時 (JST)
        now = datetime.now(jst)
        return now.isoformat()