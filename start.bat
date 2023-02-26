set AI_CHAT_API_PATH=.\API
set AI_CHAT_WEBAPP_PATH=.\Web App

start cmd /k "cd %AI_CHAT_API_PATH% && python main.py"
start cmd /k "cd %AI_CHAT_WEBAPP_PATH% && node index.js"
