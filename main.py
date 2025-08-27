import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 구글 인증 키 파일 읽기
with open('google_key.json') as f:
    creds_json = json.load(f)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
gc = gspread.authorize(credentials)

# ✅ [1] 구글 시트 ID 여기에 붙여넣기
SHEET_ID = "1TthaoxGe-etYTXnidvwLMfAGzUlCpn9Ot970aR63VGU"
sheet = gc.open_by_key(SHEET_ID).sheet1

# 디스코드 봇 세팅
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # ✅ 이 줄은 꼭 있어야 해!

bot = commands.Bot(command_prefix="!", intents=intents)  # ✅ 깔끔하게 정리

@bot.event
async def on_ready():
    print(f'✅ 봇 로그인 성공: {bot.user.name}')

    @bot.command()
    async def 명단(ctx):
        import datetime

        ROLE_ORDER = {
            "클랜마스터": 0,
            "운영진": 1,
            "고문": 2,
            "정회원": 3,
            "준회원": 4,
            "일반회원": 5,
            "지인": 6
        }

        guild = ctx.guild
        members = [member async for member in guild.fetch_members(limit=None) if not member.bot]
        print(f"✅ 전체 멤버 수: {len(members)}")

        sheet.clear()
        data = [["번호", "역할군", "닉네임", "아이디", "나이", "마지막 출석일"]]

        # 출석체크 채널 이름 정확히 지정
        check_channel = discord.utils.get(guild.text_channels, name="│：✅⠐출석체크")
        if not check_channel:
            await ctx.send("❗ '✅⠐출석체크' 채널을 찾을 수 없습니다.")
            return

        KST = datetime.timezone(datetime.timedelta(hours=9))
        now_kst = datetime.datetime.now(KST)

        member_rows = []

        for i, member in enumerate(members, start=1):
            display_name = member.display_name
            top_role = member.top_role.name if member.top_role else "없음"

            # 닉네임 파싱
            parts = display_name.split("/")
            if len(parts) == 3:
                age, nickname, game_id = parts
            else:
                age, nickname, game_id = ("-", display_name, "-")

            # 출석 메시지 검색 (출석 or 출첵 포함)
            last_attendance = None
            async for msg in check_channel.history(limit=200, oldest_first=False):
                if msg.author == member and ("출석" in msg.content or "출첵" in msg.content):
                    last_attendance = msg.created_at.astimezone(KST)
                    break

            last_date_str = last_attendance.strftime('%Y-%m-%d') if last_attendance else "없음"

            member_rows.append([
                0,  # 번호는 정렬 후에 다시 부여
                top_role,
                nickname,
                game_id,
                age,
                last_date_str
            ])

        # 역할 순서 기준으로 정렬
        member_rows.sort(key=lambda x: ROLE_ORDER.get(x[1], 999))

        # 정렬 후 번호 다시 부여
        for idx, row in enumerate(member_rows, start=1):
            row[0] = idx
            data.append(row)

        sheet.append_rows(data)
        await ctx.send(f"✅ 총 {len(members)}명의 명단을 역할군 순서로 시트에 저장했어요.")


# ✅ [2] 디스코드 봇 토큰 여기에 붙여넣기
bot.run("MTQwMDEyMzA1NDk5ODQyNTYwMQ.Gac6sQ.V4QIhobuWhANoYL_fD4po15KoMh4yyUVuwxPYo")
