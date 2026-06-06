# シーズン管理をどうしよう
# 勝率計算が変な気がする
# お金がかかる
# 花婿人形がうまくいくか怪しい

import discord
import cv2
import numpy as np
import os
from discord.ext import commands
import asyncio
import psycopg2
from urllib.parse import urlparse

# 環境変数からトークンを取得
TOKEN = os.getenv("DISCORD_TOKEN")

# DiscordのBotクライアント設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容のアクセスを許可
bot = commands.Bot(command_prefix="!", intents=intents)

# 処理中の状態を保持する変数
is_processing = False

# テンプレート画像フォルダのパス
TEMPLATE_FOLDER_MAP = 'templates_map'
TEMPLATE_FOLDER_HUNTER = 'templates_hunter'
TEMPLATE_FOLDER_SURVIVOR = 'templates_survivor'
TEMPLATE_FOLDER_RESULT = 'templates_result'
TEMPLATE_FOLDER_DECODE = 'templates_decode'

# PostgreSQLデータベースへの接続
def connect_db():
    url = urlparse(os.getenv("DATABASE_URL"))
    conn = psycopg2.connect(
        database=url.path[1:],  # データベース名
        user=url.username,       # ユーザー名
        password=url.password,   # パスワード
        host=url.hostname,       # ホスト名
        port=url.port            # ポート
    )
    return conn

# マップ
async def process_map(input_gray):
    found_map = None
    map_name = None
    # マップ名とデータベース番号のマッピング
    map_mapping = {
        "軍需工場": "1",
        "聖心病院": "2",
        "赤の教会": "3",
        "湖景村": "4",
        "月の河公園": "5",
        "レオの思い出": "6",
        "永眠町": "7",
        "中華街": "8",
        "罪の森": "9",
        "不明": "0"
    }

    # マップ画像の判定
    for template_filename in os.listdir(TEMPLATE_FOLDER_MAP):
        template_path = os.path.join(TEMPLATE_FOLDER_MAP, template_filename)
        template_image = cv2.imread(template_path)

        if template_image is None:
            continue

        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(input_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.91    # 0.90だと誤認識した
        locations = np.where(result >= threshold)

        if len(locations[0]) > 0:
            found_map = template_filename.split('.')[0]
            map_name = {
                "Arms_Factory": "軍需工場",
                "Sacred_Heart_Hospital": "聖心病院",
                "The_Red_Church": "赤の教会",
                "Lakeside_Village": "湖景村",
                "Moonlit_River_Park": "月の河公園",
                "Leo's_Memory": "レオの思い出",
                "Eversleeping_Town": "永眠町",
                "China_Town": "中華街",
                "Darkwoods": "罪の森"
            }.get(found_map, "不明")

            # マップ番号を取得
            map_db = map_mapping.get(map_name, "0") # 0はただのデフォルト値
        
            # マッチした場合:結果を返す（関数を終了し、戻り値を返す）
            return map_name, map_db
    
    # マッチしなかった場合:結果を返す（関数を終了し、戻り値を返す）
    return "不明", "0"

# ハンター
async def process_hunter(input_gray):
    found_hunter = None
    hunter_name = None
    # ハンター名とデータベース番号のマッピング
    hunter_mapping = {
        "復讐者": "1", "道化師": "2", "断罪狩人": "3", "リッパー": "4", "結魂者": "5",
        "芸者": "6", "白黒無常": "7", "写真家": "8", "狂眼": "9", "黄衣の王": "10",
        "夢の魔女": "11", "泣き虫": "12", "魔トカゲ": "13", "血の女王": "14",
        "ガードNo.26": "15", "「使徒」": "16", "ヴァイオリニスト": "17", "彫刻師": "18",
        "「アンデッド」": "19", "破輪": "20", "漁師": "21", "蝋人形師": "22",
        "「悪夢」": "23", "書記官": "24", "隠者": "25", "夜の番人": "26",
        "オペラ歌手": "27", "「フールズ・ゴールド」": "28", "時空の影": "29",
        "「足萎えの羊」": "30", "「フラバルー」": "31", "不明": "0"
    }

    # ハンター画像の判定
    for template_filename in os.listdir(TEMPLATE_FOLDER_HUNTER):
        template_path = os.path.join(TEMPLATE_FOLDER_HUNTER, template_filename)
        template_image = cv2.imread(template_path)

        if template_image is None:
            continue
        
        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(input_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.90
        locations = np.where(result >= threshold)

        if len(locations[0]) > 0:
            found_hunter = template_filename.split('.')[0]
            hunter_name = {
                "Hell_Ember": "復讐者", "Hell_Ember2": "復讐者", "Hell_Ember3": "復讐者", "Smiley_Face": "道化師", "Gamekeeper": "断罪狩人",
                "The_Ripper": "リッパー", "Soul_Weaver": "結魂者", "Geisha": "芸者",
                "Wu_Chang": "白黒無常", "Photographer": "写真家", "Mad_Eyes": "狂眼",
                "The_Feaster": "黄衣の王", "Dream_Witch": "夢の魔女", "Axe_Boy": "泣き虫",
                "Evil_Reptilian": "魔トカゲ", "Bloody_Queen": "血の女王", "Guard_26": "ガードNo.26",
                "Disciple": "「使徒」", "Violinist": "ヴァイオリニスト", "Sculptor": "彫刻師",
                "Undead": "「アンデッド」", "The_Breaking_Wheel": "破輪", "Naiad": "漁師",
                "Wax_Artist": "蝋人形師", "Nightmare": "「悪夢」", "Clerk": "書記官",
                "Hermit": "隠者", "Night_Watch": "夜の番人", "Opera_Singer": "オペラ歌手",
                "Fool's_Gold": "「フールズ・ゴールド」", "The_Shadow": "時空の影",
                "Goatman": "「足萎えの羊」", "Hullabaloo": "「フラバルー」"
            }.get(found_hunter, "不明")

            # ハンター番号を取得
            hunter_db = hunter_mapping.get(hunter_name, "0")
            # マッチした場合:結果を返す（関数を終了し、戻り値を返す）
            return hunter_name, hunter_db
    
    # マッチしなかった場合:結果を返す（関数を終了し、戻り値を返す）
    return "不明", "0"
    
# リザルト
async def process_result(input_gray):
    found_result = None
    result_db = None
    # 勝敗名とデータベース番号のマッピング
    result_mapping = {
        "勝ち": "1",
        "負け": "2",
        "引分け": "3",
        "不明": "0"
    }

    # 勝敗画像の判定
    for template_filename in os.listdir(TEMPLATE_FOLDER_RESULT):
        template_path = os.path.join(TEMPLATE_FOLDER_RESULT, template_filename)
        template_image = cv2.imread(template_path)

        if template_image is None:
            continue

        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(input_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.90
        locations = np.where(result >= threshold)

        if len(locations[0]) > 0:
            found_result = template_filename.split('.')[0]
            result_name = {
                "win_1": "勝ち",
                "win_2": "勝ち",
                "win_3": "勝ち",
                "lose_1": "負け",
                "lose_2": "負け",
                "lose_3": "負け",
                "draw_1": "引分け",
                "draw_2": "引分け",
                "draw_3": "引分け"
            }.get(found_result, "不明")

            # リザルト番号を取得
            result_db = result_mapping.get(result_name, "0")
            # マッチした場合:結果を返す（関数を終了し、戻り値を返す）
            return result_name, result_db
    
    # マッチしなかった場合:結果を返す（関数を終了し、戻り値を返す）
    return "不明", "0"

# 通電
async def process_decode(input_gray):
    found_decode = None
    decode_db = None
    # 通電名とデータベース番号のマッピング
    decode_mapping = {
        "通電": "1",
        "未通電": "2",
        "不明": "0"
    }

    # 暗号機画像の判定
    for template_filename in os.listdir(TEMPLATE_FOLDER_DECODE):
        template_path = os.path.join(TEMPLATE_FOLDER_DECODE, template_filename)
        template_image = cv2.imread(template_path)

        if template_image is None:
            continue

        template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(input_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        threshold = 0.95
        locations = np.where(result >= threshold)

        if len(locations[0]) > 0:
            found_decode = template_filename.split('.')[0]
            decode_name = {
                "decode0_1": "通電",
                "decode0_2": "通電",
                # "decode0_3": "通電",
                # "decode0_4": "通電",
                # "decode0_5": "通電",
                "decode1_1": "未通電",
                # "decode1_2": "未通電",
                # "decode1_3": "未通電",
                # "decode1_4": "未通電",
                # "decode1_5": "未通電",
                "decode2_1": "未通電",
                # "decode2_2": "未通電",
                # "decode2_3": "未通電",
                # "decode2_4": "未通電",
                # "decode2_5": "未通電",
                "decode3_1": "未通電",
                # "decode3_2": "未通電",
                # "decode3_3": "未通電",
                # "decode3_4": "未通電",
                # "decode3_5": "通電",
                "decode4_1": "未通電",
                # "decode4_2": "未通電",
                # "decode4_3": "未通電",
                # "decode4_4": "未通電",
                # "decode4_5": "未通電",
                "decode5_1": "未通電",
                "decode5_2": "未通電",
                "decode5_3": "未通電"
                # "decode5_4": "未通電"
                # "decode5_5": "未通電"
            }.get(found_decode, "不明")

            # 通電番号を取得
            decode_db = decode_mapping.get(decode_name, "0")
            # マッチした場合:結果を返す（関数を終了し、戻り値を返す）
            return decode_name, decode_db
    
    # マッチしなかった場合:結果を返す（関数を終了し、戻り値を返す）
    return "不明", "0"

# !inputコマンド
@bot.command(name='input')
async def input(ctx, player_id:int):
    global is_processing    # これしないと、グローバル変数は変更できない

    # シーズン変更はここから
    season_num = 35

    # 処理中ならエラーメッセージを送信
    if is_processing:
        await ctx.send("現在処理中です。しばらく待ってからもう一度入力してください。")
        return
    
    # 処理を開始
    is_processing = True
    await ctx.send("処理を開始します。しばらくお待ちください。")

    # player_idが指定されていない場合のエラーメッセージ
    if not player_id:
        await ctx.send("プレイヤーIDを指定してください。例: `!input <player_id>`")
        return
    
    # メッセージに画像が添付されているか確認
    if not ctx.message.attachments:
        await ctx.send("画像ファイルを添付してください。")
        return

    try:
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()

        # 添付された画像を取得
        attachments = ctx.message.attachments
        response_messages = []

        for index, attachment in enumerate(attachments, start=1):
            img_data = await attachment.read()
            input_image = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)

            if input_image is None:
                response_messages.append(f"添付された画像 {attachment.filename} が読み込めませんでした。")
                continue


            # トリミングの範囲を指定
            top_crop = 185     # 上側のトリミング幅
            bottom_crop = 75  # 下側のトリミング幅
            left_crop = 740   # 左側のトリミング幅
            right_crop = 1275  # 右側のトリミング幅

            # トリミング処理
            input_image = input_image[top_crop:input_image.shape[0] - bottom_crop, 
                                       left_crop:input_image.shape[1] - right_crop]
            
            if input_image is None or input_image.size == 0:
                response_messages.append(f"画像 {attachment.filename} のトリミング処理に失敗しました。")
                continue

            input_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

            # サバイバー
            found_survivors = []
            survivor_name = None
            # サバイバー画像の判定（4人分の検出を実装）
            survivor_db = []  # サバイバー番号を格納するリストを初期化

            # サバイバー名と番号のマッピング
            survivor_mapping = {
                "Doctor": ("医師", "1"),
                "Lawyer": ("弁護士", "2"),
                "Thief": ("泥棒", "3"),
                "Gardener": ("庭師", "4"),
                "Magician": ("マジシャン", "5"),
                "Explorer": ("冒険家", "6"),
                "Mercenary": ("傭兵", "7"),
                "Coordinator": ("空軍", "8"),
                "Priestess": ("祭司", "9"),
                "Mecanic": ("機械技師", "10"),
                "Forward": ("オフェンス", "11"),
                "Forward2": ("オフェンス", "11"),
                "The_Mind's_Eyes": ("心眼", "12"),
                "Perfumer": ("調香師", "13"),
                "Cowboy": ("カウボーイ", "14"),
                "Female_Dancer": ("踊り子", "15"),
                "Seer": ("占い師", "16"),
                "Embalmer": ("納棺師", "17"),
                "Prospecter": ("探鉱者", "18"),
                "Enhantress": ("呪術師", "19"),
                "Wilding": ("野人", "20"),
                "Acrobat": ("曲芸師", "21"),
                "First_Officer": ("一等航海士", "22"),
                "Barmaid": ("バーメイド", "23"),
                "Postman": ("ポストマン", "24"),
                "Grave_Keeper": ("墓守", "25"),
                "Prisoner": ("「囚人」", "26"),
                "Entomologist": ("昆虫学者", "27"),
                "Painter": ("画家", "28"),
                "Batter": ("バッツマン", "29"),
                "Toy_Merchant": ("玩具職人", "30"),
                "Patient": ("患者", "31"),
                "Psychologist": ("「心理学者」", "32"),
                "Novelist": ("小説家", "33"),
                "Little_Girl": ("「少女」", "34"),
                "Weeping_Clown": ("泣きピエロ", "35"),
                "Professor": ("教授", "36"),
                "Antiquarian": ("骨董商", "37"),
                "Composer": ("作曲家", "38"),
                "Journalist": ("記者", "39"),
                "Aeroplanist": ("航空エンジニア", "40"),
                "Cheerleader": ("応援団", "41"),
                "Puppeteer": ("人形師", "42"),
                "Fire_Investigator": ("火災調査員", "43"),
                "Faro_Lady": ("「レディ・ファウロ」", "44"),
                "Knight": ("「騎士」", "45"),
                "Lucky_Guy": ("幸運児", "100"),
            }

            for template_filename in os.listdir(TEMPLATE_FOLDER_SURVIVOR):
                template_path = os.path.join(TEMPLATE_FOLDER_SURVIVOR, template_filename)
                template_image = cv2.imread(template_path)

                if template_image is None:
                    continue

                template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(input_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                threshold = 0.90
                locations = np.where(result >= threshold)

                if len(locations[0]) > 0:
                    found_survivor = template_filename.split('.')[0]
                    survivor_name, survivor_number = survivor_mapping.get(found_survivor, ("不明", "0"))
                    found_survivors.append(survivor_name)
                    survivor_db.append(survivor_number)

                    if len(survivor_db) == 4:
                        break  # 4人分検出したら終了
            
            # 出力結果を得る
            results = await asyncio.gather(process_map(input_gray), process_hunter(input_gray), process_result(input_gray), process_decode(input_gray))
            map_name, map_db = results[0]
            hunter_name, hunter_db = results[1]
            result_name, result_db = results[2]
            decode_name, decode_db = results[3]

            if result_db == "2" or result_db == "3":
                decode_name, decode_db = ["通電", "1"]
                # await ctx.send(f"１にした")

            for i in range(4):
                survivor_db.append("0")
                found_survivors.append("不明")
           
            # データを挿入し、挿入されたIDを取得
            cursor.execute(
                """
                INSERT INTO rank_match 
                (player_id, hunter, map, result, survivor1, survivor2, survivor3, survivor4, decode, season) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (player_id, hunter_db, map_db, result_db, survivor_db[0], survivor_db[1], survivor_db[2], survivor_db[3], decode_db, season_num)
            )

            # 挿入されたIDを取得
            inserted_id = cursor.fetchone()[0]
            print(f"挿入された行のID: {inserted_id}")

            conn.commit()

            # 個別の画像判定結果をメッセージに追加
            response_messages.append(
                f"{index}枚目の画像:\n試合ID: {inserted_id}\nマップ: {map_name or '不明'}\nハンター: {hunter_name or '不明'}\n"
                f"サバイバー: {', '.join(found_survivors[:4]) or '不明'}\n勝敗: {result_name or '不明'}\n{decode_name or '不明'}"
            )
        # 結果をメッセージとして送信
        await ctx.send("\n\n".join(response_messages))

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()
        is_processing = False
        await ctx.send("処理が完了しました！")

# !deleteコマンド
@bot.command(name='delete_ad')
async def delete_ad(ctx, id:int):
    try:
        # データベースに接続
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()

        # 指定されたIDが存在するか確認
        cursor.execute(f"SELECT * FROM rank_match WHERE id = %s", (id,))
        record = cursor.fetchone()

        if record:
            # 指定されたIDを削除
            cursor.execute(f"DELETE FROM rank_match WHERE id = %s", (id,))
            conn.commit()
            await ctx.send(f"試合ID: {id} のデータを削除しました。")
        else:
            await ctx.send(f"試合ID: {id} のデータは存在しません。")

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()


# !delete_adコマンド
@bot.command(name='delete')
async def delete(ctx, player_id:int, id:int):
    try:
        # データベースに接続
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()

        # 指定されたIDが存在するか確認
        cursor.execute(f"SELECT * FROM rank_match WHERE id = %s", (id,))
        record = cursor.fetchone()

        if record:
            if record[1] == player_id:
                # 指定されたIDを削除
                cursor.execute(f"DELETE FROM rank_match WHERE id = %s", (id,))
                conn.commit()
                await ctx.send(f"試合ID: {id} のデータを削除しました。")
            else:
                print(f"その試合ID: {id} はプレイヤーID: {player_id} の試合ではありません。")
        else:
            await ctx.send(f"試合ID: {id} のデータは存在しません。")

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()


# !output_allコマンド
@bot.command(name='output_all')
async def output_all(ctx, player_id:int):
    try:
        # データベースに接続
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()
        
    # 試合数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s", (player_id,))
        result = cursor.fetchone()
        if result is not None:        
            match_count = result[0]
        else:
            match_count = 0
        # マップ
        map_match_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s", (player_id, i))
            result = cursor.fetchone()
            if result is not None:
                map_match_count.append(result[0])
            else:
                map_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_match_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, i, i, i, i))
            result = cursor.fetchone()
            if result is not None:
                survivor_match_count.append(result[0])
            else:
                survivor_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, 100, 100, 100, 100))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_count = result[0]
        else:
            lucky_guy_count = 0

    # 勝利数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND result = %s", (player_id, 1))
        result = cursor.fetchone()
        if result is not None:
            win_count = result[0]
        else:
            win_count = 0
        # マップ
        map_win_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND result = %s", (player_id, i, 1))
            result = cursor.fetchone()
            if result is not None:
                map_win_count.append(result[0])
            else:
                map_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_win_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, i, i, i, i, 1))
            result = cursor.fetchone()
            if result is not None:
                survivor_win_count.append(result[0])
            else:
                survivor_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, 100, 100, 100, 100, 1))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_win_count = result[0]
        else:
            lucky_guy_win_count = 0
    
    #引分け数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND result = %s", (player_id, 3))
        result = cursor.fetchone()
        if result is not None:
            draw_count = result[0]
        else:
            draw_count = 0
        # マップ
        map_draw_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND result = %s", (player_id, i, 3))
            result = cursor.fetchone()
            if result is not None:
                map_draw_count.append(result[0])
            else:
                map_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_draw_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, i, i, i, i, 3))
            result = cursor.fetchone()
            if result is not None:
                survivor_draw_count.append(result[0])
            else:
                survivor_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, 100, 100, 100, 100, 3))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_draw_count = result[0]
        else:
            lucky_guy_draw_count = 0

    # 通電数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND decode = %s", (player_id, 1))
        result = cursor.fetchone()
        if result is not None:        
            decode_count = result[0]
        else:
            decode_count = 0
        # マップ
        map_decode_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND decode = %s", (player_id, i, 1))
            result = cursor.fetchone()
            if result is not None:
                map_decode_count.append(result[0])
            else:
                map_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_decode_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, i, i, i, i, 1))
            result = cursor.fetchone()
            if result is not None:
                survivor_decode_count.append(result[0])
            else:
                survivor_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, 100, 100, 100, 100, 1))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_decode_count = result[0]
        else:
            lucky_guy_decode_count = 0

        embed1 = discord.Embed(
            title=f"1/3\nプレイヤーID: {player_id}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed1.add_field(name="全体", value=f"```試合数: {match_count}\n勝率: {win_rate(match_count, win_count, draw_count):.2f}%\n通電率: {decode_rate(match_count, decode_count):.2f}%```")
        embed1.add_field(name="軍需工場", value=f"```試合数: {map_match_count[1]}\n勝率: {win_rate(map_match_count[1], map_win_count[1], map_draw_count[1]):.2f}%\n通電率: {decode_rate(map_match_count[1], map_decode_count[1]):.2f}%```")
        embed1.add_field(name="聖心病院", value=f"```試合数: {map_match_count[2]}\n勝率: {win_rate(map_match_count[2], map_win_count[2], map_draw_count[2]):.2f}%\n通電率: {decode_rate(map_match_count[2], map_decode_count[2]):.2f}%```")
        embed1.add_field(name="赤の教会", value=f"```試合数: {map_match_count[3]}\n勝率: {win_rate(map_match_count[3], map_win_count[3], map_draw_count[3]):.2f}%\n通電率: {decode_rate(map_match_count[3], map_decode_count[3]):.2f}%```")
        embed1.add_field(name="湖景村", value=f"```試合数: {map_match_count[4]}\n勝率: {win_rate(map_match_count[4], map_win_count[4], map_draw_count[4]):.2f}%\n通電率: {decode_rate(map_match_count[4], map_decode_count[4]):.2f}%```")
        embed1.add_field(name="月の河公園", value=f"```試合数: {map_match_count[5]}\n勝率: {win_rate(map_match_count[5], map_win_count[5], map_draw_count[5]):.2f}%\n通電率: {decode_rate(map_match_count[5], map_decode_count[5]):.2f}%```")
        embed1.add_field(name="レオの思い出", value=f"```試合数: {map_match_count[6]}\n勝率: {win_rate(map_match_count[6], map_win_count[6], map_draw_count[6]):.2f}%\n通電率: {decode_rate(map_match_count[6], map_decode_count[6]):.2f}%```")
        embed1.add_field(name="永眠町", value=f"```試合数: {map_match_count[7]}\n勝率: {win_rate(map_match_count[7], map_win_count[7], map_draw_count[7]):.2f}%\n通電率: {decode_rate(map_match_count[7], map_decode_count[7]):.2f}%```")
        embed1.add_field(name="中華街", value=f"```試合数: {map_match_count[8]}\n勝率: {win_rate(map_match_count[8], map_win_count[8], map_draw_count[8]):.2f}%\n通電率: {decode_rate(map_match_count[8], map_decode_count[8]):.2f}%```")
        embed1.add_field(name="罪の森", value=f"```試合数: {map_match_count[9]}\n勝率: {win_rate(map_match_count[9], map_win_count[9], map_draw_count[9]):.2f}%\n通電率: {decode_rate(map_match_count[9], map_decode_count[9]):.2f}%```")
        embed1.add_field(name="マップ不明", value=f"```試合数: {map_match_count[0]}\n勝率: {win_rate(map_match_count[0], map_win_count[0], map_draw_count[0]):.2f}%\n通電率: {decode_rate(map_match_count[0], map_decode_count[0]):.2f}%```")

        embed2 = discord.Embed(
            title=f"2/3\nプレイヤーID: {player_id}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed2.add_field(name="医師", value=f"```試合数: {survivor_match_count[1]}\n勝率: {win_rate(survivor_match_count[1], survivor_win_count[1], survivor_draw_count[1]):.2f}%\n通電率: {decode_rate(survivor_match_count[1], survivor_decode_count[1]):.2f}%```")
        embed2.add_field(name="弁護士", value=f"```試合数: {survivor_match_count[2]}\n勝率: {win_rate(survivor_match_count[2], survivor_win_count[2], survivor_draw_count[2]):.2f}%\n通電率: {decode_rate(survivor_match_count[2], survivor_decode_count[2]):.2f}%```")
        embed2.add_field(name="泥棒", value=f"```試合数: {survivor_match_count[3]}\n勝率: {win_rate(survivor_match_count[3], survivor_win_count[3], survivor_draw_count[3]):.2f}%\n通電率: {decode_rate(survivor_match_count[3], survivor_decode_count[3]):.2f}%```")
        embed2.add_field(name="庭師", value=f"```試合数: {survivor_match_count[4]}\n勝率: {win_rate(survivor_match_count[4], survivor_win_count[4], survivor_draw_count[4]):.2f}%\n通電率: {decode_rate(survivor_match_count[4], survivor_decode_count[4]):.2f}%```")
        embed2.add_field(name="マジシャン", value=f"```試合数: {survivor_match_count[5]}\n勝率: {win_rate(survivor_match_count[5], survivor_win_count[5], survivor_draw_count[5]):.2f}%\n通電率: {decode_rate(survivor_match_count[5], survivor_decode_count[5]):.2f}%```")
        embed2.add_field(name="冒険家", value=f"```試合数: {survivor_match_count[6]}\n勝率: {win_rate(survivor_match_count[6], survivor_win_count[6], survivor_draw_count[6]):.2f}%\n通電率: {decode_rate(survivor_match_count[6], survivor_decode_count[6]):.2f}%```")
        embed2.add_field(name="傭兵", value=f"```試合数: {survivor_match_count[7]}\n勝率: {win_rate(survivor_match_count[7], survivor_win_count[7], survivor_draw_count[7]):.2f}%\n通電率: {decode_rate(survivor_match_count[7], survivor_decode_count[7]):.2f}%```")
        embed2.add_field(name="空軍", value=f"```試合数: {survivor_match_count[8]}\n勝率: {win_rate(survivor_match_count[8], survivor_win_count[8], survivor_draw_count[8]):.2f}%\n通電率: {decode_rate(survivor_match_count[8], survivor_decode_count[8]):.2f}%```")
        embed2.add_field(name="祭司", value=f"```試合数: {survivor_match_count[9]}\n勝率: {win_rate(survivor_match_count[9], survivor_win_count[9], survivor_draw_count[9]):.2f}%\n通電率: {decode_rate(survivor_match_count[9], survivor_decode_count[9]):.2f}%```")
        embed2.add_field(name="機械技師", value=f"```試合数: {survivor_match_count[10]}\n勝率: {win_rate(survivor_match_count[10], survivor_win_count[10], survivor_draw_count[10]):.2f}%\n通電率: {decode_rate(survivor_match_count[10], survivor_decode_count[10]):.2f}%```")
        embed2.add_field(name="オフェンス", value=f"```試合数: {survivor_match_count[11]}\n勝率: {win_rate(survivor_match_count[11], survivor_win_count[11], survivor_draw_count[11]):.2f}%\n通電率: {decode_rate(survivor_match_count[11], survivor_decode_count[11]):.2f}%```")
        embed2.add_field(name="心眼", value=f"```試合数: {survivor_match_count[12]}\n勝率: {win_rate(survivor_match_count[12], survivor_win_count[12], survivor_draw_count[12]):.2f}%\n通電率: {decode_rate(survivor_match_count[12], survivor_decode_count[12]):.2f}%```")
        embed2.add_field(name="調香師", value=f"```試合数: {survivor_match_count[13]}\n勝率: {win_rate(survivor_match_count[13], survivor_win_count[13], survivor_draw_count[13]):.2f}%\n通電率: {decode_rate(survivor_match_count[13], survivor_decode_count[13]):.2f}%```")
        embed2.add_field(name="カウボーイ", value=f"```試合数: {survivor_match_count[14]}\n勝率: {win_rate(survivor_match_count[14], survivor_win_count[14], survivor_draw_count[14]):.2f}%\n通電率: {decode_rate(survivor_match_count[14], survivor_decode_count[14]):.2f}%```")
        embed2.add_field(name="踊り子", value=f"```試合数: {survivor_match_count[15]}\n勝率: {win_rate(survivor_match_count[15], survivor_win_count[15], survivor_draw_count[15]):.2f}%\n通電率: {decode_rate(survivor_match_count[15], survivor_decode_count[15]):.2f}%```")
        embed2.add_field(name="占い師", value=f"```試合数: {survivor_match_count[16]}\n勝率: {win_rate(survivor_match_count[16], survivor_win_count[16], survivor_draw_count[16]):.2f}%\n通電率: {decode_rate(survivor_match_count[16], survivor_decode_count[16]):.2f}%```")
        embed2.add_field(name="納棺師", value=f"```試合数: {survivor_match_count[17]}\n勝率: {win_rate(survivor_match_count[17], survivor_win_count[17], survivor_draw_count[17]):.2f}%\n通電率: {decode_rate(survivor_match_count[17], survivor_decode_count[17]):.2f}%```")
        embed2.add_field(name="探鉱者", value=f"```試合数: {survivor_match_count[18]}\n勝率: {win_rate(survivor_match_count[18], survivor_win_count[18], survivor_draw_count[18]):.2f}%\n通電率: {decode_rate(survivor_match_count[18], survivor_decode_count[18]):.2f}%```")
        embed2.add_field(name="呪術師", value=f"```試合数: {survivor_match_count[19]}\n勝率: {win_rate(survivor_match_count[19], survivor_win_count[19], survivor_draw_count[19]):.2f}%\n通電率: {decode_rate(survivor_match_count[19], survivor_decode_count[19]):.2f}%```")
        embed2.add_field(name="野人", value=f"```試合数: {survivor_match_count[20]}\n勝率: {win_rate(survivor_match_count[20], survivor_win_count[20], survivor_draw_count[20]):.2f}%\n通電率: {decode_rate(survivor_match_count[20], survivor_decode_count[20]):.2f}%```")
        embed2.add_field(name="曲芸師", value=f"```試合数: {survivor_match_count[21]}\n勝率: {win_rate(survivor_match_count[21], survivor_win_count[21], survivor_draw_count[21]):.2f}%\n通電率: {decode_rate(survivor_match_count[21], survivor_decode_count[21]):.2f}%```")
        embed2.add_field(name="一等航海士", value=f"```試合数: {survivor_match_count[22]}\n勝率: {win_rate(survivor_match_count[22], survivor_win_count[22], survivor_draw_count[22]):.2f}%\n通電率: {decode_rate(survivor_match_count[22], survivor_decode_count[22]):.2f}%```")
        embed2.add_field(name="バーメイド", value=f"```試合数: {survivor_match_count[23]}\n勝率: {win_rate(survivor_match_count[23], survivor_win_count[23], survivor_draw_count[23]):.2f}%\n通電率: {decode_rate(survivor_match_count[23], survivor_decode_count[23]):.2f}%```")
        embed2.add_field(name="ポストマン", value=f"```試合数: {survivor_match_count[24]}\n勝率: {win_rate(survivor_match_count[24], survivor_win_count[24], survivor_draw_count[24]):.2f}%\n通電率: {decode_rate(survivor_match_count[24], survivor_decode_count[24]):.2f}%```")
        
        embed3 = discord.Embed(
            title=f"3/3\nプレイヤーID: {player_id}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed3.add_field(name="墓守", value=f"```試合数: {survivor_match_count[25]}\n勝率: {win_rate(survivor_match_count[25], survivor_win_count[25], survivor_draw_count[25]):.2f}%\n通電率: {decode_rate(survivor_match_count[25], survivor_decode_count[25]):.2f}%```")
        embed3.add_field(name="「囚人」", value=f"```試合数: {survivor_match_count[26]}\n勝率: {win_rate(survivor_match_count[26], survivor_win_count[26], survivor_draw_count[26]):.2f}%\n通電率: {decode_rate(survivor_match_count[26], survivor_decode_count[26]):.2f}%```")
        embed3.add_field(name="昆虫学者", value=f"```試合数: {survivor_match_count[27]}\n勝率: {win_rate(survivor_match_count[27], survivor_win_count[27], survivor_draw_count[27]):.2f}%\n通電率: {decode_rate(survivor_match_count[27], survivor_decode_count[27]):.2f}%```")
        embed3.add_field(name="画家", value=f"```試合数: {survivor_match_count[28]}\n勝率: {win_rate(survivor_match_count[28], survivor_win_count[28], survivor_draw_count[28]):.2f}%\n通電率: {decode_rate(survivor_match_count[28], survivor_decode_count[28]):.2f}%```")
        embed3.add_field(name="バッツマン", value=f"```試合数: {survivor_match_count[29]}\n勝率: {win_rate(survivor_match_count[29], survivor_win_count[29], survivor_draw_count[29]):.2f}%\n通電率: {decode_rate(survivor_match_count[29], survivor_decode_count[29]):.2f}%```")
        embed3.add_field(name="玩具職人", value=f"```試合数: {survivor_match_count[30]}\n勝率: {win_rate(survivor_match_count[30], survivor_win_count[30], survivor_draw_count[30]):.2f}%\n通電率: {decode_rate(survivor_match_count[30], survivor_decode_count[30]):.2f}%```")
        embed3.add_field(name="患者", value=f"```試合数: {survivor_match_count[31]}\n勝率: {win_rate(survivor_match_count[31], survivor_win_count[31], survivor_draw_count[31]):.2f}%\n通電率: {decode_rate(survivor_match_count[31], survivor_decode_count[31]):.2f}%```")
        embed3.add_field(name="「心理学者」", value=f"```試合数: {survivor_match_count[32]}\n勝率: {win_rate(survivor_match_count[32], survivor_win_count[32], survivor_draw_count[32]):.2f}%\n通電率: {decode_rate(survivor_match_count[32], survivor_decode_count[32]):.2f}%```")
        embed3.add_field(name="小説家", value=f"```試合数: {survivor_match_count[33]}\n勝率: {win_rate(survivor_match_count[33], survivor_win_count[33], survivor_draw_count[33]):.2f}%\n通電率: {decode_rate(survivor_match_count[33], survivor_decode_count[33]):.2f}%```")
        embed3.add_field(name="「少女」", value=f"```試合数: {survivor_match_count[34]}\n勝率: {win_rate(survivor_match_count[34], survivor_win_count[34], survivor_draw_count[34]):.2f}%\n通電率: {decode_rate(survivor_match_count[34], survivor_decode_count[34]):.2f}%```")
        embed3.add_field(name="泣きピエロ", value=f"```試合数: {survivor_match_count[35]}\n勝率: {win_rate(survivor_match_count[35], survivor_win_count[35], survivor_draw_count[35]):.2f}%\n通電率: {decode_rate(survivor_match_count[35], survivor_decode_count[35]):.2f}%```")
        embed3.add_field(name="教授", value=f"```試合数: {survivor_match_count[36]}\n勝率: {win_rate(survivor_match_count[36], survivor_win_count[36], survivor_draw_count[36]):.2f}%\n通電率: {decode_rate(survivor_match_count[36], survivor_decode_count[36]):.2f}%```")
        embed3.add_field(name="骨董商", value=f"```試合数: {survivor_match_count[37]}\n勝率: {win_rate(survivor_match_count[37], survivor_win_count[37], survivor_draw_count[37]):.2f}%\n通電率: {decode_rate(survivor_match_count[37], survivor_decode_count[37]):.2f}%```")
        embed3.add_field(name="作曲家", value=f"```試合数: {survivor_match_count[38]}\n勝率: {win_rate(survivor_match_count[38], survivor_win_count[38], survivor_draw_count[38]):.2f}%\n通電率: {decode_rate(survivor_match_count[38], survivor_decode_count[38]):.2f}%```")
        embed3.add_field(name="記者", value=f"```試合数: {survivor_match_count[39]}\n勝率: {win_rate(survivor_match_count[39], survivor_win_count[39], survivor_draw_count[39]):.2f}%\n通電率: {decode_rate(survivor_match_count[39], survivor_decode_count[39]):.2f}%```")
        embed3.add_field(name="航空エンジニア", value=f"```試合数: {survivor_match_count[40]}\n勝率: {win_rate(survivor_match_count[40], survivor_win_count[40], survivor_draw_count[40]):.2f}%\n通電率: {decode_rate(survivor_match_count[40], survivor_decode_count[40]):.2f}%```")
        embed3.add_field(name="応援団", value=f"```試合数: {survivor_match_count[41]}\n勝率: {win_rate(survivor_match_count[41], survivor_win_count[41], survivor_draw_count[41]):.2f}%\n通電率: {decode_rate(survivor_match_count[41], survivor_decode_count[41]):.2f}%```")
        embed3.add_field(name="人形師", value=f"```試合数: {survivor_match_count[42]}\n勝率: {win_rate(survivor_match_count[42], survivor_win_count[42], survivor_draw_count[42]):.2f}%\n通電率: {decode_rate(survivor_match_count[42], survivor_decode_count[42]):.2f}%```")
        embed3.add_field(name="火災調査員", value=f"```試合数: {survivor_match_count[43]}\n勝率: {win_rate(survivor_match_count[43], survivor_win_count[43], survivor_draw_count[43]):.2f}%\n通電率: {decode_rate(survivor_match_count[43], survivor_decode_count[43]):.2f}%```")
        embed3.add_field(name="「レディ・ファウロ」", value=f"```試合数: {survivor_match_count[44]}\n勝率: {win_rate(survivor_match_count[44], survivor_win_count[44], survivor_draw_count[44]):.2f}%\n通電率: {decode_rate(survivor_match_count[44], survivor_decode_count[44]):.2f}%```")
        embed3.add_field(name="「騎士」", value=f"```試合数: {survivor_match_count[45]}\n勝率: {win_rate(survivor_match_count[45], survivor_win_count[45], survivor_draw_count[45]):.2f}%\n通電率: {decode_rate(survivor_match_count[45], survivor_decode_count[45]):.2f}%```")
        embed3.add_field(name="幸運児", value=f"```試合数: {lucky_guy_count}\n勝率: {win_rate(lucky_guy_count, lucky_guy_win_count, lucky_guy_draw_count):.2f}%\n通電率: {decode_rate(lucky_guy_count, lucky_guy_decode_count):.2f}%```")
        embed3.add_field(name="サバ不明", value=f"```試合数: {survivor_match_count[0]}\n勝率: {win_rate(survivor_match_count[0], survivor_win_count[0], survivor_draw_count[0]):.2f}%\n通電率: {decode_rate(survivor_match_count[0], survivor_decode_count[0]):.2f}%```")
        # 1 embed につき 25 field が限界の個数らしい

        # メッセージをDiscordチャンネルに送信
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()

# !output_huntコマンド
@bot.command(name='output_hunt')
async def output_hunt(ctx, player_id:int, hunter_num:str):

    # ハンター名とデータベース番号のマッピング
    hunter_mapping = {
        "復讐者": "1", "道化師": "2", "断罪狩人": "3", "リッパー": "4", "結魂者": "5",
        "芸者": "6", "白黒無常": "7", "写真家": "8", "狂眼": "9", "黄衣の王": "10",
        "夢の魔女": "11", "泣き虫": "12", "魔トカゲ": "13", "血の女王": "14",
        "ガードNo.26": "15", "「使徒」": "16", "ヴァイオリニスト": "17", "彫刻師": "18",
        "「アンデッド」": "19", "破輪": "20", "漁師": "21", "蝋人形師": "22",
        "「悪夢」": "23", "書記官": "24", "隠者": "25", "夜の番人": "26",
        "オペラ歌手": "27", "「フールズ・ゴールド」": "28", "時空の影": "29",
        "「足萎えの羊」": "30", "「フラバルー」": "31", "不明": "0"
    }

    # 数字をキーとして、ハンター名を取得できるように反転マッピングを作成
    number_to_hunter = {v: k for k, v in hunter_mapping.items()}

    try:
        # データベースに接続
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()
        
    # 試合数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s", (player_id, hunter_num))
        result = cursor.fetchone()
        if result is not None:        
            match_count = result[0]
        else:
            match_count = 0
        # マップ
        map_match_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s", (player_id, hunter_num, i))
            result = cursor.fetchone()
            if result is not None:
                map_match_count.append(result[0])
            else:
                map_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_match_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, hunter_num, i, i, i, i))
            result = cursor.fetchone()
            if result is not None:
                survivor_match_count.append(result[0])
            else:
                survivor_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, hunter_num, 100, 100, 100, 100))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_count = result[0]
        else:
            lucky_guy_count = 0

    # 勝利数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND result = %s", (player_id, hunter_num, 1))
        result = cursor.fetchone()
        if result is not None:        
            win_count = result[0]
        else:
            win_count = 0
        # マップ
        map_win_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s AND result = %s", (player_id, hunter_num, i, 1))
            result = cursor.fetchone()
            if result is not None:
                map_win_count.append(result[0])
            else:
                map_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_win_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, hunter_num, i, i, i, i, 1))
            result = cursor.fetchone()
            if result is not None:
                survivor_win_count.append(result[0])
            else:
                survivor_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, hunter_num, 100, 100, 100, 100, 1))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_win_count = result[0]
        else:
            lucky_guy_win_count = 0

    # 引分け数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND result = %s", (player_id, hunter_num, 3))
        result = cursor.fetchone()
        if result is not None:        
            draw_count = result[0]
        else:
            draw_count = 0
        # マップ
        map_draw_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s AND result = %s", (player_id, hunter_num, i, 3))
            result = cursor.fetchone()
            if result is not None:
                map_draw_count.append(result[0])
            else:
                map_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_draw_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, hunter_num, i, i, i, i, 3))
            result = cursor.fetchone()
            if result is not None:
                survivor_draw_count.append(result[0])
            else:
                survivor_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, hunter_num, 100, 100, 100, 100, 3))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_draw_count = result[0]
        else:
            lucky_guy_draw_count = 0

    # 通電数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND decode = %s", (player_id, hunter_num, 1))
        result = cursor.fetchone()
        if result is not None:        
            decode_count = result[0]
        else:
            decode_count = 0
        # マップ
        map_decode_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s AND decode = %s", (player_id, hunter_num, i, 1))
            result = cursor.fetchone()
            if result is not None:
                map_decode_count.append(result[0])
            else:
                map_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_decode_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, hunter_num, i, i, i, i, 1))
            result = cursor.fetchone()
            if result is not None:
                survivor_decode_count.append(result[0])
            else:
                survivor_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, hunter_num, 100, 100, 100, 100, 1))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_decode_count = result[0]
        else:
            lucky_guy_decode_count = 0

        # 入力された数字に対応するハンター名を取得
        hunter_name = number_to_hunter.get(str(hunter_num), "Error")

        embed1 = discord.Embed(
            title=f"1/3\nプレイヤーID: {player_id}\n使用ハンター: {hunter_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed1.add_field(name="全体", value=f"```試合数: {match_count}\n勝率: {win_rate(match_count, win_count, draw_count):.2f}%\n通電率: {decode_rate(match_count, decode_count):.2f}%```")
        embed1.add_field(name="軍需工場", value=f"```試合数: {map_match_count[1]}\n勝率: {win_rate(map_match_count[1], map_win_count[1], map_draw_count[1]):.2f}%\n通電率: {decode_rate(map_match_count[1], map_decode_count[1]):.2f}%```")
        embed1.add_field(name="聖心病院", value=f"```試合数: {map_match_count[2]}\n勝率: {win_rate(map_match_count[2], map_win_count[2], map_draw_count[2]):.2f}%\n通電率: {decode_rate(map_match_count[2], map_decode_count[2]):.2f}%```")
        embed1.add_field(name="赤の教会", value=f"```試合数: {map_match_count[3]}\n勝率: {win_rate(map_match_count[3], map_win_count[3], map_draw_count[3]):.2f}%\n通電率: {decode_rate(map_match_count[3], map_decode_count[3]):.2f}%```")
        embed1.add_field(name="湖景村", value=f"```試合数: {map_match_count[4]}\n勝率: {win_rate(map_match_count[4], map_win_count[4], map_draw_count[4]):.2f}%\n通電率: {decode_rate(map_match_count[4], map_decode_count[4]):.2f}%```")
        embed1.add_field(name="月の河公園", value=f"```試合数: {map_match_count[5]}\n勝率: {win_rate(map_match_count[5], map_win_count[5], map_draw_count[5]):.2f}%\n通電率: {decode_rate(map_match_count[5], map_decode_count[5]):.2f}%```")
        embed1.add_field(name="レオの思い出", value=f"```試合数: {map_match_count[6]}\n勝率: {win_rate(map_match_count[6], map_win_count[6], map_draw_count[6]):.2f}%\n通電率: {decode_rate(map_match_count[6], map_decode_count[6]):.2f}%```")
        embed1.add_field(name="永眠町", value=f"```試合数: {map_match_count[7]}\n勝率: {win_rate(map_match_count[7], map_win_count[7], map_draw_count[7]):.2f}%\n通電率: {decode_rate(map_match_count[7], map_decode_count[7]):.2f}%```")
        embed1.add_field(name="中華街", value=f"```試合数: {map_match_count[8]}\n勝率: {win_rate(map_match_count[8], map_win_count[8], map_draw_count[8]):.2f}%\n通電率: {decode_rate(map_match_count[8], map_decode_count[8]):.2f}%```")
        embed1.add_field(name="罪の森", value=f"```試合数: {map_match_count[9]}\n勝率: {win_rate(map_match_count[9], map_win_count[9], map_draw_count[9]):.2f}%\n通電率: {decode_rate(map_match_count[9], map_decode_count[9]):.2f}%```")
        embed1.add_field(name="マップ不明", value=f"```試合数: {map_match_count[0]}\n勝率: {win_rate(map_match_count[0], map_win_count[0], map_draw_count[0]):.2f}%\n通電率: {decode_rate(map_match_count[0], map_decode_count[0]):.2f}%```")

        embed2 = discord.Embed(
            title=f"2/3\nプレイヤーID: {player_id}\n使用ハンター: {hunter_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed2.add_field(name="医師", value=f"```試合数: {survivor_match_count[1]}\n勝率: {win_rate(survivor_match_count[1], survivor_win_count[1], survivor_draw_count[1]):.2f}%\n通電率: {decode_rate(survivor_match_count[1], survivor_decode_count[1]):.2f}%```")
        embed2.add_field(name="弁護士", value=f"```試合数: {survivor_match_count[2]}\n勝率: {win_rate(survivor_match_count[2], survivor_win_count[2], survivor_draw_count[2]):.2f}%\n通電率: {decode_rate(survivor_match_count[2], survivor_decode_count[2]):.2f}%```")
        embed2.add_field(name="泥棒", value=f"```試合数: {survivor_match_count[3]}\n勝率: {win_rate(survivor_match_count[3], survivor_win_count[3], survivor_draw_count[3]):.2f}%\n通電率: {decode_rate(survivor_match_count[3], survivor_decode_count[3]):.2f}%```")
        embed2.add_field(name="庭師", value=f"```試合数: {survivor_match_count[4]}\n勝率: {win_rate(survivor_match_count[4], survivor_win_count[4], survivor_draw_count[4]):.2f}%\n通電率: {decode_rate(survivor_match_count[4], survivor_decode_count[4]):.2f}%```")
        embed2.add_field(name="マジシャン", value=f"```試合数: {survivor_match_count[5]}\n勝率: {win_rate(survivor_match_count[5], survivor_win_count[5], survivor_draw_count[5]):.2f}%\n通電率: {decode_rate(survivor_match_count[5], survivor_decode_count[5]):.2f}%```")
        embed2.add_field(name="冒険家", value=f"```試合数: {survivor_match_count[6]}\n勝率: {win_rate(survivor_match_count[6], survivor_win_count[6], survivor_draw_count[6]):.2f}%\n通電率: {decode_rate(survivor_match_count[6], survivor_decode_count[6]):.2f}%```")
        embed2.add_field(name="傭兵", value=f"```試合数: {survivor_match_count[7]}\n勝率: {win_rate(survivor_match_count[7], survivor_win_count[7], survivor_draw_count[7]):.2f}%\n通電率: {decode_rate(survivor_match_count[7], survivor_decode_count[7]):.2f}%```")
        embed2.add_field(name="空軍", value=f"```試合数: {survivor_match_count[8]}\n勝率: {win_rate(survivor_match_count[8], survivor_win_count[8], survivor_draw_count[8]):.2f}%\n通電率: {decode_rate(survivor_match_count[8], survivor_decode_count[8]):.2f}%```")
        embed2.add_field(name="祭司", value=f"```試合数: {survivor_match_count[9]}\n勝率: {win_rate(survivor_match_count[9], survivor_win_count[9], survivor_draw_count[9]):.2f}%\n通電率: {decode_rate(survivor_match_count[9], survivor_decode_count[9]):.2f}%```")
        embed2.add_field(name="機械技師", value=f"```試合数: {survivor_match_count[10]}\n勝率: {win_rate(survivor_match_count[10], survivor_win_count[10], survivor_draw_count[10]):.2f}%\n通電率: {decode_rate(survivor_match_count[10], survivor_decode_count[10]):.2f}%```")
        embed2.add_field(name="オフェンス", value=f"```試合数: {survivor_match_count[11]}\n勝率: {win_rate(survivor_match_count[11], survivor_win_count[11], survivor_draw_count[11]):.2f}%\n通電率: {decode_rate(survivor_match_count[11], survivor_decode_count[11]):.2f}%```")
        embed2.add_field(name="心眼", value=f"```試合数: {survivor_match_count[12]}\n勝率: {win_rate(survivor_match_count[12], survivor_win_count[12], survivor_draw_count[12]):.2f}%\n通電率: {decode_rate(survivor_match_count[12], survivor_decode_count[12]):.2f}%```")
        embed2.add_field(name="調香師", value=f"```試合数: {survivor_match_count[13]}\n勝率: {win_rate(survivor_match_count[13], survivor_win_count[13], survivor_draw_count[13]):.2f}%\n通電率: {decode_rate(survivor_match_count[13], survivor_decode_count[13]):.2f}%```")
        embed2.add_field(name="カウボーイ", value=f"```試合数: {survivor_match_count[14]}\n勝率: {win_rate(survivor_match_count[14], survivor_win_count[14], survivor_draw_count[14]):.2f}%\n通電率: {decode_rate(survivor_match_count[14], survivor_decode_count[14]):.2f}%```")
        embed2.add_field(name="踊り子", value=f"```試合数: {survivor_match_count[15]}\n勝率: {win_rate(survivor_match_count[15], survivor_win_count[15], survivor_draw_count[15]):.2f}%\n通電率: {decode_rate(survivor_match_count[15], survivor_decode_count[15]):.2f}%```")
        embed2.add_field(name="占い師", value=f"```試合数: {survivor_match_count[16]}\n勝率: {win_rate(survivor_match_count[16], survivor_win_count[16], survivor_draw_count[16]):.2f}%\n通電率: {decode_rate(survivor_match_count[16], survivor_decode_count[16]):.2f}%```")
        embed2.add_field(name="納棺師", value=f"```試合数: {survivor_match_count[17]}\n勝率: {win_rate(survivor_match_count[17], survivor_win_count[17], survivor_draw_count[17]):.2f}%\n通電率: {decode_rate(survivor_match_count[17], survivor_decode_count[17]):.2f}%```")
        embed2.add_field(name="探鉱者", value=f"```試合数: {survivor_match_count[18]}\n勝率: {win_rate(survivor_match_count[18], survivor_win_count[18], survivor_draw_count[18]):.2f}%\n通電率: {decode_rate(survivor_match_count[18], survivor_decode_count[18]):.2f}%```")
        embed2.add_field(name="呪術師", value=f"```試合数: {survivor_match_count[19]}\n勝率: {win_rate(survivor_match_count[19], survivor_win_count[19], survivor_draw_count[19]):.2f}%\n通電率: {decode_rate(survivor_match_count[19], survivor_decode_count[19]):.2f}%```")
        embed2.add_field(name="野人", value=f"```試合数: {survivor_match_count[20]}\n勝率: {win_rate(survivor_match_count[20], survivor_win_count[20], survivor_draw_count[20]):.2f}%\n通電率: {decode_rate(survivor_match_count[20], survivor_decode_count[20]):.2f}%```")
        embed2.add_field(name="曲芸師", value=f"```試合数: {survivor_match_count[21]}\n勝率: {win_rate(survivor_match_count[21], survivor_win_count[21], survivor_draw_count[21]):.2f}%\n通電率: {decode_rate(survivor_match_count[21], survivor_decode_count[21]):.2f}%```")
        embed2.add_field(name="一等航海士", value=f"```試合数: {survivor_match_count[22]}\n勝率: {win_rate(survivor_match_count[22], survivor_win_count[22], survivor_draw_count[22]):.2f}%\n通電率: {decode_rate(survivor_match_count[22], survivor_decode_count[22]):.2f}%```")
        embed2.add_field(name="バーメイド", value=f"```試合数: {survivor_match_count[23]}\n勝率: {win_rate(survivor_match_count[23], survivor_win_count[23], survivor_draw_count[23]):.2f}%\n通電率: {decode_rate(survivor_match_count[23], survivor_decode_count[23]):.2f}%```")
        embed2.add_field(name="ポストマン", value=f"```試合数: {survivor_match_count[24]}\n勝率: {win_rate(survivor_match_count[24], survivor_win_count[24], survivor_draw_count[24]):.2f}%\n通電率: {decode_rate(survivor_match_count[24], survivor_decode_count[24]):.2f}%```")
                
        embed3 = discord.Embed(
            title=f"3/3\nプレイヤーID: {player_id}\n使用ハンター: {hunter_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed3.add_field(name="墓守", value=f"```試合数: {survivor_match_count[25]}\n勝率: {win_rate(survivor_match_count[25], survivor_win_count[25], survivor_draw_count[25]):.2f}%\n通電率: {decode_rate(survivor_match_count[25], survivor_decode_count[25]):.2f}%```")
        embed3.add_field(name="「囚人」", value=f"```試合数: {survivor_match_count[26]}\n勝率: {win_rate(survivor_match_count[26], survivor_win_count[26], survivor_draw_count[26]):.2f}%\n通電率: {decode_rate(survivor_match_count[26], survivor_decode_count[26]):.2f}%```")
        embed3.add_field(name="昆虫学者", value=f"```試合数: {survivor_match_count[27]}\n勝率: {win_rate(survivor_match_count[27], survivor_win_count[27], survivor_draw_count[27]):.2f}%\n通電率: {decode_rate(survivor_match_count[27], survivor_decode_count[27]):.2f}%```")
        embed3.add_field(name="画家", value=f"```試合数: {survivor_match_count[28]}\n勝率: {win_rate(survivor_match_count[28], survivor_win_count[28], survivor_draw_count[28]):.2f}%\n通電率: {decode_rate(survivor_match_count[28], survivor_decode_count[28]):.2f}%```")
        embed3.add_field(name="バッツマン", value=f"```試合数: {survivor_match_count[29]}\n勝率: {win_rate(survivor_match_count[29], survivor_win_count[29], survivor_draw_count[29]):.2f}%\n通電率: {decode_rate(survivor_match_count[29], survivor_decode_count[29]):.2f}%```")
        embed3.add_field(name="玩具職人", value=f"```試合数: {survivor_match_count[30]}\n勝率: {win_rate(survivor_match_count[30], survivor_win_count[30], survivor_draw_count[30]):.2f}%\n通電率: {decode_rate(survivor_match_count[30], survivor_decode_count[30]):.2f}%```")
        embed3.add_field(name="患者", value=f"```試合数: {survivor_match_count[31]}\n勝率: {win_rate(survivor_match_count[31], survivor_win_count[31], survivor_draw_count[31]):.2f}%\n通電率: {decode_rate(survivor_match_count[31], survivor_decode_count[31]):.2f}%```")
        embed3.add_field(name="「心理学者」", value=f"```試合数: {survivor_match_count[32]}\n勝率: {win_rate(survivor_match_count[32], survivor_win_count[32], survivor_draw_count[32]):.2f}%\n通電率: {decode_rate(survivor_match_count[32], survivor_decode_count[32]):.2f}%```")
        embed3.add_field(name="小説家", value=f"```試合数: {survivor_match_count[33]}\n勝率: {win_rate(survivor_match_count[33], survivor_win_count[33], survivor_draw_count[33]):.2f}%\n通電率: {decode_rate(survivor_match_count[33], survivor_decode_count[33]):.2f}%```")
        embed3.add_field(name="「少女」", value=f"```試合数: {survivor_match_count[34]}\n勝率: {win_rate(survivor_match_count[34], survivor_win_count[34], survivor_draw_count[34]):.2f}%\n通電率: {decode_rate(survivor_match_count[34], survivor_decode_count[34]):.2f}%```")
        embed3.add_field(name="泣きピエロ", value=f"```試合数: {survivor_match_count[35]}\n勝率: {win_rate(survivor_match_count[35], survivor_win_count[35], survivor_draw_count[35]):.2f}%\n通電率: {decode_rate(survivor_match_count[35], survivor_decode_count[35]):.2f}%```")
        embed3.add_field(name="教授", value=f"```試合数: {survivor_match_count[36]}\n勝率: {win_rate(survivor_match_count[36], survivor_win_count[36], survivor_draw_count[36]):.2f}%\n通電率: {decode_rate(survivor_match_count[36], survivor_decode_count[36]):.2f}%```")
        embed3.add_field(name="骨董商", value=f"```試合数: {survivor_match_count[37]}\n勝率: {win_rate(survivor_match_count[37], survivor_win_count[37], survivor_draw_count[37]):.2f}%\n通電率: {decode_rate(survivor_match_count[37], survivor_decode_count[37]):.2f}%```")
        embed3.add_field(name="作曲家", value=f"```試合数: {survivor_match_count[38]}\n勝率: {win_rate(survivor_match_count[38], survivor_win_count[38], survivor_draw_count[38]):.2f}%\n通電率: {decode_rate(survivor_match_count[38], survivor_decode_count[38]):.2f}%```")
        embed3.add_field(name="記者", value=f"```試合数: {survivor_match_count[39]}\n勝率: {win_rate(survivor_match_count[39], survivor_win_count[39], survivor_draw_count[39]):.2f}%\n通電率: {decode_rate(survivor_match_count[39], survivor_decode_count[39]):.2f}%```")
        embed3.add_field(name="航空エンジニア", value=f"```試合数: {survivor_match_count[40]}\n勝率: {win_rate(survivor_match_count[40], survivor_win_count[40], survivor_draw_count[40]):.2f}%\n通電率: {decode_rate(survivor_match_count[40], survivor_decode_count[40]):.2f}%```")
        embed3.add_field(name="応援団", value=f"```試合数: {survivor_match_count[41]}\n勝率: {win_rate(survivor_match_count[41], survivor_win_count[41], survivor_draw_count[41]):.2f}%\n通電率: {decode_rate(survivor_match_count[41], survivor_decode_count[41]):.2f}%```")
        embed3.add_field(name="人形師", value=f"```試合数: {survivor_match_count[42]}\n勝率: {win_rate(survivor_match_count[42], survivor_win_count[42], survivor_draw_count[42]):.2f}%\n通電率: {decode_rate(survivor_match_count[42], survivor_decode_count[42]):.2f}%```")
        embed3.add_field(name="火災調査員", value=f"```試合数: {survivor_match_count[43]}\n勝率: {win_rate(survivor_match_count[43], survivor_win_count[43], survivor_draw_count[43]):.2f}%\n通電率: {decode_rate(survivor_match_count[43], survivor_decode_count[43]):.2f}%```")
        embed3.add_field(name="「レディ・ファウロ」", value=f"```試合数: {survivor_match_count[44]}\n勝率: {win_rate(survivor_match_count[44], survivor_win_count[44], survivor_draw_count[44]):.2f}%\n通電率: {decode_rate(survivor_match_count[44], survivor_decode_count[44]):.2f}%```")
        embed3.add_field(name="「騎士」", value=f"```試合数: {survivor_match_count[45]}\n勝率: {win_rate(survivor_match_count[45], survivor_win_count[45], survivor_draw_count[45]):.2f}%\n通電率: {decode_rate(survivor_match_count[45], survivor_decode_count[45]):.2f}%```")
        embed3.add_field(name="幸運児", value=f"```試合数: {lucky_guy_count}\n勝率: {win_rate(lucky_guy_count, lucky_guy_win_count, lucky_guy_draw_count):.2f}%\n通電率: {decode_rate(lucky_guy_count, lucky_guy_decode_count):.2f}%```")
        embed3.add_field(name="サバ不明", value=f"```試合数: {survivor_match_count[0]}\n勝率: {win_rate(survivor_match_count[0], survivor_win_count[0], survivor_draw_count[0]):.2f}%\n通電率: {decode_rate(survivor_match_count[0], survivor_decode_count[0]):.2f}%```")
        # 1 embed につき 25 field が限界の個数らしい

        # メッセージをDiscordチャンネルに送信
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()

# !output_mapコマンド
@bot.command(name='output_map')
async def output_map(ctx, player_id:int, map_num:str):

    # マップ名とデータベース番号のマッピング
    map_mapping = {
        "軍需工場": "1",
        "聖心病院": "2",
        "赤の教会": "3",
        "湖景村": "4",
        "月の河公園": "5",
        "レオの思い出": "6",
        "永眠町": "7",
        "中華街": "8",
        "罪の森": "9",
        "不明": "0"
    }

    # 数字をキーとして、マップ名を取得できるように反転マッピングを作成
    number_to_map = {v: k for k, v in map_mapping.items()}

    try:
        # データベースに接続
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()
        
    # 試合数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s", (player_id, map_num))
        result = cursor.fetchone()
        if result is not None:        
            match_count = result[0]
        else:
            match_count = 0
        # ハンター
        hunter_match_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s", (player_id, i, map_num))
            result = cursor.fetchone()
            if result is not None:
                hunter_match_count.append(result[0])
            else:
                hunter_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_match_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, map_num, i, i, i, i))
            result = cursor.fetchone()
            if result is not None:
                survivor_match_count.append(result[0])
            else:
                survivor_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, map_num, 100, 100, 100, 100))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_count = result[0]
        else:
            lucky_guy_count = 0

    # 勝利数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND result = %s", (player_id, map_num, 1))
        result = cursor.fetchone()
        if result is not None:        
            win_count = result[0]
        else:
            win_count = 0
        # ハンター
        hunter_win_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s AND result = %s", (player_id, i, map_num, 1))
            result = cursor.fetchone()
            if result is not None:
                hunter_win_count.append(result[0])
            else:
                hunter_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_win_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, map_num, i, i, i, i, 1))
            result = cursor.fetchone()
            if result is not None:
                survivor_win_count.append(result[0])
            else:
                survivor_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, map_num, 100, 100, 100, 100, 1))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_win_count = result[0]
        else:
            lucky_guy_win_count = 0

    # 引分け数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND result = %s", (player_id, map_num, 3))
        result = cursor.fetchone()
        if result is not None:        
            draw_count = result[0]
        else:
            draw_count = 0
        # ハンター
        hunter_draw_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s AND result = %s", (player_id, i, map_num, 3))
            result = cursor.fetchone()
            if result is not None:
                hunter_draw_count.append(result[0])
            else:
                hunter_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_draw_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, map_num, i, i, i, i, 3))
            result = cursor.fetchone()
            if result is not None:
                survivor_draw_count.append(result[0])
            else:
                survivor_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, map_num, 100, 100, 100, 100, 3))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_draw_count = result[0]
        else:
            lucky_guy_draw_count = 0

    # 通電数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND decode = %s", (player_id, map_num, 1))
        result = cursor.fetchone()
        if result is not None:        
            decode_count = result[0]
        else:
            decode_count = 0
        # ハンター
        hunter_decode_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND map = %s AND decode = %s", (player_id, i, map_num, 1))
            result = cursor.fetchone()
            if result is not None:
                hunter_decode_count.append(result[0])
            else:
                hunter_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # サバイバー
        survivor_decode_count = []
        for i in range(46):  # 0から45まで 0:unknown ~ 45:knight
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, map_num, i, i, i, i, 1))
            result = cursor.fetchone()
            if result is not None:
                survivor_decode_count.append(result[0])
            else:
                survivor_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # 幸運児
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, map_num, 100, 100, 100, 100, 1))
        result = cursor.fetchone()
        if result is not None:        
            lucky_guy_decode_count = result[0]
        else:
            lucky_guy_decode_count = 0

        # 入力された数字に対応するマップ名を取得
        map_name = number_to_map.get(str(map_num), "Error")

        embed1 = discord.Embed(
            title=f"1/4\nプレイヤーID: {player_id}\nマップ: {map_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed1.add_field(name="全体", value=f"```試合数: {match_count}\n勝率: {win_rate(match_count, win_count, draw_count):.2f}%\n通電率: {decode_rate(match_count, decode_count):.2f}%```")
        embed1.add_field(name="復讐者", value=f"```試合数: {hunter_match_count[1]}\n勝率: {win_rate(hunter_match_count[1], hunter_win_count[1], hunter_draw_count[1]):.2f}%\n通電率: {decode_rate(hunter_match_count[1], hunter_decode_count[1]):.2f}%```")
        embed1.add_field(name="道化師", value=f"```試合数: {hunter_match_count[2]}\n勝率: {win_rate(hunter_match_count[2], hunter_win_count[2], hunter_draw_count[2]):.2f}%\n通電率: {decode_rate(hunter_match_count[2], hunter_decode_count[2]):.2f}%```")
        embed1.add_field(name="断罪狩人", value=f"```試合数: {hunter_match_count[3]}\n勝率: {win_rate(hunter_match_count[3], hunter_win_count[3], hunter_draw_count[3]):.2f}%\n通電率: {decode_rate(hunter_match_count[3], hunter_decode_count[3]):.2f}%```")
        embed1.add_field(name="リッパー", value=f"```試合数: {hunter_match_count[4]}\n勝率: {win_rate(hunter_match_count[4], hunter_win_count[4], hunter_draw_count[4]):.2f}%\n通電率: {decode_rate(hunter_match_count[4], hunter_decode_count[4]):.2f}%```")
        embed1.add_field(name="結魂者", value=f"```試合数: {hunter_match_count[5]}\n勝率: {win_rate(hunter_match_count[5], hunter_win_count[5], hunter_draw_count[5]):.2f}%\n通電率: {decode_rate(hunter_match_count[5], hunter_decode_count[5]):.2f}%```")
        embed1.add_field(name="芸者", value=f"```試合数: {hunter_match_count[6]}\n勝率: {win_rate(hunter_match_count[6], hunter_win_count[6], hunter_draw_count[6]):.2f}%\n通電率: {decode_rate(hunter_match_count[6], hunter_decode_count[6]):.2f}%```")
        embed1.add_field(name="白黒無常", value=f"```試合数: {hunter_match_count[7]}\n勝率: {win_rate(hunter_match_count[7], hunter_win_count[7], hunter_draw_count[7]):.2f}%\n通電率: {decode_rate(hunter_match_count[7], hunter_decode_count[7]):.2f}%```")
        embed1.add_field(name="写真家", value=f"```試合数: {hunter_match_count[8]}\n勝率: {win_rate(hunter_match_count[8], hunter_win_count[8], hunter_draw_count[8]):.2f}%\n通電率: {decode_rate(hunter_match_count[8], hunter_decode_count[8]):.2f}%```")
        embed1.add_field(name="狂眼", value=f"```試合数: {hunter_match_count[9]}\n勝率: {win_rate(hunter_match_count[9], hunter_win_count[9], hunter_draw_count[9]):.2f}%\n通電率: {decode_rate(hunter_match_count[9], hunter_decode_count[9]):.2f}%```")
        embed1.add_field(name="黄衣の王", value=f"```試合数: {hunter_match_count[10]}\n勝率: {win_rate(hunter_match_count[10], hunter_win_count[10], hunter_draw_count[10]):.2f}%\n通電率: {decode_rate(hunter_match_count[10], hunter_decode_count[10]):.2f}%```")
        embed1.add_field(name="夢の魔女", value=f"```試合数: {hunter_match_count[11]}\n勝率: {win_rate(hunter_match_count[11], hunter_win_count[11], hunter_draw_count[11]):.2f}%\n通電率: {decode_rate(hunter_match_count[11], hunter_decode_count[11]):.2f}%```")
        embed1.add_field(name="泣き虫", value=f"```試合数: {hunter_match_count[12]}\n勝率: {win_rate(hunter_match_count[12], hunter_win_count[12], hunter_draw_count[12]):.2f}%\n通電率: {decode_rate(hunter_match_count[12], hunter_decode_count[12]):.2f}%```")
        embed1.add_field(name="魔トカゲ", value=f"```試合数: {hunter_match_count[13]}\n勝率: {win_rate(hunter_match_count[13], hunter_win_count[13], hunter_draw_count[13]):.2f}%\n通電率: {decode_rate(hunter_match_count[13], hunter_decode_count[13]):.2f}%```")
        embed1.add_field(name="血の女王", value=f"```試合数: {hunter_match_count[14]}\n勝率: {win_rate(hunter_match_count[14], hunter_win_count[14], hunter_draw_count[14]):.2f}%\n通電率: {decode_rate(hunter_match_count[14], hunter_decode_count[14]):.2f}%```")
        embed1.add_field(name="ガードNo.26", value=f"```試合数: {hunter_match_count[15]}\n勝率: {win_rate(hunter_match_count[15], hunter_win_count[15], hunter_draw_count[15]):.2f}%\n通電率: {decode_rate(hunter_match_count[15], hunter_decode_count[15]):.2f}%```")
        embed1.add_field(name="「使徒」", value=f"```試合数: {hunter_match_count[16]}\n勝率: {win_rate(hunter_match_count[16], hunter_win_count[16], hunter_draw_count[16]):.2f}%\n通電率: {decode_rate(hunter_match_count[16], hunter_decode_count[16]):.2f}%```")
        embed1.add_field(name="ヴァイオリニスト", value=f"```試合数: {hunter_match_count[17]}\n勝率: {win_rate(hunter_match_count[17], hunter_win_count[17], hunter_draw_count[17]):.2f}%\n通電率: {decode_rate(hunter_match_count[17], hunter_decode_count[17]):.2f}%```")
        embed1.add_field(name="彫刻師", value=f"```試合数: {hunter_match_count[18]}\n勝率: {win_rate(hunter_match_count[18], hunter_win_count[18], hunter_draw_count[18]):.2f}%\n通電率: {decode_rate(hunter_match_count[18], hunter_decode_count[18]):.2f}%```")
        embed1.add_field(name="「アンデッド」", value=f"```試合数: {hunter_match_count[19]}\n勝率: {win_rate(hunter_match_count[19], hunter_win_count[19], hunter_draw_count[19]):.2f}%\n通電率: {decode_rate(hunter_match_count[19], hunter_decode_count[19]):.2f}%```")
        embed1.add_field(name="破輪", value=f"```試合数: {hunter_match_count[20]}\n勝率: {win_rate(hunter_match_count[20], hunter_win_count[20], hunter_draw_count[20]):.2f}%\n通電率: {decode_rate(hunter_match_count[20], hunter_decode_count[20]):.2f}%```")
        embed1.add_field(name="漁師", value=f"```試合数: {hunter_match_count[21]}\n勝率: {win_rate(hunter_match_count[21], hunter_win_count[21], hunter_draw_count[21]):.2f}%\n通電率: {decode_rate(hunter_match_count[21], hunter_decode_count[21]):.2f}%```")
        embed1.add_field(name="蝋人形師", value=f"```試合数: {hunter_match_count[22]}\n勝率: {win_rate(hunter_match_count[22], hunter_win_count[22], hunter_draw_count[22]):.2f}%\n通電率: {decode_rate(hunter_match_count[22], hunter_decode_count[22]):.2f}%```")
        embed1.add_field(name="「悪夢」", value=f"```試合数: {hunter_match_count[23]}\n勝率: {win_rate(hunter_match_count[23], hunter_win_count[23], hunter_draw_count[23]):.2f}%\n通電率: {decode_rate(hunter_match_count[23], hunter_decode_count[23]):.2f}%```")
        
        embed2 = discord.Embed(
            title=f"2/4\nプレイヤーID: {player_id}\nマップ: {map_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed2.add_field(name="書記官", value=f"```試合数: {hunter_match_count[24]}\n勝率: {win_rate(hunter_match_count[24], hunter_win_count[24], hunter_draw_count[24]):.2f}%\n通電率: {decode_rate(hunter_match_count[24], hunter_decode_count[24]):.2f}%```")
        embed2.add_field(name="隠者", value=f"```試合数: {hunter_match_count[25]}\n勝率: {win_rate(hunter_match_count[25], hunter_win_count[25], hunter_draw_count[25]):.2f}%\n通電率: {decode_rate(hunter_match_count[25], hunter_decode_count[25]):.2f}%```")
        embed2.add_field(name="夜の番人", value=f"```試合数: {hunter_match_count[26]}\n勝率: {win_rate(hunter_match_count[26], hunter_win_count[26], hunter_draw_count[26]):.2f}%\n通電率: {decode_rate(hunter_match_count[26], hunter_decode_count[26]):.2f}%```")
        embed2.add_field(name="オペラ歌手", value=f"```試合数: {hunter_match_count[27]}\n勝率: {win_rate(hunter_match_count[27], hunter_win_count[27], hunter_draw_count[27]):.2f}%\n通電率: {decode_rate(hunter_match_count[27], hunter_decode_count[27]):.2f}%```")
        embed2.add_field(name="「フールズ・ゴールド」", value=f"```試合数: {hunter_match_count[28]}\n勝率: {win_rate(hunter_match_count[28], hunter_win_count[28], hunter_draw_count[28]):.2f}%\n通電率: {decode_rate(hunter_match_count[28], hunter_decode_count[28]):.2f}%```")
        embed2.add_field(name="時空の影", value=f"```試合数: {hunter_match_count[29]}\n勝率: {win_rate(hunter_match_count[29], hunter_win_count[29], hunter_draw_count[29]):.2f}%\n通電率: {decode_rate(hunter_match_count[29], hunter_decode_count[29]):.2f}%```")
        embed2.add_field(name="「足萎えの羊」", value=f"```試合数: {hunter_match_count[30]}\n勝率: {win_rate(hunter_match_count[30], hunter_win_count[30], hunter_draw_count[30]):.2f}%\n通電率: {decode_rate(hunter_match_count[30], hunter_decode_count[30]):.2f}%```")
        embed2.add_field(name="「フラバルー」", value=f"```試合数: {hunter_match_count[31]}\n勝率: {win_rate(hunter_match_count[31], hunter_win_count[31], hunter_draw_count[31]):.2f}%\n通電率: {decode_rate(hunter_match_count[31], hunter_decode_count[31]):.2f}%```")
        embed2.add_field(name="ハンター不明", value=f"```試合数: {hunter_match_count[0]}\n勝率: {win_rate(hunter_match_count[0], hunter_win_count[0], hunter_draw_count[0]):.2f}%\n通電率: {decode_rate(hunter_match_count[0], hunter_decode_count[0]):.2f}%```")

        embed3 = discord.Embed(
            title=f"3/4\nプレイヤーID: {player_id}\nマップ: {map_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed3.add_field(name="医師", value=f"```試合数: {survivor_match_count[1]}\n勝率: {win_rate(survivor_match_count[1], survivor_win_count[1], survivor_draw_count[1]):.2f}%\n通電率: {decode_rate(survivor_match_count[1], survivor_decode_count[1]):.2f}%```")
        embed3.add_field(name="弁護士", value=f"```試合数: {survivor_match_count[2]}\n勝率: {win_rate(survivor_match_count[2], survivor_win_count[2], survivor_draw_count[2]):.2f}%\n通電率: {decode_rate(survivor_match_count[2], survivor_decode_count[2]):.2f}%```")
        embed3.add_field(name="泥棒", value=f"```試合数: {survivor_match_count[3]}\n勝率: {win_rate(survivor_match_count[3], survivor_win_count[3], survivor_draw_count[3]):.2f}%\n通電率: {decode_rate(survivor_match_count[3], survivor_decode_count[3]):.2f}%```")
        embed3.add_field(name="庭師", value=f"```試合数: {survivor_match_count[4]}\n勝率: {win_rate(survivor_match_count[4], survivor_win_count[4], survivor_draw_count[4]):.2f}%\n通電率: {decode_rate(survivor_match_count[4], survivor_decode_count[4]):.2f}%```")
        embed3.add_field(name="マジシャン", value=f"```試合数: {survivor_match_count[5]}\n勝率: {win_rate(survivor_match_count[5], survivor_win_count[5], survivor_draw_count[5]):.2f}%\n通電率: {decode_rate(survivor_match_count[5], survivor_decode_count[5]):.2f}%```")
        embed3.add_field(name="冒険家", value=f"```試合数: {survivor_match_count[6]}\n勝率: {win_rate(survivor_match_count[6], survivor_win_count[6], survivor_draw_count[6]):.2f}%\n通電率: {decode_rate(survivor_match_count[6], survivor_decode_count[6]):.2f}%```")
        embed3.add_field(name="傭兵", value=f"```試合数: {survivor_match_count[7]}\n勝率: {win_rate(survivor_match_count[7], survivor_win_count[7], survivor_draw_count[7]):.2f}%\n通電率: {decode_rate(survivor_match_count[7], survivor_decode_count[7]):.2f}%```")
        embed3.add_field(name="空軍", value=f"```試合数: {survivor_match_count[8]}\n勝率: {win_rate(survivor_match_count[8], survivor_win_count[8], survivor_draw_count[8]):.2f}%\n通電率: {decode_rate(survivor_match_count[8], survivor_decode_count[8]):.2f}%```")
        embed3.add_field(name="祭司", value=f"```試合数: {survivor_match_count[9]}\n勝率: {win_rate(survivor_match_count[9], survivor_win_count[9], survivor_draw_count[9]):.2f}%\n通電率: {decode_rate(survivor_match_count[9], survivor_decode_count[9]):.2f}%```")
        embed3.add_field(name="機械技師", value=f"```試合数: {survivor_match_count[10]}\n勝率: {win_rate(survivor_match_count[10], survivor_win_count[10], survivor_draw_count[10]):.2f}%\n通電率: {decode_rate(survivor_match_count[10], survivor_decode_count[10]):.2f}%```")
        embed3.add_field(name="オフェンス", value=f"```試合数: {survivor_match_count[11]}\n勝率: {win_rate(survivor_match_count[11], survivor_win_count[11], survivor_draw_count[11]):.2f}%\n通電率: {decode_rate(survivor_match_count[11], survivor_decode_count[11]):.2f}%```")
        embed3.add_field(name="心眼", value=f"```試合数: {survivor_match_count[12]}\n勝率: {win_rate(survivor_match_count[12], survivor_win_count[12], survivor_draw_count[12]):.2f}%\n通電率: {decode_rate(survivor_match_count[12], survivor_decode_count[12]):.2f}%```")
        embed3.add_field(name="調香師", value=f"```試合数: {survivor_match_count[13]}\n勝率: {win_rate(survivor_match_count[13], survivor_win_count[13], survivor_draw_count[13]):.2f}%\n通電率: {decode_rate(survivor_match_count[13], survivor_decode_count[13]):.2f}%```")
        embed3.add_field(name="カウボーイ", value=f"```試合数: {survivor_match_count[14]}\n勝率: {win_rate(survivor_match_count[14], survivor_win_count[14], survivor_draw_count[14]):.2f}%\n通電率: {decode_rate(survivor_match_count[14], survivor_decode_count[14]):.2f}%```")
        embed3.add_field(name="踊り子", value=f"```試合数: {survivor_match_count[15]}\n勝率: {win_rate(survivor_match_count[15], survivor_win_count[15], survivor_draw_count[15]):.2f}%\n通電率: {decode_rate(survivor_match_count[15], survivor_decode_count[15]):.2f}%```")
        embed3.add_field(name="占い師", value=f"```試合数: {survivor_match_count[16]}\n勝率: {win_rate(survivor_match_count[16], survivor_win_count[16], survivor_draw_count[16]):.2f}%\n通電率: {decode_rate(survivor_match_count[16], survivor_decode_count[16]):.2f}%```")
        embed3.add_field(name="納棺師", value=f"```試合数: {survivor_match_count[17]}\n勝率: {win_rate(survivor_match_count[17], survivor_win_count[17], survivor_draw_count[17]):.2f}%\n通電率: {decode_rate(survivor_match_count[17], survivor_decode_count[17]):.2f}%```")
        embed3.add_field(name="探鉱者", value=f"```試合数: {survivor_match_count[18]}\n勝率: {win_rate(survivor_match_count[18], survivor_win_count[18], survivor_draw_count[18]):.2f}%\n通電率: {decode_rate(survivor_match_count[18], survivor_decode_count[18]):.2f}%```")
        embed3.add_field(name="呪術師", value=f"```試合数: {survivor_match_count[19]}\n勝率: {win_rate(survivor_match_count[19], survivor_win_count[19], survivor_draw_count[19]):.2f}%\n通電率: {decode_rate(survivor_match_count[19], survivor_decode_count[19]):.2f}%```")
        embed3.add_field(name="野人", value=f"```試合数: {survivor_match_count[20]}\n勝率: {win_rate(survivor_match_count[20], survivor_win_count[20], survivor_draw_count[20]):.2f}%\n通電率: {decode_rate(survivor_match_count[20], survivor_decode_count[20]):.2f}%```")
        embed3.add_field(name="曲芸師", value=f"```試合数: {survivor_match_count[21]}\n勝率: {win_rate(survivor_match_count[21], survivor_win_count[21], survivor_draw_count[21]):.2f}%\n通電率: {decode_rate(survivor_match_count[21], survivor_decode_count[21]):.2f}%```")
        embed3.add_field(name="一等航海士", value=f"```試合数: {survivor_match_count[22]}\n勝率: {win_rate(survivor_match_count[22], survivor_win_count[22], survivor_draw_count[22]):.2f}%\n通電率: {decode_rate(survivor_match_count[22], survivor_decode_count[22]):.2f}%```")
        embed3.add_field(name="バーメイド", value=f"```試合数: {survivor_match_count[23]}\n勝率: {win_rate(survivor_match_count[23], survivor_win_count[23], survivor_draw_count[23]):.2f}%\n通電率: {decode_rate(survivor_match_count[23], survivor_decode_count[23]):.2f}%```")
        embed3.add_field(name="ポストマン", value=f"```試合数: {survivor_match_count[24]}\n勝率: {win_rate(survivor_match_count[24], survivor_win_count[24], survivor_draw_count[24]):.2f}%\n通電率: {decode_rate(survivor_match_count[24], survivor_decode_count[24]):.2f}%```")
                
        embed4 = discord.Embed(
            title=f"4/4\nプレイヤーID: {player_id}\nマップ: {map_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed4.add_field(name="墓守", value=f"```試合数: {survivor_match_count[25]}\n勝率: {win_rate(survivor_match_count[25], survivor_win_count[25], survivor_draw_count[25]):.2f}%\n通電率: {decode_rate(survivor_match_count[25], survivor_decode_count[25]):.2f}%```")
        embed4.add_field(name="「囚人」", value=f"```試合数: {survivor_match_count[26]}\n勝率: {win_rate(survivor_match_count[26], survivor_win_count[26], survivor_draw_count[26]):.2f}%\n通電率: {decode_rate(survivor_match_count[26], survivor_decode_count[26]):.2f}%```")
        embed4.add_field(name="昆虫学者", value=f"```試合数: {survivor_match_count[27]}\n勝率: {win_rate(survivor_match_count[27], survivor_win_count[27], survivor_draw_count[27]):.2f}%\n通電率: {decode_rate(survivor_match_count[27], survivor_decode_count[27]):.2f}%```")
        embed4.add_field(name="画家", value=f"```試合数: {survivor_match_count[28]}\n勝率: {win_rate(survivor_match_count[28], survivor_win_count[28], survivor_draw_count[28]):.2f}%\n通電率: {decode_rate(survivor_match_count[28], survivor_decode_count[28]):.2f}%```")
        embed4.add_field(name="バッツマン", value=f"```試合数: {survivor_match_count[29]}\n勝率: {win_rate(survivor_match_count[29], survivor_win_count[29], survivor_draw_count[29]):.2f}%\n通電率: {decode_rate(survivor_match_count[29], survivor_decode_count[29]):.2f}%```")
        embed4.add_field(name="玩具職人", value=f"```試合数: {survivor_match_count[30]}\n勝率: {win_rate(survivor_match_count[30], survivor_win_count[30], survivor_draw_count[30]):.2f}%\n通電率: {decode_rate(survivor_match_count[30], survivor_decode_count[30]):.2f}%```")
        embed4.add_field(name="患者", value=f"```試合数: {survivor_match_count[31]}\n勝率: {win_rate(survivor_match_count[31], survivor_win_count[31], survivor_draw_count[31]):.2f}%\n通電率: {decode_rate(survivor_match_count[31], survivor_decode_count[31]):.2f}%```")
        embed4.add_field(name="「心理学者」", value=f"```試合数: {survivor_match_count[32]}\n勝率: {win_rate(survivor_match_count[32], survivor_win_count[32], survivor_draw_count[32]):.2f}%\n通電率: {decode_rate(survivor_match_count[32], survivor_decode_count[32]):.2f}%```")
        embed4.add_field(name="小説家", value=f"```試合数: {survivor_match_count[33]}\n勝率: {win_rate(survivor_match_count[33], survivor_win_count[33], survivor_draw_count[33]):.2f}%\n通電率: {decode_rate(survivor_match_count[33], survivor_decode_count[33]):.2f}%```")
        embed4.add_field(name="「少女」", value=f"```試合数: {survivor_match_count[34]}\n勝率: {win_rate(survivor_match_count[34], survivor_win_count[34], survivor_draw_count[34]):.2f}%\n通電率: {decode_rate(survivor_match_count[34], survivor_decode_count[34]):.2f}%```")
        embed4.add_field(name="泣きピエロ", value=f"```試合数: {survivor_match_count[35]}\n勝率: {win_rate(survivor_match_count[35], survivor_win_count[35], survivor_draw_count[35]):.2f}%\n通電率: {decode_rate(survivor_match_count[35], survivor_decode_count[35]):.2f}%```")
        embed4.add_field(name="教授", value=f"```試合数: {survivor_match_count[36]}\n勝率: {win_rate(survivor_match_count[36], survivor_win_count[36], survivor_draw_count[36]):.2f}%\n通電率: {decode_rate(survivor_match_count[36], survivor_decode_count[36]):.2f}%```")
        embed4.add_field(name="骨董商", value=f"```試合数: {survivor_match_count[37]}\n勝率: {win_rate(survivor_match_count[37], survivor_win_count[37], survivor_draw_count[37]):.2f}%\n通電率: {decode_rate(survivor_match_count[37], survivor_decode_count[37]):.2f}%```")
        embed4.add_field(name="作曲家", value=f"```試合数: {survivor_match_count[38]}\n勝率: {win_rate(survivor_match_count[38], survivor_win_count[38], survivor_draw_count[38]):.2f}%\n通電率: {decode_rate(survivor_match_count[38], survivor_decode_count[38]):.2f}%```")
        embed4.add_field(name="記者", value=f"```試合数: {survivor_match_count[39]}\n勝率: {win_rate(survivor_match_count[39], survivor_win_count[39], survivor_draw_count[39]):.2f}%\n通電率: {decode_rate(survivor_match_count[39], survivor_decode_count[39]):.2f}%```")
        embed4.add_field(name="航空エンジニア", value=f"```試合数: {survivor_match_count[40]}\n勝率: {win_rate(survivor_match_count[40], survivor_win_count[40], survivor_draw_count[40]):.2f}%\n通電率: {decode_rate(survivor_match_count[40], survivor_decode_count[40]):.2f}%```")
        embed4.add_field(name="応援団", value=f"```試合数: {survivor_match_count[41]}\n勝率: {win_rate(survivor_match_count[41], survivor_win_count[41], survivor_draw_count[41]):.2f}%\n通電率: {decode_rate(survivor_match_count[41], survivor_decode_count[41]):.2f}%```")
        embed4.add_field(name="人形師", value=f"```試合数: {survivor_match_count[42]}\n勝率: {win_rate(survivor_match_count[42], survivor_win_count[42], survivor_draw_count[42]):.2f}%\n通電率: {decode_rate(survivor_match_count[42], survivor_decode_count[42]):.2f}%```")
        embed4.add_field(name="火災調査員", value=f"```試合数: {survivor_match_count[43]}\n勝率: {win_rate(survivor_match_count[43], survivor_win_count[43], survivor_draw_count[43]):.2f}%\n通電率: {decode_rate(survivor_match_count[43], survivor_decode_count[43]):.2f}%```")
        embed4.add_field(name="「レディ・ファウロ」", value=f"```試合数: {survivor_match_count[44]}\n勝率: {win_rate(survivor_match_count[44], survivor_win_count[44], survivor_draw_count[44]):.2f}%\n通電率: {decode_rate(survivor_match_count[44], survivor_decode_count[44]):.2f}%```")
        embed4.add_field(name="「騎士」", value=f"```試合数: {survivor_match_count[45]}\n勝率: {win_rate(survivor_match_count[45], survivor_win_count[45], survivor_draw_count[45]):.2f}%\n通電率: {decode_rate(survivor_match_count[45], survivor_decode_count[45]):.2f}%```")
        embed4.add_field(name="幸運児", value=f"```試合数: {lucky_guy_count}\n勝率: {win_rate(lucky_guy_count, lucky_guy_win_count, lucky_guy_draw_count):.2f}%\n通電率: {decode_rate(lucky_guy_count, lucky_guy_decode_count):.2f}%```")
        embed4.add_field(name="サバ不明", value=f"```試合数: {survivor_match_count[0]}\n勝率: {win_rate(survivor_match_count[0], survivor_win_count[0], survivor_draw_count[0]):.2f}%\n通電率: {decode_rate(survivor_match_count[0], survivor_decode_count[0]):.2f}%```")
        # 1 embed につき 25 field が限界の個数らしい

        # メッセージをDiscordチャンネルに送信
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)
        await ctx.send(embed=embed4)

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()

# !output_survコマンド
@bot.command(name='output_surv')
async def output_surv(ctx, player_id:int, survivor_num:str):

    # 生存者名とデータベース番号のマッピング
    survivor_mapping = {
        "医師": "1", "弁護士": "2", "泥棒": "3", "庭師": "4",
        "マジシャン": "5", "冒険家": "6", "傭兵": "7", "空軍": "8",
        "祭司": "9", "機械技師": "10", "オフェンス": "11", "心眼": "12",
        "調香師": "13", "カウボーイ": "14", "踊り子": "15", "占い師": "16",
        "納棺師": "17", "探鉱者": "18", "呪術師": "19", "野人": "20",
        "曲芸師": "21", "一等航海士": "22", "バーメイド": "23", "ポストマン": "24",
        "墓守": "25", "「囚人」": "26", "昆虫学者": "27", "画家": "28",
        "バッツマン": "29", "玩具職人": "30", "患者": "31", "「心理学者」": "32",
        "小説家": "33", "「少女」": "34", "泣きピエロ": "35", "教授": "36",
        "骨董商": "37", "作曲家": "38", "記者": "39", "航空エンジニア": "40",
        "応援団": "41", "人形師": "42", "火災調査員": "43", "「レディ・ファウロ」": "44",
        "「騎士」": "45", "幸運児": "100", "不明": "0"
    }

    # 数字をキーとして、サバイバー名を取得できるように反転マッピングを作成
    number_to_survivor = {v: k for k, v in survivor_mapping.items()}

    try:
        # データベースに接続
        conn = connect_db()  # PostgreSQLへの接続
        cursor = conn.cursor()
        
    # 試合数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, survivor_num, survivor_num, survivor_num, survivor_num))
        result = cursor.fetchone()
        if result is not None:        
            match_count = result[0]
        else:
            match_count = 0
        # マップ
        map_match_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num))
            result = cursor.fetchone()
            if result is not None:
                map_match_count.append(result[0])
            else:
                map_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # ハンター
        hunter_match_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s)", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num))
            result = cursor.fetchone()
            if result is not None:
                hunter_match_count.append(result[0])
            else:
                hunter_match_count.append(0)  # データがない場合は 0 を追加
            i = i + 1

    # 勝利数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, survivor_num, survivor_num, survivor_num, survivor_num, 1))
        result = cursor.fetchone()
        if result is not None:        
            win_count = result[0]
        else:
            win_count = 0
        # マップ
        map_win_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num, 1))
            result = cursor.fetchone()
            if result is not None:
                map_win_count.append(result[0])
            else:
                map_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # ハンター
        hunter_win_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num, 1))
            result = cursor.fetchone()
            if result is not None:
                hunter_win_count.append(result[0])
            else:
                hunter_win_count.append(0)  # データがない場合は 0 を追加
            i = i + 1

    # 引分け数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, survivor_num, survivor_num, survivor_num, survivor_num, 3))
        result = cursor.fetchone()
        if result is not None:        
            draw_count = result[0]
        else:
            draw_count = 0
        # マップ
        map_draw_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num, 3))
            result = cursor.fetchone()
            if result is not None:
                map_draw_count.append(result[0])
            else:
                map_draw_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # ハンター
        hunter_draw_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND result = %s", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num, 3))
            result = cursor.fetchone()
            if result is not None:
                hunter_draw_count.append(result[0])
            else:
                hunter_draw_count.append(0)  # データがない場合は 0 を追加

    # 通電数をカウント
        # 全体
        cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, survivor_num, survivor_num, survivor_num, survivor_num, 1))
        result = cursor.fetchone()
        if result is not None:        
            decode_count = result[0]
        else:
            decode_count = 0
        # マップ
        map_decode_count = []
        for i in range(10):  # 0から9まで 0:unknown ~ 9:darkwoods
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND map = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num, 1))
            result = cursor.fetchone()
            if result is not None:
                map_decode_count.append(result[0])
            else:
                map_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1
        # ハンター
        hunter_decode_count = []
        for i in range(32):  # 0から31まで 0:unknown ~ 31:Hullabaloo
            cursor.execute("SELECT COUNT(*) FROM rank_match WHERE player_id = %s AND hunter = %s AND (survivor1 = %s OR survivor2 = %s OR survivor3 = %s OR survivor4 = %s) AND decode = %s", (player_id, i, survivor_num, survivor_num, survivor_num, survivor_num, 1))
            result = cursor.fetchone()
            if result is not None:
                hunter_decode_count.append(result[0])
            else:
                hunter_decode_count.append(0)  # データがない場合は 0 を追加
            i = i + 1

        # 入力された数字に対応するマップ名を取得
        survivor_name = number_to_survivor.get(str(survivor_num), "Error")

        embed1 = discord.Embed(
            title=f"1/3\nプレイヤーID: {player_id}\n相手サバイバー: {survivor_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed1.add_field(name="全体", value=f"```試合数: {match_count}\n勝率: {win_rate(match_count, win_count, draw_count):.2f}%\n通電率: {decode_rate(match_count, decode_count):.2f}%```")
        embed1.add_field(name="軍需工場", value=f"```試合数: {map_match_count[1]}\n勝率: {win_rate(map_match_count[1], map_win_count[1], map_draw_count[1]):.2f}%\n通電率: {decode_rate(map_match_count[1], map_decode_count[1]):.2f}%```")
        embed1.add_field(name="聖心病院", value=f"```試合数: {map_match_count[2]}\n勝率: {win_rate(map_match_count[2], map_win_count[2], map_draw_count[2]):.2f}%\n通電率: {decode_rate(map_match_count[2], map_decode_count[2]):.2f}%```")
        embed1.add_field(name="赤の教会", value=f"```試合数: {map_match_count[3]}\n勝率: {win_rate(map_match_count[3], map_win_count[3], map_draw_count[3]):.2f}%\n通電率: {decode_rate(map_match_count[3], map_decode_count[3]):.2f}%```")
        embed1.add_field(name="湖景村", value=f"```試合数: {map_match_count[4]}\n勝率: {win_rate(map_match_count[4], map_win_count[4], map_draw_count[4]):.2f}%\n通電率: {decode_rate(map_match_count[4], map_decode_count[4]):.2f}%```")
        embed1.add_field(name="月の河公園", value=f"```試合数: {map_match_count[5]}\n勝率: {win_rate(map_match_count[5], map_win_count[5], map_draw_count[5]):.2f}%\n通電率: {decode_rate(map_match_count[5], map_decode_count[5]):.2f}%```")
        embed1.add_field(name="レオの思い出", value=f"```試合数: {map_match_count[6]}\n勝率: {win_rate(map_match_count[6], map_win_count[6], map_draw_count[6]):.2f}%\n通電率: {decode_rate(map_match_count[6], map_decode_count[6]):.2f}%```")
        embed1.add_field(name="永眠町", value=f"```試合数: {map_match_count[7]}\n勝率: {win_rate(map_match_count[7], map_win_count[7], map_draw_count[7]):.2f}%\n通電率: {decode_rate(map_match_count[7], map_decode_count[7]):.2f}%```")
        embed1.add_field(name="中華街", value=f"```試合数: {map_match_count[8]}\n勝率: {win_rate(map_match_count[8], map_win_count[8], map_draw_count[8]):.2f}%\n通電率: {decode_rate(map_match_count[8], map_decode_count[8]):.2f}%```")
        embed1.add_field(name="罪の森", value=f"```試合数: {map_match_count[9]}\n勝率: {win_rate(map_match_count[9], map_win_count[9], map_draw_count[9]):.2f}%\n通電率: {decode_rate(map_match_count[9], map_decode_count[9]):.2f}%```")
        embed1.add_field(name="マップ不明", value=f"```試合数: {map_match_count[0]}\n勝率: {win_rate(map_match_count[0], map_win_count[0], map_draw_count[0]):.2f}%\n通電率: {decode_rate(map_match_count[0], map_decode_count[0]):.2f}%```")

        embed2 = discord.Embed(
            title=f"2/3\nプレイヤーID: {player_id}\n相手サバイバー: {survivor_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed2.add_field(name="復讐者", value=f"```試合数: {hunter_match_count[1]}\n勝率: {win_rate(hunter_match_count[1], hunter_win_count[1], hunter_draw_count[1]):.2f}%\n通電率: {decode_rate(hunter_match_count[1], hunter_decode_count[1]):.2f}%```")
        embed2.add_field(name="道化師", value=f"```試合数: {hunter_match_count[2]}\n勝率: {win_rate(hunter_match_count[2], hunter_win_count[2], hunter_draw_count[2]):.2f}%\n通電率: {decode_rate(hunter_match_count[2], hunter_decode_count[2]):.2f}%```")
        embed2.add_field(name="断罪狩人", value=f"```試合数: {hunter_match_count[3]}\n勝率: {win_rate(hunter_match_count[3], hunter_win_count[3], hunter_draw_count[3]):.2f}%\n通電率: {decode_rate(hunter_match_count[3], hunter_decode_count[3]):.2f}%```")
        embed2.add_field(name="リッパー", value=f"```試合数: {hunter_match_count[4]}\n勝率: {win_rate(hunter_match_count[4], hunter_win_count[4], hunter_draw_count[4]):.2f}%\n通電率: {decode_rate(hunter_match_count[4], hunter_decode_count[4]):.2f}%```")
        embed2.add_field(name="結魂者", value=f"```試合数: {hunter_match_count[5]}\n勝率: {win_rate(hunter_match_count[5], hunter_win_count[5], hunter_draw_count[5]):.2f}%\n通電率: {decode_rate(hunter_match_count[5], hunter_decode_count[5]):.2f}%```")
        embed2.add_field(name="芸者", value=f"```試合数: {hunter_match_count[6]}\n勝率: {win_rate(hunter_match_count[6], hunter_win_count[6], hunter_draw_count[6]):.2f}%\n通電率: {decode_rate(hunter_match_count[6], hunter_decode_count[6]):.2f}%```")
        embed2.add_field(name="白黒無常", value=f"```試合数: {hunter_match_count[7]}\n勝率: {win_rate(hunter_match_count[7], hunter_win_count[7], hunter_draw_count[7]):.2f}%\n通電率: {decode_rate(hunter_match_count[7], hunter_decode_count[7]):.2f}%```")
        embed2.add_field(name="写真家", value=f"```試合数: {hunter_match_count[8]}\n勝率: {win_rate(hunter_match_count[8], hunter_win_count[8], hunter_draw_count[8]):.2f}%\n通電率: {decode_rate(hunter_match_count[8], hunter_decode_count[8]):.2f}%```")
        embed2.add_field(name="狂眼", value=f"```試合数: {hunter_match_count[9]}\n勝率: {win_rate(hunter_match_count[9], hunter_win_count[9], hunter_draw_count[9]):.2f}%\n通電率: {decode_rate(hunter_match_count[9], hunter_decode_count[9]):.2f}%```")
        embed2.add_field(name="黄衣の王", value=f"```試合数: {hunter_match_count[10]}\n勝率: {win_rate(hunter_match_count[10], hunter_win_count[10], hunter_draw_count[10]):.2f}%\n通電率: {decode_rate(hunter_match_count[10], hunter_decode_count[10]):.2f}%```")
        embed2.add_field(name="夢の魔女", value=f"```試合数: {hunter_match_count[11]}\n勝率: {win_rate(hunter_match_count[11], hunter_win_count[11], hunter_draw_count[11]):.2f}%\n通電率: {decode_rate(hunter_match_count[11], hunter_decode_count[11]):.2f}%```")
        embed2.add_field(name="泣き虫", value=f"```試合数: {hunter_match_count[12]}\n勝率: {win_rate(hunter_match_count[12], hunter_win_count[12], hunter_draw_count[12]):.2f}%\n通電率: {decode_rate(hunter_match_count[12], hunter_decode_count[12]):.2f}%```")
        embed2.add_field(name="魔トカゲ", value=f"```試合数: {hunter_match_count[13]}\n勝率: {win_rate(hunter_match_count[13], hunter_win_count[13], hunter_draw_count[13]):.2f}%\n通電率: {decode_rate(hunter_match_count[13], hunter_decode_count[13]):.2f}%```")
        embed2.add_field(name="血の女王", value=f"```試合数: {hunter_match_count[14]}\n勝率: {win_rate(hunter_match_count[14], hunter_win_count[14], hunter_draw_count[14]):.2f}%\n通電率: {decode_rate(hunter_match_count[14], hunter_decode_count[14]):.2f}%```")
        embed2.add_field(name="ガードNo.26", value=f"```試合数: {hunter_match_count[15]}\n勝率: {win_rate(hunter_match_count[15], hunter_win_count[15], hunter_draw_count[15]):.2f}%\n通電率: {decode_rate(hunter_match_count[15], hunter_decode_count[15]):.2f}%```")
        embed2.add_field(name="「使徒」", value=f"```試合数: {hunter_match_count[16]}\n勝率: {win_rate(hunter_match_count[16], hunter_win_count[16], hunter_draw_count[16]):.2f}%\n通電率: {decode_rate(hunter_match_count[16], hunter_decode_count[16]):.2f}%```")
        embed2.add_field(name="ヴァイオリニスト", value=f"```試合数: {hunter_match_count[17]}\n勝率: {win_rate(hunter_match_count[17], hunter_win_count[17], hunter_draw_count[17]):.2f}%\n通電率: {decode_rate(hunter_match_count[17], hunter_decode_count[17]):.2f}%```")
        embed2.add_field(name="彫刻師", value=f"```試合数: {hunter_match_count[18]}\n勝率: {win_rate(hunter_match_count[18], hunter_win_count[18], hunter_draw_count[18]):.2f}%\n通電率: {decode_rate(hunter_match_count[18], hunter_decode_count[18]):.2f}%```")
        embed2.add_field(name="「アンデッド」", value=f"```試合数: {hunter_match_count[19]}\n勝率: {win_rate(hunter_match_count[19], hunter_win_count[19], hunter_draw_count[19]):.2f}%\n通電率: {decode_rate(hunter_match_count[19], hunter_decode_count[19]):.2f}%```")
        embed2.add_field(name="破輪", value=f"```試合数: {hunter_match_count[20]}\n勝率: {win_rate(hunter_match_count[20], hunter_win_count[20], hunter_draw_count[20]):.2f}%\n通電率: {decode_rate(hunter_match_count[20], hunter_decode_count[20]):.2f}%```")
        embed2.add_field(name="漁師", value=f"```試合数: {hunter_match_count[21]}\n勝率: {win_rate(hunter_match_count[21], hunter_win_count[21], hunter_draw_count[21]):.2f}%\n通電率: {decode_rate(hunter_match_count[21], hunter_decode_count[21]):.2f}%```")
        embed2.add_field(name="蝋人形師", value=f"```試合数: {hunter_match_count[22]}\n勝率: {win_rate(hunter_match_count[22], hunter_win_count[22], hunter_draw_count[22]):.2f}%\n通電率: {decode_rate(hunter_match_count[22], hunter_decode_count[22]):.2f}%```")
        embed2.add_field(name="「悪夢」", value=f"```試合数: {hunter_match_count[23]}\n勝率: {win_rate(hunter_match_count[23], hunter_win_count[23], hunter_draw_count[23]):.2f}%\n通電率: {decode_rate(hunter_match_count[23], hunter_decode_count[23]):.2f}%```")
        embed2.add_field(name="書記官", value=f"```試合数: {hunter_match_count[24]}\n勝率: {win_rate(hunter_match_count[24], hunter_win_count[24], hunter_draw_count[24]):.2f}%\n通電率: {decode_rate(hunter_match_count[24], hunter_decode_count[24]):.2f}%```")
        
        embed3 = discord.Embed(
            title=f"3/3\nプレイヤーID: {player_id}\n相手サバイバー: {survivor_name}",
            color=0x00ff00, # フレーム色指定(今回は緑)
        )
        embed3.add_field(name="隠者", value=f"```試合数: {hunter_match_count[25]}\n勝率: {win_rate(hunter_match_count[25], hunter_win_count[25], hunter_draw_count[25]):.2f}%\n通電率: {decode_rate(hunter_match_count[25], hunter_decode_count[25]):.2f}%```")
        embed3.add_field(name="夜の番人", value=f"```試合数: {hunter_match_count[26]}\n勝率: {win_rate(hunter_match_count[26], hunter_win_count[26], hunter_draw_count[26]):.2f}%\n通電率: {decode_rate(hunter_match_count[26], hunter_decode_count[26]):.2f}%```")
        embed3.add_field(name="オペラ歌手", value=f"```試合数: {hunter_match_count[27]}\n勝率: {win_rate(hunter_match_count[27], hunter_win_count[27], hunter_draw_count[27]):.2f}%\n通電率: {decode_rate(hunter_match_count[27], hunter_decode_count[27]):.2f}%```")
        embed3.add_field(name="「フールズ・ゴールド」", value=f"```試合数: {hunter_match_count[28]}\n勝率: {win_rate(hunter_match_count[28], hunter_win_count[28], hunter_draw_count[28]):.2f}%\n通電率: {decode_rate(hunter_match_count[28], hunter_decode_count[28]):.2f}%```")
        embed3.add_field(name="時空の影", value=f"```試合数: {hunter_match_count[29]}\n勝率: {win_rate(hunter_match_count[29], hunter_win_count[29], hunter_draw_count[29]):.2f}%\n通電率: {decode_rate(hunter_match_count[29], hunter_decode_count[29]):.2f}%```")
        embed3.add_field(name="「足萎えの羊」", value=f"```試合数: {hunter_match_count[30]}\n勝率: {win_rate(hunter_match_count[30], hunter_win_count[30], hunter_draw_count[30]):.2f}%\n通電率: {decode_rate(hunter_match_count[30], hunter_decode_count[30]):.2f}%```")
        embed3.add_field(name="「フラバルー」", value=f"```試合数: {hunter_match_count[31]}\n勝率: {win_rate(hunter_match_count[31], hunter_win_count[31], hunter_draw_count[31]):.2f}%\n通電率: {decode_rate(hunter_match_count[31], hunter_decode_count[31]):.2f}%```")
        embed3.add_field(name="ハンター不明", value=f"```試合数: {hunter_match_count[0]}\n勝率: {win_rate(hunter_match_count[0], hunter_win_count[0], hunter_draw_count[0]):.2f}%\n通電率: {decode_rate(hunter_match_count[0], hunter_decode_count[0]):.2f}%```")
        # 1 embed につき 25 field が限界の個数らしい

        # メッセージをDiscordチャンネルに送信
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)
        await ctx.send(embed=embed3)

    except Exception as e:
        await ctx.send(f"エラーが発生しました: {e}")

    finally:
        # データベース接続を閉じる
        conn.close()



# ％を計算する関数、母数が0なら0になる
def decode_rate(match_count, decode_count):
    if match_count == 0:
        rate = 0
    else:
        rate = decode_count / match_count * 100
    return rate

# ％を計算する関数、母数が0なら0になる
def win_rate(match_count, win_count, draw_count):
    if match_count == 0 or match_count == draw_count:
        win_rate = 0
    else:
        win_rate = win_count / (match_count - draw_count) * 100
    return win_rate


# Botの起動
bot.run(TOKEN)


