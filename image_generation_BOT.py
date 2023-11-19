import discord
import re
import os
import requests
from io import BytesIO
from PIL import Image
from openai import OpenAI
from datetime import datetime
import argparse

# urlから画像をダウンロードして保存する関数
def download_image(url, save_directory, prompt):
    response = requests.get(url)
    
    if response.status_code == 200:
        
        image_content = BytesIO(response.content)
        
        # 現在の日時から一意のファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # promptをファイル名に含める
        file_name = prompt+ f"image_{timestamp}.png"
        
        save_path = f"{save_directory}/{file_name}"
        
        # 画像ファイルが開けなかった場合はNoneを返す
        try :
            image = Image.open(image_content)
            
        except:
            print(f":エラー: 画像が読み取れませんでした。")
            
            return None
        
        
        image.save(save_path)
        print(f"画像を {save_path} に保存しました。")
        
        return save_path
        
    else:
        print(f"エラー: {response.status_code}")
        
        return None


### 設定 ###

# OpenAIクライアントの作成
os.environ["OPENAI_API_KEY"] = "YOUR API KEY"
openai_client = OpenAI()

# Discordクライアントの作成
TOKEN = "YOUR DISCORD BOT TOKEN"
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
discord_client = discord.Client(intents=intents)


# ログインした時にコマンドラインに通知する
@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user.name}')


# メインの処理
@discord_client.event
async def on_message(message):
    
    # メッセージの送信者がボット自体の場合は無視
    if message.author == discord_client.user:
        return

    if discord_client.user in message.mentions:
        
        # メンション部分を削除
        prompt = re.sub(r'<@!?\d+>', '', message.content)

        # 画像を生成
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        
        save_directory = '/images'  # 画像を保存する場所，必要に応じて変更してください
        
        save_path = download_image(image_url, save_directory, prompt)
        
        if save_path is None:
            await message.channel.send("エラーが発生しました．")
        
        else :
            # 画像をDiscordに送信
            await message.channel.send(file=discord.File(save_path))

if __name__ == "__main__":
    discord_client.run(TOKEN)
