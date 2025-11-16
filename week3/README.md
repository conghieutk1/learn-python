Cấu trúc project gợi ý

week3_github_telegram/
config.json # danh sách repo + optional settings
state.json # file state, auto tạo nếu chưa có
main.py # entrypoint
github_client.py # functions gọi GitHub API
telegram_client.py # functions gửi message Telegram
util.py # hàm load/save json, retry helper
